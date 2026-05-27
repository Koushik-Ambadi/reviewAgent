# src/repo_review/repo_build/reporter.py

from __future__ import annotations

from .models import BuildResult


def build_result_to_dict(result: BuildResult) -> dict:
    return {
        "status": result.status,
        "return_code": result.return_code,
        "repo_root": result.repo_root,
        "build_script": result.build_script,
        "build_log_path": result.build_log_path,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "started_at": result.started_at,
        "completed_at": result.completed_at,
    }