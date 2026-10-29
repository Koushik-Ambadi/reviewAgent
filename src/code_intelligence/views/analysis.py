from __future__ import annotations

from collections import defaultdict

from code_intelligence.graph import KnowledgeGraph
from code_intelligence.identity import edge_id
from code_intelligence.models import (
    EdgeKind,
    GraphEdge,
    NodeKind,
    RelationResolution,
)

from .projections import GraphProjection


_VARIABLE_KINDS = {
    NodeKind.GLOBAL_VARIABLE,
    NodeKind.PARAMETER,
    NodeKind.LOCAL_VARIABLE,
    NodeKind.FIELD,
}


def variable_access_graph(graph: KnowledgeGraph) -> GraphProjection:
    graph.validate()
    access_kinds = {EdgeKind.READS, EdgeKind.WRITES, EdgeKind.REFERENCES}
    edges = tuple(edge for edge in graph.edges if edge.kind in access_kinds)
    endpoints = {value for edge in edges for value in (edge.source, edge.target)}
    nodes = tuple(node for node in graph.nodes if node.id in endpoints)
    return GraphProjection(
        kind="variable_access_graph",
        nodes=nodes,
        edges=edges,
        metadata={
            "access_counts": {
                kind.value: sum(edge.kind == kind for edge in edges)
                for kind in sorted(access_kinds, key=lambda item: item.value)
            },
            "classification": "conservative_ast_context_v1",
        },
    )


def exact_clone_graph(graph: KnowledgeGraph) -> GraphProjection:
    graph.validate()
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    nodes_by_id = {node.id: node for node in graph.nodes}
    for node in graph.nodes:
        fingerprint = node.attributes.get("token_fingerprint")
        method = node.attributes.get("token_fingerprint_method")
        if node.kind == NodeKind.FUNCTION and fingerprint and method:
            groups[(str(method), str(fingerprint))].append(node.id)

    clone_groups = [sorted(group) for group in groups.values() if len(group) > 1]
    edges = []
    for group in sorted(clone_groups):
        representative = group[0]
        for duplicate in group[1:]:
            edges.append(
                GraphEdge(
                    id=edge_id(
                        EdgeKind.CLONE_OF,
                        source=duplicate,
                        target=representative,
                    ),
                    kind=EdgeKind.CLONE_OF,
                    source=duplicate,
                    target=representative,
                    resolution=RelationResolution.COMPILER_DERIVED,
                    attributes={"method": "exact_function_tokens_v1"},
                )
            )
    endpoint_ids = {value for edge in edges for value in (edge.source, edge.target)}
    return GraphProjection(
        kind="exact_clone_graph",
        nodes=tuple(nodes_by_id[identity] for identity in sorted(endpoint_ids)),
        edges=tuple(edges),
        metadata={"clone_groups": sorted(clone_groups)},
    )


def complexity_graph(graph: KnowledgeGraph) -> GraphProjection:
    graph.validate()
    nodes = tuple(
        node
        for node in graph.nodes
        if node.kind == NodeKind.FUNCTION
        and "cyclomatic_complexity" in node.attributes
    )
    metrics = {
        node.id: {
            "cyclomatic_complexity": node.attributes["cyclomatic_complexity"],
            "statement_count": node.attributes.get("statement_count"),
            "method": node.attributes.get("complexity_method"),
        }
        for node in nodes
    }
    return GraphProjection(
        kind="complexity_graph",
        nodes=nodes,
        edges=(),
        metadata={"metrics_by_function": metrics},
    )


def memory_estimate_graph(graph: KnowledgeGraph) -> GraphProjection:
    graph.validate()
    sized = {
        node.id: int(node.attributes["size_bytes"])
        for node in graph.nodes
        if node.kind in _VARIABLE_KINDS and "size_bytes" in node.attributes
    }
    relevant_edges = tuple(
        edge
        for edge in graph.edges
        if edge.kind in {EdgeKind.CONTAINS, EdgeKind.PARAMETER_OF, EdgeKind.FIELD_OF}
        and edge.target in sized
    )
    endpoint_ids = set(sized)
    endpoint_ids.update(edge.source for edge in relevant_edges)
    nodes_by_id = {node.id: node for node in graph.nodes}
    local_storage: dict[str, int] = defaultdict(int)
    for edge in relevant_edges:
        if nodes_by_id[edge.source].kind == NodeKind.FUNCTION:
            local_storage[edge.source] += sized[edge.target]
    globals_total = sum(
        size
        for identity, size in sized.items()
        if nodes_by_id[identity].kind == NodeKind.GLOBAL_VARIABLE
    )
    unknown = sorted(
        node.id
        for node in graph.nodes
        if node.kind in _VARIABLE_KINDS and node.id not in sized
    )
    return GraphProjection(
        kind="memory_estimate_graph",
        nodes=tuple(nodes_by_id[identity] for identity in sorted(endpoint_ids)),
        edges=relevant_edges,
        metadata={
            "size_bytes_by_symbol": dict(sorted(sized.items())),
            "global_storage_estimate_bytes": globals_total,
            "local_and_parameter_storage_estimate_by_function": dict(
                sorted(local_storage.items())
            ),
            "unknown_size_symbols": unknown,
            "authority": "type_size_estimate_not_linker_or_stack_evidence",
        },
    )
