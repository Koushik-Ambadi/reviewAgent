"""Structured model-output schema and transport-independent parsing."""

from __future__ import annotations

import json
from typing import Any


REMEDIATION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "cases": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "case_ref": {"type": "string"},
                    "disposition": {
                        "type": "string",
                        "enum": ["candidate", "context_required"],
                    },
                    "candidate": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                    "note": {"type": "string"},
                    "question": {"type": "string"},
                },
                "required": [
                    "case_ref",
                    "disposition",
                    "candidate",
                    "confidence",
                    "note",
                    "question",
                ],
            },
        }
    },
    "required": ["cases"],
}


def parse_structured_response(response: dict[str, Any]) -> dict[str, Any]:
    """Extract the strict JSON result while preserving refusal/error semantics."""
    for output in response.get("output", []):
        if output.get("type") != "message":
            continue
        for content in output.get("content", []):
            if content.get("type") == "refusal":
                raise ValueError("The model refused the remediation request.")
            if content.get("type") == "output_text":
                try:
                    parsed = json.loads(content["text"])
                except (KeyError, TypeError, json.JSONDecodeError) as error:
                    raise ValueError(
                        "Model remediation returned invalid structured output."
                    ) from error
                if not isinstance(parsed, dict) or not isinstance(
                    parsed.get("cases"), list
                ):
                    raise ValueError(
                        "Model remediation returned an unexpected structured output shape."
                    )
                return parsed
    raise ValueError("Model remediation returned no output text.")


def restore_case_ids(
    results: list[dict[str, Any]],
    case_ref_to_id: dict[str, str],
) -> list[dict[str, Any]]:
    """Replace prompt-local ordinals with application IDs after generation."""
    restored: list[dict[str, Any]] = []
    seen_refs: set[str] = set()
    for result in results:
        case_ref = str(result.get("case_ref", ""))
        if case_ref not in case_ref_to_id or case_ref in seen_refs:
            raise ValueError(
                "Model remediation returned a missing, duplicate, or unknown case reference."
            )
        seen_refs.add(case_ref)
        restored.append(
            {
                key: value
                for key, value in result.items()
                if key != "case_ref"
            }
            | {"case_id": case_ref_to_id[case_ref]}
        )
    if seen_refs != set(case_ref_to_id):
        raise ValueError("Model remediation did not return every requested case.")
    return restored
