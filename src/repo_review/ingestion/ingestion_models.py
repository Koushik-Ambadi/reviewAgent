# src/repo_review/ingestion/ingestion_models.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class IngestionContext:
    source_kind: str

    source_path: Path
    workspace_path: Path

    policy_path: Path

    review_results_path: Path
    report_output_path: Path

    compile_db_dir: Path

    target_folders: list[Path]