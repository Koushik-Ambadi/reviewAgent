# src/orchestrator/workspace/run_workspace.py

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from orchestrator.config import (
    WORKSPACE_ROOT,
)

def create_run_workspace() -> Path:

    WORKSPACE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_id = (
        f"{datetime.now():%Y%m%d_%H%M%S}_"
        f"{uuid4().hex[:8]}"
    )

    workspace = WORKSPACE_ROOT / run_id

    workspace.mkdir(
        parents=True,
        exist_ok=False,
    )

    return workspace.resolve()
