# src/repo_review/pipeline/stages/ingestion_stage.py

from __future__ import annotations

from ..context import PipelineContext

from ...ingestion.local_ingestion import ingest_local_source
from ...ingestion.config_loader import load_policy


def run(context: PipelineContext) -> PipelineContext:
    """
    Pipeline ingestion stage.
    Delegates ingestion handling to ingestion subsystem.
    """

    # -----------------------------------------
    # LOAD PIPELINE CONFIG
    # -----------------------------------------

    pipeline_config = load_policy(
        context.pipeline_config_path
    )

    context.pipeline_config = pipeline_config

    # -----------------------------------------
    # INGEST SOURCE
    # -----------------------------------------

    ingestion_context = ingest_local_source(
        source_path=context.source_path,
        config=pipeline_config,
    )

    context.ingestion = ingestion_context

    # -----------------------------------------
    # LOAD REVIEW POLICY
    # -----------------------------------------

    context.policy = load_policy(
        ingestion_context.policy_path
    )

    return context