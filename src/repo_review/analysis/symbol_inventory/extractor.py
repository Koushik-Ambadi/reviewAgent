# src/repo_review/analysis/symbol_inventory/extractor.py

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, Any

from code_intelligence.analysis import parse_translation_unit
from code_intelligence.extraction import extract_translation_unit
from code_intelligence.graph import KnowledgeGraph
from code_intelligence.models import GraphFragment
from code_intelligence.storage import write_snapshot

from .ast_walker import walk_ast
from .libclang_resolver import configure_libclang
from .symbol_extractors import is_within_root

if TYPE_CHECKING:
    from clang.cindex import (
        CompilationDatabase,
        Index,
    )


def _ensure_libclang() -> None:
    configure_libclang()

def extract_symbols(
    file_path: Path,
    repo_root: Path,
    index: Index,
    compdb: CompilationDatabase,
    target_folders: list[Path],
    graph_fragments: list[GraphFragment] | None = None,
) -> dict[str, Any] | None:

    try:
        tu = parse_translation_unit(
            file_path,
            index=index,
            compilation_database=compdb,
        )
    except Exception:
        return None
    if tu is None:
        return None


    relative_file = file_path.resolve().relative_to(
        repo_root.resolve()
    )


    result = {
        "file": relative_file.as_posix(),
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

    if graph_fragments is not None:
        graph_fragments.append(
            extract_translation_unit(
                tu.cursor,
                repo_root=repo_root,
                translation_unit=file_path,
            )
        )

    return result


def _source_provenance(repo_root: Path) -> dict[str, Any]:
    revision = "unversioned"
    dirty: bool | None = None
    try:
        revision_result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        revision = revision_result.stdout.strip() or revision
        dirty_result = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        dirty = bool(dirty_result.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return {
        "source_revision": revision,
        "dirty": dirty,
        "producer": "repo_review.analysis",
        "producer_version": "0.1.0",
    }

def build_symbol_inventory(
    repo_root: Path,
    analysis_dir: Path,
    output_path: Path,
    policy: dict[str, Any],
) -> dict[str, Any]:

    _ensure_libclang()

    from clang.cindex import (
        CompilationDatabase,
        Index,
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

    graph_fragments: list[GraphFragment] = []

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
            graph_fragments=graph_fragments,
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

    graph = KnowledgeGraph.from_fragments(graph_fragments)
    graph_path = analysis_dir / "code-intelligence.json"
    write_snapshot(
        graph,
        graph_path,
        provenance=_source_provenance(repo_root),
    )

    return {
        **artifact,
        "status": "success",
        "processed_files": len(all_results),
        "skipped_files": skipped_files,
        "results": all_results,
        "written": output_path.exists(),
        "graph_path": str(graph_path),
        "graph_nodes": len(graph.nodes),
        "graph_edges": len(graph.edges),
    }
