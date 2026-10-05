# src/repo_review/checks/naming/common_identifier.py

import re


def is_within_length(
    name: str,
    min_length: int | None = None,
    max_length: int | None = None,
) -> bool:
    length = len(name)

    if min_length is not None and length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True


def has_valid_characters(
    name: str,
    pattern: str,
) -> bool:
    return re.fullmatch(pattern, name) is not None


def has_leading_underscore(name: str) -> bool:
    return name.startswith("_")


def has_consecutive_underscores(name: str) -> bool:
    return "__" in name


def has_trailing_underscore(name: str) -> bool:
    return name.endswith("_")