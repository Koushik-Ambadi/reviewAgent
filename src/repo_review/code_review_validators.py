# src/repo_review/code_review_validators.py

import json
import re
from pathlib import Path
from typing import Any


DEFAULT_RULES = {
    "function_name_pattern": r"^[A-Z][a-z]*(_[a-z]+)+$",
    "macro_name_pattern": r"^[A-Z]+(_[A-Z]+)*$",
    "excluded_function_patterns": [
        r"^look\d_",
        r"^plook_",
        r"^intrp",
        r"^binsearch_",
    ],
    "excluded_macro_patterns": [
        r"^{module}_IN_",
    ],
    "macro_value_type": "value",
}


def _merge_rules(rules: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_RULES)
    if rules:
        merged.update(rules)
    return merged


def is_excluded_function(name: str, rules: dict[str, Any] | None = None) -> bool:
    merged = _merge_rules(rules)
    return any(re.match(pattern, name) for pattern in merged["excluded_function_patterns"])


def is_excluded_macro(name: str, module_name: str, rules: dict[str, Any] | None = None) -> bool:
    merged = _merge_rules(rules)
    patterns = [
        pattern.format(module=module_name.lower())
        for pattern in merged["excluded_macro_patterns"]
    ]
    return any(re.match(pattern, name) for pattern in patterns)


def load_review_results(path: Path | str) -> list[dict[str, Any]]:
    with open(Path(path), "r", encoding="utf-8") as f:
        return json.load(f)


def validate_array_sizes(review_results):
    results = []

    for file_review in review_results:
        file_path = file_review.get("file", "")
        globals_list = file_review.get("globals", [])

        for global_var in globals_list:
            name = global_var.get("name", "")
            array_suffixes = global_var.get("array_suffixes", [])

            if not array_suffixes:
                continue

            for suffix in array_suffixes:
                dimension = suffix.replace("[", "").replace("]", "").strip()

                if dimension.isdigit():
                    results.append(
                        {
                            "status": "FAILED",
                            "rule": "array_sizes",
                            "file": file_path,
                            "message": (
                                f"[ARRAY SIZE] {file_path} -> {name} uses raw numeric "
                                f"array size [{dimension}]"
                            ),
                        }
                    )
                else:
                    results.append(
                        {
                            "status": "PASSED",
                            "rule": "array_sizes",
                            "file": file_path,
                            "message": (
                                f"[ARRAY SIZE] {file_path} -> {name} uses symbolic "
                                f"array size [{dimension}]"
                            ),
                        }
                    )

    return results


def validate_function_names(review_results, module_name, rules=None):
    results = []
    merged = _merge_rules(rules)
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


def validate_macro_names(review_results, module_name, rules=None):
    results = []
    merged = _merge_rules(rules)
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


def run_code_review_validations(review_results, module_name, rules=None):
    results = []
    results.extend(validate_function_names(review_results, module_name, rules))
    results.extend(validate_macro_names(review_results, module_name, rules))
    results.extend(validate_array_sizes(review_results))
    return results


def load_and_run(review_results_path: Path | str, module_name: str, rules=None):
    review_results = load_review_results(review_results_path)
    return run_code_review_validations(review_results, module_name, rules)


def _print_summary(results):
    passed_count = sum(1 for result in results if result["status"] == "PASSED")
    exception_count = sum(1 for result in results if result["status"] == "EXCEPTION")
    failed_count = sum(1 for result in results if result["status"] == "FAILED")

    print("\nCODE REVIEW RESULTS:\n")
    for result in results:
        if result["status"] != "PASSED":
            print(f"[{result['status']}] {result['message']}")

    print("\nSUMMARY:\n")
    print(f"PASSED   : {passed_count}")
    print(f"EXCEPTION: {exception_count}")
    print(f"FAILED   : {failed_count}")


if __name__ == "__main__":
    default_path = Path("soc") / "review_results.json"
    if default_path.exists():
        _print_summary(load_and_run(default_path, "soc"))
    else:
        print(f"Review results file not found: {default_path}")
