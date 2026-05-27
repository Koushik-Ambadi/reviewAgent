# src/repo_review/structure/allowed_extensions.py

try:
    from ...models import ValidationIssue
except ImportError:  # pragma: no cover
    from models import ValidationIssue

from .utils import normalize, match_pattern



def validate_allowed_extensions(nodes, policy):
    issues = []

    rules = policy.get("allowed_extensions", {})

    for base, allowed in rules.items():
        base = normalize(base).rstrip("/")

        for node in nodes:
            if node.is_dir:
                continue

            path = normalize(node.relative_path)

            if match_pattern(path, base + "/**"):
                if node.extension not in allowed:
                    issues.append(
                        ValidationIssue(
                            severity="MEDIUM",
                            rule="allowed_extensions",
                            path=node.relative_path,
                            message=f"Extension {node.extension} not allowed in {base}",
                        )
                    )

    return issues

