import json

from repo_remediation.generation import (
    RemediationModelProfile,
    compile_remediation_prompt,
    restore_case_ids,
)


def test_prompt_compiler_deduplicates_rules_across_batch_cases():
    compiled = compile_remediation_prompt(
        profile=RemediationModelProfile(
            profile_id="test-profile",
            model="test-nano",
        ),
        check_id="function_names",
        cases=[
            {
                "case_id": "persistent-a",
                "name": "Shunt_Read",
                "failed_rules": [
                    {
                        "rule_id": "LOWERCASE",
                        "text": "Letters after module prefix 'Shunt_' must be lowercase.",
                    }
                ],
            },
            {
                "case_id": "persistent-b",
                "name": "Shunt_Write",
                "failed_rules": [
                    {
                        "rule_id": "LOWERCASE",
                        "text": "Letters after module prefix 'Shunt_' must be lowercase.",
                    }
                ],
            },
        ],
    )

    model_input = json.loads(compiled.payload["input"][1]["content"])
    assert model_input["rules"] == [
        {
            "ref": "R1",
            "text": "Letters after module prefix 'Shunt_' must be lowercase.",
        }
    ]
    assert [case["failed_rules"] for case in model_input["cases"]] == [
        ["R1"],
        ["R1"],
    ]
    assert compiled.case_ref_to_id == {
        "C1": "persistent-a",
        "C2": "persistent-b",
    }


def test_restore_case_ids_rejects_unknown_duplicate_or_missing_refs():
    invalid_results = [
        [{"case_ref": "C9"}],
        [{"case_ref": "C1"}, {"case_ref": "C1"}],
        [{"case_ref": "C1"}],
    ]
    for results in invalid_results:
        try:
            restore_case_ids(
                results,
                {"C1": "persistent-a", "C2": "persistent-b"},
            )
        except ValueError as error:
            assert "case" in str(error).lower()
        else:
            raise AssertionError("Expected an invalid case reference failure")
