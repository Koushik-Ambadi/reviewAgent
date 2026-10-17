"""Developer-context requirements applied before model generation."""

from __future__ import annotations

import re
from typing import Any


_GLOBAL_CATEGORICAL_RULES = {
    "ABS-POLICY-GLOBAL-DATA-TYPE",
    "ABS-POLICY-GLOBAL-DATA-SIZE",
    "ABS-POLICY-GLOBAL-MODULE",
    "ABS-POLICY-GLOBAL-UNIT",
    "ABS-SCS-17.g",
    "ABS-POLICY-GLOBAL-SEGMENTS",
}

_SEMANTIC_RULES = {
    "ABS-POLICY-FUNCTION-DESCRIPTION",
    "ABS-POLICY-MACRO-DESCRIPTION",
    "ABS-POLICY-TYPE-DESCRIPTION",
    "ABS-POLICY-ENUM-DESCRIPTION",
}


def preflight_case(
    check_id: str,
    case: dict[str, Any],
    module_name: str,
    context_answers: dict[str, str],
) -> dict[str, Any]:
    case_id = case["case_id"]
    rule_ids = set(rule_ids_from_reasons(case.get("reasons", [])))
    case_context = "\n".join(
        answer
        for question_id, answer in context_answers.items()
        if question_id.startswith(f"{case_id}:")
    )

    if check_id == "required_paths":
        return {
            "kind": "unsupported",
            "limitation": limitation(
                case,
                "Repository structure remediation needs artifact ownership, "
                "content, and generation context.",
            ),
        }

    if check_id == "global_variable_names" and rule_ids & _GLOBAL_CATEGORICAL_RULES:
        if case_context:
            return {"kind": "eligible", "developer_context": case_context}
        return {
            "kind": "question",
            "question": {
                "question_id": f"{case_id}:global_segments",
                "case_ids": [case_id],
                "field": "global_segments",
                "prompt": (
                    "Provide the trusted module, data type, size, unit, and "
                    f"meaning required for global '{case.get('name', '')}'."
                ),
                "input_type": "text",
                "required": True,
            },
        }

    question = known_context_question(check_id, case, rule_ids, module_name)
    if question:
        answer = context_answers.get(question["question_id"], "")
        if not answer and not case_context:
            return {"kind": "question", "question": question}
        return {
            "kind": "eligible",
            "developer_context": answer or case_context,
        }

    return {"kind": "eligible", "developer_context": case_context}


def known_context_question(
    check_id: str,
    case: dict[str, Any],
    rule_ids: set[str],
    module_name: str,
) -> dict[str, Any] | None:
    name = str(case.get("name", ""))
    prompt = ""
    field = "purpose"

    if check_id == "parameter_names" and (
        "ABS-SCS-17.e" in rule_ids or "ABS-SCS-16.2.e" in rule_ids
    ):
        prompt = f"What does parameter '{name or 'unnamed parameter'}' represent?"
        field = "parameter_purpose"
    elif check_id == "local_variable_names" and "ABS-SCS-17.e" in rule_ids:
        prompt = f"What does local variable '{name}' represent in its function?"
        field = "local_variable_purpose"
    elif check_id == "array_sizes":
        prompt = (
            f"What limit or dimension does array '{name}' represent, and what "
            "symbolic size name should express it?"
        )
        field = "array_dimension_meaning"
    elif rule_ids & _SEMANTIC_RULES and not _has_semantic_stem(
        check_id, name, module_name
    ):
        prompt = f"What purpose or domain concept should '{name}' describe?"
        field = "symbol_purpose"
    elif check_id == "global_variable_names" and any(
        rule_id.startswith("ABS-POLICY-GLOBAL-DESCRIPTION")
        for rule_id in rule_ids
    ) and not _global_description(name):
        prompt = f"What does global variable '{name}' represent?"
        field = "global_description"

    if not prompt:
        return None
    return {
        "question_id": f"{case['case_id']}:{field}",
        "case_ids": [case["case_id"]],
        "field": field,
        "prompt": prompt,
        "input_type": "text",
        "required": True,
    }


def rule_ids_from_reasons(reasons: list[Any]) -> list[str]:
    ids: list[str] = []
    for reason in reasons:
        match = re.match(r"^\[([^\]]+)\]", str(reason))
        if match and match.group(1) not in ids:
            ids.append(match.group(1))
    return ids


def limitation(case: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "name": case.get("name", "Unnamed case"),
        "message": message,
    }


def _has_semantic_stem(check_id: str, name: str, module_name: str) -> bool:
    module_title = module_name[:1].upper() + module_name[1:].lower()
    module_upper = module_name.upper()
    stem = name
    if check_id in {"function_names", "type_names"}:
        stem = re.sub(
            rf"^{re.escape(module_title)}_", "", stem, flags=re.IGNORECASE
        )
    elif check_id in {"macro_names", "enum_constant_names"}:
        stem = re.sub(
            rf"^{re.escape(module_upper)}_", "", stem, flags=re.IGNORECASE
        )
    if check_id == "type_names":
        stem = re.sub(r"_t$", "", stem, flags=re.IGNORECASE)
    return bool(stem.strip("_"))


def _global_description(name: str) -> str:
    parts = name.split("_")
    return "_".join(parts[2:]) if len(parts) >= 3 else ""
