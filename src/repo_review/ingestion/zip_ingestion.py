# src/repo_review/ingestion/zip_ingestion.py

from pathlib import Path
from zipfile import ZipFile


def ingest_zip_source(
    zip_path: Path | str,
    workspace_path: Path,
) -> Path:

    zip_path = Path(zip_path)

    with ZipFile(zip_path, "r") as archive:
        archive.extractall(workspace_path)

    repo_root = _detect_repo_root(
        workspace_path
    )

    try:
        zip_path.unlink()
    except OSError:
        pass

    return repo_root


def _detect_repo_root(
    workspace_path: Path,
) -> Path:

    directories = [
        path
        for path in workspace_path.iterdir()
        if path.is_dir()
    ]

    if len(directories) != 1:
        raise RuntimeError(
            "ZIP must contain exactly one top-level repository directory"
        )

    return directories[0]