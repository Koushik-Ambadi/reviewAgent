from __future__ import annotations

import json
from pathlib import Path

from repo_review.analysis.symbol_inventory import extractor


def test_review_inventory_and_graph_share_translation_unit_parse(
    tmp_path: Path,
):
    repo_root = tmp_path / "repository"
    source_dir = repo_root / "src"
    source_dir.mkdir(parents=True)
    fixture_dir = (
        Path(__file__).parent / "fixtures" / "code_intelligence"
    )
    source = source_dir / "sample.c"
    header = source_dir / "sample.h"
    source.write_text(
        (fixture_dir / "sample.c").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    header.write_text(
        (fixture_dir / "sample.h").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    analysis_dir = tmp_path / "analysis"
    build_dir = analysis_dir / "cmake_build"
    build_dir.mkdir(parents=True)
    compile_commands = [
        {
            "directory": str(repo_root),
            "file": str(source),
            "arguments": [
                "clang",
                f"-I{source_dir}",
                "-c",
                str(source),
            ],
        }
    ]
    (build_dir / "compile_commands.json").write_text(
        json.dumps(compile_commands), encoding="utf-8"
    )

    symbols_path = analysis_dir / "symbols.json"
    parse_calls = 0
    original_parse = extractor.parse_translation_unit

    def counted_parse(*args, **kwargs):
        nonlocal parse_calls
        parse_calls += 1
        return original_parse(*args, **kwargs)

    extractor.parse_translation_unit = counted_parse
    try:
        result = extractor.build_symbol_inventory(
            repo_root=repo_root,
            analysis_dir=analysis_dir,
            output_path=symbols_path,
            policy={
                "ast": {
                    "target_folders": ["src"],
                    "target_extensions": [".c"],
                }
            },
        )
    finally:
        extractor.parse_translation_unit = original_parse

    assert result["status"] == "success"
    assert result["processed_files"] == 1
    assert parse_calls == 1
    assert symbols_path.exists()
    graph_path = Path(result["graph_path"])
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    assert graph["schema_version"] == "1.1"
    assert graph["translation_units"] == ["src/sample.c"]
    assert {node["name"] for node in graph["nodes"]} >= {
        "control_step",
        "duplicate_step",
        "read_state",
        "system_state",
    }
    assert result["graph_nodes"] == len(graph["nodes"])
    assert result["graph_edges"] == len(graph["edges"])
