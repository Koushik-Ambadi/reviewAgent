# src/repo_review/pipeline/utils.py

from pathlib import Path
import yaml



POLICY_DIR = (
    Path(__file__).parent.parent
    / "policies"
)


def load_policy(
    policy_name: str,
    module_name: str,
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

    return expand_policy(
        policy,
        module_name,
    )

def expand_policy(
    value,
    module_name: str,
):

    if isinstance(value, str):
        return value.replace(
            "{module}",
            module_name,
        )

    if isinstance(value, list):
        return [
            expand_policy(
                item,
                module_name,
            )
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: expand_policy(
                val,
                module_name,
            )
            for key, val in value.items()
        }

    return value