# src/repo_review/pipeline/pipeline.py
from .context import PipelineContext

from .utils import (
    load_policy,
    extract_module_name,
    create_run_workspace,
)

from .stages.ingestion_stage import run as ingestion_stage
from .stages.structure_stage import run as structure_stage
from .stages.analysis_stage import (run as analysis_stage)
from .stages.checks_stage import (run as checks_stage)
from .stages.reporting_stage import (run as reporting_stage)


def run_pipeline(
    context: PipelineContext,
):

    context.policy = load_policy(
        context.policy_name
    )

    if not context.module_name:
        context.module_name = (
            extract_module_name(
                context.source_path
            )
        )
    context.workspace_path = (
        create_run_workspace()
    )
    stages = [
        ingestion_stage,
        structure_stage,
        analysis_stage,
        checks_stage,
        reporting_stage,
    ]

    for stage in stages:
        context = stage(context)

    return context

