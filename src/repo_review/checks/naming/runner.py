# src/repo_review/checks/naming/runner.py


from .function_names import validate_function_names
from .macro_names import validate_macro_names
from .array_sizes import validate_array_sizes
from .global_variable_names import validate_global_variable_names

def run_validations(
    review_results,
    module_name,
    rules=None,
):

    results = []

    results.extend(
        validate_function_names(
            review_results,
            module_name,
            rules,
        )
    )

    results.extend(
        validate_macro_names(
            review_results,
            module_name,
            rules,
        )
    )

    results.extend(
        validate_array_sizes(review_results)
    )

    results.extend(
        validate_global_variable_names(
            review_results,
            rules,
        )
    )

    return results