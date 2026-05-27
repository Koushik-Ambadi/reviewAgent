# src/repo_review/structure/forbidden_extensions.py


try:
    from ...models import ValidationIssue
except ImportError:  # pragma: no cover
    from models import ValidationIssue

from .utils import normalize, match_pattern


def validate_forbidden_extensions(nodes, policy):
    issues = []

    rules = policy.get("forbidden_extensions", {})

    for base, forbidden in rules.items():
        base = normalize(base).rstrip("/")

        for node in nodes:
            if node.is_dir:
                continue

            path = normalize(node.relative_path)

            if match_pattern(path, base + "/**"):
                if node.extension in forbidden:
                    issues.append(
                        ValidationIssue(
                            severity="HIGH",
                            rule="forbidden_extensions",
                            path=node.relative_path,
                            message=f"Forbidden extension {node.extension}",
                        )
                    )

    return issues

