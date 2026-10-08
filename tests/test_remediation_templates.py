from repo_remediation.providers import PlaceholderRemediationProvider


def test_required_path_remediation_uses_policy_specific_template():
    remediation = PlaceholderRemediationProvider().suggest(
        run_id="run-1",
        check={"check_id": "required_paths", "title": "Required Paths"},
        cases=[
            {
                "case_id": "case-1",
                "name": "src/module.c",
                "location": "src/module.c",
                "reasons": ["Required path is missing: src/module.c"],
            }
        ],
        scope="case",
    )

    suggestion = remediation["suggestions"][0]
    assert remediation["provider"] == "policy-template-remediation-v2"
    assert "policy-defined location" in suggestion["description"]
    assert suggestion["reasons"] == ["Required path is missing: src/module.c"]
    assert suggestion["actions"]
    assert suggestion["verification"]
