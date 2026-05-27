# src/repo_review/compilation/generator.py
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


def generate_compile_commands(
    source_root: Path,
    analysis_dir: Path,
    config: dict[str, Any],
) -> dict[str, Any]:

    compilation_config = config.get("compilation", {})
    ast_config = config.get("ast", {})



    build_dir = analysis_dir / "cmake_build"

    output_dir = analysis_dir

    compile_db_path = output_dir / "compile_commands.json"



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
        "output_dir": str(output_dir),
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

        output_dir.mkdir(
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



        generated_db = build_dir / "compile_commands.json"



        if not generated_db.exists():

            artifact["status"] = "failed"

            artifact["error"] = (
                "compile_commands.json not generated"
            )



            return artifact

        shutil.copy2(
            generated_db,
            compile_db_path,
        )



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