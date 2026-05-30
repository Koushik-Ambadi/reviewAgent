# src/repo_review/reporting/formatter.py
from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)

from .schemas import (
    REPORT_VERSION,
    STATUS_FAILED,
    STATUS_WARNING,
    STATUS_PASSED,
    SECTION_STRUCTURE,
    SECTION_CODE_REVIEW,
)

from .serializers import (
    serialize_issue,
    serialize_list,
)


def normalize_structure_issues(
    issues,
):
    normalized = []

    for issue in issues:

        item = serialize_issue(issue)

        item["status"] = "FAILED"

        normalized.append(item)

    return normalized


def summarize_results(
    results,
):

    failed = sum(
        1
        for item in results
        if item.get("status") == "FAILED"
    )

    exception = sum(
        1
        for item in results
        if item.get("status") == "EXCEPTION"
    )

    passed = sum(
        1
        for item in results
        if item.get("status") == "PASSED"
    )

    return {
        "failed": failed,
        "exception": exception,
        "passed": passed,
        "total": (
            failed
            + exception
            + passed
        ),
    }


def merge_summaries(
    *summaries,
):

    merged = {
        "failed": 0,
        "exception": 0,
        "passed": 0,
    }

    for summary in summaries:

        merged["failed"] += (
            summary["failed"]
        )

        merged["exception"] += (
            summary["exception"]
        )

        merged["passed"] += (
            summary["passed"]
        )

    merged["total"] = (
        merged["failed"]
        + merged["exception"]
        + merged["passed"]
    )

    if merged["failed"]:

        merged["overall_status"] = (
            STATUS_FAILED
        )

    elif merged["exception"]:

        merged["overall_status"] = (
            STATUS_WARNING
        )

    else:

        merged["overall_status"] = (
            STATUS_PASSED
        )

    return merged


def build_metadata(
    context,
):

    return {
        "report_version":
            REPORT_VERSION,

        "module_name":
            context.module_name,

        "source_type":
            context.source_type,

        "policy_name":
            context.policy_name,

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


def format_structure_section(
    issues,
    summary,
):

    return {
        "name":
            SECTION_STRUCTURE,

        "status":
            STATUS_FAILED
            if issues
            else STATUS_PASSED,

        "summary":
            summary,

        "issues":
            issues,
    }


def format_validation_section(
    issues,
    summary,
):

    if summary["failed"]:

        status = STATUS_FAILED

    elif summary["exception"]:

        status = STATUS_WARNING

    else:

        status = STATUS_PASSED

    return {
        "name":
            SECTION_CODE_REVIEW,

        "status":
            status,

        "summary":
            summary,

        "issues":
            issues,
    }


def build_report_data(
    context,
):

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

    summary = (
        merge_summaries(
            structure_summary,
            validation_summary,
        )
    )

    return {
        "metadata":
            build_metadata(
                context
            ),

        "summary":
            summary,

        "sections": [
            format_structure_section(
                structure_issues,
                structure_summary,
            ),

            format_validation_section(
                validation_issues,
                validation_summary,
            ),
        ],
    }