# src/repo_review/ast/clang_config.py

from pathlib import Path
from clang.cindex import Config


def configure_libclang(libclang_path: str | None) -> None:
    if not libclang_path:
        return

    try:
        if Path(libclang_path).exists():
            Config.set_library_file(libclang_path)
    except Exception:
        pass