# src/repo_review/checks/naming/function_names.py

import re

from .rules import (
    merge_rules,
    is_excluded_function,
)

def validate_function_names(review_results, module_name, rules=None):
    results = []
    merged = merge_rules(rules)
    function_pattern = re.compile(merged["function_name_pattern"])

    expected_prefix = module_name[0].upper() + module_name[1:].lower() if module_name else ""

    for file_review in review_results:
        file_path = file_review.get("file", "")
        functions = file_review.get("functions_defined", [])

        for function in functions:
            name = function.get("name", "")

            if is_excluded_function(name, merged):
                results.append(
                    {
                        "status": "EXCEPTION",
                        "rule": "function_names",
                        "file": file_path,
                        "message": f"[FUNCTION] {file_path} -> {name} skipped (excluded pattern)",
                    }
                )
                continue

            if not function_pattern.match(name):
                results.append(
                    {
                        "status": "FAILED",
                        "rule": "function_names",
                        "file": file_path,
                        "message": f"[FUNCTION] {file_path} -> Invalid function name: {name}",
                    }
                )
                continue

            actual_prefix = name.split("_")[0]

            if expected_prefix and actual_prefix != expected_prefix:
                results.append(
                    {
                        "status": "FAILED",
                        "rule": "function_names",
                        "file": file_path,
                        "message": (
                            f"[FUNCTION] {file_path} -> {name} must start with "
                            f"{expected_prefix}_"
                        ),
                    }
                )
                continue

            results.append(
                {
                    "status": "PASSED",
                    "rule": "function_names",
                    "file": file_path,
                    "message": f"[FUNCTION] {file_path} -> {name} passed validation",
                }
            )

    return results

