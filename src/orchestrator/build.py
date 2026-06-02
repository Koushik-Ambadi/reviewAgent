# src/orchestrator/build.py

import json
from pathlib import Path

from repo_build.runner import (
    execute_firmware_build,
)

from orchestrator.config import (
    WORKSPACE_ROOT,
)


def get_repo_root_for_run(
    run_id: str,
) -> Path:

    run_path = (
        WORKSPACE_ROOT
        / run_id
    )

    report_path = (
        run_path
        / "report.json"
    )

    with open(
        report_path,
        "r",
        encoding="utf-8",
    ) as f:
        report = json.load(f)

    module_name = (
        report["metadata"]
        ["module_name"]
    )

    repo_root = (
        run_path
        / module_name
    )

    if not repo_root.exists():
        raise RuntimeError(
            f"Repo root not found: {repo_root}"
        )

    return repo_root


def build_run(
    run_id: str,
):

    repo_root = get_repo_root_for_run(
        run_id
    )

    return execute_firmware_build(
        repo_root
    )