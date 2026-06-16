# src/repo_review/analysis/source_index/generator.py
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def build_source_index(
    repo_root: Path,
    analysis_dir: Path,
    config: dict[str, Any],
) -> dict[str, Any]:

    compilation_config = config.get("compilation", {})
    ast_config = config.get("ast", {})

    build_dir = analysis_dir / "cmake_build"
    compile_db_path = build_dir / "compile_commands.json"

    cmake_exe = compilation_config.get("cmake_exe", "cmake")
    generator = compilation_config.get("generator", "Ninja")

    # =====================================================
    # FIX: Linux-safe compiler defaults
    # =====================================================
    clang_path = ast_config.get(
        "clang_path",
        "/usr/bin/gcc",
    )

    clangxx_path = ast_config.get(
        "clangxx_path",
        "/usr/bin/g++",
    )

    artifact = {
        "status": "pending",
        "repo_root": str(repo_root),
        "build_dir": str(build_dir),
        "compile_db_path": str(compile_db_path),
        "generator": generator,
        "error": None,
    }

    try:

        # =====================================================
        # CLEAN BUILD DIRECTORY
        # =====================================================
        if build_dir.exists():
            shutil.rmtree(build_dir)

        build_dir.mkdir(parents=True, exist_ok=True)

        # =====================================================
        # FIX: Safe environment (prevents CC=C issue)
        # =====================================================
        env = os.environ.copy()
        env["CC"] = "/usr/bin/gcc"
        env["CXX"] = "/usr/bin/g++"

        # =====================================================
        # BUILD CMAKE COMMAND
        # =====================================================
        command = [
            cmake_exe,
            "-S",
            str(repo_root),
            "-B",
            str(build_dir),
            "-G",
            generator,
            "-DAST_ANALYSIS=ON",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
        ]

        # =====================================================
        # FIX: Only inject compiler if valid path exists
        # =====================================================
        if Path(clang_path).exists():
            command.append(f"-DCMAKE_C_COMPILER={clang_path}")

        if Path(clangxx_path).exists():
            command.append(f"-DCMAKE_CXX_COMPILER={clangxx_path}")

        # =====================================================
        # RUN CMAKE CONFIGURE
        # =====================================================
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

        # =====================================================
        # VERIFY OUTPUT
        # =====================================================
        if not compile_db_path.exists():
            artifact["status"] = "failed"
            artifact["error"] = "compile_commands.json not generated"
            return artifact

        artifact["status"] = "success"
        return artifact

    except subprocess.CalledProcessError as e:

        artifact["status"] = "failed"
        artifact["error"] = (
            e.stderr
            or e.stdout
            or str(e)
        )
        return artifact

    except Exception as e:

        artifact["status"] = "failed"
        artifact["error"] = str(e)
        return artifact
