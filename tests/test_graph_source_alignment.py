from __future__ import annotations

import json
from pathlib import Path

from scripts.verify_graph_source_alignment import verify_graph_source_alignment


def test_alignment_distinguishes_repeated_relations_from_duplicate_occurrences(
    tmp_path: Path,
):
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "sample.c").write_text(
        "int signal;\nint run(void) { return signal + signal; }\n",
        encoding="utf-8",
    )
    graph = {
        "nodes": [
            {"id": "fn:run", "kind": "function", "name": "run"},
            {"id": "fn:helper", "kind": "function", "name": "helper"},
            {"id": "global:signal", "kind": "global_variable", "name": "signal"},
        ],
        "edges": [
            {
                "id": "read:1",
                "kind": "reads",
                "source": "fn:run",
                "target": "global:signal",
                "location": {"path": "sample.c", "line": 2, "column": 24},
            },
            {
                "id": "read:2",
                "kind": "reads",
                "source": "fn:run",
                "target": "global:signal",
                "location": {"path": "sample.c", "line": 2, "column": 33},
            },
            {
                "id": "call:macro",
                "kind": "calls",
                "source": "fn:run",
                "target": "fn:helper",
                "location": {"path": "sample.c", "line": 1, "column": 1},
            },
        ],
    }
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(graph), encoding="utf-8")

    result = verify_graph_source_alignment(graph_path, source_root)

    assert result["consistent"] is True
    assert result["exact_duplicate_occurrences"] == []
    assert result["repeated_relations"][0]["count"] == 2
    assert result["notes"][0]["code"] == "call_target_not_textual"
