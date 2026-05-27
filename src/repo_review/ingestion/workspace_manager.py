# src/repo_review/ingestion/workspace_manager.py

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .ingestion_utils import ensure_directory


WORKSPACE_ROOT = Path("workspace/runs")


def create_run_workspace() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_id = f"{timestamp}_{uuid4().hex[:8]}"

    workspace = WORKSPACE_ROOT / run_id

    ensure_directory(workspace)

    return workspace.resolve()