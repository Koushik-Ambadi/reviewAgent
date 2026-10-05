# src/repo_review/checks/naming/common_identifier.py

import re
from typing import Any


def is_within_length(
    name: str,
    min_length: int | None = None,
    max_length: int | None = None,
) -> bool:
    length = len(name)

    if min_length is not None and length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True


def has_valid_characters(
    name: str,
    pattern: str,
) -> bool:
    return re.fullmatch(pattern, name) is not None


def has_leading_underscore(name: str) -> bool:
    return name.startswith("_")


def has_consecutive_underscores(name: str) -> bool:
    return "__" in name


def has_trailing_underscore(name: str) -> bool:
    return name.endswith("_")


def evaluate_atomic_rules(
    name: str,
    rules: list[dict[str, Any]],
    *,
    context: dict[str, Any] | None = None,
    symbol_type: str = "",
) -> list[str]:
    """Evaluate only enabled automatic rules declared by the loaded policy."""
    values = {"name": name, **(context or {})}
    failures: list[str] = []

    for rule in rules:
        if not rule.get("enabled", True) or rule.get("mode", "automatic") != "automatic":
            continue

        validator = rule["validator"]
        rule_values = dict(values)
        module = str(rule_values.get("module", ""))
        if rule.get("module_case") == "title":
            module = module[:1].upper() + module[1:].lower()
        elif rule.get("module_case") == "upper":
            module = module.upper()
        rule_values["module"] = module
        expected = str(rule.get("value", "")).format(**rule_values)
        applies = True

        if rule.get("when_symbol_type") == "pointer_to_pointer":
            applies = symbol_type.count("*") >= 2
        elif rule.get("when_symbol_type") == "pointer":
            applies = symbol_type.count("*") == 1
        elif rule.get("when_symbol_type") == "non_pointer":
            applies = "*" not in symbol_type
        if rule.get("when_symbol_type") == "pointer" and symbol_type.count("*") >= 2:
            applies = False

        if not applies:
            continue

        valid = True
        if validator == "fullmatch":
            valid = re.fullmatch(expected, name) is not None
        elif validator == "max_length":
            valid = len(name) <= int(rule["limit"])
        elif validator == "min_length":
            valid = len(name) >= int(rule["limit"])
        elif validator == "starts_with":
            valid = name.startswith(expected)
        elif validator == "not_starts_with":
            valid = not name.startswith(expected)
        elif validator == "not_contains":
            valid = expected not in name
        elif validator == "not_ends_with":
            valid = not name.endswith(expected)
        elif validator == "uppercase_only":
            valid = not any(char.isalpha() and not char.isupper() for char in name)
        elif validator == "nonempty_after_prefix":
            valid = not name.startswith(expected) or bool(name[len(expected):].strip("_"))
        elif validator == "pointer_suffix":
            valid = name.endswith(expected)
        elif validator == "not_empty":
            valid = bool(name)
        else:
            raise ValueError(f"Unsupported naming policy validator: {validator}")

        if not valid:
            reason = rule["reason"].format(
                **rule_values,
                expected=expected,
                limit=rule.get("limit", ""),
                name_length=len(name),
            )
            failures.append(f"[{rule['id']}] {reason}")

    return failures


def find_applicability_exclusion(
    name: str,
    exclusions: list[Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, str] | None:
    values = {**(context or {})}
    for item in exclusions:
        rule = item if isinstance(item, dict) else {"pattern": item}
        rule_values = dict(values)
        module = str(rule_values.get("module", ""))
        if rule.get("module_case") == "upper":
            module = module.upper()
        elif rule.get("module_case") == "title":
            module = module[:1].upper() + module[1:].lower()
        rule_values["module"] = module
        pattern = rule["pattern"].format(**rule_values)
        if re.match(pattern, name):
            return {
                "id": rule.get("id", "ABS-POLICY-APPLICABILITY-EXCLUSION"),
                "reason": rule.get("reason", "Symbol is excluded by the loaded policy."),
            }
    return None
