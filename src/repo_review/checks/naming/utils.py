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
    for item in patterns:
        pattern = item["pattern"] if isinstance(item, dict) else item
        if re.match(pattern.format(module=module_name.upper()), name):
            return True
    return False


def is_excluded_global(
    var_type: str,
    patterns: list[str],
) -> bool:

    return any(
        re.match(pattern, var_type)
        for pattern in patterns
    )
