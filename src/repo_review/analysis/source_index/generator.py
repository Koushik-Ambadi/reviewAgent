# src/repo_review/analysis/source_index/generator.py
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


def build_source_index(
    source_root: Path,
    analysis_dir: Path,
    config: dict[str, Any],
) -> dict[str, Any]:

    compilation_config = config.get("compilation", {})
    ast_config = config.get("ast", {})



    build_dir = analysis_dir / "cmake_build"

    compile_db_path = (
        build_dir /
        "compile_commands.json"
    )



    cmake_exe = compilation_config.get(
        "cmake_exe",
        "cmake",
    )

    generator = compilation_config.get(
        "generator",
        "Ninja",
    )

    clang_path = ast_config.get(
        "clang_path",
        r"C:/Program Files/LLVM/bin/clang.exe",
    )

    clangxx_path = ast_config.get(
        "clangxx_path",
        r"C:/Program Files/LLVM/bin/clang++.exe",
    )

    artifact = {
        "status": "pending",
        "source_root": str(source_root),
        "build_dir": str(build_dir),
        "compile_db_path": str(compile_db_path),
        "generator": generator,
        "error": None,
    }

    try:

        # =====================================================
        # CLEAN
        # =====================================================

        if build_dir.exists():
            shutil.rmtree(build_dir)

        build_dir.mkdir(
            parents=True,
            exist_ok=True,
        )




        # =====================================================
        # CMAKE CONFIGURE
        # =====================================================

        command = [
            cmake_exe,
            "-S",
            str(source_root),
            "-B",
            str(build_dir),
            "-G",
            generator,
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




        if not compile_db_path.exists():

            artifact["status"] = "failed"

            artifact["error"] = (
                "compile_commands.json not generated"
            )



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