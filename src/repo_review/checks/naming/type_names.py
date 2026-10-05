# src/repo_review/checks/naming/type_names.py
from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .common_identifier import evaluate_atomic_rules


def validate_type_names(
    symbols,
    module_name,
    naming_policy,
):
    cases = []

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")

        for typedef in file_symbols.get(
            "typedefs",
            [],
        ):
            name = typedef.get("name", "")
            line = typedef.get("line", "")

            location = (
                f"{file_path}:"
                f"{name}:"
                f"{line}"
            )

            reasons = evaluate_atomic_rules(
                name,
                naming_policy["rules"],
                context={"module": module_name},
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
        title="Type Names",
        check_id="type_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
