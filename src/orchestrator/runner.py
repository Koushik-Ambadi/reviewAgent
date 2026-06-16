# src/orchestrator/runner.py

from orchestrator.workspace import (
    create_run_workspace,
)

from orchestrator.ingestion.ingestion_manager import (
    ingest_source,
)


def prepare_review_run(
    *,
    source_path,
    source_type,
):

    workspace_path = (
        create_run_workspace()
    )

    repo_root = ingest_source(
        source_type=source_type,
        source_path=source_path,
        workspace_path=workspace_path,
    )

    module_name = repo_root.name

    return (
        workspace_path,
        repo_root,
        module_name,
    )