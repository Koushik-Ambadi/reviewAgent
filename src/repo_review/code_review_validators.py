import json
import re


# =====================================================
# RULES
# =====================================================

FUNCTION_PATTERN = re.compile(
    r"^[A-Z][a-z]*(_[a-z]+)+$"
)

MACRO_PATTERN = re.compile(
    r"^[A-Z]+(_[A-Z]+)*$"
)


# =====================================================
# EXCLUSIONS
# =====================================================

EXCLUDED_FUNCTION_PATTERNS = [
    r"^look\d_",
    r"^plook_",
    r"^intrp",
    r"^binsearch_",
]

EXCLUDED_MACRO_PATTERNS = [
    r"^{module}_IN_",
]


# =====================================================
# HELPERS
# =====================================================

def is_excluded_function(name):

    return any(
        re.match(pattern, name)
        for pattern in EXCLUDED_FUNCTION_PATTERNS
    )


def is_excluded_macro(
    name,
    module_name,
):

    patterns = [
        pattern.format(
            module=module_name.lower()
        )
        for pattern in EXCLUDED_MACRO_PATTERNS
    ]

    return any(
        re.match(pattern, name)
        for pattern in patterns
    )


# =====================================================
# ARRAY SIZE VALIDATION
# =====================================================

def validate_array_sizes(
    review_results,
):

    results = []

    for file_review in review_results:

        file_path = file_review.get(
            "file",
            ""
        )

        globals_list = file_review.get(
            "globals",
            []
        )

        for global_var in globals_list:

            name = global_var.get(
                "name",
                ""
            )

            array_suffixes = global_var.get(
                "array_suffixes",
                []
            )

            # ---------------------------------
            # Skip non-arrays
            # ---------------------------------

            if not array_suffixes:
                continue

            # ---------------------------------
            # Validate every dimension
            # ---------------------------------

            for suffix in array_suffixes:

                dimension = (
                    suffix
                    .replace("[", "")
                    .replace("]", "")
                    .strip()
                )

                # ---------------------------------
                # FAILED
                # ---------------------------------

                if dimension.isdigit():

                    results.append({
                        "status": "FAILED",
                        "message":
                            f"[ARRAY SIZE] {file_path} -> "
                            f"{name} uses raw numeric "
                            f"array size [{dimension}]"
                    })

                # ---------------------------------
                # PASSED
                # ---------------------------------

                else:

                    results.append({
                        "status": "PASSED",
                        "message":
                            f"[ARRAY SIZE] {file_path} -> "
                            f"{name} uses symbolic "
                            f"array size [{dimension}]"
                    })

    return results


# =====================================================
# FUNCTION VALIDATION
# =====================================================

def validate_function_names(
    review_results,
    module_name,
):

    results = []

    expected_prefix = (
        module_name[0].upper()
        + module_name[1:].lower()
    )

    for file_review in review_results:

        file_path = file_review.get(
            "file",
            ""
        )

        functions = file_review.get(
            "functions_defined",
            []
        )

        for function in functions:

            name = function.get(
                "name",
                ""
            )

            # ---------------------------------
            # EXCEPTION
            # ---------------------------------

            if is_excluded_function(name):

                results.append({
                    "status": "EXCEPTION",
                    "message":
                        f"[FUNCTION] {file_path} -> "
                        f"{name} skipped "
                        f"(excluded pattern)"
                })

                continue

            # ---------------------------------
            # FAILED
            # ---------------------------------

            if not FUNCTION_PATTERN.match(name):

                results.append({
                    "status": "FAILED",
                    "message":
                        f"[FUNCTION] {file_path} -> "
                        f"Invalid function name: "
                        f"{name}"
                })

                continue

            actual_prefix = (
                name.split("_")[0]
            )

            if actual_prefix != expected_prefix:

                results.append({
                    "status": "FAILED",
                    "message":
                        f"[FUNCTION] {file_path} -> "
                        f"{name} must start with "
                        f"{expected_prefix}_"
                })

                continue

            # ---------------------------------
            # PASSED
            # ---------------------------------

            results.append({
                "status": "PASSED",
                "message":
                    f"[FUNCTION] {file_path} -> "
                    f"{name} passed validation"
            })

    return results


# =====================================================
# MACRO VALIDATION
# =====================================================

def validate_macro_names(
    review_results,
    module_name,
):

    results = []

    for file_review in review_results:

        file_path = file_review.get(
            "file",
            ""
        )

        macros = file_review.get(
            "macros",
            []
        )

        for macro in macros:

            name = macro.get(
                "name",
                ""
            )

            macro_type = macro.get(
                "type",
                ""
            )

            # ---------------------------------
            # Skip non-value macros
            # ---------------------------------

            if macro_type != "value":
                continue

            # ---------------------------------
            # EXCEPTION
            # ---------------------------------

            if is_excluded_macro(
                name,
                module_name,
            ):

                results.append({
                    "status": "EXCEPTION",
                    "message":
                        f"[MACRO] {file_path} -> "
                        f"{name} skipped "
                        f"(excluded pattern)"
                })

                continue

            # ---------------------------------
            # FAILED
            # ---------------------------------

            if not MACRO_PATTERN.match(name):

                results.append({
                    "status": "FAILED",
                    "message":
                        f"[MACRO] {file_path} -> "
                        f"Invalid macro name: "
                        f"{name}"
                })

                continue

            # ---------------------------------
            # PASSED
            # ---------------------------------

            results.append({
                "status": "PASSED",
                "message":
                    f"[MACRO] {file_path} -> "
                    f"{name} passed validation"
            })

    return results


# =====================================================
# MAIN
# =====================================================

with open(
    "soc/review_results.json",
    "r",
    encoding="utf-8"
) as f:

    review_results = json.load(f)


module_name = "soc"

all_results = []

all_results.extend(
    validate_function_names(
        review_results,
        module_name,
    )
)

all_results.extend(
    validate_macro_names(
        review_results,
        module_name,
    )
)

all_results.extend(
    validate_array_sizes(
        review_results,
    )
)


# =====================================================
# OUTPUT
# =====================================================

print("\nCODE REVIEW RESULTS:\n")

passed_count = 0
exception_count = 0
failed_count = 0

for result in all_results:

    status = result["status"]

    if status == "PASSED":
        passed_count += 1

    elif status == "EXCEPTION":
        exception_count += 1
        print(
            f"[{status}] "
            f"{result['message']}"
        )
    elif status == "FAILED":
        failed_count += 1
        print(
            f"[{status}] "
            f"{result['message']}"
        )




print("\nSUMMARY:\n")

print(f"PASSED   : {passed_count}")
print(f"EXCEPTION: {exception_count}")
print(f"FAILED   : {failed_count}")