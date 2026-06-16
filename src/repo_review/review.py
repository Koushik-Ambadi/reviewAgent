# src/repo_review/review.py

from .pipeline.context import (
    PipelineContext,
)

from .pipeline.pipeline import (
    run_pipeline,
)


def run_review(
    *,
    repo_root,
    workspace_path,
    module_name,
    policy_name="default",
):

    context = PipelineContext(
        repo_root=repo_root,
        workspace_path=workspace_path,
        module_name=module_name,
        policy_name=policy_name,
    )

    return run_pipeline(context)