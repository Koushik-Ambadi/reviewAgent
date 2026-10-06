# src/repo_build/runner.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .models import BuildResult
from .artifacts import discover_artifacts
from .intelligence import (
    PlaceholderBuildIntelligenceProvider,
    select_important_diagnostics,
)
from .parser import detect_build_log, determine_status
from .reporter import build_result_to_dict
from .builder import run_build_script


def execute_firmware_build(
    repo_root: str | Path,
    run_id: str,
    build_script: str = "cmake-build.bat",
):
    repo_root = Path(repo_root).resolve()

    started_at = datetime.now(timezone.utc).isoformat()

    try:
        raw = run_build_script(
            repo_root=repo_root,
            build_script=build_script,
        )
    except FileNotFoundError as error:
        raw = {
            "return_code": 1,
            "stdout": [],
            "stderr": [str(error)],
        }

    completed_at = datetime.now(timezone.utc).isoformat()

    result = BuildResult(
        run_id=run_id,
        status=determine_status(raw["return_code"]),
        return_code=raw["return_code"],
        repo_root=str(repo_root),
        build_script=build_script,
        stdout=raw["stdout"],
        stderr=raw["stderr"],
        build_log_path=detect_build_log(repo_root),
        format_step={
            "status": "skipped",
            "command": None,
            "message": "Formatting is not configured for this uploaded repository.",
        },
        build_step={
            "status": determine_status(raw["return_code"]),
            "command": build_script,
            "message": (
                "Build completed successfully."
                if raw["return_code"] == 0
                else "Build command did not complete successfully."
            ),
        },
        important_diagnostics=select_important_diagnostics(
            raw["stdout"],
            raw["stderr"],
        ),
        artifact_manifest=(
            discover_artifacts(repo_root)
            if raw["return_code"] == 0
            else []
        ),
        started_at=started_at,
        completed_at=completed_at,
    )

    result_data = build_result_to_dict(result)
    result_data["intelligence_summary"] = (
        PlaceholderBuildIntelligenceProvider().summarize(result_data)
    )
    return result_data
