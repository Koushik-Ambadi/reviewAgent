from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable


_CONFIG_NAME = "review-build.json"
_CLANG_FORMAT_NAME = ".clang-format"
_SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
_IGNORED_DIRECTORIES = {".git", "analysis", "build", "out", "CMakeFiles", "node_modules"}
OutputCallback = Callable[[str, str], None]


def load_formatter_configuration(repo_root: Path) -> dict[str, Any] | None:
    """Load the repository's reviewed formatting configuration.

    A repository-local wrapper remains supported. When no wrapper is present,
    a root `.clang-format` file enables the built-in C/C++ formatter.
    """
    config_path = repo_root / _CONFIG_NAME
    if config_path.is_file():
        with config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
        format_config = config.get("format", {})
        script = format_config.get("script")
        if isinstance(script, str) and script.strip():
            return {
                "kind": "script",
                "script": script.strip(),
                "config_path": _CONFIG_NAME,
            }

    if (repo_root / _CLANG_FORMAT_NAME).is_file():
        return {
            "kind": "clang-format",
            "command": "clang-format --style=file",
            "config_path": _CLANG_FORMAT_NAME,
        }
    return None


def run_clang_format(
    repo_root: Path,
    on_output: OutputCallback | None = None,
) -> dict[str, object]:
    """Format repository C/C++ files using the checked-in `.clang-format` file."""
    executable = shutil.which("clang-format") or shutil.which("clang-format.exe")
    if executable is None:
        return {
            "process_return_code": 1,
            "stdout": [],
            "stderr": [
                "clang-format was requested by .clang-format but is not available on PATH."
            ],
        }

    source_files = discover_format_sources(repo_root)
    if not source_files:
        return {
            "process_return_code": 0,
            "stdout": ["No C/C++ source files were found for formatting."],
            "stderr": [],
        }

    message = (
        f"Formatting {len(source_files)} C/C++ source file(s) using {_CLANG_FORMAT_NAME}."
    )
    if on_output:
        on_output("stdout", message)
    stdout = [message]
    stderr: list[str] = []

    for source_file in source_files:
        process = subprocess.run(
            [
                executable,
                "--style=file",
                "--fallback-style=none",
                f"--assume-filename={repo_root / 'format.cpp'}",
            ],
            cwd=repo_root,
            input=source_file.read_bytes(),
            capture_output=True,
            check=False,
        )
        process_stderr = process.stderr.decode(errors="replace")
        if process.returncode != 0:
            stderr.extend(_lines(process_stderr))
            error = f"clang-format failed for {source_file.relative_to(repo_root).as_posix()}."
            stderr.append(error)
            if on_output:
                for line in _lines(process_stderr):
                    on_output("stderr", line)
                on_output("stderr", error)
            return {
                "process_return_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
            }
        source_file.write_bytes(process.stdout)

    completion = "Formatting completed successfully."
    stdout.append(completion)
    if on_output:
        on_output("stdout", completion)
    return {"process_return_code": 0, "stdout": stdout, "stderr": stderr}


def discover_format_sources(repo_root: Path) -> list[Path]:
    return sorted(
        path
        for path in repo_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in _SOURCE_SUFFIXES
        and not any(part in _IGNORED_DIRECTORIES for part in path.relative_to(repo_root).parts)
    )


def _lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line]