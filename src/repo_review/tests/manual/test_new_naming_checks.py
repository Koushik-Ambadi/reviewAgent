# src/repo_review/tests/manual/test_new_naming_checks.py


import json
from pathlib import Path

from repo_review.checks.naming.enum_constant_names import (
    validate_enum_constant_names,
)
from repo_review.checks.naming.local_variable_names import (
    validate_local_variable_names,
)
from repo_review.checks.naming.parameter_names import (
    validate_parameter_names,
)
from repo_review.checks.naming.type_names import (
    validate_type_names,
)


WORKSPACE = Path(
    r"workspace\runs\20260727_131845_e479c8c0"
)

SYMBOLS_PATH = WORKSPACE / "analysis" / "symbols.json"

MODULE_NAME = "soc"


TYPE_NAMES_POLICY = {
    "max_length": 31,
    "allowed_characters_pattern": r"^[A-Za-z0-9_]+$",
    "leading_underscore_allowed": False,
    "consecutive_underscores_allowed": False,
    "trailing_underscore_allowed": False,
    "module_prefix": "{module}_",
    "suffix": "_t",
    "description_required": True,
    "applicability_exclusions": [],
}


ENUM_CONSTANT_NAMES_POLICY = {
    "max_length": 31,
    "allowed_characters_pattern":
        r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$",
    "leading_underscore_allowed": False,
    "consecutive_underscores_allowed": False,
    "trailing_underscore_allowed": False,
    "module_prefix": "{module}_",
    "description_required": True,
    "applicability_exclusions": [],
    "pointer_suffix": "_ptr",
    "pointer_to_pointer_suffix": "_ptr_ptr",
}


PARAMETER_NAMES_POLICY = {
    "min_length": 3,
    "max_length": 31,
    "allowed_characters_pattern": r"^[A-Za-z0-9_]+$",
    "missing_name_allowed": False,
    "leading_underscore_allowed": False,
    "consecutive_underscores_allowed": False,
    "trailing_underscore_allowed": False,
    "pointer_suffix": "_ptr",
    "pointer_to_pointer_suffix": "_ptr_ptr",
    "applicability_exclusions": [],
}


LOCAL_VARIABLE_NAMES_POLICY = {
    "min_length": 3,
    "max_length": 31,
    "allowed_characters_pattern": r"^[A-Za-z0-9_]+$",
    "missing_name_allowed": False,
    "leading_underscore_allowed": False,
    "consecutive_underscores_allowed": False,
    "trailing_underscore_allowed": False,
    "applicability_exclusions": [],
}


def print_result(result):
    print()
    print("=" * 80)
    print(result.title)
    print("=" * 80)

    print(
        f"Status : {result.status}"
    )

    print(
        f"Passed : {result.summary.passed}"
    )

    print(
        f"Failed : {result.summary.failed}"
    )

    print(
        f"Skipped: {result.summary.skipped}"
    )

    print(
        f"Total  : {result.summary.total}"
    )

    print()

    for case in result.cases:
        print(
            f"[{case.status}] "
            f"{case.name} "
            f"@ {case.location}"
        )

        for reason in case.reasons:
            print(f"    - {reason}")


def main():
    with open(
        SYMBOLS_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        symbols = json.load(f)

    results = [
        validate_type_names(
            symbols,
            MODULE_NAME,
            TYPE_NAMES_POLICY,
        ),
        validate_enum_constant_names(
            symbols,
            MODULE_NAME,
            ENUM_CONSTANT_NAMES_POLICY,
        ),
        validate_parameter_names(
            symbols,
            PARAMETER_NAMES_POLICY,
        ),
        validate_local_variable_names(
            symbols,
            LOCAL_VARIABLE_NAMES_POLICY,
        ),
    ]

    for result in results:
        print_result(result)


if __name__ == "__main__":
    main()