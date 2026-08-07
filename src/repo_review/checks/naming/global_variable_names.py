# src/repo_review/checks/naming/global_variable_names.py

import re

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)


def validate_global_variable_names(
    symbols,
    naming_policy,
):

    cases = []

    allowed_chars_pattern = re.compile(
        naming_policy[
            "allowed_chars_pattern"
        ]
    )

    allowed_data_types = naming_policy[
        "data_types"
    ]

    allowed_data_sizes = naming_policy[
        "data_sizes"
    ]

    allowed_modules = naming_policy[
        "modules"
    ]

    allowed_units = naming_policy[
        "units"
    ]

    max_length = naming_policy[
        "name_max_length"
    ]

    excluded_type_patterns = naming_policy[
        "excluded_type_patterns"
    ]

    description_min_length = naming_policy[
        "description_min_length"
    ]

    description_max_length = naming_policy[
        "description_max_length"   
    ]

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

            var_type = global_var.get(
                "type",
                "",
            )

            line = global_var.get(
                "line",
                "",
            )

            location = (
                f"{file_path}:{line}"
            )

            #
            # Skip excluded/system globals
            #

            if any(
                re.match(
                    pattern,
                    var_type,
                )
                for pattern in excluded_type_patterns
            ):

                cases.append(
                    CaseResult(
                        status=CaseStatus.SKIPPED,
                        name=name,
                        location=location,
                        reasons=[
                            (
                                "Excluded global variable "
                                f"type '{var_type}' "
                                "by policy."
                            )
                        ],
                    )
                )

                continue

            failures = []

            #
            # Overall max length
            #

            if len(name) > max_length:

                failures.append(
                    f"Name exceeds max length ({max_length})."
                )

            #
            # Allowed characters
            #

            if not allowed_chars_pattern.fullmatch(
                name
            ):

                failures.append(
                    "Name contains invalid characters."
                )

            #
            # Minimum length
            #

            if len(name) < 3:

                failures.append(
                    "Name is too short to parse."
                )

            #
            # Data type
            #

            data_type = ""

            if len(name) >= 1:

                data_type = name[0]

                if data_type not in allowed_data_types:

                    failures.append(
                        (
                            f"Invalid data type "
                            f"'{data_type}'."
                        )
                    )

            #
            # Data size
            #

            data_size = ""

            if len(name) >= 2:

                data_size = name[1]

                if data_size not in allowed_data_sizes:

                    failures.append(
                        (
                            f"Invalid data size "
                            f"'{data_size}'."
                        )
                    )

            remaining = (
                name[2:]
                if len(name) > 2
                else ""
            )

            parts = remaining.split("_")

            module = ""
            unit = ""
            description = ""

            if len(parts) != 3:

                failures.append(
                    (
                        "Expected naming format "
                        "<type><size><module>_<unit>_<description>."
                    )
                )

            else:

                module = parts[0]
                unit = parts[1]
                description = parts[2]

            #
            # Module
            #

            if module:

                if module not in allowed_modules:

                    failures.append(
                        f"Invalid module '{module}'."
                    )

            #
            # Unit
            #

            if unit:

                if unit not in allowed_units:

                    failures.append(
                        f"Invalid unit '{unit}'."
                    )

            #
            # Description
            #

            if description:

                if not description[0].islower():

                    failures.append(
                        "Description must start "
                        "with lowercase letter."
                    )

                if not description.isalnum():

                    failures.append(
                        (
                            "Description must contain "
                            "only letters and numbers."
                        )
                    )

                if len(description) < description_min_length:

                    failures.append(
                        f"Description length must be >= {description_min_length}."
                    )

                if len(description) > description_max_length:

                    failures.append(
                        f"Description length must be <= {description_max_length}."
                    )

            else:

                failures.append(
                    "Description missing."
                )

            #
            # Final case
            #

            if failures:

                cases.append(
                    CaseResult(
                        status=CaseStatus.FAILED,
                        name=name,
                        location=location,
                        reasons=failures,
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
        title="Global Variable Names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )