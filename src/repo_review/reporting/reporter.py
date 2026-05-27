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


# =========================================================
# TERMINAL VIEW
# =========================================================

def print_report(
    report: dict,
) -> None:

    summary = report.get(
        "summary",
        {},
    )

    console.print(
        f"[bold]Report[/bold] "
        f"failed={summary.get('failed', 0)} "
        f"exception={summary.get('exception', 0)} "
        f"passed={summary.get('passed', 0)}"
    )

    for section in report.get(
        "sections",
        [],
    ):

        console.print(
            f"\n[bold]{section['title']}[/bold] "
            f"[{section['status']}]"
        )

        issues = section.get(
            "issues",
            [],
        )

        if not issues:
            console.print(
                "- no issues"
            )
            continue

        for item in issues[:10]:

            if isinstance(item, dict):

                if "message" in item:

                    console.print(
                        f"- {item['message']}"
                    )

                    continue

                if (
                    "file" in item
                    and "reason" in item
                ):

                    console.print(
                        f"- {item['file']} "
                        f"-> {item['reason']}"
                    )

                    continue

            console.print(
                f"- {item}"
            )

        if len(issues) > 10:

            console.print(
                f"- ... and "
                f"{len(issues) - 10} more"
            )