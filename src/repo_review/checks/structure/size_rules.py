# src/repo_review/checks/structure/size_rules.py

from .models import ValidationIssue
from .utils import normalize, match_pattern

def validate_size_rules(nodes, policy):
    issues = []

    rules = policy.get("size_rules", {})

    global_limit = rules.get("max_file_size_mb", 0)
    ext_limits = rules.get("extension_limits", {})
    path_limits = rules.get("path_limits", {})
    min_size = rules.get("min_file_size_bytes", 0)

    for node in nodes:
        if node.is_dir:
            continue

        size_mb = node.size / (1024 * 1024)
        path = normalize(node.relative_path)

        if global_limit and size_mb > global_limit:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="size_rules",
                    path=node.relative_path,
                    message=f"Exceeded global size limit {global_limit} MB",
                )
            )

        if node.extension in ext_limits:
            if size_mb > ext_limits[node.extension]:
                issues.append(
                    ValidationIssue(
                        severity="MEDIUM",
                        rule="size_rules",
                        path=node.relative_path,
                        message=f"{node.extension} exceeds limit",
                    )
                )

        for pattern, limit in path_limits.items():
            if match_pattern(path, pattern):
                if size_mb > limit:
                    issues.append(
                        ValidationIssue(
                            severity="HIGH",
                            rule="size_rules",
                            path=node.relative_path,
                            message=f"Exceeded path limit {limit} MB",
                        )
                    )

        if node.size < min_size:
            issues.append(
                ValidationIssue(
                    severity="LOW",
                    rule="size_rules",
                    path=node.relative_path,
                    message="Empty file detected",
                )
            )

    return issues

