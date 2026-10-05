# src/repo_review/pipeline/utils.py

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
        policy = yaml.safe_load(f)

    return policy
