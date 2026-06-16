# src/repo_review/analysis/symbol_inventory/libclang_resolver.py

from clang import cindex
import os
from pathlib import Path


def configure_libclang():

    if cindex.Config.loaded:
        return

    candidates = [
        os.getenv("LIBCLANG_PATH"),
        "/usr/lib/x86_64-linux-gnu/libclang-19.so.19",
        "/usr/lib/libclang.so",
    ]

    for path in candidates:
        if path and Path(path).exists():
            cindex.Config.set_library_file(path)
            return

    raise RuntimeError(
        "libclang not found"
    )