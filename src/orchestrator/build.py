# src/orchestrator/build.py

from pathlib import Path

from repo_build.runner import (
    execute_firmware_build,
)
from repo_build.artifact_references import find_successful_artifact_references
from repo_remediation.observability import redact_sensitive

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
    run_format: bool = True,
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
    trace = build_result.pop("_build_remediation_trace", None)
    build_result["artifact_references"] = (
        find_successful_artifact_references(
            get_run_path(run_id).parent,
            current_run_id=run_id,
            module_name=str(load_report(run_id)["metadata"]["module_name"]),
        )
        if build_result.get("status") == "failed"
        else []
    )
    write_json(get_run_path(run_id) / "build.json", build_result)
    if trace is not None:
        write_json(get_run_path(run_id) / "build-remediation.json", redact_sensitive({
            "run_id": run_id,
            "build_status": build_result.get("status"),
            "trace": trace,
            "remediation": (build_result.get("intelligence_summary") or {}).get(
                "remediation"
            ),
        }))
    update_report_extension(run_id, "build_result", build_result)
    return build_result
