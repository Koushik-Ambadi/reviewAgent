# src/repo_review/pipeline/stages/structure_stage.py
from __future__ import annotations

from ...checks.structure.runner import (
    run_structure_checks,
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
    
    check_results = run_structure_checks(
        repo_root=context.repo_root,
        module_name=context.module_name,
        structure_policy=context.policy["checks"]["repository_structure"],
    )

    stage = StageResult(
        title="Repository Structure",
        status=StageStatus.COMPLETED,
        summary=build_stage_summary(
            check_results
        ),
        checks=check_results,
    )

    context.stage_results.append(stage)

    return context