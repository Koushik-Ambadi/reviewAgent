# src/repo_review/firmware_build.py

from __future__ import annotations

import subprocess
from pathlib import Path


def build_firmware(
    repo_root: str,
    build_script: str = "cmake-build.bat",
) -> None:
    """
    Executes the official firmware build batch script.

    Uses the existing validated Windows build flow:
    - clean-up.bat
    - GHS environment setup
    - CMake configure
    - firmware build
    - build.log generation
    """

    repo_root = Path(repo_root).resolve()
    build_script_path = repo_root / build_script

    if not build_script_path.exists():
        raise FileNotFoundError(
            f"Build script not found: {build_script_path}"
        )

    print(f"[FW] Running firmware build script:")
    print(f"[FW] {build_script_path}")

    subprocess.run(
        ["cmd", "/c", str(build_script_path)],
        cwd=str(repo_root),
        check=True,
    )

    print("[FW] Build complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--repo-root",
        required=True,
        help="Repository root containing cmake-build.bat",
    )

    args = parser.parse_args()

    build_firmware(args.repo_root)