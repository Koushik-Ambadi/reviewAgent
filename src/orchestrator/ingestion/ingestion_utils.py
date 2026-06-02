# src/repo_review/ingestion/ingestion_utils.py

from __future__ import annotations

from pathlib import Path


def resolve_path(path: Path | str) -> Path:
    return Path(path).resolve()


def ensure_directory(path: Path | str) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path