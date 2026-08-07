# src/repo_review/checks/naming/array_sizes.py

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

    enforce_symbolic_sizes = (
        naming_policy[
            "enforce_symbolic_array_sizes"
        ]
    )

    if not enforce_symbolic_sizes:

        cases.append(
            CaseResult(
                status=CaseStatus.SKIPPED,
                name="Array Size Check",
                location="",
                reasons=[
                    "Symbolic array size validation disabled by policy."
                ],
            )
        )

        return CheckResult(
            title="Array Sizes",
            status=CheckStatus.COMPLETED,
            summary=build_check_summary(cases),
            cases=cases,
        )

    for file_symbols in symbols:

        file_path = file_symbols.get(
            "file",
            "",
        )

        globals_list = file_symbols.get(
            "globals",
            [],
        )

        for global_var in globals_list:

            name = global_var.get(
                "name",
                "",
            )

            array_suffixes = global_var.get(
                "array_suffixes",
                [],
            )

            if not array_suffixes:
                continue

            for suffix in array_suffixes:

                dimension = (
                    suffix
                    .replace("[", "")
                    .replace("]", "")
                    .strip()
                )

                location = file_path

                if global_var.get("line"):

                    location = (
                        f"{file_path}:"
                        f"{global_var['line']}"
                    )

                if dimension.isdigit():

                    cases.append(
                        CaseResult(
                            status=CaseStatus.FAILED,
                            name=name,
                            location=location,
                            reasons=[
                                (
                                    f"Array '{name}' uses "
                                    f"raw numeric size "
                                    f"[{dimension}]. "
                                    "Symbolic constants are "
                                    "required by policy."
                                )
                            ],
                        )
                    )

                else:

                    cases.append(
                        CaseResult(
                            status=CaseStatus.SUCCESS,
                            name=name,
                            location=location,
                            reasons=[
                                (
                                    f"Array '{name}' uses "
                                    f"symbolic size "
                                    f"[{dimension}]."
                                )
                            ],
                        )
                    )

    return CheckResult(
        title="Array Sizes",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )