#src/repo_review/analysis/symbol_inventory/libclang.py

from pathlib import Path

from clang.cindex import Config


DEFAULT_LIBCLANG_PATH = (
    r"C:/Program Files/LLVM/bin/libclang.dll"
)


def configure_libclang() -> None:

    try:
        if Path(DEFAULT_LIBCLANG_PATH).exists():
            Config.set_library_file(
                DEFAULT_LIBCLANG_PATH
            )
    except Exception:
        pass