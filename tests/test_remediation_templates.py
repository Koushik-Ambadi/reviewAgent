import json
import tempfile
from pathlib import Path

import httpx

from app.services.remediation_service import _upsert_remediation, create_remediation
from orchestrator import run_store
from repo_remediation.providers import (
    OpenAIRemediationProvider,
    OpenAIResponsesClient,
    PlaceholderRemediationProvider,
    RemediationProviderUnavailableError,
)
from repo_review.pipeline.utils import load_policy


class FakeResponsesClient:
    def __init__(self, cases):
        self.cases = cases
        self.payloads = []

    def create(self, payload):
        self.payloads.append(payload)
        return {
            "id": "resp_test",
            "model": payload["model"],
            "usage": {
                "input_tokens": 120,
                "output_tokens": 30,
                "output_tokens_details": {"reasoning_tokens": 5},
            },
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps({"cases": self.cases}),
                        }
                    ],
                }
            ],
        }


def _policy(check_id):
    return load_policy("default")["checks"]["symbol_naming"][check_id]


def _case(case_id, name, *reasons):
    return {
        "case_id": case_id,
        "name": name,
        "location": "src/module.c:10",
        "reasons": list(reasons),
    }


def test_function_length_batch_calls_model_once_and_validates_candidate():
    client = FakeResponsesClient(
        [
            {
                "case_id": "case-1",
                "disposition": "candidate",
                "candidate": "Shunt_get_plaus_currfault",
                "confidence": "medium",
                "note": "Shortens plausibility while retaining current-fault meaning.",
                "question": "",
            }
        ]
    )
    provider = OpenAIRemediationProvider(client=client, model="test-nano")

    result = provider.suggest(
        run_id="run-1",
        module_name="shunt",
        check={"check_id": "function_names", "title": "Function Names"},
        check_policy=_policy("function_names"),
        cases=[
            _case(
                "case-1",
                "Shunt_get_plausibility_currfault",
                "[ABS-SCS-16.1.d] Function name is 32 characters; the maximum is 31.",
            )
        ],
        scope="check",
    )

    assert result["status"] == "candidate_ready"
    assert result["suggestions"][0]["candidate_name"] == "Shunt_get_plaus_currfault"
    assert result["suggestions"][0]["policy_validation"] == "passed"
    assert result["model"]["input_tokens"] == 120
    assert len(client.payloads) == 1

    model_input = json.loads(client.payloads[0]["input"][1]["content"])
    assert "policy" in model_input
    assert "reasons" not in model_input["cases"][0]
    assert model_input["cases"][0]["failed_rule_ids"] == ["ABS-SCS-16.1.d"]


def test_single_letter_parameter_requests_context_without_model_call():
    client = FakeResponsesClient([])
    provider = OpenAIRemediationProvider(client=client, model="test-nano")

    result = provider.suggest(
        run_id="run-1",
        module_name="shunt",
        check={"check_id": "parameter_names", "title": "Parameter Names"},
        check_policy=_policy("parameter_names"),
        cases=[
            _case(
                "case-p",
                "p",
                "[ABS-SCS-17.e] Parameter name is 1 characters; the minimum is 3.",
            )
        ],
        scope="case",
    )

    assert result["status"] == "input_required"
    assert result["questions"][0]["field"] == "parameter_purpose"
    assert result["suggestions"] == []
    assert client.payloads == []


def test_parameter_context_continuation_generates_candidate():
    client = FakeResponsesClient(
        [
            {
                "case_id": "case-p",
                "disposition": "candidate",
                "candidate": "payloadByte",
                "confidence": "high",
                "note": "Uses the supplied payload-byte purpose.",
                "question": "",
            }
        ]
    )
    provider = OpenAIRemediationProvider(client=client, model="test-nano")
    question_id = "case-p:parameter_purpose"

    result = provider.suggest(
        run_id="run-1",
        module_name="shunt",
        check={"check_id": "parameter_names", "title": "Parameter Names"},
        check_policy=_policy("parameter_names"),
        cases=[
            _case(
                "case-p",
                "p",
                "[ABS-SCS-17.e] Parameter name is 1 characters; the minimum is 3.",
            )
        ],
        scope="case",
        context_answers={question_id: "The byte position inside the CAN payload."},
    )

    assert result["status"] == "candidate_ready"
    assert result["suggestions"][0]["candidate_name"] == "payloadByte"
    model_input = json.loads(client.payloads[0]["input"][1]["content"])
    assert model_input["cases"][0]["developer_context"].startswith(
        "The byte position"
    )


def test_model_question_can_be_answered_on_a_follow_up():
    question_client = FakeResponsesClient(
        [
            {
                "case_id": "case-f",
                "disposition": "context_required",
                "candidate": "",
                "confidence": "low",
                "note": "The current words do not identify the intended action.",
                "question": "What operation does this function perform?",
            }
        ]
    )
    provider = OpenAIRemediationProvider(client=question_client, model="test-nano")
    case = _case(
        "case-f",
        "Shunt_process_data_value",
        "[ABS-SCS-16.1.d] Function name is 32 characters; the maximum is 31.",
    )

    pending = provider.suggest(
        run_id="run-1",
        module_name="shunt",
        check={"check_id": "function_names", "title": "Function Names"},
        check_policy=_policy("function_names"),
        cases=[case],
        scope="case",
    )

    assert pending["status"] == "input_required"
    question_id = pending["questions"][0]["question_id"]

    answer_client = FakeResponsesClient(
        [
            {
                "case_id": "case-f",
                "disposition": "candidate",
                "candidate": "Shunt_decode_curr",
                "confidence": "high",
                "note": "Uses the supplied current-decoding purpose.",
                "question": "",
            }
        ]
    )
    provider = OpenAIRemediationProvider(client=answer_client, model="test-nano")
    completed = provider.suggest(
        run_id="run-1",
        module_name="shunt",
        check={"check_id": "function_names", "title": "Function Names"},
        check_policy=_policy("function_names"),
        cases=[case],
        scope="case",
        context_answers={question_id: "It decodes the measured current value."},
    )

    assert completed["status"] == "candidate_ready"
    model_input = json.loads(answer_client.payloads[0]["input"][1]["content"])
    assert model_input["cases"][0]["developer_context"].startswith("It decodes")


def test_global_categorical_failure_is_deferred_without_model_call():
    client = FakeResponsesClient([])
    provider = OpenAIRemediationProvider(client=client, model="test-nano")

    result = provider.suggest(
        run_id="run-1",
        module_name="shunt",
        check={
            "check_id": "global_variable_names",
            "title": "Global Variable Names",
        },
        check_policy=_policy("global_variable_names"),
        cases=[
            _case(
                "case-g",
                "shunt_U",
                "[ABS-POLICY-GLOBAL-DATA-TYPE] 's' is not an allowed data type code.",
                "[ABS-POLICY-GLOBAL-UNIT] 'U' is not an allowed unit code.",
            )
        ],
        scope="case",
    )

    assert result["status"] == "unsupported"
    assert "deferred" in result["limitations"][0]["message"]
    assert client.payloads == []


def test_remediation_continuation_replaces_original_record():
    original = {
        "remediation_id": "rem-1",
        "check_id": "parameter_names",
        "scope": "case",
        "generated_at": "2026-10-16T01:00:00+00:00",
    }
    replacement = {
        "remediation_id": "new-id",
        "check_id": "parameter_names",
        "scope": "case",
        "generated_at": "2026-10-16T02:00:00+00:00",
    }

    result = _upsert_remediation(
        [original],
        replacement,
        remediation_id="rem-1",
        check_id="parameter_names",
        scope="case",
    )

    assert len(result) == 1
    assert result[0]["remediation_id"] == "rem-1"
    assert result[0]["generated_at"] == original["generated_at"]


def test_service_persists_and_replaces_context_continuation():
    policy = load_policy("default")
    report = {
        "run_id": "run-remediation",
        "policy_version": str(policy["version"]),
        "metadata": {
            "module_name": "shunt",
            "policy_name": policy["metadata"]["name"],
        },
        "stages": [
            {
                "checks": [
                    {
                        "check_id": "parameter_names",
                        "title": "Parameter Names",
                        "cases": [
                            {
                                **_case(
                                    "case-p",
                                    "p",
                                    "[ABS-SCS-17.e] Parameter name is 1 characters; the minimum is 3.",
                                ),
                                "status": "FAILED",
                            }
                        ],
                    }
                ]
            }
        ],
    }
    original_workspace = run_store.WORKSPACE_ROOT
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        run_path = workspace / report["run_id"]
        run_path.mkdir()
        (run_path / "report.json").write_text(json.dumps(report), encoding="utf-8")
        run_store.WORKSPACE_ROOT = workspace
        try:
            pending = create_remediation(
                run_id=report["run_id"],
                scope="case",
                check_id="parameter_names",
                case_id="case-p",
                provider=OpenAIRemediationProvider(
                    client=FakeResponsesClient([]), model="test-nano"
                ),
            )["remediation"]
            assert pending["status"] == "input_required"

            candidate_client = FakeResponsesClient(
                [
                    {
                        "case_id": "case-p",
                        "disposition": "candidate",
                        "candidate": "payloadByte",
                        "confidence": "high",
                        "note": "Uses the supplied purpose.",
                        "question": "",
                    }
                ]
            )
            completed = create_remediation(
                run_id=report["run_id"],
                scope="case",
                check_id="parameter_names",
                case_id="case-p",
                remediation_id=pending["remediation_id"],
                context_answers={
                    pending["questions"][0]["question_id"]: (
                        "The byte position inside the CAN payload."
                    )
                },
                provider=OpenAIRemediationProvider(
                    client=candidate_client, model="test-nano"
                ),
            )["remediation"]
        finally:
            run_store.WORKSPACE_ROOT = original_workspace

        stored = json.loads((run_path / "remediation.json").read_text())
        persisted_report = json.loads((run_path / "report.json").read_text())
        assert completed["remediation_id"] == pending["remediation_id"]
        assert len(stored["remediation"]) == 1
        assert stored["remediation"][0]["status"] == "candidate_ready"
        assert len(persisted_report["remediation"]) == 1


def test_responses_client_retries_one_transient_failure():
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(503, json={"error": {"message": "busy"}})
        return httpx.Response(200, json={"id": "resp-ok", "output": []})

    client = OpenAIResponsesClient(
        api_key="test-key",
        timeout_seconds=1,
        transport=httpx.MockTransport(handler),
    )

    assert client.create({"model": "test"})["id"] == "resp-ok"
    assert len(calls) == 2


def test_responses_client_requires_environment_key():
    client = OpenAIResponsesClient(api_key="")
    client.api_key = ""
    try:
        client.create({"model": "test"})
    except RemediationProviderUnavailableError as error:
        assert "OPENAI_API_KEY" in str(error)
    else:
        raise AssertionError("Expected missing-key failure")


def test_placeholder_provider_remains_available_for_offline_callers():
    remediation = PlaceholderRemediationProvider().suggest(
        run_id="run-1",
        check={"check_id": "required_paths", "title": "Required Paths"},
        cases=[
            _case(
                "case-1",
                "src/module.c",
                "Required path is missing: src/module.c",
            )
        ],
        scope="case",
    )

    assert remediation["provider"] == "policy-template-remediation-v2"
    assert remediation["suggestions"][0]["actions"]
