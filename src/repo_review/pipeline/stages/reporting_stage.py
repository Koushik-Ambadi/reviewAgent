# src/repo_review/pipeline/stages/reporting_stage.py

from __future__ import annotations

from ..context import PipelineContext

from ...reporting.reporter import (
    build_final_report,
    write_report,
)


def run(
    context: PipelineContext,
) -> PipelineContext:

    report = build_final_report(
        context,
    )

    output_path = (
        context.workspace_path
        / "report.json"
    )

    context.report_path = write_report(
        report,
        output_path,
    )

    context.run_result = report

    return context