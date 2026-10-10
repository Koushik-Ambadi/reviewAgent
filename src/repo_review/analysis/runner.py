# src/repo_review/analysis/runner.py


from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from ..contracts import (
    InventoryArtifact,
    InventoryItem,
    InventoryAuditSummary,
    InventoryGroup,
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


def _text_evidence(label: str, value) -> str | None:
    if value is None or value == "":
        return None
    return f"{label}: {value}"


def _artifact_evidence(group_id: str, record: dict, parent: str = "") -> list[str]:
    evidence: list[str | None]
    if group_id in {"function_definitions", "function_declarations"}:
        evidence = [
            _text_evidence("Returns", record.get("return_type")),
            _text_evidence("Parameters", record.get("parameter_count")),
            _text_evidence("Storage", record.get("storage_class")),
        ]
    elif group_id in {"global_variables", "local_variables", "structure_fields"}:
        evidence = [
            _text_evidence("Type", record.get("type")),
            _text_evidence("Declaration", record.get("raw_declaration")),
            _text_evidence("Storage", record.get("storage_class")),
            _text_evidence("Member of", parent),
        ]
    elif group_id == "parameters":
        evidence = [_text_evidence("Type", record.get("type"))]
    elif group_id == "structures":
        evidence = [_text_evidence("Fields", len(record.get("fields") or []))]
    elif group_id == "enumerations":
        evidence = [
            _text_evidence("Underlying type", record.get("underlying_type")),
            _text_evidence("Constants", len(record.get("constants") or [])),
        ]
    elif group_id == "enum_constants":
        evidence = [
            _text_evidence("Value", record.get("value")),
            _text_evidence("Member of", parent),
        ]
    elif group_id == "typedefs":
        evidence = [
            _text_evidence("Underlying type", record.get("underlying_type")),
            _text_evidence("Canonical type", record.get("canonical_type")),
        ]
    elif group_id == "macros":
        evidence = [
            _text_evidence("Macro type", record.get("type")),
            _text_evidence("Replacement", record.get("replacement")),
        ]
    else:
        evidence = []
    return [item for item in evidence if item]


def _inventory_artifact(
    group_id: str,
    file_path: str,
    record: dict,
    ordinal: int,
    parent: str = "",
) -> InventoryArtifact:
    name = record.get("name") or f"<anonymous {group_id.rstrip('s')}>"
    display_name = f"{parent}.{name}" if parent else name
    line = record.get("line")
    location = f"{file_path}:{line}" if line else file_path
    identity = f"analysis:{group_id}:{location}:{display_name}:{ordinal}"
    return InventoryArtifact(
        artifact_id=uuid5(NAMESPACE_URL, identity).hex,
        name=display_name,
        location=location,
        evidence=_artifact_evidence(group_id, record, parent),
    )


def _inventory_groups(symbols: list[dict]) -> list[InventoryGroup]:
    grouped: dict[str, list[InventoryArtifact]] = {
        group_id: [] for group_id, _, _ in INVENTORY_FIELDS
    }
    grouped["structure_fields"] = []
    grouped["enum_constants"] = []

    for file_symbols in symbols:
        file_path = file_symbols.get("file") or "unknown source"
        for group_id, _, field in INVENTORY_FIELDS:
            for ordinal, record in enumerate(file_symbols.get(field) or []):
                grouped[group_id].append(
                    _inventory_artifact(group_id, file_path, record, ordinal)
                )
                if group_id == "structures":
                    parent = record.get("name") or "<anonymous struct>"
                    for field_ordinal, field_record in enumerate(record.get("fields") or []):
                        grouped["structure_fields"].append(
                            _inventory_artifact(
                                "structure_fields",
                                file_path,
                                field_record,
                                field_ordinal,
                                parent,
                            )
                        )
                elif group_id == "enumerations":
                    parent = record.get("name") or "<anonymous enum>"
                    for constant_ordinal, constant in enumerate(record.get("constants") or []):
                        grouped["enum_constants"].append(
                            _inventory_artifact(
                                "enum_constants",
                                file_path,
                                constant,
                                constant_ordinal,
                                parent,
                            )
                        )

    labels = [
        ("function_definitions", "Function definitions"),
        ("function_declarations", "Function declarations"),
        ("global_variables", "Global variables"),
        ("local_variables", "Local variables"),
        ("parameters", "Parameters"),
        ("structures", "Structures"),
        ("structure_fields", "Structure fields"),
        ("enumerations", "Enumerations"),
        ("enum_constants", "Enum constants"),
        ("typedefs", "Type definitions"),
        ("macros", "Macros"),
    ]
    return [
        InventoryGroup(group_id=group_id, label=label, artifacts=grouped[group_id])
        for group_id, label in labels
    ]


def summarize_symbol_inventory(
    symbols: list[dict],
    skipped_files: list[dict] | None = None,
) -> InventorySummary:
    groups = _inventory_groups(symbols)
    items = [
        InventoryItem(
            inventory_id=group.group_id,
            label=group.label,
            identified=len(group.artifacts),
        )
        for group in groups
    ]
    identified = sum(item.identified for item in items)
    return InventorySummary(
        parsed_files=len(symbols),
        skipped_files=len(skipped_files or []),
        items=items,
        groups=groups,
        audit=InventoryAuditSummary(not_audited=identified),
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
