from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .models import EdgeKind, NodeKind


def normalized_path(path: Path, repo_root: Path) -> tuple[str, bool]:
    resolved = path.resolve()
    root = repo_root.resolve()
    try:
        return resolved.relative_to(root).as_posix(), False
    except ValueError:
        return resolved.as_posix(), True


def cursor_usr(cursor: Any) -> str | None:
    try:
        value = cursor.get_usr()
    except (AttributeError, RuntimeError):
        return None
    return str(value) if value else None


def node_id(
    kind: NodeKind,
    *,
    name: str,
    path: str,
    usr: str | None = None,
    scope: str | None = None,
) -> str:
    if usr:
        return f"{kind.value}:usr:{usr}"
    scoped_name = f"{scope}:{name}" if scope else name
    return f"{kind.value}:fallback:{path}:{scoped_name}"


def edge_id(
    kind: EdgeKind,
    *,
    source: str,
    target: str,
    discriminator: str = "",
) -> str:
    value = "\x1f".join((kind.value, source, target, discriminator))
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"edge:{digest}"
