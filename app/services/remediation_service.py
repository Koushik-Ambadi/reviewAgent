from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from orchestrator.run_store import (
    get_run_path,
    load_report,
    update_report_extension,
    write_json,
)
from repo_remediation import (
    OpenAIRemediationProvider,
    RemediationProvider,
    RemediationProviderError,
)
from repo_remediation.hierarchy import (
    aggregate_status,
    flatten_case_results,
    merge_case_results,
    normalize_case_results,
)
from repo_review.pipeline.utils import load_policy


def create_remediation(
    *,
    run_id: str,
    scope: str,
    check_id: str,
    case_id: str | None,
    remediation_id: str | None = None,
    context_answers: dict[str, str] | None = None,
    developer_context: dict[str, str] | None = None,
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
        selected_cases = [
            case for case in failed_cases if case.get("case_id") == case_id
        ]
        if not selected_cases:
            raise LookupError("Failed case not found for this check.")

    if not failed_cases:
        raise LookupError("This check has no failed cases to remediate.")

    remediation = _load_remediations(run_id)
    existing = (
        _find_continuation(
            remediation,
            remediation_id=remediation_id,
            check_id=check_id,
        )
        if remediation_id
        else _find_check_remediation(remediation, check_id)
    )
    case_results = normalize_case_results(existing, failed_cases)
    supplied_context = _validated_developer_context(
        developer_context or {},
        failed_cases,
    )
    merged_answers = dict(context_answers or {})
    merged_answers.update(
        {
            f"{target_case_id}:developer_context": value
            for target_case_id, value in supplied_context.items()
        }
    )
    target_case_ids = _target_case_ids(
        scope=scope,
        case_id=case_id,
        case_results=case_results,
        continuation=existing is not None,
        context_answers=merged_answers,
    )
    target_cases = [
        case for case in failed_cases if str(case.get("case_id")) in target_case_ids
    ]
    if not target_cases and existing:
        return {"run_id": run_id, "remediation": existing}
    if not target_cases:
        raise LookupError("No unremediated failed cases remain for this check.")
    try:
        result = (provider or OpenAIRemediationProvider()).suggest(
            run_id=run_id,
            module_name=str((report.get("metadata") or {}).get("module_name") or ""),
            check=check,
            check_policy=check_policy,
            cases=target_cases,
            scope=scope,
            context_answers=merged_answers,
        )
    except RemediationProviderError as error:
        if error.call_trace:
            failed_turn = error.call_trace
            failed_turn["parent_turn_id"] = (
                existing.get("latest_turn_id") if existing else None
            )
            _append_call_log(
                run_id,
                (existing or {}).get("remediation_id")
                or remediation_id
                or uuid4().hex,
                failed_turn,
            )
        raise

    provider_case_results = list(result.get("case_results") or [])
    result["case_results"] = merge_case_results(
        failed_cases,
        case_results,
        provider_case_results,
    )
    suggestions, questions, limitations = flatten_case_results(
        result["case_results"]
    )
    result["scope"] = "check"
    result["case_id"] = None
    result["affected_cases"] = [
        {
            "case_id": case["case_id"],
            "name": case.get("name", "Unnamed case"),
            "location": case.get("location", ""),
            "reasons": list(case.get("reasons", [])),
        }
        for case in failed_cases
    ]
    result["suggestions"] = suggestions
    result["questions"] = questions
    result["limitations"] = limitations
    result["status"] = aggregate_status(result["case_results"])
    result["summary"] = _case_result_summary(result["case_results"])

    new_turns = list(result.get("turns") or [])
    persisted_remediation_id = existing.get("remediation_id") if existing else None
    remediation = _upsert_remediation(
        remediation,
        result,
        remediation_id=persisted_remediation_id,
        check_id=check_id,
    )
    for turn in new_turns:
        _append_call_log(run_id, result["remediation_id"], turn)
        _append_metrics_log(run_id, result["remediation_id"], turn)
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
) -> list[dict[str, Any]]:
    if not remediation_id:
        _link_new_turns(result, parent_turn_id=None)
        return [*remediation, result]

    updated = list(remediation)
    for index, existing in enumerate(updated):
        if existing.get("remediation_id") != remediation_id:
            continue
        _validate_continuation(existing, check_id=check_id)
        prior_turns = list(existing.get("turns") or [])
        new_turns = list(result.get("turns") or [])
        _link_new_turns(
            result,
            parent_turn_id=existing.get("latest_turn_id"),
        )
        result["remediation_id"] = remediation_id
        result["generated_at"] = existing.get(
            "generated_at", result["generated_at"]
        )
        result["turns"] = [*prior_turns, *new_turns]
        updated[index] = result
        return updated
    raise LookupError(f"Remediation not found: {remediation_id}")


def _find_continuation(
    remediation: list[dict[str, Any]],
    *,
    remediation_id: str | None,
    check_id: str,
) -> dict[str, Any] | None:
    if not remediation_id:
        return None
    for existing in remediation:
        if existing.get("remediation_id") == remediation_id:
            _validate_continuation(existing, check_id=check_id)
            return existing
    raise LookupError(f"Remediation not found: {remediation_id}")


def _validate_continuation(
    existing: dict[str, Any],
    *,
    check_id: str,
) -> None:
    if existing.get("check_id") != check_id:
        raise ValueError("Remediation continuation does not match the original request.")


def _find_check_remediation(
    remediation: list[dict[str, Any]],
    check_id: str,
) -> dict[str, Any] | None:
    for existing in reversed(remediation):
        if existing.get("check_id") == check_id:
            return existing
    return None


def _validated_developer_context(
    developer_context: dict[str, str],
    failed_cases: list[dict[str, Any]],
) -> dict[str, str]:
    valid_case_ids = {str(case.get("case_id")) for case in failed_cases}
    unknown = set(developer_context) - valid_case_ids
    if unknown:
        raise ValueError("Developer context contains an unknown failed case ID.")
    return {
        str(case_id): str(value).strip()
        for case_id, value in developer_context.items()
        if str(value).strip()
    }


def _target_case_ids(
    *,
    scope: str,
    case_id: str | None,
    case_results: list[dict[str, Any]],
    continuation: bool,
    context_answers: dict[str, str],
) -> set[str]:
    context_case_ids = {
        str(question_id).split(":", 1)[0]
        for question_id, value in context_answers.items()
        if str(value).strip()
    }
    if scope == "case":
        selected_case_id = str(case_id)
        if not continuation or selected_case_id in context_case_ids:
            return {selected_case_id}
        selected = next(
            (
                item
                for item in case_results
                if str(item.get("case_id")) == selected_case_id
            ),
            None,
        )
        if selected and selected.get("status") == "not_requested":
            return {selected_case_id}
        return set()
    if continuation and context_case_ids:
        return context_case_ids
    return {
        str(item.get("case_id"))
        for item in case_results
        if item.get("status") == "not_requested"
    } | context_case_ids


def _case_result_summary(case_results: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for item in case_results:
        status = str(item.get("status", "not_requested"))
        counts[status] = counts.get(status, 0) + 1
    return (
        f"{counts.get('candidate_ready', 0)} candidate(s), "
        f"{counts.get('input_required', 0)} awaiting context, "
        f"{counts.get('unsupported', 0)} limited, and "
        f"{counts.get('not_requested', 0)} not generated."
    )


def _link_new_turns(
    result: dict[str, Any],
    *,
    parent_turn_id: str | None,
) -> None:
    previous_turn_id = parent_turn_id
    for turn in result.get("turns") or []:
        turn["parent_turn_id"] = previous_turn_id
        previous_turn_id = turn.get("turn_id")
    if previous_turn_id is not None:
        result["latest_turn_id"] = previous_turn_id


def _append_call_log(
    run_id: str,
    remediation_id: str,
    turn: dict[str, Any],
) -> None:
    record = {
        "schema_version": 1,
        "run_id": run_id,
        "remediation_id": remediation_id,
        "recorded_at": datetime.now(UTC).isoformat(),
        "turn": turn,
    }
    path = get_run_path(run_id) / "remediation-calls.jsonl"
    with path.open("a", encoding="utf-8") as call_log:
        call_log.write(json.dumps(record, separators=(",", ":")))
        call_log.write("\n")


def _append_metrics_log(
    run_id: str,
    remediation_id: str,
    turn: dict[str, Any],
) -> None:
    provider_call = turn.get("provider_call") or {}
    metrics = provider_call.get("metrics")
    if not isinstance(metrics, dict):
        return
    request_context = turn.get("request_context") or {}
    record = {
        "schema_version": 1,
        "run_id": run_id,
        "remediation_id": remediation_id,
        "turn_id": turn.get("turn_id"),
        "recorded_at": datetime.now(UTC).isoformat(),
        "check_id": request_context.get("check_id"),
        "case_ids": list(request_context.get("case_ids") or []),
        "status": (turn.get("outcome") or {}).get("status"),
        **metrics,
    }
    path = get_run_path(run_id) / "remediation-metrics.jsonl"
    with path.open("a", encoding="utf-8") as metrics_log:
        metrics_log.write(json.dumps(record, separators=(",", ":")))
        metrics_log.write("\n")


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
