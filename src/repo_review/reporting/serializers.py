# src/repo_review/reporting/serializers.py
from __future__ import annotations

from pathlib import Path
from dataclasses import asdict, is_dataclass


def serialize_issue(item):

    if isinstance(item, dict):
        return item

    if is_dataclass(item):
        return asdict(item)

    if hasattr(item, "model_dump"):
        return item.model_dump()

    if hasattr(item, "dict"):
        return item.dict()

    return vars(item)


def serialize_list(items):

    return [
        serialize_issue(item)
        for item in items
    ]


def serialize_path(
    path: Path | str,
) -> str:

    return str(path)