# src/repo_review/reporting/reporter.py

from __future__ import annotations

import json

from pathlib import Path

from rich.console import Console

from .formatter import (
    build_report_data,
)

console = Console()


# =========================================================
# FINAL REPORT BUILDER
# =========================================================

def build_final_report(
    context,
) -> dict:

    return build_report_data(
        context
    )


# =========================================================
# REPORT WRITER
# =========================================================

def write_report(
    report: dict,
    output_path: Path | str,
) -> Path:

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=True,
        )

    return path
