# src/repo_review/checks/naming/macro_names.py

import re

from .utils import (
    is_excluded_macro,
)


def validate_macro_names(
    symbols,
    module_name,
    naming_policy,
):
    results = []

    macro_pattern = re.compile(
        naming_policy["macro_name_pattern"]
    )

    value_type = naming_policy["macro_value_type"]

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

            if macro_type != value_type:
                continue

            if is_excluded_macro(
                name,
                naming_policy["excluded_macro_patterns"],
                module_name,
            ):
                results.append(
                    {
                        "status": "EXCEPTION",
                        "rule": "macro_names",
                        "file": file_path,
                        "message": (
                            f"[MACRO] {file_path} -> "
                            f"{name} skipped "
                            f"(excluded pattern)"
                        ),
                    }
                )
                continue

            if not macro_pattern.match(name):
                results.append(
                    {
                        "status": "FAILED",
                        "rule": "macro_names",
                        "file": file_path,
                        "message": (
                            f"[MACRO] {file_path} -> "
                            f"Invalid macro name: {name}"
                        ),
                    }
                )
                continue

            results.append(
                {
                    "status": "PASSED",
                    "rule": "macro_names",
                    "file": file_path,
                    "message": (
                        f"[MACRO] {file_path} -> "
                        f"{name} passed validation"
                    ),
                }
            )

    return results