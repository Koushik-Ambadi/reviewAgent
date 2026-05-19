from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .ast_builder import build_ast_review_results
    from .code_review_validators import load_review_results, run_code_review_validations
    from .config_loader import load_policy
    from .ingestion import ingest_local_source, load_yaml_config
    from .reporter import normalize_structure_issues
    from .tree_builder import build_tree
    from .validators import run_structure_validations
except ImportError:  # pragma: no cover
    from ast_builder import build_ast_review_results
    from code_review_validators import load_review_results, run_code_review_validations
    from config_loader import load_policy
    from ingestion import ingest_local_source, load_yaml_config
    from reporter import normalize_structure_issues
    from tree_builder import build_tree
    from validators import run_structure_validations


def _render_value(value: Any, module_name: str) -> Any:
    if isinstance(value, str):
        return value.replace("{module}", module_name)
    if isinstance(value, list):
        return [_render_value(item, module_name) for item in value]
    if isinstance(value, dict):
        return {key: _render_value(item, module_name) for key, item in value.items()}
    return value


def render_policy(policy: dict, module_name: str) -> dict:
    return _render_value(policy, module_name)


def _bucket_issue(issue: dict[str, Any]) -> str:
    if issue["status"] == "EXCEPTION":
        return "exception"
    if issue["status"] == "PASSED":
        return "passed"
    return "failed"


def _summarize(results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "failed": sum(1 for result in results if result["status"] == "FAILED"),
        "exception": sum(1 for result in results if result["status"] == "EXCEPTION"),
        "passed": sum(1 for result in results if result["status"] == "PASSED"),
    }


def build_review_report(
    *,
    source_path: Path | str,
    module_name: str,
    repo_url: str,
    pipeline_config_path: Path | str,
):
    pipeline_config = load_yaml_config(pipeline_config_path)
    ingestion = ingest_local_source(source_path, pipeline_config)
    policy = render_policy(load_policy(ingestion["policy_path"]), module_name)

    source_root = Path(ingestion["source_path"])
    structure_nodes = build_tree(source_root)
    structure_issues = normalize_structure_issues(run_structure_validations(structure_nodes, policy))

    ast_artifact = build_ast_review_results(source_root, pipeline_config)
    naming_rules = pipeline_config.get("code_review", {})
    naming_issues: list[dict[str, Any]] = []
    review_results_path = Path(ast_artifact.get("output_path", ingestion["review_results_path"]))
    if ast_artifact["status"] == "success" and review_results_path.exists():
        review_results = load_review_results(review_results_path)
        naming_issues = run_code_review_validations(
            review_results,
            module_name,
            naming_rules,
        )
    elif ast_artifact["status"] == "success":
        ast_artifact["status"] = "missing_review_results"
        ast_artifact["error"] = f"Review results file not found: {review_results_path}"

    structure_summary = _summarize(structure_issues)
    naming_summary = _summarize(naming_issues)
    ast_summary = {
        "status": ast_artifact["status"],
        "processed_files": ast_artifact.get("processed_files", 0),
        "compile_db_path": ast_artifact.get("compile_db_path"),
        "output_path": ast_artifact.get("output_path"),
        "review_results_exists": review_results_path.exists(),
        "error": ast_artifact.get("error"),
    }

    combined_failed = structure_summary["failed"] + naming_summary["failed"]
    combined_exception = structure_summary["exception"] + naming_summary["exception"]
    combined_passed = structure_summary["passed"] + naming_summary["passed"]

    body = {"failed": [], "exception": [], "passed": []}
    for issue in structure_issues + naming_issues:
        body[_bucket_issue(issue)].append(issue["message"])

    return {
        "metadata": {
            "repo_url": repo_url,
            "module_name": module_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_path": str(source_root),
            "policy_path": str(ingestion["policy_path"]),
            "review_results_path": str(ingestion["review_results_path"]),
            "report_output_path": str(ingestion["report_output_path"]),
        },
        "ingestion": {
            "source_kind": ingestion["source_kind"],
            "source_path": str(ingestion["source_path"]),
            "compile_db_dir": str(ingestion["compile_db_dir"]),
            "target_folders": [str(path) for path in ingestion["target_folders"]],
        },
        "ast": ast_summary,
        "summary": {
            "failed": combined_failed,
            "exception": combined_exception,
            "passed": combined_passed,
            "total": combined_failed + combined_exception + combined_passed,
            "overall_status": "failed" if combined_failed else ("warning" if combined_exception else "passed"),
        },
        "body": body,
        "sections": [
            {
                "name": "folder_and_file_structure",
                "title": "Folder and File Structure",
                "status": "failed" if structure_issues else "passed",
                "summary": structure_summary,
                "issues": structure_issues,
            },
            {
                "name": "ast_review_results",
                "title": "AST Review Results",
                "status": ast_artifact["status"],
                "summary": ast_summary,
                "issues": ast_artifact.get("skipped_files", []),
            },
            {
                "name": "code_review_checks",
                "title": "Code Review Checks",
                "status": "failed" if naming_summary["failed"] else ("warning" if naming_summary["exception"] else "passed"),
                "summary": naming_summary,
                "issues": naming_issues,
            },
        ],
    }
