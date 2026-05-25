# src/repo_review/ast_compile_db.py

from __future__ import annotations

import subprocess
import shutil
from pathlib import Path


def generate_compile_db(
    source_dir: str,
    build_dir: str,
    output_dir: str,
    generator: str = "Ninja",
    cmake_exe: str = "cmake",
) -> Path:
    """
    Generates compile_commands.json using Clang ONLY (AST analysis mode).
    Does NOT touch firmware toolchain.
    """

    source_dir = Path(source_dir).resolve()
    build_dir = Path(build_dir).resolve()
    output_dir = Path(output_dir).resolve()

    # ----------------------------
    # IMPORTANT: clean build state
    # ----------------------------
    if build_dir.exists():
        shutil.rmtree(build_dir)

    build_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[AST] Clean configure: {build_dir}")

    clang = r"C:/Program Files/LLVM/bin/clang.exe"
    clangxx = r"C:/Program Files/LLVM/bin/clang++.exe"

    # ----------------------------
    # FORCE CLEAN CMAKE CONFIGURE
    # ----------------------------
    subprocess.run(
        [
            "cmake",
            "-S", str(source_dir),
            "-B", str(build_dir),
            "-G", "Ninja",

            "-DAST_ANALYSIS=ON",

            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            "-DCMAKE_C_COMPILER=C:/Program Files/LLVM/bin/clang.exe",
            "-DCMAKE_CXX_COMPILER=C:/Program Files/LLVM/bin/clang++.exe",
        ],
        check=True,
    )
    compile_db = build_dir / "compile_commands.json"

    if not compile_db.exists():
        raise RuntimeError(
            f"compile_commands.json not generated at {compile_db}"
        )

    # ----------------------------
    # COPY OUTPUT (your pipeline)
    # ----------------------------
    target = output_dir / "compile_commands.json"
    shutil.copy2(compile_db, target)

    print(f"[AST] compile_commands.json -> {target}")

    return target


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--out", required=True)

    args = parser.parse_args()

    generate_compile_db(args.source, args.build, args.out)