"""Compile failed findings into compact, check-specific model prompts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .model_selection import RemediationModelProfile
from .response_contract import REMEDIATION_RESPONSE_SCHEMA


@dataclass(frozen=True)
class CompiledRemediationPrompt:
    """Provider payload plus private mappings excluded from model input."""

    payload: dict[str, Any]
    case_ref_to_id: dict[str, str]
    prompt_profile_id: str


_BASE_INSTRUCTION = (
    "Return one decision for every case. A candidate must differ from "
    "current_name and satisfy all referenced failed rules. Use only meaning "
    "visible in the current name or developer context. If required meaning is "
    "missing, request one specific piece of context instead of guessing."
)

_CHECK_INSTRUCTIONS = {
    "function_names": (
        "For length failures, shorten visible words with conservative acronyms "
        "or abbreviations. Do not invent the function's operation or domain."
    ),
    "parameter_names": (
        "A parameter name must communicate its purpose. For an opaque or "
        "single-letter name without developer context, request that purpose."
    ),
    "local_variable_names": (
        "A local name must communicate its role in the function. Request that "
        "role when the current name and developer context do not establish it."
    ),
    "global_variable_names": (
        "Never invent module, data-type, size, unit, or meaning segments. "
        "Request the exact missing or corrected fact before proposing a name."
    ),
    "macro_names": (
        "Preserve visible macro meaning. If the name does not establish its "
        "purpose, request the macro's purpose or value role."
    ),
    "type_names": (
        "Preserve the represented type concept. Request that concept when it "
        "is not visible in the current name or developer context."
    ),
    "enum_constant_names": (
        "Preserve the enum value's domain meaning. Request that meaning when "
        "it is not visible in the current name or developer context."
    ),
    "array_sizes": (
        "A symbolic array size must express the represented limit or dimension. "
        "Request that fact when it is not supplied."
    ),
}


def compile_remediation_prompt(
    *,
    profile: RemediationModelProfile,
    check_id: str,
    cases: list[dict[str, Any]],
) -> CompiledRemediationPrompt:
    """Send only current names, developer context, and failed atomic rules."""
    rule_refs: dict[tuple[str, str], str] = {}
    prompt_rules: list[dict[str, str]] = []
    prompt_cases: list[dict[str, Any]] = []
    case_ref_to_id: dict[str, str] = {}

    for case_index, case in enumerate(cases, start=1):
        case_ref = f"C{case_index}"
        case_ref_to_id[case_ref] = str(case["case_id"])
        failed_rule_refs: list[str] = []
        for rule in case.get("failed_rules", []):
            key = (str(rule["rule_id"]), str(rule["text"]))
            rule_ref = rule_refs.get(key)
            if rule_ref is None:
                rule_ref = f"R{len(rule_refs) + 1}"
                rule_refs[key] = rule_ref
                prompt_rules.append({"ref": rule_ref, "text": key[1]})
            failed_rule_refs.append(rule_ref)

        prompt_case: dict[str, Any] = {
            "ref": case_ref,
            "current_name": str(case.get("name", "")),
            "failed_rules": failed_rule_refs,
        }
        developer_context = str(case.get("developer_context", "")).strip()
        if developer_context:
            prompt_case["developer_context"] = developer_context
        prompt_cases.append(prompt_case)

    profile_id = f"naming-{check_id}-v1"
    instruction = " ".join(
        part for part in (_BASE_INSTRUCTION, _CHECK_INSTRUCTIONS.get(check_id, "")) if part
    )
    payload = {
        "model": profile.model,
        "store": False,
        "reasoning": {"effort": profile.reasoning_effort},
        "max_output_tokens": profile.max_output_tokens(len(cases)),
        "input": [
            {"role": "developer", "content": instruction},
            {
                "role": "user",
                "content": json.dumps(
                    {"rules": prompt_rules, "cases": prompt_cases},
                    separators=(",", ":"),
                ),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "remediation_batch",
                "strict": True,
                "schema": REMEDIATION_RESPONSE_SCHEMA,
            },
            "verbosity": profile.verbosity,
        },
    }
    return CompiledRemediationPrompt(
        payload=payload,
        case_ref_to_id=case_ref_to_id,
        prompt_profile_id=profile_id,
    )
