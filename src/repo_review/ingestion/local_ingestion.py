# src/repo_review/ingestion/local_ingestion.py

from __future__ import annotations
from pathlib import Path

from .ingestion_models import IngestionContext
from .ingestion_utils import resolve_path
from .workspace_manager import create_run_workspace


def ingest_local_source(
    source_path: Path | str,
    config: dict,
) -> IngestionContext:

    source_root = resolve_path(source_path)

    runtime = config.get("runtime", {})
    ast_config = config.get("ast", {})

    workspace = create_run_workspace()

    policy_path = Path(runtime.get("policy_path", "policies/default.yaml"))

    if not policy_path.is_absolute():
        policy_path = resolve_path(policy_path)

    return IngestionContext(
        source_kind="local_directory",

        source_path=source_root,
        workspace_path=workspace,

        policy_path=policy_path,

        review_results_path=workspace / runtime.get(
            "review_results_filename",
            "review_results.json",
        ),

        report_output_path=workspace / runtime.get(
            "output_report_filename",
            "review_report.json",
        ),

        compile_db_dir=workspace / "compile_db",

        target_folders=[
            source_root / folder
            for folder in ast_config.get("target_folders", ["src"])
        ],
    )