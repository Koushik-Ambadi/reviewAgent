# src/repo_review/pipeline/stages/checks_stage.py
from __future__ import annotations

from pathlib import Path
from ..context import PipelineContext

from ...checks.naming.runner import run_naming_checks


def run(context: PipelineContext) -> PipelineContext:



    issues = run_naming_checks(
        context.workspace_path,
        context.module_name,
        context.policy,
    )

    context.validation_issues.extend(issues)

    return context