# src/repo_review/checks/naming/utils.py

import re

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)


def validate_function_names(
    symbols,
    module_name,
    naming_policy,
):

    cases = []

    function_pattern = re.compile(
        naming_policy["pattern"]
    )

    expected_prefix = (
        module_name[0].upper()
        + module_name[1:].lower()
        if module_name
        else ""
    )

    exclusion_patterns = naming_policy[
        "applicability_exclusions"
    ]

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

            # Skip excluded functions
            if any(
                re.match(pattern, name)
                for pattern in exclusion_patterns
            ):

                cases.append(
                    CaseResult(
                        status=CaseStatus.SKIPPED,
                        name=name,
                        location=location,
                        reasons=[
                            "Excluded by policy",
                        ],
                    )
                )

                continue

            reasons = []

            # Validate naming pattern
            if not function_pattern.match(name):
                reasons.append(
                    "Invalid function naming pattern"
                )

            # Validate module prefix
            actual_prefix = name.split("_")[0]

            if (
                expected_prefix
                and actual_prefix != expected_prefix
            ):
                reasons.append(
                    f"Function must start with '{expected_prefix}_'"
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
