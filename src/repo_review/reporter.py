from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

try:
    from .models import ValidationIssue
except ImportError:  # pragma: no cover
    from models import ValidationIssue


console = Console()


def _as_dict(item):
    if isinstance(item, ValidationIssue):
        if hasattr(item, "model_dump"):
            return item.model_dump()
        return item.dict()
    return dict(item)


def normalize_structure_issues(issues):
    normalized = []
    for issue in issues:
        item = _as_dict(issue)
        item["status"] = "FAILED"
        normalized.append(item)
    return normalized


def print_report(report):
    summary = report.get("summary", {})
    console.print(
        f"[bold]Report[/bold] failed={summary.get('failed', 0)} "
        f"exception={summary.get('exception', 0)} passed={summary.get('passed', 0)}"
    )

    for section in report.get("sections", []):
        console.print(f"\n[bold]{section['title']}[/bold] [{section['status']}]")
        issues = section.get("issues", [])
        if not issues:
            console.print("- no issues")
            continue
        for item in issues[:10]:
            if isinstance(item, dict) and "message" in item:
                console.print(f"- {item['message']}")
            elif isinstance(item, dict) and "file" in item and "reason" in item:
                console.print(f"- {item['file']} -> {item['reason']}")
            else:
                console.print(f"- {item}")
        if len(issues) > 10:
            console.print(f"- ... and {len(issues) - 10} more")


def write_report(report, output_path: Path | str):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=True)
    return path
