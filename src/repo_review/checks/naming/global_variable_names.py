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
    min_length = naming_policy["minimum_name_length"]
    layout = naming_policy["layout"]

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
                        reasons=["[ABS-SCS-17.e] Variable name is missing."],
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
                                f"[{naming_policy['excluded_type_rule_id']}] Excluded global variable "
                                f"type '{var_type}' "
                                "by policy."
                            )
                        ],
                    )
                )

                continue

            failures = []

            if not naming_policy["leading_underscore_allowed"] and name.startswith("_"):
                failures.append(
                    "[ABS-SCS-17.c] Variable name must not start with an underscore."
                )

            pointer_count = var_type.count("*")
            schema_name = name
            if pointer_count >= 2:
                pointer_suffix = naming_policy["pointer_to_pointer_suffix"]
                if name.endswith(pointer_suffix):
                    schema_name = name[:-len(pointer_suffix)]
                else:
                    failures.append(
                        f"[ABS-SCS-17.j] Pointer-to-pointer name must end with '{pointer_suffix}'."
                    )
            elif pointer_count == 1:
                pointer_suffix = naming_policy["pointer_suffix"]
                if name.endswith(pointer_suffix):
                    schema_name = name[:-len(pointer_suffix)]
                else:
                    failures.append(
                        f"[ABS-SCS-17.i] Pointer name must end with '{pointer_suffix}'."
                    )

            #
            # Overall max length
            #

            if len(name) < min_length:
                failures.append(
                    f"[ABS-SCS-17.e] Name is shorter than the required {min_length} characters."
                )

            if len(name) > max_length:

                failures.append(
                    f"[ABS-SCS-17.d] Name exceeds the configured maximum of {max_length} characters."
                )

            #
            # Allowed characters
            #

            if not allowed_chars_pattern.fullmatch(
                name
            ):

                failures.append(
                    "[ABS-POLICY-GLOBAL-CHARACTERS] Name contains characters outside the configured identifier pattern."
                )

            #
            #
            # Data type
            #

            data_type_position = layout["data_type_position"]
            data_type = schema_name[data_type_position:data_type_position + 1]

            if not data_type:
                failures.append("[ABS-POLICY-GLOBAL-DATA-TYPE] Data type code is missing.")
            elif data_type not in allowed_data_types:
                failures.append(f"[ABS-POLICY-GLOBAL-DATA-TYPE] '{data_type}' is not an allowed data type code.")

            #
            # Data size
            #

            data_size_position = layout["data_size_position"]
            data_size = schema_name[data_size_position:data_size_position + 1]

            if not data_size:
                failures.append("[ABS-POLICY-GLOBAL-DATA-SIZE] Data size code is missing.")
            elif data_size not in allowed_data_sizes:
                failures.append(f"[ABS-POLICY-GLOBAL-DATA-SIZE] '{data_size}' is not an allowed data size code.")

            remaining = (
                schema_name[layout["remainder_start"]:]
                if len(schema_name) > layout["remainder_start"]
                else ""
            )

            parts = remaining.split(layout["separator"]) if len(schema_name) >= layout["remainder_start"] else []
            module_position = layout["module_position"]
            unit_position = layout["unit_position"]
            description_position = layout["description_position"]
            module = parts[module_position] if len(parts) > module_position else ""
            unit = parts[unit_position] if len(parts) > unit_position else ""
            description_parts = parts[description_position:] if len(parts) > description_position else []
            separator = layout["separator"]
            description = separator.join(description_parts)

            if len(parts) < naming_policy["layout"]["minimum_segment_count"]:
                failures.append(
                    "[ABS-POLICY-GLOBAL-SEGMENTS] Name must contain module, unit, and description segments separated by underscores."
                )

            if len(description_parts) > 1 and not naming_policy["description_separator_allowed"]:
                failures.append(
                    f"[ABS-POLICY-GLOBAL-DESCRIPTION] Keep the description as one lowerCamelCase segment without '{separator}'."
                )

            #
            # Module
            #

            if module and module not in allowed_modules:
                failures.append(f"[ABS-POLICY-GLOBAL-MODULE] '{module}' is not an allowed module code.")
            elif not module and naming_policy.get("enforce_module_required", True):
                failures.append("[ABS-POLICY-GLOBAL-MODULE] Module code is required.")

            #
            # Unit
            #

            if unit and unit not in allowed_units:
                failures.append(f"[ABS-POLICY-GLOBAL-UNIT] '{unit}' is not an allowed unit code.")
            elif not unit and naming_policy.get("enforce_unit_required", True):
                failures.append("[ABS-POLICY-GLOBAL-UNIT] Unit code is required.")

            #
            # Description
            #

            if description:
                if (
                    separator not in description
                    and not description_allowed_characters_pattern.fullmatch(
                        description
                    )
                ):
                    failures.append(
                        "[ABS-POLICY-GLOBAL-DESCRIPTION] Description may contain only letters and numbers."
                    )

                if (
                    naming_policy.get("description_must_start_lowercase", True)
                    and not description[0].islower()
                ):
                    failures.append("[ABS-POLICY-GLOBAL-DESCRIPTION] Description must start with a lowercase letter.")

                if len(description) < description_min_length:
                    failures.append(
                        f"[ABS-POLICY-GLOBAL-DESCRIPTION] Description is shorter than the configured {description_min_length} characters."
                    )

                if len(description) > description_max_length:
                    failures.append(
                        f"[ABS-POLICY-GLOBAL-DESCRIPTION] Description exceeds the configured {description_max_length} characters."
                    )
            elif naming_policy.get("enforce_description_required", True):
                failures.append("[ABS-POLICY-GLOBAL-DESCRIPTION] Description is required.")

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
