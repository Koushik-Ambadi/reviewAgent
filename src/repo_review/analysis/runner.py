# src/repo_review/analysis/runner.py


from pathlib import Path

from ..contracts import (
    InventoryItem,
    InventorySummary,
    StageResult,
    StageSummary,
    StageStatus,
)

from .source_index.generator import build_source_index
from .symbol_inventory.extractor import build_symbol_inventory


INVENTORY_FIELDS = (
    ("function_definitions", "Function definitions", "functions_defined"),
    ("function_declarations", "Function declarations", "functions_declared"),
    ("global_variables", "Global variables", "globals"),
    ("local_variables", "Local variables", "locals"),
    ("parameters", "Parameters", "parameters"),
    ("structures", "Structures", "structs"),
    ("enumerations", "Enumerations", "enums"),
    ("typedefs", "Type definitions", "typedefs"),
    ("macros", "Macros", "macros"),
)


def summarize_symbol_inventory(
    symbols: list[dict],
    skipped_files: list[dict] | None = None,
) -> InventorySummary:
    items = [
        InventoryItem(
            inventory_id=inventory_id,
            label=label,
            identified=sum(len(file_symbols.get(field) or []) for file_symbols in symbols),
        )
        for inventory_id, label, field in INVENTORY_FIELDS
    ]
    items.insert(
        7,
        InventoryItem(
            inventory_id="enum_constants",
            label="Enum constants",
            identified=sum(
                len(enum.get("constants") or [])
                for file_symbols in symbols
                for enum in file_symbols.get("enums") or []
            ),
        )
    )
    return InventorySummary(
        parsed_files=len(symbols),
        skipped_files=len(skipped_files or []),
        items=items,
    )


def run_analysis(
    repo_root: Path,
    workspace_path: Path,
    policy: dict,
) -> StageResult:

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

    return StageResult(
        title="Analysis",
        stage_id="analysis",
        status=StageStatus.COMPLETED,
        summary=StageSummary(),
        inventory=summarize_symbol_inventory(
            symbol_result["results"],
            symbol_result.get("skipped_files"),
        ),
    )
