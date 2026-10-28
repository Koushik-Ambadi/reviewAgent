from __future__ import annotations

import json
from pathlib import Path

from app.services.graph_service import (
    get_graph_catalog,
    get_inter_module_graph,
    get_run_graph,
)
import orchestrator.run_store as run_store


def _node(
    identity: str,
    kind: str,
    name: str,
    *,
    path: str,
    definition: bool | None = None,
) -> dict:
    return {
        "id": identity,
        "kind": kind,
        "name": name,
        "location": {"path": path, "line": 1},
        "is_definition": definition,
        "attributes": {
            "path": path,
            "external": False,
        }
        if kind == "file"
        else {"external": False},
    }


def _edge(identity: str, kind: str, source: str, target: str) -> dict:
    return {
        "id": identity,
        "kind": kind,
        "source": source,
        "target": target,
        "resolution": "compiler_derived",
        "attributes": {},
    }


def _write_run(
    root: Path,
    run_id: str,
    module_name: str,
    nodes: list[dict],
    edges: list[dict],
) -> None:
    run = root / run_id
    analysis = run / "analysis"
    analysis.mkdir(parents=True)
    (run / "report.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "metadata": {
                    "module_name": module_name,
                    "generated_at": "2026-10-28T00:00:00+00:00",
                },
            }
        ),
        encoding="utf-8",
    )
    (analysis / "code-intelligence.json").write_text(
        json.dumps(
            {
                "schema_version": "1.1",
                "nodes": nodes,
                "edges": edges,
                "provenance": {"source_revision": "fixture"},
            }
        ),
        encoding="utf-8",
    )


def test_run_graph_supports_file_and_module_scopes(tmp_path: Path):
    file_a = _node("file:a", "file", "a.c", path="src/a.c")
    file_b = _node("file:b", "file", "b.c", path="src/b.c")
    function_a = _node(
        "fn:a", "function", "step_a", path="src/a.c", definition=True
    )
    function_b = _node(
        "fn:b", "function", "step_b", path="src/b.c", definition=True
    )
    signal = _node(
        "global:signal",
        "global_variable",
        "signal",
        path="src/b.c",
        definition=True,
    )
    nodes = [file_a, file_b, function_a, function_b, signal]
    edges = [
        _edge("owns:a", "contains", "file:a", "fn:a"),
        _edge("owns:b", "contains", "file:b", "fn:b"),
        _edge("owns:signal", "contains", "file:b", "global:signal"),
        _edge("call", "calls", "fn:a", "fn:b"),
        _edge("read", "reads", "fn:a", "global:signal"),
    ]
    _write_run(tmp_path, "run-a", "module-a", nodes, edges)
    original_root = run_store.WORKSPACE_ROOT
    run_store.WORKSPACE_ROOT = tmp_path
    try:
        file_graph = get_run_graph(
            "run-a",
            scope="file",
            selected_file="src/a.c",
            layers=["calls", "reads"],
        )
        module_graph = get_run_graph(
            "run-a", scope="module", layers=["calls", "reads"]
        )
    finally:
        run_store.WORKSPACE_ROOT = original_root

    assert file_graph["selected_file"] == "src/a.c"
    assert {edge["kind"] for edge in file_graph["edges"]} >= {
        "calls",
        "reads",
    }
    assert {node["label"] for node in module_graph["nodes"]} == {"a.c", "b.c"}
    assert {(edge["kind"], edge["count"]) for edge in module_graph["edges"]} == {
        ("calls", 1),
        ("reads", 1),
    }
    call_edge = next(edge for edge in module_graph["edges"] if edge["kind"] == "calls")
    assert call_edge["interactions"] == [
        {
            "source_id": "fn:a",
            "source_label": "step_a",
            "source_kind": "function",
            "target_id": "fn:b",
            "target_label": "step_b",
            "target_kind": "function",
            "path": "",
            "line": None,
        }
    ]


def test_inter_module_graph_reports_signal_direction(tmp_path: Path):
    consumer_nodes = [
        _node("file:consumer", "file", "consumer.c", path="src/consumer.c"),
        _node(
            "fn:consumer",
            "function",
            "consume",
            path="src/consumer.c",
            definition=True,
        ),
        _node(
            "global:shared",
            "global_variable",
            "shared_signal",
            path="shared.h",
            definition=False,
        ),
    ]
    producer_nodes = [
        _node("file:producer", "file", "producer.c", path="src/producer.c"),
        _node(
            "global:shared",
            "global_variable",
            "shared_signal",
            path="src/producer.c",
            definition=True,
        ),
    ]
    _write_run(
        tmp_path,
        "run-consumer",
        "consumer",
        consumer_nodes,
        [_edge("read", "reads", "fn:consumer", "global:shared")],
    )
    _write_run(tmp_path, "run-producer", "producer", producer_nodes, [])

    graph = get_inter_module_graph(
        workspace_root=tmp_path,
        layers=["reads", "writes"],
    )

    assert graph["summary"] == {
        "modules": 2,
        "relationships": 1,
        "signal_names": 1,
    }
    assert graph["edges"][0]["source"] == "consumer"
    assert graph["edges"][0]["target"] == "producer"
    assert graph["edges"][0]["signals"] == ["shared_signal"]
    consumer = next(node for node in graph["nodes"] if node["id"] == "consumer")
    producer = next(node for node in graph["nodes"] if node["id"] == "producer")
    assert consumer["inputs"] == ["shared_signal"]
    assert producer["outputs"] == ["shared_signal"]
    catalog = get_graph_catalog(workspace_root=tmp_path)
    assert catalog["count"] == 2
    assert [item["module_name"] for item in catalog["modules"]] == [
        "consumer",
        "producer",
    ]
