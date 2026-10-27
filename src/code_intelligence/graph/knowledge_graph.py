from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable

from code_intelligence.models import GraphEdge, GraphFragment, GraphNode


class GraphConflictError(ValueError):
    """Raised when one stable identity describes incompatible graph facts."""


class KnowledgeGraph:
    schema_version = "1.1"

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._translation_units: set[str] = set()
        self._diagnostics: list[str] = []

    @property
    def nodes(self) -> tuple[GraphNode, ...]:
        return tuple(
            sorted(self._nodes.values(), key=lambda node: (node.kind.value, node.id))
        )

    @property
    def edges(self) -> tuple[GraphEdge, ...]:
        return tuple(
            sorted(self._edges.values(), key=lambda edge: (edge.kind.value, edge.id))
        )

    @property
    def translation_units(self) -> tuple[str, ...]:
        return tuple(sorted(self._translation_units))

    @property
    def diagnostics(self) -> tuple[str, ...]:
        return tuple(sorted(set(self._diagnostics)))

    def add_fragment(self, fragment: GraphFragment) -> None:
        self._translation_units.add(fragment.translation_unit)
        self._diagnostics.extend(fragment.diagnostics)
        for node in fragment.nodes:
            self.add_node(node)
        for edge in fragment.edges:
            self.add_edge(edge)

    def add_node(self, node: GraphNode) -> None:
        existing = self._nodes.get(node.id)
        if existing is None:
            self._nodes[node.id] = node
            return
        if existing.kind != node.kind or existing.name != node.name:
            raise GraphConflictError(
                f"Node identity conflict for {node.id}: "
                f"{existing.kind.value}/{existing.name} != "
                f"{node.kind.value}/{node.name}"
            )

        attributes = _merge_attributes(existing.attributes, node.attributes, node.id)
        preferred = _preferred_node(existing, node)
        self._nodes[node.id] = replace(
            preferred,
            usr=preferred.usr or existing.usr or node.usr,
            location=preferred.location or existing.location or node.location,
            is_definition=_merge_definition(
                existing.is_definition, node.is_definition
            ),
            attributes=attributes,
        )

    def add_edge(self, edge: GraphEdge) -> None:
        existing = self._edges.get(edge.id)
        if existing is None:
            self._edges[edge.id] = edge
            return
        if existing != edge:
            raise GraphConflictError(f"Edge identity conflict for {edge.id}")

    def validate(self) -> None:
        dangling = [
            edge.id
            for edge in self._edges.values()
            if edge.source not in self._nodes or edge.target not in self._nodes
        ]
        if dangling:
            raise GraphConflictError(
                "Graph contains edges with missing endpoints: " + ", ".join(dangling)
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "translation_units": list(self.translation_units),
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "diagnostics": list(self.diagnostics),
        }

    @classmethod
    def from_fragments(cls, fragments: Iterable[GraphFragment]) -> "KnowledgeGraph":
        graph = cls()
        for fragment in fragments:
            graph.add_fragment(fragment)
        graph.validate()
        return graph


def _merge_definition(first: bool | None, second: bool | None) -> bool | None:
    if first is True or second is True:
        return True
    if first is False or second is False:
        return False
    return None


def _preferred_node(first: GraphNode, second: GraphNode) -> GraphNode:
    if first.is_definition is True and second.is_definition is not True:
        return first
    if second.is_definition is True and first.is_definition is not True:
        return second
    return min((first, second), key=_node_preference_key)


def _node_preference_key(node: GraphNode) -> tuple[str, int, int]:
    if node.location is None:
        return ("", 0, 0)
    return (
        node.location.path,
        node.location.line or 0,
        node.location.column or 0,
    )


def _merge_attributes(
    first: dict[str, Any], second: dict[str, Any], identity: str
) -> dict[str, Any]:
    merged = dict(first)
    for key, value in second.items():
        if key in merged and merged[key] != value:
            raise GraphConflictError(
                f"Node attribute conflict for {identity}.{key}: "
                f"{merged[key]!r} != {value!r}"
            )
        merged[key] = value
    return merged
