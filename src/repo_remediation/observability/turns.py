"""Immutable turn evidence for remediation request hierarchies."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .redaction import redact_sensitive


def completed_turn(
    *,
    turn_id: str,
    started_at: str,
    scope: str,
    check_id: str,
    cases: list[dict[str, Any]],
    context_answers: dict[str, str],
    eligible_cases: list[dict[str, Any]],
    provider_call: dict[str, Any] | None,
    status: str,
    suggestions: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "turn_id": turn_id,
        "parent_turn_id": None,
        "started_at": started_at,
        "completed_at": datetime.now(UTC).isoformat(),
        "status": "completed",
        "request_context": _turn_request(
            scope=scope,
            check_id=check_id,
            cases=cases,
            context_answers=context_answers,
        ),
        "preflight": {
            "eligible_case_ids": [case["case_id"] for case in eligible_cases],
            "model_call_made": provider_call is not None,
        },
        "provider_call": redact_sensitive(provider_call),
        "outcome": {
            "status": status,
            "suggestions": redact_sensitive(suggestions),
            "questions": redact_sensitive(questions),
            "limitations": redact_sensitive(limitations),
        },
    }


def failed_turn(
    *,
    turn_id: str,
    started_at: str,
    scope: str,
    check_id: str,
    cases: list[dict[str, Any]],
    context_answers: dict[str, str],
    eligible_cases: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
    provider_trace: dict[str, Any] | None,
    message: str,
) -> dict[str, Any]:
    return {
        "turn_id": turn_id,
        "parent_turn_id": None,
        "started_at": started_at,
        "completed_at": datetime.now(UTC).isoformat(),
        "status": "failed",
        "request_context": _turn_request(
            scope=scope,
            check_id=check_id,
            cases=cases,
            context_answers=context_answers,
        ),
        "preflight": {
            "eligible_case_ids": [case["case_id"] for case in eligible_cases],
            "model_call_made": provider_trace is not None,
        },
        "provider_call": redact_sensitive(provider_trace),
        "outcome": {
            "status": "provider_error",
            "suggestions": [],
            "questions": redact_sensitive(questions),
            "limitations": redact_sensitive(limitations),
            "error": {"message": message},
        },
    }


def _turn_request(
    *,
    scope: str,
    check_id: str,
    cases: list[dict[str, Any]],
    context_answers: dict[str, str],
) -> dict[str, Any]:
    return {
        "scope": scope,
        "check_id": check_id,
        "case_ids": [str(case.get("case_id", "")) for case in cases],
        "context_answers": redact_sensitive(context_answers),
    }
