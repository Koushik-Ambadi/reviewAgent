# src/repo_review/checks/naming/runner.py
import json
from .function_names import (
    validate_function_names,
)

from .macro_names import (
    validate_macro_names,
)

from .array_sizes import (
    validate_array_sizes,
)

from .global_variable_names import (
    validate_global_variable_names,
)


def run_naming_checks(
    workspace_path,
    module_name,
    policy,
):
    symbols_path =(
        workspace_path
        / "analysis"
        / "symbols.json"
    )

    with open(
        symbols_path,
        "r",
        encoding="utf-8",
    ) as f:

        symbols = json.load(f)

    naming_policy = policy["naming"]

    results = []

    results.extend(
        validate_function_names(
            symbols,
            module_name,
            naming_policy,
        )
    )

    results.extend(
        validate_macro_names(
            symbols,
            module_name,
            naming_policy,
        )
    )

    results.extend(
        validate_array_sizes(
            symbols,
            naming_policy,
        )
    )

    results.extend(
        validate_global_variable_names(
            symbols,
            naming_policy,
        )
    )

    return results

