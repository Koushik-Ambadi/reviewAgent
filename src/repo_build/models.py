# src/repo_build/models.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class BuildResult:
    status: str
    return_code: int

    repo_root: str
    build_script: str

    stdout: List[str] = field(default_factory=list)
    stderr: List[str] = field(default_factory=list)

    build_log_path: str | None = None

    started_at: str | None = None
    completed_at: str | None = None