# src/repo_review/checks/naming/rules.py

import re
from typing import Any


DEFAULT_RULES = {
    "function_name_pattern": r"^[A-Z][a-z]*(_[a-z]+)+$",
    "macro_name_pattern": r"^[A-Z]+(_[A-Z]+)*$",
    "excluded_function_patterns": [
        r"^look\d_",
        r"^plook_",
        r"^intrp",
        r"^binsearch_",
    ],
    "excluded_macro_patterns": [
        r"^{module}_IN_",
    ],
    "macro_value_type": "value",
}


def merge_rules(rules: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_RULES)

    if rules:
        merged.update(rules)

    return merged


def is_excluded_function(name: str, rules: dict[str, Any] | None = None) -> bool:
    merged = merge_rules(rules)

    return any(
        re.match(pattern, name)
        for pattern in merged["excluded_function_patterns"]
    )


def is_excluded_macro(
    name: str,
    module_name: str,
    rules: dict[str, Any] | None = None,
) -> bool:

    merged = merge_rules(rules)

    patterns = [
        pattern.format(module=module_name.lower())
        for pattern in merged["excluded_macro_patterns"]
    ]

    return any(re.match(pattern, name) for pattern in patterns)