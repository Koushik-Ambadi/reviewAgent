# src/repo_review/pipeline/stages/structure_stage.py

from __future__ import annotations
from ..context import PipelineContext
from ...checks.structure.runner import (
    run_structure_checks,
)


def run(
    context: PipelineContext,
) -> PipelineContext:

    context.structure_issues = (
        run_structure_checks(
            repo_root=context.repo_root,
            module_name=context.module_name,
            policy=context.policy,
        )
    )

    return context