# src/repo_review/checks/naming/loader.py

import json
from pathlib import Path


def load_review_results(path: Path | str):

    with open(Path(path), "r", encoding="utf-8") as f:
        return json.load(f)