# src/repo_review/checks/structure/tree_rules.py

from .models import ValidationIssue

def validate_tree_rules(nodes, policy):
    issues = []

    rules = policy.get("tree_rules", {})

    max_depth = rules.get("max_depth")
    max_files = rules.get("max_total_files")
    max_dirs = rules.get("max_total_dirs")

    if max_depth:
        for node in nodes:
            if node.depth > max_depth:
                issues.append(
                    ValidationIssue(
                        severity="MEDIUM",
                        rule="tree_rules",
                        path=node.relative_path,
                        message=f"Exceeded max depth {max_depth}",
                    )
                )

    if max_files:
        file_count = sum(1 for n in nodes if not n.is_dir)

        if file_count > max_files:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="tree_rules",
                    path="/",
                    message=f"Too many files: {file_count}",
                )
            )

    if max_dirs:
        dir_count = sum(1 for n in nodes if n.is_dir)

        if dir_count > max_dirs:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="tree_rules",
                    path="/",
                    message=f"Too many directories: {dir_count}",
                )
            )

    return issues

