# src/repo_review/main.py

from pathlib import Path

from config_loader import load_policy
from reporter import print_report
from tree_builder import build_tree
from validators import run_validations


def main():
    repo_path = Path("soc")
    policy_path = Path("policies/default.yaml")

    policy = load_policy(policy_path)

    module_name = "auth"

    for i, path in enumerate(policy.get("required_paths", [])):
        policy["required_paths"][i] = path.replace(
            "{module}",
            module_name,
        )

    nodes = build_tree(repo_path)

    issues = run_validations(nodes, policy)

    print_report(issues)



if __name__ == "__main__":
    main()

