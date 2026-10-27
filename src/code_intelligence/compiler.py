from __future__ import annotations

import glob
import os
from pathlib import Path


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
