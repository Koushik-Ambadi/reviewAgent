# src/repo_review/checks/naming/parameter_names.py
from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .common_identifier import evaluate_atomic_rules


def validate_parameter_names(
    symbols,
    naming_policy,
):
    cases = []

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")

        for parameter in file_symbols.get(
            "parameters",
            [],
        ):
            name = parameter.get("name", "")
            line = parameter.get("line", "")
            symbol_type = parameter.get("type", "")

            location = (
                f"{file_path}:"
                f"{name}:"
                f"{line}"
            )

            reasons = evaluate_atomic_rules(
                name,
                naming_policy["rules"],
                symbol_type=symbol_type,
            )

            cases.append(
                CaseResult(
                    status=(
                        CaseStatus.FAILED
                        if reasons
                        else CaseStatus.SUCCESS
                    ),
                    name=name,
                    location=location,
                    reasons=reasons,
                )
            )

    return CheckResult(
        title="Parameter Names",
        check_id="parameter_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
