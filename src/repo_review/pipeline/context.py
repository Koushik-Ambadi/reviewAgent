# src/repo_review/pipeline/context.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..contracts import RunResult


@dataclass
class PipelineContext:

    # request
    policy_name: str = "default"
    workspace_path: Path | None = None
    repo_root: Path | None = None


    # loaded runtime objects
    policy: dict[str, Any] = field(default_factory=dict)

    # workspace
    module_name: str = ""

    stage_results: list = field(default_factory=list)

    report: dict[str, Any] = field(default_factory=dict)

    diagnostics: list = field(default_factory=list)

    run_result: RunResult | None = None