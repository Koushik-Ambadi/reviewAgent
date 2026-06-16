# src/repo_build/runner.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .models import BuildResult
from .parser import detect_build_log, determine_status
from .reporter import build_result_to_dict
from .builder import run_build_script


def execute_firmware_build(
    repo_root: str | Path,
    build_script: str = "cmake-build.bat",
):
    repo_root = Path(repo_root).resolve()

    started_at = datetime.now(timezone.utc).isoformat()

    raw = run_build_script(
        repo_root=repo_root,
        build_script=build_script,
    )

    completed_at = datetime.now(timezone.utc).isoformat()

    result = BuildResult(
        status=determine_status(raw["return_code"]),
        return_code=raw["return_code"],
        repo_root=str(repo_root),
        build_script=build_script,
        stdout=raw["stdout"],
        stderr=raw["stderr"],
        build_log_path=detect_build_log(repo_root),
        started_at=started_at,
        completed_at=completed_at,
    )

    return build_result_to_dict(result)