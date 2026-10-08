# src/repo_review/reporting/formatter.py

from __future__ import annotations

from datetime import (
    datetime,
    timezone,
UTC,
)
from uuid import NAMESPACE_URL, uuid5

from .serializer import serialize

REPORT_VERSION = "2.0"


def build_metadata(
    context,
):

    return {
        "module_name": context.module_name,
        "run_id": context.workspace_path.name,
        "policy_name": context.policy.get("metadata", {}).get(
            "name",
            context.policy_name,
        ),
        "profile": context.policy.get("metadata", {}).get("profile", {}),
        "generated_at": datetime.now(
            UTC,
        ).isoformat(),
    }


def build_report_data(
    context,
):

    context.run_result.run_id = context.workspace_path.name
    context.run_result.report_version = REPORT_VERSION
    context.run_result.policy_version = str(
        context.policy.get("version", "")
    )
    assign_case_ids(context.run_result)
    context.run_result.metadata = build_metadata(
        context,
    )

    return serialize(
        context.run_result,
    )


def assign_case_ids(run_result):
    """Assign stable IDs from check identity and case location/name."""
    for stage in run_result.stages:
        for check in stage.checks:
            for index, case in enumerate(check.cases):
                identity = (
                    f"{check.check_id}:{case.location}:"
                    f"{case.name}:{index}"
                )
                case.case_id = uuid5(
                    NAMESPACE_URL,
                    identity,
                ).hex
