# src/repo_review/analysis/symbol_inventory/libclang_resolver.py


from clang import cindex
import os
from pathlib import Path
import glob


def configure_libclang():

    if cindex.Config.loaded:
        return

    candidates = [
        os.getenv("LIBCLANG_PATH"),
    ]

    if os.name == "posix":
        candidates.extend([
            "/usr/lib/x86_64-linux-gnu/libclang.so",
            "/usr/lib/x86_64-linux-gnu/libclang-*.so.*",
            "/usr/lib/llvm-*/lib/libclang.so*",
        ])

    elif os.name == "nt":
        candidates.extend([
            r"C:\Program Files\LLVM\bin\libclang.dll",
            r"C:\Program Files\LLVM\bin\libclang.dll",
        ])

    for candidate in candidates:

        if not candidate:
            continue

        matches = glob.glob(candidate)

        for path in matches:
            if Path(path).exists():
                cindex.Config.set_library_file(path)
                return

    raise RuntimeError(
        "libclang not found. Set LIBCLANG_PATH."
    )