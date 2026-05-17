import json
import re
import sys
from pathlib import Path

# ============================================================
# Naming Rule
# ============================================================
#
# Rule:
#   ModuleName_snake_case
#
# Examples:
#   Soc_initialize        -> VALID
#   Soc_read_inputs       -> VALID
#   Soc_GetState          -> INVALID
#   soc_initialize        -> INVALID
#
# Regex:
#   First word:
#       Starts with capital letter
#       Remaining letters lowercase/digits
#
#   Remaining words:
#       Strict snake_case lowercase
#
# ============================================================

FUNCTION_REGEX = re.compile(
    r'^[A-Z][a-z0-9]*(?:_[a-z0-9]+)*$'
)


def is_valid_function_name(name: str) -> bool:
    return bool(FUNCTION_REGEX.fullmatch(name))


def check_functions(data):
    errors = []

    sections = [
        ("functions_defined", data.get("functions_defined", [])),
        ("functions_declared", data.get("functions_declared", [])),
    ]

    for section_name, functions in sections:
        for func in functions:
            name = func.get("name", "")
            line = func.get("line", "Unknown")

            if not is_valid_function_name(name):
                errors.append({
                    "section": section_name,
                    "function": name,
                    "line": line,
                    "message": (
                        "Invalid function name. "
                        "Expected format: Module_snake_case "
                        "(Example: Soc_read_inputs)"
                    )
                })

    return errors


def print_report(file_path, errors):
    print("\n========================================")
    print(" Function Naming Convention Report")
    print("========================================")

    print(f"\nFile: {file_path}")

    if not errors:
        print("\n✅ No naming violations found.")
        return

    print(f"\n❌ Total Violations: {len(errors)}\n")

    for idx, err in enumerate(errors, 1):
        print(f"{idx}. Line {err['line']}")
        print(f"   Section : {err['section']}")
        print(f"   Function: {err['function']}")
        print(f"   Error   : {err['message']}")
        print()


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("    python check_names.py <json_file>")
        sys.exit(1)

    json_file = Path(sys.argv[1])

    if not json_file.exists():
        print(f"ERROR: File not found -> {json_file}")
        sys.exit(1)

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = check_functions(data)

    print_report(data.get("file", str(json_file)), errors)


if __name__ == "__main__":
    main()