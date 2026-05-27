# src/repo_review/compilation/runner.py

from .generator import generate_compile_commands


def run_compilation_stage(source_root, config):
    return generate_compile_commands(
        source_root=source_root,
        config=config,
    )