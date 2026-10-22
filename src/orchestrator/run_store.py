from __future__ import annotations

import json
import re
import time
from uuid import uuid4
from pathlib import Path
from typing import Any

from .config import WORKSPACE_ROOT


_RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class RunNotFoundError(FileNotFoundError):
    """Raised when a requested run does not exist in the file-backed store."""


class RunStoreError(ValueError):
    """Raised when a supplied run ID is unsafe or malformed."""


def get_run_path(run_id: str) -> Path:
    if not _RUN_ID_PATTERN.fullmatch(run_id):
        raise RunStoreError("Run ID contains unsupported characters.")

    run_path = WORKSPACE_ROOT / run_id
    if not run_path.is_dir():
        raise RunNotFoundError(f"Run not found: {run_id}")

    return run_path


def load_report(run_id: str) -> dict[str, Any]:
    report_path = get_run_path(run_id) / "report.json"
    if not report_path.is_file():
        raise RunNotFoundError(f"Review report not found: {run_id}")

    with report_path.open(encoding="utf-8") as report_file:
        return json.load(report_file)


def write_json(path: Path, content: dict[str, Any]) -> None:
    # A process-shared fixed `.tmp` name allows reload workers to overwrite or
    # replace one another's temporary file. Use a unique sibling and retry a
    # short-lived Windows sharing violation on the destination replacement.
    temporary_path = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
    try:
        with temporary_path.open("w", encoding="utf-8") as output_file:
            json.dump(content, output_file, indent=2)
        for attempt in range(8):
            try:
                temporary_path.replace(path)
                return
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(0.05 * (attempt + 1))
    finally:
        temporary_path.unlink(missing_ok=True)


def update_report_extension(
    run_id: str,
    field_name: str,
    value: Any,
) -> dict[str, Any]:
    report = load_report(run_id)
    report[field_name] = value
    write_json(get_run_path(run_id) / "report.json", report)
    return report
