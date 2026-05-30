# src/repo_review/pipeline/stages/ingestion_stage.py
from __future__ import annotations

from ..context import PipelineContext

from ..utils import (
    create_run_workspace,
)

from ...ingestion.ingestion_manager import (
    ingest_source,
)


def run(
    context: PipelineContext,
) -> PipelineContext:

    context.repo_root = ingest_source(
        source_type=context.source_type,
        source_path=context.source_path,
        workspace_path=context.workspace_path,
    )

    return context