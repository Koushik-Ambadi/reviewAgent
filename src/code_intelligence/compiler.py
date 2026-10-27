from __future__ import annotations

import glob
import os
from pathlib import Path


DEFAULT_FORCE_LANGUAGE = "c"
DEFAULT_LANGUAGE_STANDARD = "c99"
_CONSUME_NEXT = {"-o", "-MF", "-MT", "-MQ", "--output", "-Xclang"}
_SKIP_EXACT = {"-c", "-MD", "-MMD", "-MP", "-Winvalid-pch", "-gcodeview"}
_SKIP_PREFIXES = (
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
)


def sanitize_compile_args(args: list[str]) -> list[str]:
    """Remove driver/output arguments that libclang cannot consume."""

    cleaned: list[str] = []
    skip_next = False
    for argument in args:
        if skip_next:
            skip_next = False
            continue
        if argument in _CONSUME_NEXT:
            skip_next = True
            continue
        if argument in _SKIP_EXACT or argument.startswith(_SKIP_PREFIXES):
            continue
        cleaned.append(argument)
    cleaned.extend(
        ["-x", DEFAULT_FORCE_LANGUAGE, f"-std={DEFAULT_LANGUAGE_STANDARD}"]
    )
    return cleaned


def configure_libclang() -> str:
    """Configure clang bindings from an explicit or well-known installation."""

    from clang import cindex

    if cindex.Config.loaded:
        return "already_loaded"
    candidates = [os.getenv("LIBCLANG_PATH")]
    if os.name == "nt":
        candidates.append(r"C:\Program Files\LLVM\bin\libclang.dll")
    else:
        candidates.extend(
            [
                "/usr/lib/x86_64-linux-gnu/libclang.so",
                "/usr/lib/x86_64-linux-gnu/libclang-*.so.*",
                "/usr/lib/llvm-*/lib/libclang.so*",
            ]
        )
    for candidate in candidates:
        if not candidate:
            continue
        for match in glob.glob(candidate):
            path = Path(match)
            if path.exists():
                cindex.Config.set_library_file(str(path))
                return str(path)
    raise RuntimeError("libclang not found. Set LIBCLANG_PATH.")
