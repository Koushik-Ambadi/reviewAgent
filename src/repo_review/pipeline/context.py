# src/repo_review/pipeline/context.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PipelineContext:

    # request
    source_path: str | Path

    source_type: str = "local"
    policy_name: str = "default"

    module_name: str = ""

    # loaded runtime objects
    policy: dict[str, Any] = field(default_factory=dict)

    # workspace
    workspace_path: Path | None = None
    repo_root: Path | None = None
    analysis_path: Path | None = None

    structure_issues: list = field(default_factory=list)

    validation_issues: list = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)



    report_path: Path | None = None