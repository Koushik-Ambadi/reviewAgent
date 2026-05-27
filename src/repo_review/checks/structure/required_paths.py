# src/repo_review/checks/structure/required_paths.py

from .models import ValidationIssue
from .utils import normalize, match_pattern

def validate_required_paths(nodes, policy):
    issues = []

    files = [
        normalize(n.relative_path)
        for n in nodes
        if not n.is_dir
    ]

    dirs = {
        normalize(n.relative_path)
        for n in nodes
        if n.is_dir
    }

    for required in policy.get("required_paths", []):
        req = normalize(required)

        if req.endswith("/"):
            req_dir = req.rstrip("/")

            if req_dir not in dirs:
                issues.append(
                    ValidationIssue(
                        severity="HIGH",
                        rule="required_paths",
                        path=req,
                        message=f"Missing required directory: {req}",
                    )
                )
            continue

        found = False

        for file_path in files:
            if match_pattern(file_path, req):
                found = True
                break

        if not found:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="required_paths",
                    path=req,
                    message=f"Missing required path: {req}",
                )
            )

    return issues