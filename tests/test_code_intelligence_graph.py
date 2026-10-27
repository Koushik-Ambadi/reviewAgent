from __future__ import annotations

import json
from pathlib import Path

from code_intelligence.graph import GraphConflictError, KnowledgeGraph
from code_intelligence.models import (
    EdgeKind,
    GraphEdge,
    GraphFragment,
    GraphNode,
    NodeKind,
    RelationResolution,
    SourceLocation,
)
from code_intelligence.storage import canonical_snapshot_bytes, write_snapshot
from code_intelligence.views import call_graph, include_graph


def _node(
    identity: str,
    kind: NodeKind,
    name: str,
    *,
    definition: bool | None = None,
    line: int = 1,
) -> GraphNode:
    return GraphNode(
        id=identity,
        kind=kind,
        name=name,
        location=SourceLocation("src/control.c", line=line),
        is_definition=definition,
    )


def _edge(
    identity: str,
    kind: EdgeKind,
    source: str,
    target: str,
    *,
    resolution: RelationResolution = RelationResolution.COMPILER_DERIVED,
) -> GraphEdge:
    return GraphEdge(
        id=identity,
        kind=kind,
        source=source,
        target=target,
        resolution=resolution,
        location=SourceLocation("src/control.c", line=10),
    )


def _fragments() -> tuple[GraphFragment, GraphFragment]:
    file_node = _node("file:control", NodeKind.FILE, "control.c")
    header_node = _node("file:header", NodeKind.FILE, "control.h")
    declaration = _node(
        "function:step", NodeKind.FUNCTION, "step", definition=False, line=2
    )
    definition = _node(
        "function:step", NodeKind.FUNCTION, "step", definition=True, line=8
    )
    callee = _node(
        "function:read", NodeKind.FUNCTION, "read_sensor", definition=True
    )
    first = GraphFragment(
        translation_unit="src/control.c",
        nodes=[file_node, header_node, declaration, callee],
        edges=[
            _edge("include:1", EdgeKind.INCLUDES, file_node.id, header_node.id),
            _edge("call:1", EdgeKind.CALLS, declaration.id, callee.id),
        ],
    )
    second = GraphFragment(
        translation_unit="src/other.c",
        nodes=[definition, callee],
        edges=[
            _edge(
                "call:2",
                EdgeKind.CALLS,
                definition.id,
                callee.id,
                resolution=RelationResolution.UNRESOLVED,
            )
        ],
    )
    return first, second


def test_graph_merge_prefers_definition_and_projects_views():
    graph = KnowledgeGraph.from_fragments(_fragments())

    step = next(node for node in graph.nodes if node.id == "function:step")
    assert step.is_definition is True
    assert step.location.line == 8
    assert graph.translation_units == ("src/control.c", "src/other.c")

    calls = call_graph(graph)
    includes = include_graph(graph)
    assert len(calls.nodes) == 2
    assert len(calls.edges) == 2
    assert calls.unresolved_edges == 1
    assert len(includes.nodes) == 2
    assert len(includes.edges) == 1


def test_graph_rejects_conflicting_identity():
    graph = KnowledgeGraph()
    graph.add_node(_node("function:same", NodeKind.FUNCTION, "first"))

    try:
        graph.add_node(_node("function:same", NodeKind.FUNCTION, "second"))
    except GraphConflictError as error:
        assert "Node identity conflict" in str(error)
    else:
        raise AssertionError("Expected a stable-identity conflict")


def test_graph_rejects_dangling_edges():
    graph = KnowledgeGraph()
    graph.add_node(_node("function:source", NodeKind.FUNCTION, "source"))
    graph.add_edge(
        _edge("call:dangling", EdgeKind.CALLS, "function:source", "function:missing")
    )

    try:
        graph.validate()
    except GraphConflictError as error:
        assert "missing endpoints" in str(error)
    else:
        raise AssertionError("Expected dangling-edge validation failure")


def test_snapshot_is_atomic_and_deterministic(tmp_path: Path):
    graph = KnowledgeGraph.from_fragments(_fragments())
    provenance = {
        "source_revision": "abc123",
        "dirty": False,
        "producer": "code_intelligence",
        "producer_version": "0.1.0",
    }
    expected = canonical_snapshot_bytes(graph, provenance=provenance)
    output = tmp_path / "knowledge-graph.json"

    write_snapshot(graph, output, provenance=provenance)
    first = output.read_bytes()
    write_snapshot(graph, output, provenance=provenance)
    second = output.read_bytes()

    assert first == second == expected
    assert not output.with_suffix(".json.tmp").exists()
    payload = json.loads(first)
    assert payload["schema_version"] == "1.1"
    assert payload["provenance"]["source_revision"] == "abc123"


def test_snapshot_requires_replay_provenance():
    graph = KnowledgeGraph.from_fragments(_fragments())

    try:
        canonical_snapshot_bytes(graph, provenance={"source_revision": "abc123"})
    except ValueError as error:
        assert "dirty" in str(error)
        assert "producer_version" in str(error)
    else:
        raise AssertionError("Expected missing-provenance validation failure")
