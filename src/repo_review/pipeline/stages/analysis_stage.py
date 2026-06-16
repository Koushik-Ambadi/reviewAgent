# src/repo_review/pipeline/stages/analysis_stage.py
from __future__ import annotations

from ..context import PipelineContext
from ...analysis.runner import run_analysis


def run(context: PipelineContext) -> PipelineContext:
    run_analysis(
        repo_root=context.repo_root,
        workspace_path=context.workspace_path,
        policy=context.policy,
    )

    # PURE SIDE EFFECT STAGE
    return context