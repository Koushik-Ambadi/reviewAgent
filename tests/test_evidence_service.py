from app.services.evidence_service import render_evidence_pack


def test_evidence_pack_is_self_contained_and_escapes_run_content():
    report = {
        "run_id": "run-1",
        "metadata": {
            "module_name": "battery<&>",
            "policy_name": "ABS Default Policy",
            "profile": {"name": "ABS Embedded C Default", "language": "C"},
        },
        "summary": {"failed": 1, "skipped": 0, "passed": 0, "total": 1},
        "stages": [
            {
                "title": "Analysis",
                "inventory": {
                    "source_artifact": "analysis/symbols.json",
                    "parsed_files": 2,
                    "skipped_files": 1,
                    "items": [
                        {
                            "inventory_id": "macros",
                            "label": "Macros",
                            "identified": 7,
                        }
                    ],
                    "audit": {
                        "status": "inventory_initialized",
                        "audited": 0,
                        "pending_approval": 0,
                        "not_audited": 1,
                    },
                    "groups": [
                        {
                            "group_id": "macros",
                            "label": "Macros",
                            "artifacts": [
                                {
                                    "artifact_id": "macro-1",
                                    "name": "MAX_CURRENT",
                                    "location": "src/config.h:12",
                                    "evidence": ["Macro type: value", "Replacement: 100"],
                                    "audit_status": "not_audited",
                                    "audit_reason": None,
                                }
                            ],
                        }
                    ],
                },
                "checks": [],
            },
            {
                "title": "Naming",
                "checks": [
                    {
                        "title": "Function Names",
                        "cases": [
                            {
                                "status": "FAILED",
                                "name": "Bad<Name>",
                                "location": "src/a.c:2",
                                "reasons": ["Must use lower case"],
                            }
                        ],
                    }
                ],
            }
        ],
        "remediation": [
            {
                "title": "Function Names remediation",
                "summary": "Generated 1 rename candidate.",
                "case_results": [
                    {
                        "name": "Battery_get_overlong_current_value",
                        "status": "candidate_ready",
                        "candidate_name": "Battery_get_curr_value",
                    },
                    {
                        "name": "Battery_pending_name",
                        "status": "not_requested",
                        "candidate_name": None,
                    },
                ],
                "suggestions": [
                    {
                        "current_name": "Battery_get_overlong_current_value",
                        "candidate_name": "Battery_get_curr_value",
                        "description": "Shortens the existing semantic description.",
                        "confidence": "medium",
                        "policy_validation": "passed",
                        "verification": "Re-run the naming check.",
                    }
                ],
                "questions": [
                    {
                        "name": "p<&>",
                        "prompt": "What value does this parameter represent?",
                    }
                ],
                "limitations": [
                    {
                        "name": "globalName",
                        "message": "Categorical global segments are deferred.",
                    }
                ],
                "model": {
                    "model": "test-nano",
                    "input_tokens": 120,
                    "output_tokens": 30,
                },
            }
        ],
        "build_result": {},
    }

    document = render_evidence_pack(
        report,
        generated_at="2026-10-08T10:00:00+00:00",
    )

    assert "<!doctype html>" in document
    assert "battery&lt;&amp;&gt;" in document
    assert "Bad&lt;Name&gt;" in document
    assert "Atomic reasons" in document
    assert "7" in document
    assert "Macros" in document
    assert "2 files parsed; 1 file skipped" in document
    assert "Artifact audit register" in document
    assert "MAX_CURRENT" in document
    assert "src/config.h:12" in document
    assert "Replacement: 100" in document
    assert "Case coverage" in document
    assert "Battery_pending_name" in document
    assert "not_requested" in document
    assert "No audit rationale recorded." in document
    assert "1 not audited" in document
    assert "Battery_get_overlong_current_value" in document
    assert "Battery_get_curr_value" in document
    assert "Developer context required" in document
    assert "p&lt;&amp;&gt;" in document
    assert "Categorical global segments are deferred." in document
    assert "test-nano" in document
    assert "not run" in document
    assert "2026-10-08T10:00:00+00:00" in document
    assert "<script" not in document
