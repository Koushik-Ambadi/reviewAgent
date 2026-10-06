# src/repo_build/reporter.py

from __future__ import annotations

from .models import BuildResult


def build_result_to_dict(result: BuildResult) -> dict:
    return {
        "run_id": result.run_id,
        "status": result.status,
        "return_code": result.return_code,
        "process_return_code": result.process_return_code,
        "repo_root": result.repo_root,
        "build_script": result.build_script,
        "build_log_path": result.build_log_path,
        "format_step": result.format_step,
        "build_step": result.build_step,
        "important_diagnostics": result.important_diagnostics,
        "artifact_manifest": result.artifact_manifest,
        "intelligence_summary": result.intelligence_summary,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "started_at": result.started_at,
        "completed_at": result.completed_at,
    }
