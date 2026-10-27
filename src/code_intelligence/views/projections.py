from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from code_intelligence.graph import KnowledgeGraph
from code_intelligence.models import (
    EdgeKind,
    GraphEdge,
    GraphNode,
    NodeKind,
    RelationResolution,
)


@dataclass(frozen=True, slots=True)
class GraphProjection:
    kind: str
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]

    @property
    def unresolved_edges(self) -> int:
        return sum(
            edge.resolution == RelationResolution.UNRESOLVED for edge in self.edges
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "summary": {
                "nodes": len(self.nodes),
                "edges": len(self.edges),
                "unresolved_edges": self.unresolved_edges,
            },
        }


def call_graph(graph: KnowledgeGraph) -> GraphProjection:
    return _projection(
        graph,
        name="call_graph",
        node_kind=NodeKind.FUNCTION,
        edge_kind=EdgeKind.CALLS,
    )


def include_graph(graph: KnowledgeGraph) -> GraphProjection:
    return _projection(
        graph,
        name="include_graph",
        node_kind=NodeKind.FILE,
        edge_kind=EdgeKind.INCLUDES,
    )


def _projection(
    graph: KnowledgeGraph,
    *,
    name: str,
    node_kind: NodeKind,
    edge_kind: EdgeKind,
) -> GraphProjection:
    graph.validate()
    edges = tuple(edge for edge in graph.edges if edge.kind == edge_kind)
    endpoint_ids = {
        identity for edge in edges for identity in (edge.source, edge.target)
    }
    nodes = tuple(
        node
        for node in graph.nodes
        if node.kind == node_kind and node.id in endpoint_ids
    )
    return GraphProjection(kind=name, nodes=nodes, edges=edges)
