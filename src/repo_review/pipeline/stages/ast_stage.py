# src/repo_review/pipeline/stages/ast_stage.py
from __future__ import annotations

from pathlib import Path

from ..context import PipelineContext
from ...ast.ast_builder import build_ast_review_results


def run(context: PipelineContext) -> PipelineContext:
    """
    Run AST extraction stage.
    """
    source_root = Path(
        context.ingestion.source_root
    )

    compile_db_path = Path(
        context.compile_db_path
    )

    output_path = Path(
        context.ingestion.review_results_path
    )

    ast_artifact = build_ast_review_results(
        source_root=source_root,
        compile_db_path=compile_db_path,
        output_path=output_path,
        config=context.pipeline_config,
    )

    context.ast_artifact = ast_artifact

    context.review_results = ast_artifact.get(
        "results",
        [],
    )

    return context