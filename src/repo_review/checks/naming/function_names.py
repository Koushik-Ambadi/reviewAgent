# src/repo_review/checks/naming/function_names.py

import re

from .utils import (
    is_excluded_function,
)


def validate_function_names(
    symbols,
    module_name,
    naming_policy,
):

    results = []

    function_pattern = re.compile(
        naming_policy[
            "function_name_pattern"
        ]
    )

    expected_prefix = (
        module_name[0].upper()
        + module_name[1:].lower()
        if module_name
        else ""
    )

    for file_symbols in symbols:

        file_path = file_symbols.get(
            "file",
            "",
        )

        functions = file_symbols.get(
            "functions_defined",
            [],
        )

        for function in functions:

            name = function.get(
                "name",
                "",
            )

            if is_excluded_function(
                name,
                naming_policy["excluded_function_patterns"],
            ):

                results.append(
                    {
                        "status":
                            "EXCEPTION",

                        "rule":
                            "function_names",

                        "file":
                            file_path,

                        "message":
                            f"[FUNCTION] "
                            f"{file_path} -> "
                            f"{name} skipped "
                            f"(excluded pattern)",
                    }
                )

                continue

            if not function_pattern.match(
                name
            ):

                results.append(
                    {
                        "status":
                            "FAILED",

                        "rule":
                            "function_names",

                        "file":
                            file_path,

                        "message":
                            f"[FUNCTION] "
                            f"{file_path} -> "
                            f"Invalid function name: "
                            f"{name}",
                    }
                )

                continue

            actual_prefix = (
                name.split("_")[0]
            )

            if (
                expected_prefix
                and
                actual_prefix
                != expected_prefix
            ):

                results.append(
                    {
                        "status":
                            "FAILED",

                        "rule":
                            "function_names",

                        "file":
                            file_path,

                        "message":
                            (
                                f"[FUNCTION] "
                                f"{file_path} -> "
                                f"{name} must start "
                                f"with "
                                f"{expected_prefix}_"
                            ),
                    }
                )

                continue

            results.append(
                {
                    "status":
                        "PASSED",

                    "rule":
                        "function_names",

                    "file":
                        file_path,

                    "message":
                        f"[FUNCTION] "
                        f"{file_path} -> "
                        f"{name} passed validation",
                }
            )

    return results