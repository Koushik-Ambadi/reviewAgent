# src/repo_review/ingestion/ingestion_manager.py

from __future__ import annotations

from .local_ingestion import ingest_local_source
from .zip_ingestion import ingest_zip_source


def ingest_source(
    *,
    source_type: str,
    source_path,
    workspace_path,
):

    source_type = source_type.lower()

    if source_type == "local":
        return ingest_local_source(
            source_root=source_path,
            workspace_path=workspace_path,
        )

    if source_type == "zip":
        return ingest_zip_source(
            zip_path=source_path,
            workspace_path=workspace_path,
        )

    raise ValueError(
        f"Unsupported source_type: {source_type}"
    )