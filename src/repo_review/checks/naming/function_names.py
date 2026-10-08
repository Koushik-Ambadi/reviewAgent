# src/repo_review/checks/naming/function_names.py

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .common_identifier import evaluate_atomic_rules, find_applicability_exclusion


def validate_function_names(
    symbols,
    module_name,
    naming_policy,
):

    cases = []

    exclusion_patterns = naming_policy.get("applicability_exclusions", [])

    for file_symbols in symbols:

        file_path = file_symbols.get(
            "file",
            "",
        )

        for function in file_symbols.get(
            "functions_defined",
            [],
        ):

            name = function.get(
                "name",
                "",
            )

            location = (
                f"{file_path}:{function.get('line', '')}"
            )

            exclusion = find_applicability_exclusion(
                name,
                exclusion_patterns,
                context={"module": module_name},
            )
            if exclusion:
                cases.append(
                    CaseResult(
                        status=CaseStatus.SKIPPED,
                        name=name,
                        location=location,
                        reasons=[f"[{exclusion['id']}] {exclusion['reason']}"],
                    )
                )
                continue

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
        title="Function Names",
        check_id="function_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
