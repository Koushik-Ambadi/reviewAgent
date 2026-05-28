# src/repo_review/checks/naming/global_variable_names.py

import re

from .rules import (
    merge_rules,
    is_excluded_global,
)


def validate_global_variable_names(review_results, rules=None):

    results = []

    merged = merge_rules(rules)

    allowed_chars_pattern = re.compile(
        merged["global_variable_allowed_chars_pattern"]
    )

    allowed_data_types = merged["global_variable_data_types"]
    allowed_data_sizes = merged["global_variable_data_sizes"]
    allowed_modules = merged["global_variable_modules"]
    allowed_units = merged["global_variable_units"]

    max_length = merged["global_variable_name_max_length"]

    #
    # Assumptions / Known Limitations
    #
    # 1. data_type assumed to be exactly 1 character
    #
    # 2. data_size assumed to be exactly 1 character
    #
    # 3. Naming order assumed fixed:
    #    <type><size><module>_<unit>_<description>
    #
    # 4. Description cannot contain underscores
    #
    # 5. Description must start lowercase
    #
    # 6. Description length fixed to 14-22 chars
    #
    # 7. Validation is structure-based only.
    #

    for file_review in review_results:

        file_path = file_review.get("file", "")

        globals_list = file_review.get("globals", [])

        print()
        print()

        for global_var in globals_list:

            if results:
                print(results[-1]["message"], flush=True)

            name = global_var.get("name", "")
            var_type = global_var.get("type", "")
            line = global_var.get("line", "?")

            #
            # Skip generated/system globals
            #

            if is_excluded_global(var_type, merged):

                results.append(
                    {
                        "status": "EXCEPTION",
                        "rule": "global_variable_names",
                        "file": file_path,
                        "message": (
                            f"[GLOBAL] {file_path}:{line} -> "
                            f"{name} skipped (excluded type)"
                        ),
                    }
                )

                continue

            failures = []

            #
            # Overall max length
            #

            if len(name) > max_length:

                failures.append(
                    f"exceeds max length ({max_length})"
                )

            #
            # Allowed characters
            #

            if not allowed_chars_pattern.fullmatch(name):

                failures.append(
                    "contains invalid characters"
                )

            #
            # Minimum length sanity
            #

            if len(name) < 3:

                failures.append(
                    "too short to parse"
                )

            #
            # Step 1 -> data_type
            #

            data_type = ""

            if len(name) >= 1:

                data_type = name[0]

                if data_type not in allowed_data_types:

                    failures.append(
                        f"invalid data type '{data_type}'"
                    )

            #
            # Step 2 -> data_size
            #

            data_size = ""

            if len(name) >= 2:

                data_size = name[1]

                if data_size not in allowed_data_sizes:

                    failures.append(
                        f"invalid data size '{data_size}'"
                    )

            #
            # Remaining after type + size
            #

            remaining = name[2:] if len(name) > 2 else ""

            #
            # Expected:
            # module_unit_description
            #

            parts = remaining.split("_")

            if len(parts) != 3:

                failures.append(
                    "must contain exactly 2 underscores "
                    "after type/size section"
                )

                module = ""
                unit = ""
                description = ""

            else:

                module = parts[0]
                unit = parts[1]
                description = parts[2]

            #
            # Step 3 -> module validation
            #

            if module:

                if module not in allowed_modules:

                    failures.append(
                        f"invalid module '{module}'"
                    )

            #
            # Step 4 -> unit validation
            #

            if unit:

                if unit not in allowed_units:

                    failures.append(
                        f"invalid unit '{unit}'"
                    )

            #
            # Step 5 -> description validation
            #

            if description:

                #
                # Must start lowercase
                #

                if not description[0].islower():

                    failures.append(
                        "description must start "
                        "with lowercase letter"
                    )

                #
                # Alphanumeric only
                #

                if not description.isalnum():

                    failures.append(
                        "description must contain "
                        "only letters and numbers"
                    )

                #
                # Length checks
                #

                if len(description) < 14:

                    failures.append(
                        "description length must be >= 14"
                    )

                if len(description) > 22:

                    failures.append(
                        "description length must be <= 22"
                    )

            else:

                failures.append(
                    "description missing"
                )

            #
            # Final result
            #

            if failures:

                results.append(
                    {
                        "status": "FAILED",
                        "rule": "global_variable_names",
                        "file": file_path,
                        "message": (
                            f"[GLOBAL] {file_path}:{line} -> "
                            f"{name} failed validation: "
                            + "; ".join(failures)
                        ),
                    }
                )

            else:

                results.append(
                    {
                        "status": "PASSED",
                        "rule": "global_variable_names",
                        "file": file_path,
                        "message": (
                            f"[GLOBAL] {file_path}:{line} -> "
                            f"{name} passed validation"
                        ),
                    }
                )

    return results