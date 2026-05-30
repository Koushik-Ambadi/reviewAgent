# src/repo_review/analysis/symbol_inventory/compile_args.py

from __future__ import annotations


DEFAULT_FORCE_LANGUAGE = "c"

DEFAULT_LANGUAGE_STANDARD = "c99"

DEFAULT_SANITIZE_RULES = {
    "consume_next": {
        "-o",
        "-MF",
        "-MT",
        "-MQ",
        "--output",
        "-Xclang",
    },

    "skip_prefixes": (
        "--cpu=",
        "-mcpu=",
        "-mfpu=",
        "-mfloat-abi=",
        "--target=",
        "-fshort-enums",
        "-fshort-wchar",
        "--specs=",
        "-ffreestanding",
        "-fno-common",
        "-fmessage-length=",
        "-fcyclomatic-complexity",
        "-fstack-usage",
        "--diag_suppress",
        "--diag_warning",
        "--diag_error",
        "--misra_",
        "--gcc",
        "--gnu",
        "--abi",
        "--thumb",
    ),

    "skip_exact": {
        "-c",
        "-MD",
        "-MMD",
        "-MP",
        "-Winvalid-pch",
        "-gcodeview",
    },
}


def sanitize_compile_args(
    args: list[str],
) -> list[str]:

    cleaned: list[str] = []

    skip_next = False

    consume_next = DEFAULT_SANITIZE_RULES[
        "consume_next"
    ]

    skip_exact = DEFAULT_SANITIZE_RULES[
        "skip_exact"
    ]

    skip_prefixes = DEFAULT_SANITIZE_RULES[
        "skip_prefixes"
    ]

    for arg in args:

        if skip_next:
            skip_next = False
            continue

        if arg in consume_next:
            skip_next = True
            continue

        if arg in skip_exact:
            continue

        if skip_prefixes and arg.startswith(
            skip_prefixes
        ):
            continue

        cleaned.append(arg)

    cleaned.extend(
        [
            "-x",
            DEFAULT_FORCE_LANGUAGE,
            f"-std={DEFAULT_LANGUAGE_STANDARD}",
        ]
    )

    return cleaned