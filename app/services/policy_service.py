# app/services/policy_service.py

from pathlib import Path

import yaml


POLICY_DIR = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "repo_review"
    / "policies"
)


def load_policy_template(
    policy_name: str,
) -> dict:

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