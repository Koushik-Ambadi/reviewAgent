from __future__ import annotations

import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

from .build import build_run
from .run_store import RunNotFoundError, get_run_path, write_json


_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="review-build")
_run_locks: defaultdict[str, threading.Lock] = defaultdict(threading.Lock)
_start_locks: defaultdict[str, threading.Lock] = defaultdict(threading.Lock)
_MAX_LIVE_LINES = 800


def start_build_job(run_id: str, *, run_format: bool = False) -> dict[str, Any]:
    lock = _start_locks[run_id]
    with lock:
        progress = get_build_status(run_id)
        if progress.get("state") in {"queued", "running"}:
            return progress

        started_at = _now()
        progress = {
            "run_id": run_id,
            "state": "queued",
            "run_format": run_format,
            "started_at": started_at,
            "updated_at": started_at,
            "stdout": [],
            "stderr": [],
        }
        _write_progress(run_id, progress)
        _executor.submit(_execute_job, run_id, run_format)
    return progress


def get_build_status(run_id: str) -> dict[str, Any]:
    progress_path = get_run_path(run_id) / "build-progress.json"
    if not progress_path.is_file():
        build_path = get_run_path(run_id) / "build.json"
        if build_path.is_file():
            import json

            with build_path.open(encoding="utf-8") as build_file:
                return {"run_id": run_id, "state": "completed", "result": json.load(build_file)}
        return {"run_id": run_id, "state": "idle", "stdout": [], "stderr": []}

    import json

    with progress_path.open(encoding="utf-8") as progress_file:
        progress = json.load(progress_file)
    if progress.get("state") == "completed":
        build_path = get_run_path(run_id) / "build.json"
        if build_path.is_file():
            with build_path.open(encoding="utf-8") as build_file:
                progress["result"] = json.load(build_file)
    return progress


def _execute_job(run_id: str, run_format: bool) -> None:
    lock = _run_locks[run_id]
    with lock:
        _update_progress(run_id, state="running")
        try:
            result = build_run(
                run_id,
                run_format=run_format,
                on_output=lambda stream, line: _append_output(run_id, stream, line),
            )
            _update_progress(
                run_id,
                state="completed",
                completed_at=_now(),
                status=result["status"],
                return_code=result["return_code"],
            )
        except Exception as error:  # Persist job failures for the UI, then keep worker alive.
            _update_progress(
                run_id,
                state="failed",
                completed_at=_now(),
                error=str(error),
            )


def _append_output(run_id: str, stream: str, line: str) -> None:
    progress = get_build_status(run_id)
    lines = progress.setdefault(stream, [])
    lines.append(line)
    if len(lines) > _MAX_LIVE_LINES:
        del lines[:-_MAX_LIVE_LINES]
        progress["output_truncated"] = True
    progress["updated_at"] = _now()
    _write_progress(run_id, progress)


def _update_progress(run_id: str, **changes: Any) -> None:
    progress = get_build_status(run_id)
    progress.update(changes)
    progress["updated_at"] = _now()
    _write_progress(run_id, progress)


def _write_progress(run_id: str, progress: dict[str, Any]) -> None:
    write_json(get_run_path(run_id) / "build-progress.json", progress)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
