# src/repo_review/ast/sanitizers.py

from __future__ import annotations
from typing import Any


def sanitize_compile_args(
    args: list[str],
    sanitize_rules: dict[str, Any],
) -> list[str]:

    cleaned: list[str] = []

    skip_next = False

    consume_next = set(sanitize_rules.get("consume_next", []))
    skip_exact = set(sanitize_rules.get("skip_exact", []))
    skip_prefixes = tuple(sanitize_rules.get("skip_prefixes", []))

    for arg in args:
        if skip_next:
            skip_next = False
            continue

        if arg in consume_next:
            skip_next = True
            continue

        if arg in skip_exact:
            continue

        if skip_prefixes and arg.startswith(skip_prefixes):
            continue

        cleaned.append(arg)

    force_language = sanitize_rules.get("force_language", "c")
    language_standard = sanitize_rules.get("language_standard", "c99")

    cleaned.extend(
        [
            "-x",
            force_language,
            f"-std={language_standard}",
        ]
    )

    return cleaned