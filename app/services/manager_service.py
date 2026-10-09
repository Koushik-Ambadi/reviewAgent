from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from orchestrator.config import WORKSPACE_ROOT


class ManagerModuleNotFoundError(LookupError):
    """Raised when no persisted reports exist for a module."""


class ManagerRunNotFoundError(LookupError):
    """Raised when a comparison run is not part of the selected module."""


def get_portfolio(workspace_root: Path = WORKSPACE_ROOT) -> dict[str, Any]:
    reports, ignored_reports = _load_reports(workspace_root)
    latest_reports = [_module_reports(items)[0] for items in _group_by_module(reports).values()]
    latest_reports.sort(key=_report_sort_key, reverse=True)
    modules = [_run_summary(report) for report in latest_reports]
    history_by_module = _group_by_module(reports)

    for module in modules:
        history = _module_reports(history_by_module[module["module_key"]])
        module["run_count"] = len(history)
        module["previous_run_id"] = (
            _run_id(history[1]) if len(history) > 1 else None
        )

    exceptions = [
        finding
        for report in latest_reports
        for finding in _failed_cases(report)
    ]
    aggregates = {
        "modules": len(modules),
        "runs": len(reports),
        "latest_passed": sum(module["summary"]["passed"] for module in modules),
        "latest_failed": sum(module["summary"]["failed"] for module in modules),
        "latest_skipped": sum(module["summary"]["skipped"] for module in modules),
        "latest_total": sum(module["summary"]["total"] for module in modules),
        "modules_with_failures": sum(
            1 for module in modules if module["summary"]["failed"] > 0
        ),
        "builds_passed": sum(
            1 for module in modules if module["build_status"] == "passed"
        ),
        "builds_failed": sum(
            1 for module in modules if module["build_status"] == "failed"
        ),
        "builds_not_run": sum(
            1 for module in modules if module["build_status"] == "not_run"
        ),
        "artifacts": sum(module["artifact_count"] for module in modules),
        "remediations": sum(module["remediation_count"] for module in modules),
    }

    return {
        "source": {
            "authority": "persisted RunResult reports",
            "workspace": str(workspace_root),
            "ignored_reports": ignored_reports,
            "recalculated_checks": False,
        },
        "aggregates": aggregates,
        "modules": modules,
        "exception_queue": {
            "mode": "workflow_preview",
            "persisted": False,
            "total_failed_cases": len(exceptions),
            "groups": _exception_groups(exceptions),
            "items": exceptions,
        },
        "ownership_preview": [
            {
                "module_name": module["module_name"],
                "owner": "Unassigned",
                "status": "preview",
                "actions": ["assign owner", "create ticket"],
                "persisted": False,
            }
            for module in modules
        ],
        "workflow_preview": _workflow_preview(),
        "insights": _placeholder_insights(aggregates),
    }


def get_module(
    module_name: str,
    workspace_root: Path = WORKSPACE_ROOT,
) -> dict[str, Any]:
    reports, _ = _load_reports(workspace_root)
    matches = [
        report
        for report in reports
        if _module_name(report).casefold() == module_name.casefold()
    ]
    if not matches:
        raise ManagerModuleNotFoundError(f"Module not found: {module_name}")

    history = _module_reports(matches)
    latest = history[0]
    response = {
        "module_name": _module_name(latest),
        "run_count": len(history),
        "latest_run": _run_summary(latest),
        "runs": [_run_summary(report) for report in history],
        "failed_cases": list(_failed_cases(latest)),
        "comparison_defaults": {
            "base_run_id": _run_id(history[1]) if len(history) > 1 else None,
            "target_run_id": _run_id(history[0]),
            "available": len(history) > 1,
        },
        "ownership_preview": {
            "owner": "Unassigned",
            "persisted": False,
            "actions": ["assign selected failures", "create ticket"],
        },
        "insights": _placeholder_insights(
            {"latest_failed": _summary(latest)["failed"]},
            module_name=_module_name(latest),
        ),
    }
    return response


def compare_module_runs(
    module_name: str,
    base_run_id: str | None = None,
    target_run_id: str | None = None,
    workspace_root: Path = WORKSPACE_ROOT,
) -> dict[str, Any]:
    module = get_module(module_name, workspace_root)
    if (base_run_id is None) != (target_run_id is None):
        raise ValueError("Provide both base_run_id and target_run_id.")
    if base_run_id is None:
        defaults = module["comparison_defaults"]
        if not defaults["available"]:
            raise ValueError("At least two module runs are required for comparison.")
        base_run_id = defaults["base_run_id"]
        target_run_id = defaults["target_run_id"]
    if base_run_id == target_run_id:
        raise ValueError("Choose two different runs to compare.")

    reports, _ = _load_reports(workspace_root)
    module_reports = {
        _run_id(report): report
        for report in reports
        if _module_name(report).casefold() == module_name.casefold()
    }
    missing = [
        run_id
        for run_id in (base_run_id, target_run_id)
        if run_id not in module_reports
    ]
    if missing:
        raise ManagerRunNotFoundError(
            f"Run does not belong to module {module_name}: {', '.join(missing)}"
        )

    base = module_reports[base_run_id]
    target = module_reports[target_run_id]
    base_failed = {_case_key(item): item for item in _failed_cases(base)}
    target_failed = {_case_key(item): item for item in _failed_cases(target)}
    base_checks = _check_summaries(base)
    target_checks = _check_summaries(target)
    check_ids = sorted(set(base_checks) | set(target_checks))

    return {
        "module_name": _module_name(target),
        "base": _run_summary(base),
        "target": _run_summary(target),
        "summary_delta": _count_delta(_summary(base), _summary(target)),
        "build_changed": _build_status(base) != _build_status(target),
        "artifact_delta": _artifact_count(target) - _artifact_count(base),
        "remediation_delta": len(target.get("remediation") or [])
        - len(base.get("remediation") or []),
        "checks": [
            {
                "check_id": check_id,
                "title": (
                    target_checks.get(check_id) or base_checks.get(check_id)
                )["title"],
                "base": (base_checks.get(check_id) or _empty_summary())["summary"],
                "target": (target_checks.get(check_id) or _empty_summary())["summary"],
                "delta": _count_delta(
                    (base_checks.get(check_id) or _empty_summary())["summary"],
                    (target_checks.get(check_id) or _empty_summary())["summary"],
                ),
            }
            for check_id in check_ids
        ],
        "failures": {
            "new": [target_failed[key] for key in sorted(target_failed.keys() - base_failed.keys())],
            "resolved": [base_failed[key] for key in sorted(base_failed.keys() - target_failed.keys())],
            "unchanged_count": len(base_failed.keys() & target_failed.keys()),
        },
        "interpretation": (
            "Deltas are target minus base. Case matching uses persisted case IDs "
            "with a report-visible fallback for legacy records."
        ),
    }


def _load_reports(workspace_root: Path) -> tuple[list[dict[str, Any]], int]:
    reports: list[dict[str, Any]] = []
    ignored = 0
    if not workspace_root.is_dir():
        return reports, ignored
    for path in sorted(workspace_root.glob("*/report.json")):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            ignored += 1
            continue
        if not isinstance(report, dict):
            ignored += 1
            continue
        report["_manager_run_id"] = str(
            report.get("run_id")
            or (report.get("metadata") or {}).get("run_id")
            or path.parent.name
        )
        reports.append(report)
    return reports, ignored


def _group_by_module(
    reports: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for report in reports:
        grouped[_module_name(report).casefold()].append(report)
    return grouped


def _module_reports(reports: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(reports, key=_report_sort_key, reverse=True)


def _report_sort_key(report: dict[str, Any]) -> tuple[float, str]:
    generated_at = str((report.get("metadata") or {}).get("generated_at") or "")
    try:
        timestamp = datetime.fromisoformat(generated_at.replace("Z", "+00:00")).timestamp()
    except ValueError:
        timestamp = 0.0
    return timestamp, _run_id(report)


def _run_id(report: dict[str, Any]) -> str:
    return str(report.get("_manager_run_id") or report.get("run_id") or "")


def _module_name(report: dict[str, Any]) -> str:
    return str((report.get("metadata") or {}).get("module_name") or "Unknown module")


def _summary(report: dict[str, Any]) -> dict[str, int]:
    source = report.get("summary") or {}
    values = {
        key: int(source.get(key) or 0)
        for key in ("passed", "failed", "skipped", "total")
    }
    if not values["total"]:
        values["total"] = values["passed"] + values["failed"] + values["skipped"]
    return values


def _run_summary(report: dict[str, Any]) -> dict[str, Any]:
    metadata = report.get("metadata") or {}
    summary = _summary(report)
    return {
        "run_id": _run_id(report),
        "module_name": _module_name(report),
        "module_key": _module_name(report).casefold(),
        "generated_at": metadata.get("generated_at"),
        "status": report.get("status") or "UNKNOWN",
        "compliance_status": (
            "failed" if summary["failed"] else "passed" if summary["total"] else "not_run"
        ),
        "summary": summary,
        "build_status": _build_status(report),
        "artifact_count": _artifact_count(report),
        "remediation_count": len(report.get("remediation") or []),
        "policy_version": report.get("policy_version"),
        "profile": metadata.get("profile") or {},
    }


def _build_status(report: dict[str, Any]) -> str:
    build = report.get("build_result") or {}
    value = str(
        build.get("status")
        or (build.get("build_step") or {}).get("status")
        or "not_run"
    ).lower().replace(" ", "_")
    if value in {"success", "succeeded", "completed"}:
        return "passed"
    if value in {"failure", "error"}:
        return "failed"
    return value


def _artifact_count(report: dict[str, Any]) -> int:
    return len((report.get("build_result") or {}).get("artifact_manifest") or [])


def _failed_cases(report: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for stage in report.get("stages") or []:
        for check in stage.get("checks") or []:
            for index, case in enumerate(check.get("cases") or []):
                if str(case.get("status") or "").upper() != "FAILED":
                    continue
                yield {
                    "run_id": _run_id(report),
                    "module_name": _module_name(report),
                    "stage_id": stage.get("stage_id") or stage.get("title"),
                    "stage_title": stage.get("title") or stage.get("stage_id"),
                    "check_id": check.get("check_id") or check.get("title"),
                    "check_title": check.get("title") or check.get("check_id"),
                    "case_id": case.get("case_id"),
                    "name": case.get("name"),
                    "location": case.get("location"),
                    "reasons": case.get("reasons") or [],
                    "case_index": index,
                }


def _case_key(case: dict[str, Any]) -> str:
    return str(
        case.get("case_id")
        or "|".join(
            str(case.get(key) or "")
            for key in ("stage_id", "check_id", "location", "name", "case_index")
        )
    )


def _exception_groups(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in items:
        key = f'{item["module_name"]}:{item["stage_id"]}:{item["check_id"]}'
        group = grouped.setdefault(
            key,
            {
                "group_id": key,
                "module_name": item["module_name"],
                "stage_title": item["stage_title"],
                "check_title": item["check_title"],
                "failed": 0,
            },
        )
        group["failed"] += 1
    return sorted(
        grouped.values(),
        key=lambda item: (-item["failed"], item["module_name"], item["check_title"]),
    )


def _check_summaries(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for stage in report.get("stages") or []:
        for check in stage.get("checks") or []:
            check_id = str(check.get("check_id") or check.get("title") or "")
            values[check_id] = {
                "title": check.get("title") or check_id,
                "summary": {
                    key: int((check.get("summary") or {}).get(key) or 0)
                    for key in ("passed", "failed", "skipped", "total")
                },
            }
    return values


def _empty_summary() -> dict[str, Any]:
    return {"title": "", "summary": {"passed": 0, "failed": 0, "skipped": 0, "total": 0}}


def _count_delta(base: dict[str, int], target: dict[str, int]) -> dict[str, int]:
    return {
        key: int(target.get(key) or 0) - int(base.get(key) or 0)
        for key in ("passed", "failed", "skipped", "total")
    }


def _workflow_preview() -> dict[str, Any]:
    return {
        "mode": "workflow_preview",
        "persisted": False,
        "approvals": {
            "pending": 3,
            "historical": 12,
            "label": "Placeholder values — approval workflow is not connected.",
        },
        "delivery": {
            "pull_request": "not_connected",
            "continuous_integration": "not_connected",
            "label": "Future PR and CI status",
        },
        "ticketing": {
            "status": "not_connected",
            "label": "Owner and ticket actions are preview-only.",
        },
    }


def _placeholder_insights(
    aggregates: dict[str, Any],
    *,
    module_name: str | None = None,
) -> list[dict[str, Any]]:
    scope = module_name or "portfolio"
    failed = int(aggregates.get("latest_failed") or 0)
    return [
        {
            "insight_id": f"{scope.casefold()}-failure-focus",
            "source": "placeholder",
            "kind": "risk",
            "scope": scope,
            "title": "Failure concentration",
            "summary": f"{failed} failed cases are available for prioritization.",
            "evidence": [],
            "actions": ["Review grouped exceptions", "Assign an owner"],
            "status": "preview",
        },
        {
            "insight_id": f"{scope.casefold()}-remediation-ready",
            "source": "placeholder",
            "kind": "remediation",
            "scope": scope,
            "title": "Intelligence layer placeholder",
            "summary": (
                "This wrapper can later carry deterministic remediation or "
                "model-generated insight without changing the manager UI."
            ),
            "evidence": [],
            "actions": [],
            "status": "preview",
        },
    ]
