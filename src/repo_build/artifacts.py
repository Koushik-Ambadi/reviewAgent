from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


_ARTIFACT_SUFFIXES = {
    ".elf": "ELF executable",
    ".hex": "Intel HEX image",
    ".bin": "Binary image",
    ".map": "Linker map",
    ".log": "Build log",
}
_REPORT_SUFFIXES = {".html", ".htm", ".json", ".xml", ".pdf", ".txt"}
_IGNORED_DIRECTORIES = {".git", "analysis", "node_modules"}
_MAX_ARTIFACTS = 50


def discover_artifacts(repo_root: Path) -> list[dict[str, object]]:
    """Return a concise manifest of build outputs worth presenting to a user."""
    artifacts: list[dict[str, object]] = []
    for path in repo_root.rglob("*"):
        if not path.is_file() or _is_ignored(path, repo_root):
            continue

        artifact_type = _artifact_type(path)
        if artifact_type is None:
            continue

        stat = path.stat()
        artifacts.append(
            {
                "relative_path": path.relative_to(repo_root).as_posix(),
                "type": artifact_type,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime,
                    tz=UTC,
                ).isoformat(),
            }
        )

    return sorted(
        artifacts,
        key=lambda artifact: str(artifact["relative_path"]),
    )[:_MAX_ARTIFACTS]


def _artifact_type(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in _ARTIFACT_SUFFIXES:
        return _ARTIFACT_SUFFIXES[suffix]
    if "report" in path.name.lower() and suffix in _REPORT_SUFFIXES:
        return "Generated report"
    return None


def _is_ignored(path: Path, repo_root: Path) -> bool:
    return any(
        part in _IGNORED_DIRECTORIES
        for part in path.relative_to(repo_root).parts
    )
