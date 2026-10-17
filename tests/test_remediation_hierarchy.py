import json
import tempfile
from pathlib import Path

from app.services.remediation_service import create_remediation
from orchestrator import run_store
from repo_remediation.providers import OpenAIRemediationProvider
from repo_review.pipeline.utils import load_policy


class FakeResponsesClient:
    def __init__(self, cases):
        self.cases = cases
        self.payloads = []

    def create(self, payload):
        self.payloads.append(payload)
        return {
            "id": "resp_hierarchy",
            "model": payload["model"],
            "usage": {
                "input_tokens": 90,
                "output_tokens": 20,
                "total_tokens": 110,
                "output_tokens_details": {"reasoning_tokens": 0},
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


def _failed_case(case_id, name, reason):
    return {
        "case_id": case_id,
        "name": name,
        "location": f"src/module.c:{case_id[-1]}",
        "status": "FAILED",
        "reasons": [reason],
    }


def _report(run_id, check_id, title, cases):
    policy = load_policy("default")
    return {
        "run_id": run_id,
        "policy_version": str(policy["version"]),
        "metadata": {
            "module_name": "shunt",
            "policy_name": policy["metadata"]["name"],
        },
        "stages": [{"checks": [{"check_id": check_id, "title": title, "cases": cases}]}],
    }


def _candidate(case_ref, name, note="Uses visible meaning."):
    return {
        "case_ref": case_ref,
        "disposition": "candidate",
        "candidate": name,
        "confidence": "high",
        "note": note,
        "question": "",
    }


def test_check_request_excludes_case_already_generated_and_keeps_placeholders():
    cases = [
        _failed_case(
            "case-1",
            "Shunt_get_plausibility_currfault",
            "[ABS-SCS-16.1.d] Function name is 32 characters; the maximum is 31.",
        ),
        _failed_case(
            "case-2",
            "Shunt_get_temperature_measurement",
            "[ABS-SCS-16.1.d] Function name is 33 characters; the maximum is 31.",
        ),
    ]
    report = _report("run-hierarchy", "function_names", "Function Names", cases)
    first_client = FakeResponsesClient(
        [_candidate("C1", "Shunt_get_plaus_currfault")]
    )
    second_client = FakeResponsesClient(
        [_candidate("C1", "Shunt_get_temp_measurement")]
    )

    original_workspace = run_store.WORKSPACE_ROOT
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        run_path = workspace / report["run_id"]
        run_path.mkdir()
        (run_path / "report.json").write_text(json.dumps(report), encoding="utf-8")
        run_store.WORKSPACE_ROOT = workspace
        try:
            first = create_remediation(
                run_id=report["run_id"],
                scope="case",
                check_id="function_names",
                case_id="case-1",
                provider=OpenAIRemediationProvider(
                    client=first_client,
                    model="test-nano",
                ),
            )["remediation"]
            first_statuses = [item["status"] for item in first["case_results"]]
            assert first_statuses == [
                "candidate_ready",
                "not_requested",
            ], first_statuses

            combined = create_remediation(
                run_id=report["run_id"],
                scope="check",
                check_id="function_names",
                case_id=None,
                provider=OpenAIRemediationProvider(
                    client=second_client,
                    model="test-nano",
                ),
            )["remediation"]
        finally:
            run_store.WORKSPACE_ROOT = original_workspace

        assert combined["remediation_id"] == first["remediation_id"]
        assert [item["status"] for item in combined["case_results"]] == [
            "candidate_ready",
            "candidate_ready",
        ]
        second_input = json.loads(second_client.payloads[0]["input"][1]["content"])
        assert [item["current_name"] for item in second_input["cases"]] == [
            "Shunt_get_temperature_measurement"
        ]
        stored = json.loads((run_path / "remediation.json").read_text())
        assert len(stored["remediation"]) == 1
        assert len(stored["remediation"][0]["turns"]) == 2
        first_turn, second_turn = stored["remediation"][0]["turns"]
        assert second_turn["parent_turn_id"] == first_turn["turn_id"]


def test_optional_developer_context_avoids_parameter_question_round_trip():
    case = _failed_case(
        "case-p",
        "p",
        "[ABS-SCS-17.e] Parameter name is 1 characters; the minimum is 3.",
    )
    report = _report("run-context", "parameter_names", "Parameter Names", [case])
    client = FakeResponsesClient(
        [_candidate("C1", "payloadByte", "Uses developer-supplied purpose.")]
    )

    original_workspace = run_store.WORKSPACE_ROOT
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        run_path = workspace / report["run_id"]
        run_path.mkdir()
        (run_path / "report.json").write_text(json.dumps(report), encoding="utf-8")
        run_store.WORKSPACE_ROOT = workspace
        try:
            remediation = create_remediation(
                run_id=report["run_id"],
                scope="case",
                check_id="parameter_names",
                case_id="case-p",
                developer_context={
                    "case-p": "Byte position inside the CAN payload."
                },
                provider=OpenAIRemediationProvider(
                    client=client,
                    model="test-nano",
                ),
            )["remediation"]
        finally:
            run_store.WORKSPACE_ROOT = original_workspace

    assert remediation["status"] == "candidate_ready"
    assert len(client.payloads) == 1
    model_input = json.loads(client.payloads[0]["input"][1]["content"])
    assert model_input["cases"][0]["developer_context"].startswith("Byte position")
