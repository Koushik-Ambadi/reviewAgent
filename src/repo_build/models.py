# src/repo_build/models.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class BuildResult:
    run_id: str
    status: str
    return_code: int
    process_return_code: int

    repo_root: str
    build_script: str

    stdout: List[str] = field(default_factory=list)
    stderr: List[str] = field(default_factory=list)

    build_log_path: str | None = None

    format_step: dict[str, Any] = field(default_factory=dict)
    build_step: dict[str, Any] = field(default_factory=dict)
    important_diagnostics: List[str] = field(default_factory=list)
    artifact_manifest: List[dict[str, Any]] = field(default_factory=list)
    intelligence_summary: dict[str, Any] = field(default_factory=dict)

    started_at: str | None = None
    completed_at: str | None = None
