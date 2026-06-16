# src/repo_review/checks/structure/runner.py

from .tree_builder import build_tree
from .required_paths import validate_required_paths
from .forbidden_paths import validate_forbidden_paths
from .allowed_extensions import validate_allowed_extensions
from .forbidden_extensions import validate_forbidden_extensions
from .required_file_types import validate_required_file_types
from .tree_rules import validate_tree_rules
from .size_rules import validate_size_rules


def run_structure_checks(
    repo_root,
    module_name,
    policy,
):

    nodes = build_tree(repo_root)

    issues = []

    issues.extend(
        validate_required_paths(
            nodes,
            policy,
        )
    )

    issues.extend(
        validate_forbidden_paths(
            nodes,
            policy,
        )
    )

    issues.extend(
        validate_allowed_extensions(
            nodes,
            policy,
        )
    )

    issues.extend(
        validate_forbidden_extensions(
            nodes,
            policy,
        )
    )

    issues.extend(
        validate_required_file_types(
            nodes,
            policy,
        )
    )

    issues.extend(
        validate_tree_rules(
            nodes,
            policy,
        )
    )

    issues.extend(
        validate_size_rules(
            nodes,
            policy,
        )
    )

    return issues