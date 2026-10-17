"""Run/check/case projections for persisted remediation plans."""

from __future__ import annotations

from typing import Any


def project_case_results(
    cases: list[dict[str, Any]],
    *,
    suggestions: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create one uniform result row for every supplied failed case."""
    suggestions_by_case = {
        str(item.get("case_id")): item for item in suggestions
    }
    questions_by_case = {
        str(case_id): item
        for item in questions
        for case_id in item.get("case_ids", [])
    }
    limitations_by_case = {
        str(item.get("case_id")): item for item in limitations
    }
    projected: list[dict[str, Any]] = []
    for case in cases:
        case_id = str(case["case_id"])
        suggestion = suggestions_by_case.get(case_id)
        question = questions_by_case.get(case_id)
        limitation = limitations_by_case.get(case_id)
        status = "not_requested"
        if suggestion:
            status = "candidate_ready"
        elif question:
            status = "input_required"
        elif limitation:
            status = "unsupported"
        projected.append(
            {
                "case_id": case_id,
                "name": case.get("name", "Unnamed case"),
                "location": case.get("location", ""),
                "reasons": list(case.get("reasons", [])),
                "status": status,
                "candidate_name": (
                    suggestion.get("candidate_name") if suggestion else None
                ),
                "confidence": suggestion.get("confidence") if suggestion else None,
                "description": suggestion.get("description", "") if suggestion else "",
                "policy_validation": (
                    suggestion.get("policy_validation") if suggestion else None
                ),
                "question": question,
                "limitation": limitation,
            }
        )
    return projected


def normalize_case_results(
    remediation: dict[str, Any] | None,
    cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Read current and legacy plans through the same per-case projection."""
    if not remediation:
        return project_case_results(
            cases,
            suggestions=[],
            questions=[],
            limitations=[],
        )
    current = remediation.get("case_results")
    if isinstance(current, list):
        return merge_case_results(cases, [], current)
    return project_case_results(
        cases,
        suggestions=list(remediation.get("suggestions") or []),
        questions=list(remediation.get("questions") or []),
        limitations=list(remediation.get("limitations") or []),
    )


def merge_case_results(
    cases: list[dict[str, Any]],
    current: list[dict[str, Any]],
    updates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge case updates while preserving report order and empty placeholders."""
    by_case_id = {
        str(item.get("case_id")): item for item in [*current, *updates]
    }
    empty = project_case_results(
        cases,
        suggestions=[],
        questions=[],
        limitations=[],
    )
    return [by_case_id.get(item["case_id"], item) for item in empty]


def covered_case_ids(case_results: list[dict[str, Any]]) -> set[str]:
    """Return cases already attempted, including context and limitation states."""
    return {
        str(item.get("case_id"))
        for item in case_results
        if item.get("status") != "not_requested"
    }


def flatten_case_results(
    case_results: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Maintain legacy top-level collections as derived compatibility views."""
    suggestions: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    limitations: list[dict[str, Any]] = []
    for item in case_results:
        if item.get("status") == "candidate_ready":
            suggestions.append(
                {
                    "case_id": item["case_id"],
                    "title": f"Rename {item['name']}",
                    "current_name": item["name"],
                    "candidate_name": item.get("candidate_name"),
                    "confidence": item.get("confidence"),
                    "description": item.get("description", ""),
                    "policy_validation": item.get("policy_validation"),
                    "verification": (
                        "Re-run the naming check and compile affected targets after "
                        "an approved rename."
                    ),
                }
            )
        if item.get("question"):
            questions.append(item["question"])
        if item.get("limitation"):
            limitations.append(item["limitation"])
    return suggestions, questions, limitations


def aggregate_status(case_results: list[dict[str, Any]]) -> str:
    """Summarize mixed per-case states without hiding unfinished cases."""
    statuses = {str(item.get("status")) for item in case_results}
    if statuses == {"candidate_ready"}:
        return "candidate_ready"
    if statuses <= {"input_required", "not_requested"} and "input_required" in statuses:
        return "input_required"
    if statuses == {"unsupported"}:
        return "unsupported"
    if statuses == {"not_requested"}:
        return "not_started"
    return "partial"
