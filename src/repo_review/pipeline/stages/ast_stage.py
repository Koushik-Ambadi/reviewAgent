# src/repo_review/pipeline/stages/ast_stage.py

from __future__ import annotations

from pathlib import Path

from ..context import PipelineContext
from ...ast.ast_builder import build_ast_review_results


def run(context: PipelineContext) -> PipelineContext:
    """
    Run AST extraction stage.
    """

    source_root = Path(context.ingestion.source_path)

    ast_artifact = build_ast_review_results(
        source_root,
        context.pipeline_config,
    )

    context.ast_artifact = ast_artifact

    return context