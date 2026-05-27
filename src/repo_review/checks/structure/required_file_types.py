# src/repo_review/checks/structure/required_file_types.py


from .models import ValidationIssue
from .utils import normalize, match_pattern

def validate_required_file_types(nodes, policy):
    issues = []

    rules = policy.get("required_file_types", {})

    for base, required_exts in rules.items():
        base = normalize(base).rstrip("/")

        found = any(
            (not n.is_dir)
            and match_pattern(normalize(n.relative_path), base + "/**")
            and (n.extension in required_exts)
            for n in nodes
        )

        if not found:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="required_file_types",
                    path=base,
                    message=f"Missing required file types: {required_exts}",
                )
            )

    return issues

