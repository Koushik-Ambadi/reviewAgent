# src/repo_review/ingestion/config_loader.py

from __future__ import annotations

from pathlib import Path

import yaml


def load_policy(path: Path | str) -> dict:
    with open(
        Path(path),
        "r",
        encoding="utf-8",
    ) as f:
        return yaml.safe_load(f)