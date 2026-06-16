# src/repo_review/analysis/symbol_inventory/extractor.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TYPE_CHECKING

from .libclang_resolver import configure_libclang
from .compile_args import sanitize_compile_args
from .ast_walker import walk_ast
from .symbol_extractors import is_within_root

if TYPE_CHECKING:
    from clang.cindex import (
        Index,
        CompilationDatabase,
    )


def _ensure_libclang() -> None:
    configure_libclang()

def extract_symbols(
    file_path: Path,
    repo_root: Path,
    index: Index,
    compdb: CompilationDatabase,
    target_folders: list[Path],
) -> dict[str, Any] | None:

    from clang.cindex import TranslationUnit

    commands = compdb.getCompileCommands(str(file_path))

    if not commands:
        return None

    command = list(commands)[0]

    raw_args = list(command.arguments)[1:]

    if raw_args:
        try:
            if Path(raw_args[-1]).resolve() == file_path:
                raw_args = raw_args[:-1]
        except Exception:
            pass

    args = sanitize_compile_args(raw_args)

    parse_options = (
        TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    )

    try:
        tu = index.parse(
            str(file_path),
            args=args,
            options=parse_options,
        )
    except Exception:
        return None

    result = {
        "file": str(file_path),
        "includes": [],
        "functions_defined": [],
        "functions_declared": [],
        "globals": [],
        "locals": [],
        "parameters": [],
        "structs": [],
        "enums": [],
        "typedefs": [],
        "macros": [],
    }

    walk_ast(
        tu.cursor,
        result,
        file_path,
        repo_root,
        target_folders,
    )

    return result

def build_symbol_inventory(
    repo_root: Path,
    analysis_dir: Path,
    output_path: Path,
    policy: dict[str, Any],
) -> dict[str, Any]:

    _ensure_libclang()

    from clang.cindex import (
        Index,
        CompilationDatabase,
    )

    build_dir = analysis_dir / "cmake_build"

    compile_db_path = (
        build_dir / "compile_commands.json"
    )

    ast_policy = policy.get("ast", {})

    target_folders = [
        (repo_root / folder).resolve()
        for folder in ast_policy.get(
            "target_folders",
            ["src"],
        )
    ]

    target_extensions = set(
        ast_policy.get(
            "target_extensions",
            [".c", ".h"],
        )
    )

    artifact = {
        "status": "pending",
        "repo_root": str(repo_root),
        "compile_db_path": str(compile_db_path),
        "output_path": str(output_path),
        "processed_files": 0,
        "skipped_files": [],
        "results": [],
    }

    if not compile_db_path.exists():
        return {
            **artifact,
            "status": "missing_compile_db",
            "error": (
                f"Compile database not found: "
                f"{compile_db_path}"
            ),
        }

    index = Index.create()

    compdb = CompilationDatabase.fromDirectory(
        str(build_dir)
    )

    with open(
        compile_db_path,
        "r",
        encoding="utf-8",
    ) as f:
        compile_data = json.load(f)

    processed_files: set[str] = set()

    all_results: list[dict[str, Any]] = []

    skipped_files: list[dict[str, str]] = []

    for entry in compile_data:

        file_path = Path(
            entry["file"]
        ).resolve()

        if str(file_path) in processed_files:
            continue

        processed_files.add(
            str(file_path)
        )

        if not any(
            is_within_root(
                file_path,
                folder,
            )
            for folder in target_folders
        ):
            skipped_files.append(
                {
                    "file": str(file_path),
                    "reason":
                        "outside_target_folder",
                }
            )
            continue

        if (
            file_path.suffix.lower()
            not in target_extensions
        ):
            skipped_files.append(
                {
                    "file": str(file_path),
                    "reason":
                        "unsupported_extension",
                }
            )
            continue

        result = extract_symbols(
            file_path=file_path,
            repo_root=repo_root,
            index=index,
            compdb=compdb,
            target_folders=target_folders,
        )

        if result:
            all_results.append(result)
        else:
            skipped_files.append(
                {
                    "file": str(file_path),
                    "reason":
                        "parse_or_compile_error",
                }
            )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            all_results,
            f,
            indent=2,
            ensure_ascii=True,
        )

    return {
        **artifact,
        "status": "success",
        "processed_files": len(all_results),
        "skipped_files": skipped_files,
        "results": all_results,
        "written": output_path.exists(),
    }