# src/repo_review/reporting/serializers.py
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path


def serialize(obj):

    if is_dataclass(obj):
        return {
            key: serialize(value)
            for key, value in asdict(obj).items()
        }

    if isinstance(obj, dict):
        return {
            key: serialize(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [
            serialize(item)
            for item in obj
        ]

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, Enum):
        return obj.value

    return obj