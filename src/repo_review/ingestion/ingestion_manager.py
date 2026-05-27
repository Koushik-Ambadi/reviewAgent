# src/repo_review/ingestion/ingestion_manager.py

from __future__ import annotations

from pathlib import Path

from .local_ingestion import ingest_local_source
from .zip_ingestion import ingest_zip_source


def ingest_source(
    *,
    source_type: str,
    source_path: str | Path,
    config: dict,
):
    if source_type == "local":
        return ingest_local_source(
            source_path=source_path,
            config=config,
        )

    if source_type == "zip":
        return ingest_zip_source(source_path)

    raise ValueError(
        f"Unsupported source_type: {source_type}"
    )