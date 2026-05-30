# src/repo_review/pipeline/utils.py

from pathlib import Path
from datetime import datetime
from uuid import uuid4
import yaml



WORKSPACE_ROOT = (
    Path.cwd()
    / "workspace"
    / "runs"
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


from pathlib import Path
import yaml


POLICY_DIR = (
    Path(__file__).parent.parent
    / "policies"
)


def load_policy(
    policy_name: str,
):
    policy_path = (
        POLICY_DIR
        / f"{policy_name}.yaml"
    )

    if not policy_path.exists():
        raise FileNotFoundError(
            f"Policy not found: {policy_name}"
        )

    with open(
        policy_path,
        "r",
        encoding="utf-8",
    ) as f:
        return yaml.safe_load(f)

