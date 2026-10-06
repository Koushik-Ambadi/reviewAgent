# src/orchestrator/build.py

from pathlib import Path

from repo_build.runner import (
    execute_firmware_build,
)

from orchestrator.run_store import (
    get_run_path,
    load_report,
    update_report_extension,
    write_json,
)


def get_repo_root_for_run(
    run_id: str,
) -> Path:

    run_path = get_run_path(run_id)
    report = load_report(run_id)

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
    *,
    run_format: bool = False,
    on_output=None,
):

    repo_root = get_repo_root_for_run(
        run_id
    )

    build_result = execute_firmware_build(
        repo_root,
        run_id=run_id,
        run_format=run_format,
        on_output=on_output,
    )
    write_json(get_run_path(run_id) / "build.json", build_result)
    update_report_extension(run_id, "build_result", build_result)
    return build_result
