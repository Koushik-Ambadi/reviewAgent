# src/repo_review/ingestion/workspace_manager.py

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .ingestion_utils import ensure_directory


DEFAULT_WORKSPACE_ROOT = Path.cwd() / "workspace" / "runs"


def create_run_workspace(
    workspace_root: Path | None = None,
) -> Path:
    root = workspace_root or DEFAULT_WORKSPACE_ROOT

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_id = f"{timestamp}_{uuid4().hex[:8]}"

    workspace = root / run_id

    ensure_directory(workspace)

    ensure_directory(workspace / "source")
    ensure_directory(workspace / "analysis")
    ensure_directory(workspace / "reports")
    ensure_directory(workspace / "logs")
    ensure_directory(workspace / "artifacts")
    ensure_directory(workspace / "metadata")

    return workspace.resolve()