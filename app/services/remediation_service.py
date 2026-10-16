from __future__ import annotations

import json
from typing import Any

from orchestrator.run_store import (
    get_run_path,
    load_report,
    update_report_extension,
    write_json,
)
from repo_remediation import OpenAIRemediationProvider, RemediationProvider
from repo_review.pipeline.utils import load_policy


def create_remediation(
    *,
    run_id: str,
    scope: str,
    check_id: str,
    case_id: str | None,
    remediation_id: str | None = None,
    context_answers: dict[str, str] | None = None,
    provider: RemediationProvider | None = None,
) -> dict[str, Any]:
    report = load_report(run_id)
    check = _find_check(report, check_id)
    check_policy = _load_check_policy(report, check_id)
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

    result = (provider or OpenAIRemediationProvider()).suggest(
        run_id=run_id,
        module_name=str((report.get("metadata") or {}).get("module_name") or ""),
        check=check,
        check_policy=check_policy,
        cases=failed_cases,
        scope=scope,
        context_answers=context_answers,
    )
    remediation = _load_remediations(run_id)
    remediation = _upsert_remediation(
        remediation,
        result,
        remediation_id=remediation_id,
        check_id=check_id,
        scope=scope,
    )
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


def _load_check_policy(report: dict[str, Any], check_id: str) -> Any:
    """Resolve the only active policy and reject historical version drift."""
    policy = load_policy("default")
    report_version = str(report.get("policy_version") or "")
    loaded_version = str(policy.get("version") or "")
    if report_version != loaded_version:
        raise ValueError(
            "The exact policy version for this report is unavailable; rerun the "
            "review before requesting model remediation."
        )

    policy_name = str((report.get("metadata") or {}).get("policy_name") or "")
    loaded_name = str((policy.get("metadata") or {}).get("name") or "")
    if policy_name and loaded_name and policy_name != loaded_name:
        raise ValueError(
            "The report policy does not match the configured remediation policy."
        )

    checks = policy["checks"]
    if check_id in checks["repository_structure"]:
        return checks["repository_structure"][check_id]
    if check_id in checks["symbol_naming"]:
        return checks["symbol_naming"][check_id]
    raise LookupError(f"Policy not found for check: {check_id}")


def _upsert_remediation(
    remediation: list[dict[str, Any]],
    result: dict[str, Any],
    *,
    remediation_id: str | None,
    check_id: str,
    scope: str,
) -> list[dict[str, Any]]:
    if not remediation_id:
        return [*remediation, result]

    updated = list(remediation)
    for index, existing in enumerate(updated):
        if existing.get("remediation_id") != remediation_id:
            continue
        if existing.get("check_id") != check_id or existing.get("scope") != scope:
            raise ValueError(
                "Remediation continuation does not match the original request."
            )
        result["remediation_id"] = remediation_id
        result["generated_at"] = existing.get(
            "generated_at", result["generated_at"]
        )
        updated[index] = result
        return updated
    raise LookupError(f"Remediation not found: {remediation_id}")


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
