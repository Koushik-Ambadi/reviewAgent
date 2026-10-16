"""Compile report-oriented findings into a compact model prompt."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .model_settings import RemediationModelSettings
from .output import REMEDIATION_RESPONSE_SCHEMA


@dataclass(frozen=True)
class CompiledRemediationPrompt:
    """Provider payload plus private mappings excluded from model input."""

    payload: dict[str, Any]
    case_ref_to_id: dict[str, str]


def compile_remediation_prompt(
    *,
    settings: RemediationModelSettings,
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

    prompt_input = {
        "rules": prompt_rules,
        "cases": prompt_cases,
    }
    instruction = (
        "Return one decision for every case. A candidate must differ from "
        "current_name and satisfy all referenced failed rules. If the available "
        "name and developer context do not establish intent, request one specific "
        "piece of context instead of guessing."
    )
    payload = {
        "model": settings.model,
        "store": False,
        "reasoning": {"effort": settings.reasoning_effort},
        "max_output_tokens": settings.max_output_tokens(len(cases)),
        "input": [
            {"role": "developer", "content": instruction},
            {
                "role": "user",
                "content": json.dumps(prompt_input, separators=(",", ":")),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "remediation_batch",
                "strict": True,
                "schema": REMEDIATION_RESPONSE_SCHEMA,
            },
            "verbosity": settings.verbosity,
        },
    }
    return CompiledRemediationPrompt(
        payload=payload,
        case_ref_to_id=case_ref_to_id,
    )
