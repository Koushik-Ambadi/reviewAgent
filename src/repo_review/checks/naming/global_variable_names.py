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
    rules = {
        rule["key"]: rule
        for rule in naming_policy["automatic_rules"]
    }

    def policy_reason(key: str, **values: object) -> str:
        rule = rules[key]
        return f"[{rule['id']}] {rule['reason'].format(**values)}"

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
                        reasons=[policy_reason("missing_name")],
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
                            policy_reason("excluded_type", var_type=var_type)
                        ],
                    )
                )

                continue

            failures = []

            if not naming_policy["leading_underscore_allowed"] and name.startswith("_"):
                failures.append(
                    policy_reason("leading_underscore")
                )

            pointer_count = var_type.count("*")
            schema_name = name
            if pointer_count >= 2:
                pointer_suffix = naming_policy["pointer_to_pointer_suffix"]
                if name.endswith(pointer_suffix):
                    schema_name = name[:-len(pointer_suffix)]
                else:
                    failures.append(
                        policy_reason("pointer_to_pointer_suffix", expected=pointer_suffix)
                    )
            elif pointer_count == 1:
                pointer_suffix = naming_policy["pointer_suffix"]
                if name.endswith(pointer_suffix):
                    schema_name = name[:-len(pointer_suffix)]
                else:
                    failures.append(
                        policy_reason("pointer_suffix", expected=pointer_suffix)
                    )

            #
            # Overall max length
            #

            if len(name) < min_length:
                failures.append(
                    policy_reason("minimum_length", minimum_name_length=min_length)
                )

            if len(name) > max_length:

                failures.append(
                    policy_reason("maximum_length", name_max_length=max_length)
                )

            #
            # Allowed characters
            #

            if not allowed_chars_pattern.fullmatch(
                name
            ):

                failures.append(
                    policy_reason("allowed_characters")
                )

            #
            #
            # Data type
            #

            data_type_position = layout["data_type_position"]
            data_type = schema_name[data_type_position:data_type_position + 1]

            if not data_type:
                failures.append(policy_reason("data_type_missing"))
            elif data_type not in allowed_data_types:
                failures.append(policy_reason("data_type_allowed", data_type=data_type))

            #
            # Data size
            #

            data_size_position = layout["data_size_position"]
            data_size = schema_name[data_size_position:data_size_position + 1]

            if not data_size:
                failures.append(policy_reason("data_size_missing"))
            elif data_size not in allowed_data_sizes:
                failures.append(policy_reason("data_size_allowed", data_size=data_size))

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
                    policy_reason("segment_count")
                )

            if len(description_parts) > 1 and not naming_policy["description_separator_allowed"]:
                failures.append(
                    policy_reason("description_separator", separator=separator)
                )

            #
            # Module
            #

            if module and module not in allowed_modules:
                failures.append(policy_reason("module_allowed", module=module))
            elif not module and naming_policy.get("enforce_module_required", True):
                failures.append(policy_reason("module_required"))

            #
            # Unit
            #

            if unit and unit not in allowed_units:
                failures.append(policy_reason("unit_allowed", unit=unit))
            elif not unit and naming_policy.get("enforce_unit_required", True):
                failures.append(policy_reason("unit_required"))

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
                        policy_reason("description_characters")
                    )

                if (
                    naming_policy.get("description_must_start_lowercase", True)
                    and not description[0].islower()
                ):
                    failures.append(policy_reason("description_initial"))

                if len(description) < description_min_length:
                    failures.append(
                        policy_reason("description_minimum_length", description_min_length=description_min_length)
                    )

                if len(description) > description_max_length:
                    failures.append(
                        policy_reason("description_maximum_length", description_max_length=description_max_length)
                    )
            elif naming_policy.get("enforce_description_required", True):
                failures.append(policy_reason("description_required"))

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
