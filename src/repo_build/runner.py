from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .artifacts import discover_artifacts
from .builder import OutputCallback, run_batch_script
from .formatting import load_formatter_configuration
from .intelligence import (
    PlaceholderBuildIntelligenceProvider,
    select_important_diagnostics,
)
from .models import BuildResult
from .parser import detect_build_log, determine_status, normalize_build_outcome
from .reporter import build_result_to_dict


def execute_firmware_build(
    repo_root: str | Path,
    run_id: str,
    build_script: str = "cmake-build.bat",
    *,
    run_format: bool = False,
    on_output: OutputCallback | None = None,
) -> dict:
    repo_root = Path(repo_root).resolve()
    started_at = datetime.now(timezone.utc).isoformat()
    format_step, format_output = _run_format_step(repo_root, run_format, on_output)

    if format_step["status"] == "failed":
        raw = {
            "process_return_code": 1,
            "stdout": [],
            "stderr": [],
        }
        effective_return_code = 1
        build_step = {
            "status": "skipped",
            "command": build_script,
            "message": "Build was skipped because formatting failed.",
        }
    else:
        raw = _run_build(repo_root, build_script, on_output)
        effective_return_code, failure_evidence = normalize_build_outcome(raw)
        build_step = {
            "status": determine_status(effective_return_code),
            "command": build_script,
            "message": _build_message(
                raw["process_return_code"],
                effective_return_code,
                failure_evidence,
            ),
        }

    completed_at = datetime.now(timezone.utc).isoformat()
    stdout = [*format_output["stdout"], *raw["stdout"]]
    stderr = [*format_output["stderr"], *raw["stderr"]]
    result = BuildResult(
        run_id=run_id,
        status=determine_status(effective_return_code),
        return_code=effective_return_code,
        process_return_code=raw["process_return_code"],
        repo_root=str(repo_root),
        build_script=build_script,
        stdout=stdout,
        stderr=stderr,
        build_log_path=detect_build_log(repo_root),
        format_step=format_step,
        build_step=build_step,
        important_diagnostics=select_important_diagnostics(stdout, stderr),
        artifact_manifest=(discover_artifacts(repo_root) if effective_return_code == 0 else []),
        started_at=started_at,
        completed_at=completed_at,
    )
    result_data = build_result_to_dict(result)
    result_data["intelligence_summary"] = (
        PlaceholderBuildIntelligenceProvider().summarize(result_data)
    )
    return result_data


def _run_format_step(
    repo_root: Path,
    run_format: bool,
    on_output: OutputCallback | None,
) -> tuple[dict, dict[str, list[str]]]:
    no_output: dict[str, list[str]] = {"stdout": [], "stderr": []}
    configuration = load_formatter_configuration(repo_root)
    if not run_format:
        message = (
            "Formatting is disabled for this build request."
            if configuration
            else "Formatting is not configured for this uploaded repository."
        )
        return ({"status": "skipped", "command": None, "message": message}, no_output)
    if not configuration:
        return (
            {
                "status": "skipped",
                "command": None,
                "message": "No formatter wrapper is configured in review-build.json.",
            },
            no_output,
        )

    def prefixed_output(stream: str, line: str) -> None:
        if on_output:
            on_output(stream, f"[format] {line}")

    raw = _run_batch(repo_root, configuration["script"], prefixed_output)
    code, evidence = normalize_build_outcome(raw)
    output = {
        "stdout": [f"[format] {line}" for line in raw["stdout"]],
        "stderr": [f"[format] {line}" for line in raw["stderr"]],
    }
    return (
        {
            "status": determine_status(code),
            "command": configuration["script"],
            "message": (
                "Formatting completed successfully."
                if code == 0
                else _build_message(raw["process_return_code"], code, evidence)
            ),
        },
        output,
    )


def _run_build(
    repo_root: Path,
    build_script: str,
    on_output: OutputCallback | None,
) -> dict:
    def prefixed_output(stream: str, line: str) -> None:
        if on_output:
            on_output(stream, f"[build] {line}")

    raw = _run_batch(repo_root, build_script, prefixed_output)
    return {
        "process_return_code": raw["process_return_code"],
        "stdout": [f"[build] {line}" for line in raw["stdout"]],
        "stderr": [f"[build] {line}" for line in raw["stderr"]],
    }


def _run_batch(repo_root: Path, script: str, on_output: OutputCallback | None) -> dict:
    try:
        return run_batch_script(repo_root, script, on_output=on_output)
    except (FileNotFoundError, ValueError) as error:
        return {"process_return_code": 1, "stdout": [], "stderr": [str(error)]}


def _build_message(
    process_return_code: int,
    effective_return_code: int,
    failure_evidence: list[str],
) -> str:
    if effective_return_code == 0:
        return "Build completed successfully."
    if process_return_code == 0 and failure_evidence:
        return "Build output reports a failure although the batch wrapper returned 0."
    return "Build command did not complete successfully."
