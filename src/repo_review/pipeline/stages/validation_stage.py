# src/repo_review/pipeline/stages/validation_stage.py

from __future__ import annotations

from ..context import PipelineContext

from ...checks.naming.runner import (
    run_validations,
)


def run(context: PipelineContext) -> PipelineContext:
    """
    Run all modular code validations.
    """

    naming_rules = context.pipeline_config.get(
        "code_review",
        {},
    )

    issues = run_validations(
        context.review_results,
        context.module_name,
        naming_rules,
    )

    context.validation_issues.extend(issues)

    return context