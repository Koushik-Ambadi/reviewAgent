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

    description_allowed_characters_pattern = re.compile(
        naming_policy["description_allowed_characters_pattern"]
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

            if not name:
                cases.append(
                    CaseResult(
                        status=CaseStatus.FAILED,
                        name=name,
                        location=location,
                        reasons=["Variable name is missing."],
                    )
                )
                continue

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
            #
            # Data type
            #

            data_type = name[0] if name else ""

            if not data_type:
                failures.append("Data type code is missing.")
            elif data_type not in allowed_data_types:
                failures.append(f"Invalid data type code '{data_type}'.")

            #
            # Data size
            #

            data_size = name[1] if len(name) >= 2 else ""

            if not data_size:
                failures.append("Data size code is missing.")
            elif data_size not in allowed_data_sizes:
                failures.append(f"Invalid data size code '{data_size}'.")

            remaining = (
                name[2:]
                if len(name) > 2
                else ""
            )

            parts = remaining.split("_") if len(name) >= 2 else []
            module = parts[0] if parts else ""
            unit = parts[1] if len(parts) > 1 else ""
            description_parts = parts[2:] if len(parts) > 2 else []
            description = "_".join(description_parts)

            if len(parts) < 3:
                failures.append(
                    "Name must contain module, unit, and description segments separated by underscores."
                )

            if len(description_parts) > 1:
                failures.append(
                    "Description must not contain underscores; use lowerCamelCase."
                )

            #
            # Module
            #

            if module and module not in allowed_modules:
                failures.append(f"Invalid module code '{module}'.")
            elif not module and naming_policy.get("enforce_module_required", True):
                failures.append("Module code is missing.")

            #
            # Unit
            #

            if unit and unit not in allowed_units:
                failures.append(f"Invalid unit code '{unit}'.")
            elif not unit and naming_policy.get("enforce_unit_required", True):
                failures.append("Unit code is missing.")

            #
            # Description
            #

            if description:
                if (
                    "_" not in description
                    and not description_allowed_characters_pattern.fullmatch(
                        description
                    )
                ):
                    failures.append(
                        "Description may contain only letters and numbers."
                    )

                if (
                    naming_policy.get("description_must_start_lowercase", True)
                    and not description[0].islower()
                ):
                    failures.append("Description must start with a lowercase letter.")

                if len(description) < description_min_length:
                    failures.append(
                        f"Description is shorter than {description_min_length} characters."
                    )

                if len(description) > description_max_length:
                    failures.append(
                        f"Description exceeds {description_max_length} characters."
                    )
            elif naming_policy.get("enforce_description_required", True):
                failures.append("Description is missing.")

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
        check_id="global_variable_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
