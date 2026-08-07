# src/repo_review/reporting/formatter.py

from __future__ import annotations

from datetime import (
    datetime,
    timezone,
UTC,
)

from .serializer import serialize

REPORT_VERSION = "2.0"


def build_metadata(
    context,
):

    return {
        "report_version": REPORT_VERSION,
        "module_name": context.module_name,
        "run_id": context.workspace_path.name,
        "policy_name": context.policy_name,
        "generated_at": datetime.now(
            UTC,
        ).isoformat(),
    }


def build_report_data(
    context,
):

    context.run_result.metadata = build_metadata(
        context,
    )

    return serialize(
        context.run_result,
    )