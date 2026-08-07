# src/repo_review/reporting/reporter.py
from __future__ import annotations

import json
from pathlib import Path

from .formatter import (
    build_report_data,
)


def build_final_report(
    context,
) -> dict:

    return build_report_data(
        context,
    )


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
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
        )

    return path