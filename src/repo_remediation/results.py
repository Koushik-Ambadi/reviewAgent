"""Provider output mapping and report-compatible remediation views."""

from __future__ import annotations

import re
from typing import Any

from repo_remediation.contracts import RemediationProviderError
from repo_remediation.generation import validate_candidate


def map_model_results(
    *,
    check_id: str,
    module_name: str,
    check_policy: Any,
    requested_cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    expected = {case["case_id"]: case for case in requested_cases}
    received: dict[str, dict[str, Any]] = {}
    for item in results:
        case_id = item.get("case_id")
        if case_id not in expected or case_id in received:
            raise RemediationProviderError(
                "Model remediation returned missing, duplicate, or unknown case IDs."
            )
        received[case_id] = item
    if received.keys() != expected.keys():
        raise RemediationProviderError(
            "Model remediation did not return every requested case."
        )

    suggestions: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    limitations: list[dict[str, Any]] = []
    for case_id, case in expected.items():
        item = received[case_id]
        if item["disposition"] == "context_required":
            question = item["question"].strip() or (
                f"What purpose should '{case['name']}' communicate?"
            )
            questions.append(
                {
                    "question_id": f"{case_id}:model_context",
                    "case_ids": [case_id],
                    "field": "model_context",
                    "prompt": question,
                    "input_type": "text",
                    "required": True,
                }
            )
            continue

        candidate = item["candidate"].strip()
        if not candidate or candidate == case["name"]:
            limitations.append(
                {
                    "case_id": case_id,
                    "name": case["name"],
                    "message": "The model did not produce a changed candidate.",
                }
            )
            continue
        validation_status, validation_reasons = validate_candidate(
            check_id=check_id,
            candidate=candidate,
            module_name=module_name,
            check_policy=check_policy,
        )
        if validation_status == "failed":
            limitations.append(
                {
                    "case_id": case_id,
                    "name": case["name"],
                    "message": (
                        "The generated candidate did not satisfy the configured policy."
                    ),
                    "details": validation_reasons,
                }
            )
            continue
        suggestions.append(
            {
                "case_id": case_id,
                "title": f"Rename {case['name']}",
                "current_name": case["name"],
                "candidate_name": candidate,
                "confidence": item["confidence"],
                "description": item["note"].strip(),
                "policy_validation": validation_status,
                "verification": (
                    "Re-run the naming check and compile affected targets after "
                    "an approved rename."
                ),
            }
        )
    return suggestions, questions, limitations


def failed_rules(reasons: list[Any]) -> list[dict[str, str]]:
    rules: list[dict[str, str]] = []
    for index, reason in enumerate(reasons, start=1):
        text = str(reason)
        match = re.match(r"^\[([^\]]+)\]\s*(.*)$", text)
        rules.append(
            {
                "rule_id": match.group(1) if match else f"finding-{index}",
                "text": match.group(2) if match else text,
            }
        )
    return rules


def display_rules(policy: Any) -> list[dict[str, str]]:
    if not isinstance(policy, dict):
        return []
    candidates = policy.get("rules") or policy.get("automatic_rules") or []
    display: list[dict[str, str]] = []
    for rule in candidates:
        if not isinstance(rule, dict) or rule.get(
            "mode", "automatic"
        ) != "automatic":
            continue
        display.append(
            {
                "rule_id": str(rule.get("id", "")),
                "reason": str(rule.get("reason") or rule.get("statement") or ""),
            }
        )
    return display


def affected_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "name": case.get("name", "Unnamed case"),
        "location": case.get("location", ""),
        "reasons": case.get("reasons", []),
    }


def result_status(
    suggestions: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> str:
    if suggestions and (questions or limitations):
        return "partial"
    if suggestions:
        return "candidate_ready"
    if questions:
        return "input_required"
    return "unsupported"


def result_summary(
    status: str,
    suggestions: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> str:
    if status == "candidate_ready":
        suffix = "s" if len(suggestions) != 1 else ""
        return f"Generated {len(suggestions)} rename candidate{suffix}."
    if status == "input_required":
        suffix = "s" if len(questions) != 1 else ""
        return f"Developer context is required for {len(questions)} case{suffix}."
    if status == "partial":
        return (
            f"Generated {len(suggestions)} candidate(s); "
            f"{len(questions)} question(s) and "
            f"{len(limitations)} limitation(s) remain."
        )
    return "No candidate was generated within the current prototype boundary."


_CHECK_TEMPLATES = {
    "required_paths": {
        "description": "Restore the required repository path at the policy-defined location.",
        "actions": [
            "Use the reported path exactly, including capitalization and module placeholders.",
            "Confirm whether the path is source-owned or generated before adding it.",
        ],
        "verification": "Re-run the review and confirm the Required Paths case passes.",
    },
    "array_sizes": {
        "description": "Update the array declaration to use the size form required by policy.",
        "actions": ["Use a domain-meaningful symbolic size identifier."],
        "verification": "Re-run the naming stage and confirm the array-size case passes.",
    },
}

_SYMBOL_TEMPLATE = {
    "description": "Rename the symbol to satisfy the active naming policy.",
    "actions": ["Update declarations, definitions, and references together."],
    "verification": "Re-run the naming stage and confirm this case passes.",
}


def case_suggestion(check_id: str, case: dict[str, Any]) -> dict[str, Any]:
    template = _CHECK_TEMPLATES.get(check_id, _SYMBOL_TEMPLATE)
    return {
        "case_id": case["case_id"],
        "title": f"Update {case.get('name') or 'this item'}",
        "description": template["description"],
        "actions": template["actions"],
        "verification": template["verification"],
        "reasons": case.get("reasons", []),
    }
