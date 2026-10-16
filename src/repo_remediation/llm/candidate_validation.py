"""Local validation for model-generated naming candidates."""

from __future__ import annotations

from typing import Any

from repo_review.checks.naming.common_identifier import evaluate_atomic_rules


def validate_candidate(
    *,
    check_id: str,
    candidate: str,
    module_name: str,
    check_policy: Any,
) -> tuple[str, list[str]]:
    """Rerun the complete executable check policy after model generation."""
    if check_id == "global_variable_names":
        return "not_available_without_symbol_type", []
    if not isinstance(check_policy, dict) or "rules" not in check_policy:
        return "not_available", []
    reasons = evaluate_atomic_rules(
        candidate,
        check_policy["rules"],
        context={"module": module_name},
    )
    return ("failed", reasons) if reasons else ("passed", [])
