# src/repo_review/analysis/runner.py
from pathlib import Path

from .source_index.generator import (
    build_source_index,
)

from .symbol_inventory.extractor import (
    build_symbol_inventory,
)


def run_analysis(
    repo_root: Path,
    workspace_path: Path,
    policy: dict,
) -> dict:

    analysis_dir = (
        workspace_path / "analysis"
    )

    analysis_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    compile_result = (
        build_source_index(
            source_root=repo_root,
            analysis_dir=analysis_dir,
            config=policy,
        )
    )

    if (
        compile_result["status"]
        != "success"
    ):
        return {
            "status": "failed",
            "stage": "source_index",
            "error": compile_result.get(
                "error"
            ),
        }

    compile_db_path = Path(
        compile_result["compile_db_path"]
    )

    symbols_path = (
        analysis_dir
        / "symbols.json"
    )

    symbol_result = (
        build_symbol_inventory(
            source_root=repo_root,
            compile_db_path=compile_db_path,
            output_path=symbols_path,
            policy=policy,
        )
    )

    if (
        symbol_result["status"]
        != "success"
    ):
        return {
            "status": "failed",
            "stage": "symbol_inventory",
            "error": symbol_result.get(
                "error"
            ),
        }

    return {
        "status": "success",
        "analysis_path": analysis_dir,
    }