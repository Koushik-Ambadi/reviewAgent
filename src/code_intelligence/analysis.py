from __future__ import annotations

from pathlib import Path
from typing import Any

from .compiler import sanitize_compile_args


def parse_translation_unit(
    file_path: Path,
    *,
    index: Any,
    compilation_database: Any,
) -> Any | None:
    """Parse one compilation-database entry for all downstream consumers."""

    from clang.cindex import TranslationUnit

    commands = compilation_database.getCompileCommands(str(file_path))
    if not commands:
        return None
    command = list(commands)[0]
    raw_args = list(command.arguments)[1:]
    if raw_args:
        try:
            if Path(raw_args[-1]).resolve() == file_path.resolve():
                raw_args = raw_args[:-1]
        except (OSError, RuntimeError, ValueError):
            pass
    return index.parse(
        str(file_path),
        args=sanitize_compile_args(raw_args),
        options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
    )
