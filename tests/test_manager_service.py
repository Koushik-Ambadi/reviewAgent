import json

from app.services.manager_service import (
    compare_module_runs,
    get_module,
    get_portfolio,
)


def _write_report(
    root,
    run_id,
    module,
    generated_at,
    *,
    passed,
    failed,
    case_id,
    build_status=None,
):
    report = {
        "run_id": run_id,
        "metadata": {"module_name": module, "generated_at": generated_at},
        "status": "COMPLETED",
        "summary": {
            "passed": passed,
            "failed": failed,
            "skipped": 0,
            "total": passed + failed,
        },
        "stages": [
            {
                "stage_id": "naming",
                "title": "Naming",
                "checks": [
                    {
                        "check_id": "functions",
                        "title": "Functions",
                        "summary": {
                            "passed": passed,
                            "failed": failed,
                            "skipped": 0,
                            "total": passed + failed,
                        },
                        "cases": (
                            [
                                {
                                    "case_id": case_id,
                                    "status": "FAILED",
                                    "name": case_id,
                                    "location": "src/a.c:1",
                                    "reasons": ["Naming rule failed."],
                                }
                            ]
                            if failed
                            else []
                        ),
                    }
                ],
            }
        ],
        "remediation": [],
        "build_result": {"status": build_status} if build_status else {},
    }
    path = root / run_id
    path.mkdir()
    (path / "report.json").write_text(json.dumps(report), encoding="utf-8")


def test_manager_projects_latest_modules_and_compares_selected_runs(tmp_path):
    _write_report(
        tmp_path,
        "alpha-old",
        "alpha",
        "2026-10-08T10:00:00+00:00",
        passed=8,
        failed=1,
        case_id="resolved",
    )
    _write_report(
        tmp_path,
        "alpha-new",
        "alpha",
        "2026-10-09T10:00:00+00:00",
        passed=9,
        failed=1,
        case_id="new",
        build_status="failed",
    )
    _write_report(
        tmp_path,
        "beta-new",
        "beta",
        "2026-10-09T11:00:00+00:00",
        passed=4,
        failed=0,
        case_id="unused",
        build_status="passed",
    )

    portfolio = get_portfolio(tmp_path)
    alpha = next(item for item in portfolio["modules"] if item["module_name"] == "alpha")
    assert portfolio["aggregates"]["modules"] == 2
    assert portfolio["aggregates"]["latest_failed"] == 1
    assert alpha["run_id"] == "alpha-new"
    assert alpha["previous_run_id"] == "alpha-old"
    assert portfolio["workflow_preview"]["persisted"] is False

    module = get_module("alpha", tmp_path)
    assert [item["run_id"] for item in module["runs"]] == ["alpha-new", "alpha-old"]
    assert module["comparison_defaults"]["available"] is True

    comparison = compare_module_runs(
        "alpha",
        base_run_id="alpha-old",
        target_run_id="alpha-new",
        workspace_root=tmp_path,
    )
    assert comparison["summary_delta"]["passed"] == 1
    assert comparison["build_changed"] is True
    assert [item["case_id"] for item in comparison["failures"]["new"]] == ["new"]
    assert [item["case_id"] for item in comparison["failures"]["resolved"]] == [
        "resolved"
    ]
