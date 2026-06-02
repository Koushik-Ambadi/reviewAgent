# src/repo_review/pipeline/context.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PipelineContext:

    # request
    policy_name: str = "default"
    workspace_path: Path | None = None
    repo_root: Path | None = None


    # loaded runtime objects
    policy: dict[str, Any] = field(default_factory=dict)

    # workspace
    analysis_path: Path | None = None
    module_name: str = ""

    structure_issues: list = field(default_factory=list)
    validation_issues: list = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)



    report_path: Path | None = None