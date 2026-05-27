# src/repo_review/structure/forbidden_paths.py

try:
    from ...models import ValidationIssue
except ImportError:  # pragma: no cover
    from models import ValidationIssue

from .utils import normalize, match_pattern


def validate_forbidden_paths(nodes, policy):
    issues = []

    for forbidden in policy.get("forbidden_paths", []):
        for node in nodes:
            path = normalize(node.relative_path)

            if match_pattern(path, forbidden):
                issues.append(
                    ValidationIssue(
                        severity="HIGH",
                        rule="forbidden_paths",
                        path=node.relative_path,
                        message=f"Forbidden path exists: {node.relative_path}",
                    )
                )

    return issues
