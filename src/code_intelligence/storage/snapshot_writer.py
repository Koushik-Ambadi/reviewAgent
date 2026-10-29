from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from code_intelligence.graph import KnowledgeGraph


_REQUIRED_PROVENANCE = {
    "source_revision",
    "dirty",
    "producer",
    "producer_version",
}


def canonical_snapshot_bytes(
    graph: KnowledgeGraph,
    *,
    provenance: Mapping[str, Any],
) -> bytes:
    missing = sorted(_REQUIRED_PROVENANCE - provenance.keys())
    if missing:
        raise ValueError(
            "Snapshot provenance is missing required fields: " + ", ".join(missing)
        )
    payload = graph.to_dict()
    payload["provenance"] = dict(provenance)
    return (
        json.dumps(
            payload,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def write_snapshot(
    graph: KnowledgeGraph,
    output_path: Path,
    *,
    provenance: Mapping[str, Any],
) -> Path:
    """Atomically replace a graph snapshot with deterministic JSON bytes."""

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    data = canonical_snapshot_bytes(graph, provenance=provenance)

    try:
        with temporary_path.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.replace(output_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise

    return output_path
