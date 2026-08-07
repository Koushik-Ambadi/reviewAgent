# src/repo_review/pipeline/stages/naming_stage.py
from __future__ import annotations

from ...checks.naming.runner import (
    run_naming_checks,
)
from ...contracts import (
    StageResult,
    StageStatus,
    build_stage_summary,
)
from ..context import PipelineContext


def run(
    context: PipelineContext,
) -> PipelineContext:

    check_results = run_naming_checks(
        context.workspace_path,
        context.module_name,
        context.policy["checks"]["symbol_naming"],
    )

    stage = StageResult(
        title="Symbol Naming",
        status=StageStatus.COMPLETED,
        summary=build_stage_summary(check_results),
        checks=check_results,
    )

    context.stage_results.append(stage)

    return context