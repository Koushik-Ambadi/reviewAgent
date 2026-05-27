# src/repo_review/compilation/runner.py
from .generator import generate_compile_commands


def run_compilation_stage(
    source_root,
    analysis_dir,
    config,
):



    result = generate_compile_commands(
        source_root=source_root,
        analysis_dir=analysis_dir,
        config=config,
    )


    return result