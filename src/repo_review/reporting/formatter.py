# src/repo_review/reporting/formatter.py

from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)

from typing import Any

from .schemas import (
    STATUS_FAILED,
    STATUS_WARNING,
    STATUS_PASSED,
    SECTION_STRUCTURE,
    SECTION_AST,
    SECTION_CODE_REVIEW,
    DEFAULT_BODY,
    REPORT_VERSION,
)

from .serializers import (
    serialize_issue,
    serialize_list,
    serialize_path,
)


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_structure_issues(
    issues: list[Any],
) -> list[dict]:

    normalized = []

    for issue in issues:

        item = serialize_issue(issue)

        item["status"] = "FAILED"

        normalized.append(item)

    return normalized


# =========================================================
# SUMMARY
# =========================================================

def summarize_results(
    results: list[dict],
) -> dict[str, int]:

    return {
        "failed": sum(
            1
            for result in results
            if result.get("status") == "FAILED"
        ),

        "exception": sum(
            1
            for result in results
            if result.get("status") == "EXCEPTION"
        ),

        "passed": sum(
            1
            for result in results
            if result.get("status") == "PASSED"
        ),
    }


def merge_summaries(
    *summaries: dict[str, int],
) -> dict[str, int]:

    merged = {
        "failed": 0,
        "exception": 0,
        "passed": 0,
    }

    for summary in summaries:

        merged["failed"] += (
            summary.get("failed", 0)
        )

        merged["exception"] += (
            summary.get("exception", 0)
        )

        merged["passed"] += (
            summary.get("passed", 0)
        )

    merged["total"] = (
        merged["failed"]
        + merged["exception"]
        + merged["passed"]
    )

    merged["overall_status"] = (
        calculate_overall_status(
            merged
        )
    )

    return merged


def calculate_overall_status(
    summary: dict[str, int],
) -> str:

    if summary.get("failed", 0):
        return STATUS_FAILED

    if summary.get("exception", 0):
        return STATUS_WARNING

    return STATUS_PASSED


# =========================================================
# BODY
# =========================================================

def bucket_issue(
    issue: dict,
) -> str:

    status = issue.get("status")

    if status == "PASSED":
        return "passed"

    if status == "EXCEPTION":
        return "exception"

    return "failed"


def build_body(
    structure_issues: list[dict],
    validation_issues: list[dict],
) -> dict:

    body = dict(DEFAULT_BODY)

    for issue in (
        structure_issues
        + validation_issues
    ):

        bucket = bucket_issue(issue)

        body[bucket].append(
            issue.get(
                "message",
                "Unknown issue",
            )
        )

    return body


# =========================================================
# AST
# =========================================================

def build_ast_summary(
    context,
) -> dict:

    return {
        "status": (
            context.ast_artifact.get(
                "status"
            )
        ),

        "processed_files": (
            context.ast_artifact.get(
                "processed_files",
                0,
            )
        ),

        "compile_db_path": (
            context.compile_db_path
        ),

        "output_path": (
            context.ast_artifact.get(
                "output_path"
            )
        ),

        "review_results_exists": bool(
            context.review_results
        ),

        "error": (
            context.ast_artifact.get(
                "error"
            )
        ),
    }


# =========================================================
# METADATA
# =========================================================

def build_metadata(
    context,
) -> dict:

    return {
        "report_version": (
            REPORT_VERSION
        ),

        "repo_url": (
            context.repo_url
        ),

        "module_name": (
            context.module_name
        ),

        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "source_path": (
            serialize_path(
                context.ingestion.source_path
            )
        ),

        "policy_path": (
            serialize_path(
                context.ingestion.policy_path
            )
        ),

        "review_results_path": (
            serialize_path(
                context.ingestion.review_results_path
            )
        ),

        "report_output_path": (
            serialize_path(
                context.ingestion.report_output_path
            )
        ),
    }


# =========================================================
# INGESTION
# =========================================================

def build_ingestion(
    context,
) -> dict:

    return {
        "source_kind": (
            context.ingestion.source_kind
        ),

        "source_path": (
            serialize_path(
                context.ingestion.source_path
            )
        ),

        "compile_db_dir": (
            serialize_path(
                context.ingestion.compile_db_dir
            )
        ),

        "target_folders": [
            serialize_path(path)
            for path in (
                context.ingestion.target_folders
            )
        ],
    }


# =========================================================
# SECTIONS
# =========================================================

def format_structure_section(
    issues: list[dict],
    summary: dict,
) -> dict:

    return {
        "name": SECTION_STRUCTURE,

        "title": (
            "Folder and File Structure"
        ),

        "status": (
            STATUS_FAILED
            if issues
            else STATUS_PASSED
        ),

        "summary": summary,

        "issues": issues,
    }


def format_ast_section(
    ast_summary: dict,
    ast_artifact: dict,
) -> dict:

    return {
        "name": SECTION_AST,

        "title": (
            "AST Review Results"
        ),

        "status": (
            ast_artifact.get(
                "status"
            )
        ),

        "summary": ast_summary,

        "issues": (
            ast_artifact.get(
                "skipped_files",
                [],
            )
        ),
    }


def format_validation_section(
    issues: list[dict],
    summary: dict,
) -> dict:

    failed = summary.get(
        "failed",
        0,
    )

    exception = summary.get(
        "exception",
        0,
    )

    if failed:
        status = STATUS_FAILED

    elif exception:
        status = STATUS_WARNING

    else:
        status = STATUS_PASSED

    return {
        "name": SECTION_CODE_REVIEW,

        "title": (
            "Code Review Checks"
        ),

        "status": status,

        "summary": summary,

        "issues": issues,
    }


def build_sections(
    *,
    structure_issues: list[dict],
    structure_summary: dict,
    validation_issues: list[dict],
    validation_summary: dict,
    ast_summary: dict,
    ast_artifact: dict,
) -> list[dict]:

    return [
        format_structure_section(
            structure_issues,
            structure_summary,
        ),

        format_ast_section(
            ast_summary,
            ast_artifact,
        ),

        format_validation_section(
            validation_issues,
            validation_summary,
        ),
    ]


# =========================================================
# REPORT
# =========================================================

def build_report_data(
    context,
) -> dict:

    structure_issues = (
        normalize_structure_issues(
            context.structure_issues
        )
    )

    validation_issues = (
        serialize_list(
            context.validation_issues
        )
    )

    structure_summary = (
        summarize_results(
            structure_issues
        )
    )

    validation_summary = (
        summarize_results(
            validation_issues
        )
    )

    summary = merge_summaries(
        structure_summary,
        validation_summary,
    )

    ast_summary = build_ast_summary(
        context
    )

    body = build_body(
        structure_issues,
        validation_issues,
    )

    sections = build_sections(
        structure_issues=(
            structure_issues
        ),

        structure_summary=(
            structure_summary
        ),

        validation_issues=(
            validation_issues
        ),

        validation_summary=(
            validation_summary
        ),

        ast_summary=ast_summary,

        ast_artifact=(
            context.ast_artifact
        ),
    )

    return {
        "metadata": build_metadata(
            context
        ),

        "ingestion": build_ingestion(
            context
        ),

        "ast": ast_summary,

        "summary": summary,

        "body": body,

        "sections": sections,
    }