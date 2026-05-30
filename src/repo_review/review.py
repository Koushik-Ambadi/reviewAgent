# src/repo_review/review.py

from .pipeline.context import (
    PipelineContext,
)

from .pipeline.pipeline import (
    run_pipeline,
)


def run_review(
    source_path,
    policy_name="default",
):

    context = PipelineContext(
        source_path=source_path,
        source_type="local",
        policy_name=policy_name,
    )

    return run_pipeline(context)


def run_review_from_zip(
    zip_path,
    policy_name="default",
):

    context = PipelineContext(
        source_path=zip_path,
        source_type="zip",
        policy_name=policy_name,
    )

    return run_pipeline(context)