# src/repo_review/compilation/generator.py

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


def generate_compile_commands(
    source_root: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate compile_commands.json for AST analysis.
    Uses isolated Clang configuration only.
    """

    compilation_config = config.get("compilation", {})
    ast_config = config.get("ast", {})

    build_dir = source_root / compilation_config.get(
        "build_dir",
        "analysis/cmake_build",
    )

    output_dir = source_root / compilation_config.get(
        "output_dir",
        "analysis",
    )

    cmake_exe = compilation_config.get("cmake_exe", "cmake")
    generator = compilation_config.get("generator", "Ninja")

    clang_path = ast_config.get(
        "clang_path",
        r"C:/Program Files/LLVM/bin/clang.exe",
    )

    clangxx_path = ast_config.get(
        "clangxx_path",
        r"C:/Program Files/LLVM/bin/clang++.exe",
    )

    compile_db_path = output_dir / "compile_commands.json"

    artifact = {
        "status": "pending",
        "source_root": str(source_root),
        "build_dir": str(build_dir),
        "output_dir": str(output_dir),
        "compile_db_path": str(compile_db_path),
        "generator": generator,
        "error": None,
    }

    try:
        # ------------------------------------------------
        # CLEAN BUILD
        # ------------------------------------------------

        if build_dir.exists():
            shutil.rmtree(build_dir)

        build_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        # ------------------------------------------------
        # CONFIGURE CMAKE
        # ------------------------------------------------

        command = [
            cmake_exe,
            "-S", str(source_root),
            "-B", str(build_dir),
            "-G", generator,
            "-DAST_ANALYSIS=ON",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            f"-DCMAKE_C_COMPILER={clang_path}",
            f"-DCMAKE_CXX_COMPILER={clangxx_path}",
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

        generated_db = build_dir / "compile_commands.json"

        if not generated_db.exists():
            artifact["status"] = "failed"
            artifact["error"] = (
                f"compile_commands.json not generated at {generated_db}"
            )
            return artifact

        shutil.copy2(generated_db, compile_db_path)

        artifact["status"] = "success"

        return artifact

    except subprocess.CalledProcessError as e:
        artifact["status"] = "failed"
        artifact["error"] = e.stderr or str(e)
        return artifact

    except Exception as e:
        artifact["status"] = "failed"
        artifact["error"] = str(e)
        return artifact