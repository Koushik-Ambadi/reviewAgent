# src/repo_review/checks/naming/runner.py
import json

from .array_sizes import validate_array_sizes
from .enum_constant_names import validate_enum_constant_names
from .function_names import validate_function_names
from .global_variable_names import validate_global_variable_names
from .local_variable_names import validate_local_variable_names
from .macro_names import validate_macro_names
from .parameter_names import validate_parameter_names
from .type_names import validate_type_names


def run_naming_checks(
    workspace_path,
    module_name,
    naming_policy,
):
    symbols_path = (
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



    return [
         validate_function_names(
             symbols,
             module_name,
             naming_policy["function_names"],
         ),
         validate_macro_names(
             symbols,
             module_name,
             naming_policy["macro_names"],
         ),
        validate_type_names(
            symbols,
            module_name,
            naming_policy["type_names"],
        ),
        validate_enum_constant_names(
            symbols,
            module_name,
            naming_policy["enum_constant_names"],
        ),
        validate_parameter_names(
            symbols,
            naming_policy["parameter_names"],
        ),
        validate_local_variable_names(
            symbols,
           naming_policy["local_variable_names"],
        ),
         validate_array_sizes(
             symbols,
             naming_policy["array_sizes"],
         ),
         validate_global_variable_names(
             symbols,
             naming_policy["global_variable_names"],
         ),
     ]