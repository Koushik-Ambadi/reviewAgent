from __future__ import annotations

import queue
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Literal


OutputStream = Literal["stdout", "stderr"]
OutputCallback = Callable[[OutputStream, str], None]


def run_build_script(
    repo_root: Path,
    build_script: str = "cmake-build.bat",
    *,
    on_output: OutputCallback | None = None,
):
    return run_batch_script(
        repo_root,
        build_script,
        on_output=on_output,
        tail_build_log=True,
    )


def run_batch_script(
    repo_root: Path,
    script: str,
    *,
    on_output: OutputCallback | None = None,
    tail_build_log: bool = False,
) -> dict[str, object]:
    """Run a repository-local batch wrapper and optionally publish output lines."""
    repo_root = Path(repo_root).resolve()
    script_path = _resolve_repository_script(repo_root, script)

    process = subprocess.Popen(
        ["cmd", "/d", "/c", str(script_path)],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    log_path = repo_root / "build.log" if tail_build_log else None
    return _collect_process_output(process, on_output, log_path)


def _resolve_repository_script(repo_root: Path, script: str) -> Path:
    candidate = (repo_root / script).resolve()
    if not candidate.is_relative_to(repo_root):
        raise ValueError("Build scripts must be located inside the uploaded repository.")
    if not candidate.is_file():
        raise FileNotFoundError(f"Build script not found: {candidate}")
    if candidate.suffix.lower() not in {".bat", ".cmd"}:
        raise ValueError("Build wrappers must use a .bat or .cmd file.")
    return candidate


def _collect_process_output(
    process: subprocess.Popen[str],
    on_output: OutputCallback | None,
    log_path: Path | None = None,
) -> dict[str, object]:
    lines: queue.Queue[tuple[OutputStream, str | None]] = queue.Queue()
    tailer_stop = threading.Event()

    def read_stream(stream: OutputStream, handle) -> None:
        for line in iter(handle.readline, ""):
            lines.put((stream, line.rstrip("\r\n")))
        lines.put((stream, None))

    def tail_log() -> None:
        offset = log_path.stat().st_size if log_path and log_path.exists() else 0
        while not tailer_stop.wait(0.2):
            if not log_path or not log_path.exists():
                continue
            size = log_path.stat().st_size
            if size < offset:
                offset = 0
            if size == offset:
                continue
            with log_path.open(encoding="utf-8", errors="replace") as build_log:
                build_log.seek(offset)
                for line in build_log:
                    lines.put(("stdout", line.rstrip("\r\n")))
                offset = build_log.tell()

    readers = [
        threading.Thread(target=read_stream, args=("stdout", process.stdout), daemon=True),
        threading.Thread(target=read_stream, args=("stderr", process.stderr), daemon=True),
    ]
    tailer = (
        threading.Thread(target=tail_log, daemon=True)
        if log_path is not None
        else None
    )
    for reader in readers:
        reader.start()
    if tailer:
        tailer.start()

    captured: dict[OutputStream, list[str]] = {"stdout": [], "stderr": []}

    def publish(stream: OutputStream, line: str) -> None:
        captured[stream].append(line)
        if on_output:
            on_output(stream, line)

    completed_streams = 0
    while completed_streams < len(readers):
        stream, line = lines.get()
        if line is None:
            completed_streams += 1
        elif line:
            publish(stream, line)

    return_code = process.wait()
    tailer_stop.set()
    if tailer:
        tailer.join()
    while not lines.empty():
        stream, line = lines.get_nowait()
        if line:
            publish(stream, line)
    for reader in readers:
        reader.join()
    return {
        "process_return_code": return_code,
        "stdout": captured["stdout"],
        "stderr": captured["stderr"],
    }