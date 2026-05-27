# src/repo_review/checks/naming/array_sizes.py


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
