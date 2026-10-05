# src/repo_review/checks/naming/local_variable_names.py

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .common_identifier import evaluate_atomic_rules


def validate_local_variable_names(
    symbols,
    naming_policy,
):
    cases = []

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")

        for variable in file_symbols.get(
            "locals",
            [],
        ):
            name = variable.get("name", "")
            line = variable.get("line", "")
            symbol_type = variable.get("type", "")

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
        title="Local Variable Names",
        check_id="local_variable_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
