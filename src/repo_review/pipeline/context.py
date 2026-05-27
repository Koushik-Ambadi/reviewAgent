# src/repo_review/pipeline/context.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PipelineContext:

    # request
    source_path: str | Path
    module_name: str
    repo_url: str
    pipeline_config_path: str | Path

    # configs
    pipeline_config: dict[str, Any] = field(default_factory=dict)
    policy: dict[str, Any] = field(default_factory=dict)

    # ingestion
    ingestion: dict[str, Any] = field(default_factory=dict)

    # structure
    structure_nodes: list = field(default_factory=list)
    structure_issues: list = field(default_factory=list)

    # compile db
    compile_db_path: str | None = None

    # ast
    ast_artifact: dict[str, Any] = field(default_factory=dict)
    review_results: list = field(default_factory=list)

    # validations
    validation_issues: list = field(default_factory=list)

    # report
    report: dict[str, Any] = field(default_factory=dict)