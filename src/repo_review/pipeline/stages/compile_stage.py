# src/repo_review/pipeline/stages/compile_stage.py
from __future__ import annotations

from ..context import PipelineContext

from ...compilation.runner import run_compilation_stage


def run(context: PipelineContext) -> PipelineContext:



    source_root = context.ingestion.source_root



    result = run_compilation_stage(
        source_root=source_root,
        analysis_dir=context.ingestion.analysis_dir,
        config=context.pipeline_config,
    )



    if result["status"] != "success":


        raise RuntimeError(
            f"Compilation failed: {result}"
        )

    context.compile_db_path = result["compile_db_path"]



    return context