from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class RemediationProvider(ABC):
    """Produces remediation using the stable run/check/case contract."""

    provider_id: str

    @abstractmethod
    def suggest(
        self,
        *,
        run_id: str,
        check: dict[str, Any],
        cases: list[dict[str, Any]],
        scope: str,
    ) -> dict[str, Any]:
        raise NotImplementedError


class PlaceholderRemediationProvider(RemediationProvider):
    """Deterministic remediation used until a model-backed provider is enabled."""

    provider_id = "placeholder-remediation-v1"

    def suggest(
        self,
        *,
        run_id: str,
        check: dict[str, Any],
        cases: list[dict[str, Any]],
        scope: str,
    ) -> dict[str, Any]:
        affected_cases = [
            {
                "case_id": case["case_id"],
                "name": case.get("name", "Unnamed case"),
                "location": case.get("location", ""),
                "reasons": case.get("reasons", []),
            }
            for case in cases
        ]
        common_reasons = sorted(
            {
                reason
                for case in cases
                for reason in case.get("reasons", [])
            }
        )
        suggestions = [
            {
                "case_id": case["case_id"],
                "title": f"Update {case.get('name') or 'this item'}",
                "description": _case_suggestion(case),
                "reasons": case.get("reasons", []),
            }
            for case in cases
        ]

        if scope == "check":
            summary = (
                f"Review the {len(cases)} failed case"
                f"{'s' if len(cases) != 1 else ''} against the configured "
                f"{check.get('title', 'check')} rules."
            )
        else:
            summary = _case_suggestion(cases[0])

        return {
            "remediation_id": uuid4().hex,
            "run_id": run_id,
            "provider": self.provider_id,
            "scope": scope,
            "check_id": check["check_id"],
            "case_id": cases[0]["case_id"] if scope == "case" else None,
            "generated_at": datetime.now(UTC).isoformat(),
            "title": (
                f"Suggested fixes: {check.get('title', 'Check')}"
                if scope == "check"
                else f"Suggested fix: {cases[0].get('name') or 'Case'}"
            ),
            "summary": summary,
            "common_failure_patterns": common_reasons,
            "affected_cases": affected_cases,
            "suggestions": suggestions,
        }


class FutureOpenAIRemediationProvider(RemediationProvider):
    """Reserved provider boundary for the future model-backed implementation."""

    provider_id = "openai-remediation-v1"

    def suggest(
        self,
        *,
        run_id: str,
        check: dict[str, Any],
        cases: list[dict[str, Any]],
        scope: str,
    ) -> dict[str, Any]:
        raise NotImplementedError("OpenAI remediation is not configured.")


def _case_suggestion(case: dict[str, Any]) -> str:
    reasons = case.get("reasons", [])
    if reasons:
        return (
            "Update the source item so it satisfies: "
            + "; ".join(reasons)
        )
    return "Review the source item against the configured check requirements."
