from __future__ import annotations

import json
from typing import Any

from orchestrator.run_store import (
    get_run_path,
    load_report,
    update_report_extension,
    write_json,
)
from repo_remediation import PlaceholderRemediationProvider, RemediationProvider


def create_remediation(
    *,
    run_id: str,
    scope: str,
    check_id: str,
    case_id: str | None,
    provider: RemediationProvider | None = None,
) -> dict[str, Any]:
    report = load_report(run_id)
    check = _find_check(report, check_id)
    failed_cases = [
        case
        for case in check.get("cases", [])
        if str(case.get("status", "")).upper() == "FAILED"
    ]

    if scope == "case":
        if not case_id:
            raise ValueError("case_id is required when scope is 'case'.")
        failed_cases = [
            case for case in failed_cases if case.get("case_id") == case_id
        ]
        if not failed_cases:
            raise LookupError("Failed case not found for this check.")

    if not failed_cases:
        raise LookupError("This check has no failed cases to remediate.")

    result = (provider or PlaceholderRemediationProvider()).suggest(
        run_id=run_id,
        check=check,
        cases=failed_cases,
        scope=scope,
    )
    remediation = _load_remediations(run_id)
    remediation.append(result)
    _write_remediations(run_id, remediation)
    update_report_extension(run_id, "remediation", remediation)

    return {
        "run_id": run_id,
        "remediation": result,
    }


def _find_check(report: dict[str, Any], check_id: str) -> dict[str, Any]:
    for stage in report.get("stages", []):
        for check in stage.get("checks", []):
            if check.get("check_id") == check_id:
                return check
    raise LookupError(f"Check not found: {check_id}")


def _load_remediations(run_id: str) -> list[dict[str, Any]]:
    path = get_run_path(run_id) / "remediation.json"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as remediation_file:
        stored = json.load(remediation_file)
    return list(stored.get("remediation", []))


def _write_remediations(run_id: str, remediation: list[dict[str, Any]]) -> None:
    write_json(
        get_run_path(run_id) / "remediation.json",
        {"run_id": run_id, "remediation": remediation},
    )
