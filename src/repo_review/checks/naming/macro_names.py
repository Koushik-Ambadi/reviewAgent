# src/repo_review/checks/naming/macro_names.py

import re

from .rules import (
    merge_rules,
    is_excluded_macro,
)


def validate_macro_names(review_results, module_name, rules=None):
    results = []
    merged = merge_rules(rules)
    macro_pattern = re.compile(merged["macro_name_pattern"])
    value_type = merged.get("macro_value_type", "value")

    for file_review in review_results:
        file_path = file_review.get("file", "")
        macros = file_review.get("macros", [])

        for macro in macros:
            name = macro.get("name", "")
            macro_type = macro.get("type", "")

            if macro_type != value_type:
                continue

            if is_excluded_macro(name, module_name, merged):
                results.append(
                    {
                        "status": "EXCEPTION",
                        "rule": "macro_names",
                        "file": file_path,
                        "message": f"[MACRO] {file_path} -> {name} skipped (excluded pattern)",
                    }
                )
                continue

            if not macro_pattern.match(name):
                results.append(
                    {
                        "status": "FAILED",
                        "rule": "macro_names",
                        "file": file_path,
                        "message": f"[MACRO] {file_path} -> Invalid macro name: {name}",
                    }
                )
                continue

            results.append(
                {
                    "status": "PASSED",
                    "rule": "macro_names",
                    "file": file_path,
                    "message": f"[MACRO] {file_path} -> {name} passed validation",
                }
            )

    return results
