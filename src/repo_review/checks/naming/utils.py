# src/repo_review/checks/naming/utils.py

import re


def is_excluded_function(
    name: str,
    patterns: list[str],
) -> bool:

    return any(
        re.match(pattern, name)
        for pattern in patterns
    )


def is_excluded_macro(
    name: str,
    patterns: list[str],
    module_name: str,
) -> bool:

    expanded = [
        pattern.format(
            module=module_name.lower()
        )
        for pattern in patterns
    ]

    return any(
        re.match(pattern, name)
        for pattern in expanded
    )


def is_excluded_global(
    var_type: str,
    patterns: list[str],
) -> bool:

    return any(
        re.match(pattern, var_type)
        for pattern in patterns
    )