# src/repo_review/ingestion/local_ingestion.py

from pathlib import Path
import shutil

from .ingestion_utils import resolve_path


def ingest_local_source(
    source_root: Path | str,
    workspace_path: Path,
) -> Path:

    source_root = resolve_path(source_root)

    repo_root = workspace_path / source_root.name

    shutil.copytree(
        source_root,
        repo_root,
        dirs_exist_ok=True,
    )

    return repo_root