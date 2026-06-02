# src/repo_build/builder.py

from __future__ import annotations

import subprocess
from pathlib import Path


def run_build_script(
    repo_root: Path,
    build_script: str = "cmake-build.bat",
):
    repo_root = Path(repo_root).resolve()

    script_path = repo_root / build_script

    if not script_path.exists():
        raise FileNotFoundError(
            f"Build script not found: {script_path}"
        )

    process = subprocess.Popen(
        ["cmd", "/c", str(script_path)],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate()

    return {
        "return_code": process.returncode,
        "stdout": stdout.splitlines(),
        "stderr": stderr.splitlines(),
    }