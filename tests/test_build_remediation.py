import json
from pathlib import Path

from repo_build.artifact_references import find_successful_artifact_references
from repo_build.intelligence import OpenAIBuildRemediationProvider
from repo_remediation.contracts import RemediationProviderUnavailableError


class FakeBuildResponsesClient:
    def __init__(self):
        self.payloads = []

    def create(self, payload):
        self.payloads.append(payload)
        return {
            "id": "resp-build-test",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "summary": "The toolchain license server is unreachable.",
                                    "root_cause": "The compiler cannot obtain a Green Hills license from the configured host.",
                                    "actions": [
                                        "Restore network access to the configured license host.",
                                        "Retry the build and confirm the compiler validation step passes.",
                                    ],
                                    "verification": "Confirm the next build produces the expected ELF, HEX, and MAP outputs.",
                                    "confidence": "high",
                                }
                            ),
                        }
                    ],
                }
            ],
        }


def test_build_remediation_preserves_captured_strings_and_validates_output():
    client = FakeBuildResponsesClient()
    provider = OpenAIBuildRemediationProvider(client=client, model="test-nano")
    summary, trace = provider.remediate(
        build_result={
            "status": "failed",
            "return_code": 1,
            "build_step": {"status": "failed", "message": "Build failed."},
            "important_diagnostics": ["The License Manager cannot be contacted."],
            "stdout": ["GHS_LMHOST=10.10.20.34:2009"],
            "stderr": ["Reason: toolchain (11100): No licenses available."],
        },
        deterministic_summary={
            "issue_code": "ghs-license-unavailable",
            "primary_issue": "Green Hills toolchain license is unavailable.",
            "evidence": ["The License Manager cannot be contacted."],
        },
    )

    assert summary["status"] == "candidate_ready"
    assert summary["confidence"] == "high"
    assert trace["response"]["id"] == "resp-build-test"
    prompt = json.loads(client.payloads[0]["input"][1]["content"])
    assert prompt["captured_output"]["stderr_tail"] == [
        "Reason: toolchain (11100): No licenses available."
    ]


def test_reference_artifacts_use_relative_paths_and_source_run(tmp_path: Path):
    source_root = tmp_path / "20261005_success" / "shunt" / "out" / "build" / "ghs"
    source_root.mkdir(parents=True)
    for name in ("shunt-component.elf", "app.hex", "shunt-component.map"):
        (source_root / name).write_bytes(b"artifact")

    references = find_successful_artifact_references(
        tmp_path,
        current_run_id="current",
        module_name="shunt",
    )

    assert {item["relative_path"] for item in references} == {
        "out/build/ghs/app.hex",
        "out/build/ghs/shunt-component.elf",
        "out/build/ghs/shunt-component.map",
    }
    assert all(item["source_run_id"] == "20261005_success" for item in references)
    assert all(item["reference_only"] for item in references)


class UnavailableBuildResponsesClient:
    def create(self, payload):
        raise RemediationProviderUnavailableError("OPENAI_API_KEY is not configured.")


def test_unavailable_build_model_preserves_explicit_unsupported_state():
    provider = OpenAIBuildRemediationProvider(client=UnavailableBuildResponsesClient())
    summary, trace = provider.remediate(
        build_result={"status": "failed", "return_code": 1},
        deterministic_summary={"issue_code": "unclassified-build-failure"},
    )

    assert summary["status"] == "unsupported"
    assert "not configured" in summary["limitation"]
    assert trace["status"] == "provider_error"
