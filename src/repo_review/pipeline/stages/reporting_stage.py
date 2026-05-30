# src/repo_review/pipeline/stages/reporting_stage.py

from __future__ import annotations

try:
    from ..context import PipelineContext

    from ...reporting.reporter import (
        build_final_report,
        write_report,
    )

except ImportError:  # pragma: no cover

    from context import PipelineContext

    from reporting.reporter import (
        build_final_report,
        write_report,
    )


def run(
    context: PipelineContext,
) -> PipelineContext:
    """
    Reporting orchestration only.
    """

    report = build_final_report(
        context
    )

    output_path = (
        context.workspace_path
        / "report.json"
    )

    output_path = write_report(
        report,
        output_path,
    )

    report["metadata"]["report_path"] = (
        str(output_path)
    )
    context.report_path = output_path

    context.report = report

    return context