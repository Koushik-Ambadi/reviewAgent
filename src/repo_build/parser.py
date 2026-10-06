# src/repo_build/parser.py

from __future__ import annotations

from pathlib import Path
import re


_FAILURE_SIGNAL = re.compile(
    r"(?:cmake error|\berror:|\bfatal\b|configuring incomplete|"
    r"failed to build|build target .* failed|unable to build|"
    r"not able to compile|couldn't open project|no licenses available)",
    re.IGNORECASE,
)


def detect_build_log(repo_root: Path) -> str | None:
    candidates = [
        repo_root / "build.log",
        repo_root / "build" / "build.log",
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return None


def determine_status(return_code: int) -> str:
    return "success" if return_code == 0 else "failed"


def normalize_build_outcome(raw: dict) -> tuple[int, list[str]]:
    """Prevent a permissive batch wrapper from masking fatal build output."""
    process_return_code = int(raw["process_return_code"])
    failure_evidence = [
        line
        for line in [*raw.get("stderr", []), *raw.get("stdout", [])]
        if _FAILURE_SIGNAL.search(line)
    ]
    if process_return_code != 0 or failure_evidence:
        return 1, failure_evidence
    return 0, []
