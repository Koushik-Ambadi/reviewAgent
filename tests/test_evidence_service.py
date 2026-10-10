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
                        "status": "not_tracked",
                        "audited": None,
                        "pending_approval": None,
                        "not_audited": None,
                    },
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
        "remediation": [],
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
    assert "Audit coverage is not tracked." in document
    assert "not run" in document
    assert "2026-10-08T10:00:00+00:00" in document
    assert "<script" not in document
