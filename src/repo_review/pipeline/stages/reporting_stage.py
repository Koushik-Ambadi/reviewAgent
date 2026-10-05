# src/repo_review/pipeline/stages/reporting_stage.py



from __future__ import annotations

from ...contracts import (
    RunResult,
    RunStatus,
    build_run_summary,
)
from ...reporting.reporter import (
    build_final_report,
    write_report,
)
from ..context import PipelineContext


def run(
    context: PipelineContext,
) -> PipelineContext:

    context.run_result = RunResult(
        status=RunStatus.COMPLETED,
        summary=build_run_summary(
            context.stage_results,
        ),
        stages=context.stage_results,
    )

    report = build_final_report(
        context,
    )
    context.report = report

    context.report_path = write_report(
        report,
        context.workspace_path / "report.json",
    )

    return context
