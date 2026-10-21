"""Provenance-aware references to artifacts from retained successful runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import discover_artifacts


_SUCCESS_ARTIFACT_TYPES = {"ELF executable", "Intel HEX image", "Linker map"}


def find_successful_artifact_references(
    workspace_root: Path,
    *,
    current_run_id: str,
    module_name: str,
) -> list[dict[str, Any]]:
    """Return actual relative paths observed in a retained output set.

    Older runs may not have a persisted ``build.json`` even though their
    successful output tree remains. We therefore require a representative ELF,
    HEX, and map set and label the result as reference-only evidence rather than
    claiming the current run produced those files.
    """
    for run_path in sorted(
        (path for path in workspace_root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
        reverse=True,
    ):
        if run_path.name == current_run_id:
            continue
        module_root = run_path / module_name
        if not module_root.is_dir():
            continue
        manifest = discover_artifacts(module_root)
        if not _looks_like_successful_output(manifest):
            continue
        return [
            {
                **artifact,
                "source_run_id": run_path.name,
                "source_module": module_name,
                "reference_only": True,
                "evidence": "retained successful output set",
            }
            for artifact in manifest
            if artifact["type"] in _SUCCESS_ARTIFACT_TYPES
        ]
    return []


def _looks_like_successful_output(manifest: list[dict[str, Any]]) -> bool:
    types = {str(item.get("type")) for item in manifest}
    return _SUCCESS_ARTIFACT_TYPES.issubset(types)
