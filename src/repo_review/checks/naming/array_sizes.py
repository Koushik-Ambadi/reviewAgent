import re

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)


def validate_array_sizes(
    symbols,
    naming_policy,
):
    cases = []

    rule = naming_policy["rules"][0]
    outcomes = {outcome["key"]: outcome for outcome in rule["outcomes"]}

    def policy_reason(key: str, **values: object) -> str:
        outcome = outcomes[key]
        return f"[{outcome['id']}] {outcome['reason'].format(**values)}"

    if not rule.get("enabled", True) or rule.get("mode") != "automatic":
        cases.append(
            CaseResult(
                status=CaseStatus.SKIPPED,
                name="Array Size Check",
                location="",
                reasons=[policy_reason("disabled")],
            )
        )
        return _build_result(cases)

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")

        for global_var in file_symbols.get("globals", []):
            name = global_var.get("name", "")
            base_location = file_path
            if global_var.get("line"):
                base_location = f"{file_path}:{global_var['line']}"

            for dimension_index, suffix in enumerate(
                global_var.get("array_suffixes", [])
            ):
                dimension = suffix.strip().removeprefix("[").removesuffix("]").strip()
                location = f"{base_location} dimension {dimension_index + 1}"

                if not dimension:
                    status = (
                        CaseStatus.SKIPPED
                        if rule.get("allow_unspecified_dimensions", True)
                        else CaseStatus.FAILED
                    )
                    reason = policy_reason(
                        "unspecified_allowed"
                        if status == CaseStatus.SKIPPED
                        else "unspecified_required"
                    )
                    cases.append(
                        CaseResult(
                            status=status,
                            name=name,
                            location=location,
                            reasons=[reason],
                        )
                    )
                    continue

                normalized = strip_outer_parentheses(dimension)
                numeric_literal = bool(
                    re.fullmatch(rule["integer_literal_pattern"], normalized)
                    or re.fullmatch(rule["float_literal_pattern"], normalized)
                    or re.fullmatch(rule["hex_float_literal_pattern"], normalized)
                )

                if numeric_literal:
                    cases.append(
                        CaseResult(
                            status=CaseStatus.FAILED,
                            name=name,
                            location=location,
                            reasons=[
                                policy_reason("numeric_literal", dimension=dimension)
                            ],
                        )
                    )
                elif not re.search(rule["identifier_pattern"], normalized):
                    cases.append(
                        CaseResult(
                            status=CaseStatus.FAILED,
                            name=name,
                            location=location,
                            reasons=[
                                policy_reason("identifier_required", dimension=dimension)
                            ],
                        )
                    )
                else:
                    cases.append(
                        CaseResult(
                            status=CaseStatus.SUCCESS,
                            name=name,
                            location=location,
                        )
                    )

    return _build_result(cases)


def strip_outer_parentheses(value: str) -> str:
    """Remove only parentheses that enclose the entire dimension expression."""
    value = value.strip()
    while value.startswith("(") and value.endswith(")"):
        depth = 0
        wraps_expression = True
        for index, character in enumerate(value):
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0 and index != len(value) - 1:
                    wraps_expression = False
                    break
        if not wraps_expression or depth != 0:
            break
        value = value[1:-1].strip()
    return value


def _build_result(cases):
    return CheckResult(
        title="Array Sizes",
        check_id="array_sizes",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
