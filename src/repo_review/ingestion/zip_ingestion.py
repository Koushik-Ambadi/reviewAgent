# src/repo_review/ingestion/zip_ingestion.py

from __future__ import annotations

import zipfile
from pathlib import Path

from .ingestion_utils import ensure_directory
from .workspace_manager import create_run_workspace


def ingest_zip_source(zip_path: Path | str):
    zip_path = Path(zip_path).resolve()

    workspace = create_run_workspace()

    extraction_dir = workspace / "source"

    ensure_directory(extraction_dir)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extraction_dir)

    return {
        "workspace": workspace,
        "source_root": extraction_dir,
    }