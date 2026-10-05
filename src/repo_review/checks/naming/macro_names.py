# src/repo_review/checks/naming/macro_names.py

import re

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)


def validate_macro_names(
    symbols,
    module_name,
    naming_policy,
):

    cases = []

    macro_pattern = re.compile(
        naming_policy["macro_name_pattern"]
    )

    value_type = naming_policy[
        "macro_value_type"
    ]

    excluded_patterns = [
        pattern.format(
            module=module_name.lower()
        )
        for pattern in naming_policy[
            "applicability_exclusions"
        ]
    ]

    for file_symbols in symbols:

        file_path = file_symbols.get(
            "file",
            "",
        )

        macros = file_symbols.get(
            "macros",
            [],
        )

        for macro in macros:

            name = macro.get(
                "name",
                "",
            )

            macro_type = macro.get(
                "type",
                "",
            )

            line = macro.get(
                "line",
                "",
            )

            location = (
                f"{file_path}:{line}"
            )

            #
            # Only validate configured macro type
            #

            if macro_type != value_type:
                continue

            #
            # Excluded macros
            #

            if any(
                re.match(
                    pattern,
                    name,
                )
                for pattern in excluded_patterns
            ):

                cases.append(
                    CaseResult(
                        status=CaseStatus.SKIPPED,
                        name=name,
                        location=location,
                        reasons=[
                            (
                                "Macro excluded by "
                                "applicability policy."
                            )
                        ],
                    )
                )

                continue

            #
            # Naming validation
            #

            reasons = []

            if not macro_pattern.match(name):

                reasons.append(
                    (
                        "Macro name does not match "
                        "required naming pattern."
                    )
                )

            #
            # Final result
            #

            if reasons:

                cases.append(
                    CaseResult(
                        status=CaseStatus.FAILED,
                        name=name,
                        location=location,
                        reasons=reasons,
                    )
                )

            else:

                cases.append(
                    CaseResult(
                        status=CaseStatus.SUCCESS,
                        name=name,
                        location=location,
                        reasons=[],
                    )
                )

    return CheckResult(
        title="Macro Names",
        check_id="macro_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
