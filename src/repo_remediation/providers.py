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

    provider_id = "policy-template-remediation-v2"

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
            _case_suggestion(check["check_id"], case)
            for case in cases
        ]

        if scope == "check":
            summary = (
                f"Review the {len(cases)} failed case"
                f"{'s' if len(cases) != 1 else ''} against the configured "
                f"{check.get('title', 'check')} rules."
            )
        else:
            summary = suggestions[0]["description"]

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


_CHECK_TEMPLATES = {
    "required_paths": {
        "description": "Restore the required repository path at the policy-defined location.",
        "actions": [
            "Use the reported path exactly, including capitalization and module placeholders.",
            "Add the path to source control if it is a required source or configuration input.",
        ],
        "verification": "Re-run the review and confirm the Required Paths case passes.",
    },
    "array_sizes": {
        "description": "Update the array declaration to use the size form required by policy.",
        "actions": [
            "Prefer the configured symbolic size identifier when a literal dimension is rejected.",
            "Keep the declaration and all dependent initializers consistent.",
        ],
        "verification": "Re-run the naming stage and confirm the array-size case passes.",
    },
    "global_variable_names": {
        "description": "Rename the global so every policy-defined name segment is valid.",
        "actions": [
            "Apply the required type, module, unit, pointer, and description segments reported below.",
            "Update declarations, definitions, references, and exported interfaces together.",
        ],
        "verification": "Re-run the review and inspect both naming and compile results.",
    },
}

_SYMBOL_TEMPLATE = {
    "description": "Rename the symbol to satisfy the active naming policy.",
    "actions": [
        "Apply each reported atomic rule instead of addressing only the first failure.",
        "Update all declarations, definitions, references, and generated mappings together.",
    ],
    "verification": "Re-run the naming stage and confirm this case has no failed atomic reasons.",
}


def _case_suggestion(check_id: str, case: dict[str, Any]) -> dict[str, Any]:
    reasons = case.get("reasons", [])
    template = _CHECK_TEMPLATES.get(check_id)
    if template is None and check_id.endswith("_names"):
        template = _SYMBOL_TEMPLATE
    if template is None:
        template = {
            "description": "Update the source item to satisfy the active policy check.",
            "actions": ["Address every reported policy reason for this item."],
            "verification": "Re-run the review and confirm this case passes.",
        }
    return {
        "case_id": case["case_id"],
        "title": f"Update {case.get('name') or 'this item'}",
        "description": template["description"],
        "actions": template["actions"],
        "verification": template["verification"],
        "reasons": reasons,
    }
