# src/repo_review/checks/naming/array_sizes.py


def validate_array_sizes(
    symbols,
    naming_policy,
):

    enforce_symbolic_sizes = (
        naming_policy["enforce_symbolic_array_sizes"]
    )

    if not enforce_symbolic_sizes:
        return []

    results = []

    for file_symbols in symbols:

        file_path = file_symbols.get(
            "file",
            "",
        )

        globals_list = file_symbols.get(
            "globals",
            [],
        )

        for global_var in globals_list:

            name = global_var.get(
                "name",
                "",
            )

            array_suffixes = global_var.get(
                "array_suffixes",
                [],
            )

            if not array_suffixes:
                continue

            for suffix in array_suffixes:

                dimension = (
                    suffix
                    .replace("[", "")
                    .replace("]", "")
                    .strip()
                )

                if dimension.isdigit():

                    results.append(
                        {
                            "status": "FAILED",
                            "rule": "array_sizes",
                            "file": file_path,
                            "message": (
                                f"[ARRAY SIZE] "
                                f"{file_path} -> "
                                f"{name} uses raw numeric "
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
                                f"[ARRAY SIZE] "
                                f"{file_path} -> "
                                f"{name} uses symbolic "
                                f"array size [{dimension}]"
                            ),
                        }
                    )

    return results