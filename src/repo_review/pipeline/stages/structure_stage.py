# src/repo_review/pipeline/stages/structure_stage.py

from __future__ import annotations

from ..context import PipelineContext

from ...checks.structure.tree_builder import build_tree

from ...checks.structure.runner import (
    run_validations,
)

from ...reporting.formatter import (
    normalize_structure_issues,
)
def run(context: PipelineContext) -> PipelineContext:
    """
    Run repository structure validations.
    """

    source_root = context.ingestion.source_root

    structure_nodes = build_tree(source_root)

    raw_issues = run_validations(
        structure_nodes,
        context.policy,
    )

    structure_issues = normalize_structure_issues(
        raw_issues
    )

    context.structure_nodes = structure_nodes
    context.structure_issues = structure_issues

    return context