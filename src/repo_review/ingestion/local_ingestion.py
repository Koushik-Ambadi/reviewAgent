# src/repo_review/ingestion/local_ingestion.py
from __future__ import annotations

import shutil
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

    workspace_source = workspace / "source"

    shutil.copytree(
        source_root,
        workspace_source,
        dirs_exist_ok=True,
    )

    policy_path = Path(
        runtime.get(
            "policy_path",
            "policies/default.yaml",
        )
    )

    if not policy_path.is_absolute():
        policy_path = resolve_path(policy_path)

    analysis_dir = workspace / "analysis"

    reports_dir = workspace / "reports"

    logs_dir = workspace / "logs"

    artifacts_dir = workspace / "artifacts"

    metadata_dir = workspace / "metadata"

    return IngestionContext(
        source_kind="local_directory",

        source_path=source_root,

        workspace_path=workspace,

        source_root=workspace_source,

        policy_path=policy_path,

        analysis_dir=analysis_dir,
        reports_dir=reports_dir,
        logs_dir=logs_dir,
        artifacts_dir=artifacts_dir,
        metadata_dir=metadata_dir,

        review_results_path=analysis_dir / runtime.get(
            "review_results_filename",
            "review_results.json",
        ),

        report_output_path=reports_dir / runtime.get(
            "output_report_filename",
            "review_report.json",
        ),

        compile_db_dir=analysis_dir,

        target_folders=[
            workspace_source / folder
            for folder in ast_config.get(
                "target_folders",
                ["src"],
            )
        ],
    )