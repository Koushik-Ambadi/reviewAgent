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
    complexity_graph,
    exact_clone_graph,
    memory_estimate_graph,
    variable_access_graph,
)


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
        GraphNode(
            id="fn:a",
            kind=NodeKind.FUNCTION,
            name="a",
            attributes={
                "complexity_method": "ast_cyclomatic_v1",
                "cyclomatic_complexity": 3,
                "statement_count": 7,
                "token_fingerprint_method": "clang_tokens_sha256_v1",
                "token_fingerprint": "same",
            },
        ),
        GraphNode(
            id="fn:b",
            kind=NodeKind.FUNCTION,
            name="b",
            attributes={
                "complexity_method": "ast_cyclomatic_v1",
                "cyclomatic_complexity": 3,
                "statement_count": 7,
                "token_fingerprint_method": "clang_tokens_sha256_v1",
                "token_fingerprint": "same",
            },
        ),
        GraphNode(
            id="global:state",
            kind=NodeKind.GLOBAL_VARIABLE,
            name="state",
            attributes={"size_bytes": 4},
        ),
        GraphNode(
            id="local:next",
            kind=NodeKind.LOCAL_VARIABLE,
            name="next",
            attributes={"size_bytes": 2},
        ),
        GraphNode(
            id="param:request",
            kind=NodeKind.PARAMETER,
            name="request",
            attributes={"size_bytes": 1},
        ),
        GraphNode(
            id="field:unknown",
            kind=NodeKind.FIELD,
            name="unknown",
        ),
    ):
        graph.add_node(node)
    for edge in (
        _edge("contains", EdgeKind.CONTAINS, "fn:a", "local:next"),
        _edge("parameter", EdgeKind.PARAMETER_OF, "fn:a", "param:request"),
        _edge("read", EdgeKind.READS, "fn:a", "global:state"),
        _edge("write", EdgeKind.WRITES, "fn:a", "local:next"),
    ):
        graph.add_edge(edge)
    return graph


def test_variable_access_graph_reports_typed_accesses():
    projection = variable_access_graph(_graph())

    assert {edge.kind for edge in projection.edges} == {
        EdgeKind.READS,
        EdgeKind.WRITES,
    }
    assert projection.metadata["access_counts"] == {
        "reads": 1,
        "references": 0,
        "writes": 1,
    }


def test_exact_clone_graph_groups_matching_function_bodies():
    projection = exact_clone_graph(_graph())

    assert len(projection.edges) == 1
    assert projection.edges[0].kind == EdgeKind.CLONE_OF
    assert projection.metadata["clone_groups"] == [["fn:a", "fn:b"]]


def test_complexity_graph_retains_metric_method():
    projection = complexity_graph(_graph())

    assert projection.metadata["metrics_by_function"]["fn:a"] == {
        "cyclomatic_complexity": 3,
        "statement_count": 7,
        "method": "ast_cyclomatic_v1",
    }


def test_memory_graph_is_explicitly_an_estimate():
    projection = memory_estimate_graph(_graph())

    assert projection.metadata["global_storage_estimate_bytes"] == 4
    assert projection.metadata["local_and_parameter_storage_estimate_by_function"] == {
        "fn:a": 3
    }
    assert projection.metadata["unknown_size_symbols"] == ["field:unknown"]
    assert projection.metadata["authority"].endswith("not_linker_or_stack_evidence")
