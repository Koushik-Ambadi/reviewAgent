from __future__ import annotations

from code_intelligence.graph import KnowledgeGraph
from code_intelligence.models import (
    EdgeKind,
    GraphEdge,
    GraphNode,
    NodeKind,
    RelationResolution,
)
from code_intelligence.views import (
    call_depth_graph,
    dependency_impact_graph,
    module_dependency_graph,
    reachability_graph,
)


def _node(identity: str, kind: NodeKind, name: str) -> GraphNode:
    return GraphNode(id=identity, kind=kind, name=name)


def _edge(identity: str, kind: EdgeKind, source: str, target: str) -> GraphEdge:
    return GraphEdge(
        id=identity,
        kind=kind,
        source=source,
        target=target,
        resolution=RelationResolution.COMPILER_DERIVED,
    )


def _graph() -> KnowledgeGraph:
    graph = KnowledgeGraph()
    for node in (
        _node("file:main", NodeKind.FILE, "main.c"),
        _node("file:service", NodeKind.FILE, "service.c"),
        _node("file:unused", NodeKind.FILE, "unused.c"),
        _node("fn:main", NodeKind.FUNCTION, "main"),
        _node("fn:run", NodeKind.FUNCTION, "run"),
        _node("fn:a", NodeKind.FUNCTION, "a"),
        _node("fn:b", NodeKind.FUNCTION, "b"),
        _node("fn:unused", NodeKind.FUNCTION, "unused"),
    ):
        graph.add_node(node)
    for edge in (
        _edge("contains:main", EdgeKind.CONTAINS, "file:main", "fn:main"),
        _edge("contains:run", EdgeKind.CONTAINS, "file:main", "fn:run"),
        _edge("contains:a", EdgeKind.CONTAINS, "file:service", "fn:a"),
        _edge("contains:b", EdgeKind.CONTAINS, "file:service", "fn:b"),
        _edge("contains:unused", EdgeKind.CONTAINS, "file:unused", "fn:unused"),
        _edge("include:service", EdgeKind.INCLUDES, "file:main", "file:service"),
        _edge("call:main-run", EdgeKind.CALLS, "fn:main", "fn:run"),
        _edge("call:run-a", EdgeKind.CALLS, "fn:run", "fn:a"),
        _edge("call:a-b", EdgeKind.CALLS, "fn:a", "fn:b"),
        _edge("call:b-a", EdgeKind.CALLS, "fn:b", "fn:a"),
    ):
        graph.add_edge(edge)
    return graph


def test_reachability_marks_disconnected_functions():
    projection = reachability_graph(_graph(), roots=["fn:main"])

    assert projection.metadata["reachable"] == [
        "fn:a",
        "fn:b",
        "fn:main",
        "fn:run",
    ]
    assert projection.metadata["unreachable"] == ["fn:unused"]


def test_call_depth_condenses_recursive_components():
    projection = call_depth_graph(_graph(), roots=["fn:main"])

    assert projection.metadata["maximum_depth"] == 2
    assert projection.metadata["recursive_components"] == [["fn:a", "fn:b"]]
    assert projection.metadata["depth_by_node"]["fn:main"] == 0
    assert projection.metadata["depth_by_node"]["fn:run"] == 1


def test_module_dependency_uses_files_as_initial_modules():
    projection = module_dependency_graph(_graph())

    assert [edge.kind for edge in projection.edges] == [EdgeKind.DEPENDS_ON]
    assert projection.edges[0].source == "file:main"
    assert projection.edges[0].target == "file:service"
    assert projection.edges[0].attributes["evidence_kinds"] == ["calls", "includes"]
    assert projection.metadata["grouping"] == "file_as_module"


def test_dependency_impact_walks_callers_and_file_dependencies():
    projection = dependency_impact_graph(_graph(), changed_nodes=["fn:a"])

    assert projection.metadata["changed"] == ["fn:a"]
    assert "fn:run" in projection.metadata["directly_impacted"]
    assert "fn:main" in projection.metadata["transitively_impacted"]
    assert "file:main" in projection.metadata["transitively_impacted"]


def test_derived_views_reject_invalid_roots_and_changes():
    graph = _graph()
    for action in (
        lambda: reachability_graph(graph, roots=[]),
        lambda: call_depth_graph(graph, roots=["file:main"]),
        lambda: dependency_impact_graph(graph, changed_nodes=["missing"]),
    ):
        try:
            action()
        except ValueError:
            pass
        else:
            raise AssertionError("Expected invalid projection input to fail")
