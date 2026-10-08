from repo_build.intelligence import PlaceholderBuildIntelligenceProvider


def test_green_hills_license_failure_is_classified_before_generic_fallback():
    result = {
        "return_code": 1,
        "important_diagnostics": ["The License Manager cannot be contacted."],
        "artifact_manifest": [],
        "stdout": [
            "GHS_LMHOST=10.10.20.34:2009",
            "CMake Error: compiler is not able to compile a simple test program",
        ],
        "stderr": ["The License Manager cannot be contacted."],
    }

    summary = PlaceholderBuildIntelligenceProvider().summarize(result)

    assert summary["issue_code"] == "ghs-license-unavailable"
    assert summary["primary_issue"] == "Green Hills toolchain license is unavailable."
    assert "GHS_LMHOST is configured as 10.10.20.34:2009." in summary["evidence"]
    assert len(summary["next_actions"]) == 3


def test_unknown_failure_keeps_explicit_generic_fallback():
    result = {
        "return_code": 1,
        "important_diagnostics": ["unexpected tool output"],
        "artifact_manifest": [],
        "stdout": [],
        "stderr": [],
    }

    summary = PlaceholderBuildIntelligenceProvider().summarize(result)

    assert summary["issue_code"] == "unclassified-build-failure"
    assert summary["evidence"] == ["unexpected tool output"]
