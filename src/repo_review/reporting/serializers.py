# src/repo_review/reporting/serializers.py

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..models import ValidationIssue


# =========================================================
# ISSUE SERIALIZATION
# =========================================================

def serialize_issue(item: Any) -> dict:
    """
    Convert ValidationIssue / pydantic model / dict
    into plain serializable dictionary.
    """

    if isinstance(item, ValidationIssue):

        if hasattr(item, "model_dump"):
            return item.model_dump()

        return item.dict()

    return dict(item)


def serialize_list(
    items: list[Any],
) -> list[dict]:

    return [
        serialize_issue(item)
        for item in items
    ]


# =========================================================
# PATH SERIALIZATION
# =========================================================

def serialize_path(
    path: Path | str,
) -> str:

    return str(path)