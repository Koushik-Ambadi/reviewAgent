import re

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)


_INTEGER_LITERAL = re.compile(
    r"^[+-]?(?:0[xX][0-9A-Fa-f]+|0[bB][01]+|[0-9]+)"
    r"(?:[uU](?:[lL]{1,2})?|[lL]{1,2}[uU]?)?$"
)
_FLOAT_LITERAL = re.compile(
    r"^[+-]?(?:(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?|"
    r"[0-9]+[eE][+-]?[0-9]+)[fFlL]?$"
)
_HEX_FLOAT_LITERAL = re.compile(
    r"^[+-]?0[xX](?:[0-9A-Fa-f]+(?:\.[0-9A-Fa-f]*)?|\.[0-9A-Fa-f]+)"
    r"[pP][+-]?[0-9]+[fFlL]?$"
)
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def validate_array_sizes(
    symbols,
    naming_policy,
):
    cases = []

    if not naming_policy["enforce_symbolic_array_sizes"]:
        cases.append(
            CaseResult(
                status=CaseStatus.SKIPPED,
                name="Array Size Check",
                location="",
                reasons=["Symbolic array size validation is disabled by policy."],
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
                        if naming_policy.get("allow_unspecified_dimensions", True)
                        else CaseStatus.FAILED
                    )
                    reason = (
                        "Array dimension is unspecified; symbolic-size validation does not apply."
                        if status == CaseStatus.SKIPPED
                        else "Array dimension is required by policy."
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
                    _INTEGER_LITERAL.fullmatch(normalized)
                    or _FLOAT_LITERAL.fullmatch(normalized)
                    or _HEX_FLOAT_LITERAL.fullmatch(normalized)
                )

                if numeric_literal:
                    cases.append(
                        CaseResult(
                            status=CaseStatus.FAILED,
                            name=name,
                            location=location,
                            reasons=[
                                f"Array dimension '{dimension}' is a numeric literal; policy requires a symbolic size."
                            ],
                        )
                    )
                elif not _IDENTIFIER.search(normalized):
                    cases.append(
                        CaseResult(
                            status=CaseStatus.FAILED,
                            name=name,
                            location=location,
                            reasons=[
                                f"Array dimension '{dimension}' has no symbolic identifier."
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
