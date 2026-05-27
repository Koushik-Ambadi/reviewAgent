from __future__ import annotations

from ..context import PipelineContext

from ...compilation.runner import run_compilation_stage


def run(context: PipelineContext) -> PipelineContext:
    """
    Generate compile_commands.json.
    """

    source_root = context.ingestion.source_path

    result = run_compilation_stage(
        source_root=source_root,
        config=context.pipeline_config,
    )

    if result["status"] != "success":
        raise RuntimeError(result["error"])

    context.compile_db_path = result["compile_db_path"]

    return context