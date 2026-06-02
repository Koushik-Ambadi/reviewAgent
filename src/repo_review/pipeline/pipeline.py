# src/repo_review/pipeline/pipeline.py

from .context import PipelineContext

from .utils import (
    load_policy
)


from .stages.structure_stage import run as structure_stage
from .stages.analysis_stage import run as analysis_stage
from .stages.checks_stage import run as checks_stage
from .stages.reporting_stage import run as reporting_stage


def run_pipeline(
    context: PipelineContext,
):

    context.policy = load_policy(
        policy_name=context.policy_name,
        module_name=context.module_name,
    )


    stages = [
        structure_stage,
        analysis_stage,
        checks_stage,
        reporting_stage,
    ]

    for stage in stages:
        context = stage(context)

    return context