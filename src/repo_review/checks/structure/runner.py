# src/repo_review/checks/structure/runner.py
from .allowed_extensions import (
    validate_allowed_extensions,
)
from .forbidden_extensions import (
    validate_forbidden_extensions,
)
from .forbidden_paths import (
    validate_forbidden_paths,
)
from .required_file_types import (
    validate_required_file_types,
)
from .required_paths import (
    validate_required_paths,
)
from .size_rules import (
    validate_size_rules,
)
from .tree_builder import build_tree
from .tree_rules import (
    validate_tree_rules,
)


def run_structure_checks(
    repo_root,
    module_name,
    structure_policy,
):

    nodes = build_tree(
        repo_root
    )

    return [
        validate_required_paths(
            nodes,
            module_name,
            structure_policy["required_paths"],
        ),
    ]