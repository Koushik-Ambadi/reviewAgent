# src/repo_review/analysis/runner.py
from pathlib import Path

from .source_index.generator import build_source_index
from .symbol_inventory.extractor import build_symbol_inventory


def run_analysis(
    repo_root: Path,
    workspace_path: Path,
    policy: dict,
) -> None:
    analysis_dir = workspace_path / "analysis"

    analysis_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    compile_result = build_source_index(
        repo_root=repo_root,
        analysis_dir=analysis_dir,
        config=policy,
    )

    if compile_result["status"] != "success":
        raise RuntimeError(
            compile_result.get("error")
            or "Failed to generate compile_commands.json"
        )

    symbols_path = analysis_dir / "symbols.json"

    symbol_result = build_symbol_inventory(
        repo_root=repo_root,
        analysis_dir=analysis_dir,
        output_path=symbols_path,
        policy=policy,
    )

    if symbol_result["status"] != "success":
        raise RuntimeError(
            symbol_result.get("error")
            or "Failed to generate symbols.json"
        )