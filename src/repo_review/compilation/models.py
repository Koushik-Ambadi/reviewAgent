# src/repo_review/compilation/models.py

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CompilationArtifact:
    status: str
    source_root: Path
    build_dir: Path
    output_dir: Path
    compile_db_path: Path
    error: Optional[str] = None