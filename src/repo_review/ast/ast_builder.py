# src/repo_review/ast/ast_builder.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clang.cindex import (
    CompilationDatabase,
    Index,
    TranslationUnit,
)

from .clang_config import configure_libclang
from .sanitizers import sanitize_compile_args
from .traversal import walk_ast
from .extractors import is_within_root


def extract_symbols(
    file_path: Path,
    repo_root: Path,
    index: Index,
    compdb: CompilationDatabase,
    ast_config: dict[str, Any],
) -> dict[str, Any] | None:

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

    args = sanitize_compile_args(
        raw_args,
        ast_config.get("sanitize", {}),
    )

    parse_options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

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
    )

    return result


def build_ast_review_results(
    source_path: Path | str,
    config: dict[str, Any],
) -> dict[str, Any]:

    source_root = Path(source_path).resolve()

    ast_config = config.get("ast", {})

    libclang_path = ast_config.get("libclang_path")

    configure_libclang(libclang_path)

    compile_db_dir = Path(
        ast_config.get(
            "compile_db_dir",
            "analysis/cmake_build",
        )
    ).resolve()

    compile_db_path = compile_db_dir / "compile_commands.json"

    target_folders = [
        (source_root / folder).resolve()
        for folder in ast_config.get(
            "target_folders",
            ["src"],
        )
    ]

    target_extensions = set(
        ast_config.get(
            "target_extensions",
            [".c", ".h"],
        )
    )

    output_path = Path(
        source_root
        / config.get("runtime", {}).get(
            "review_results_filename",
            "review_results.json",
        )
    )

    artifact = {
        "status": "pending",
        "source_root": str(source_root),
        "compile_db_path": str(compile_db_path),
        "output_path": str(output_path),
        "processed_files": 0,
        "skipped_files": [],
        "results": [],
    }

    if not compile_db_path.exists():
        artifact["status"] = "missing_compile_db"
        artifact["error"] = (
            f"Compile database not found: {compile_db_path}"
        )
        return artifact

    index = Index.create()

    compdb = CompilationDatabase.fromDirectory(
        str(compile_db_dir)
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
        file_path = Path(entry["file"]).resolve()

        if str(file_path) in processed_files:
            continue

        processed_files.add(str(file_path))

        if not any(
            is_within_root(file_path, folder)
            for folder in target_folders
        ):
            skipped_files.append(
                {
                    "file": str(file_path),
                    "reason": "outside_target_folder",
                }
            )
            continue

        if file_path.suffix.lower() not in target_extensions:
            skipped_files.append(
                {
                    "file": str(file_path),
                    "reason": "unsupported_extension",
                }
            )
            continue

        result = extract_symbols(
            file_path,
            source_root,
            index,
            compdb,
            ast_config,
        )

        if result:
            all_results.append(result)
        else:
            skipped_files.append(
                {
                    "file": str(file_path),
                    "reason": "parse_or_compile_error",
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

    artifact.update(
        {
            "status": "success",
            "processed_files": len(all_results),
            "skipped_files": skipped_files,
            "results": all_results,
            "written": output_path.exists(),
        }
    )

    return artifact