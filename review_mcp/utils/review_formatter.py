# review_mcp/utils/review_formatter.py

from __future__ import annotations

from copy import deepcopy


def optimize_review_response(response: dict) -> dict:
    """
    Optimize review response for AI consumption without losing
    information required for reasoning.

    Optimizations:
    - Remove PASSED issues.
    - Convert absolute workspace paths to repository-relative paths.
    - Preserve all FAILED and EXCEPTION details.
    """

    report = response.get("report")
    if not report:
        return response

    optimized = deepcopy(response)

    run_id = optimized.get("run_id", "")
    module_name = optimized.get("module_name", "")

    workspace_prefix = ""
    if run_id and module_name:
        workspace_prefix = f"/app/workspace/runs/{run_id}/{module_name}/"

    sections = optimized["report"].get("sections", [])

    for section in sections:

        filtered_issues = []

        for issue in section.get("issues", []):

            if issue.get("status") == "PASSED":
                continue

            issue = deepcopy(issue)

            file_path = issue.get("file")
            if file_path and workspace_prefix and file_path.startswith(workspace_prefix):
                issue["file"] = file_path[len(workspace_prefix):]

            filtered_issues.append(issue)

        section["issues"] = filtered_issues

    return optimized