# src/repo_review/pipeline/pipeline.py

from .context import PipelineContext

from .stages.ingestion_stage import run as ingestion_stage
from .stages.compile_stage import run as compile_stage
from .stages.structure_stage import run as structure_stage
from .stages.ast_stage import run as ast_stage
from .stages.validation_stage import run as validation_stage
from .stages.reporting_stage import run as reporting_stage


def run_pipeline(context: PipelineContext):

    stages = [
        ingestion_stage,
        structure_stage,        
        compile_stage,
        ast_stage,
        validation_stage,
        reporting_stage,
    ]

    for stage in stages:
        context = stage(context)

    return context