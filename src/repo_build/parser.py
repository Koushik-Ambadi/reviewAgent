# src/repo_review/repo_build/parser.py

from __future__ import annotations

from pathlib import Path


def detect_build_log(repo_root: Path) -> str | None:
    candidates = [
        repo_root / "build.log",
        repo_root / "build" / "build.log",
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return None


def determine_status(return_code: int) -> str:
    return "success" if return_code == 0 else "failed"