from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from code_intelligence.graph import KnowledgeGraph
from code_intelligence.identity import edge_id
from code_intelligence.models import (
    EdgeKind,
    GraphEdge,
    GraphNode,
    NodeKind,
    RelationResolution,
)

from .projections import GraphProjection


def reachability_graph(
    graph: KnowledgeGraph,
    *,
    roots: Iterable[str],
) -> GraphProjection:
    graph.validate()
    root_ids = _function_roots(graph, roots)
    call_edges = tuple(edge for edge in graph.edges if edge.kind == EdgeKind.CALLS)
    adjacency = _adjacency(call_edges)
    reachable = _forward_reachable(root_ids, adjacency)
    function_nodes = tuple(
        node for node in graph.nodes if node.kind == NodeKind.FUNCTION
    )
    function_ids = {node.id for node in function_nodes}
    unreachable = sorted(function_ids - reachable)
    return GraphProjection(
        kind="reachability_graph",
        nodes=function_nodes,
        edges=call_edges,
        metadata={
            "roots": sorted(root_ids),
            "reachable": sorted(reachable),
            "unreachable": unreachable,
            "unresolved_boundary_edges": sorted(
                edge.id
                for edge in call_edges
                if edge.resolution == RelationResolution.UNRESOLVED
            ),
        },
    )


def call_depth_graph(
    graph: KnowledgeGraph,
    *,
    roots: Iterable[str],
) -> GraphProjection:
    graph.validate()
    root_ids = _function_roots(graph, roots)
    call_edges = tuple(edge for edge in graph.edges if edge.kind == EdgeKind.CALLS)
    adjacency = _adjacency(call_edges)
    reachable = _forward_reachable(root_ids, adjacency)
    scoped_adjacency = {
        node: {target for target in adjacency.get(node, set()) if target in reachable}
        for node in reachable
    }
    components = _strongly_connected_components(reachable, scoped_adjacency)
    component_index = {
        node: index for index, component in enumerate(components) for node in component
    }
    component_adjacency: dict[int, set[int]] = defaultdict(set)
    for source, targets in scoped_adjacency.items():
        for target in targets:
            source_component = component_index[source]
            target_component = component_index[target]
            if source_component != target_component:
                component_adjacency[source_component].add(target_component)

    root_components = {component_index[root] for root in root_ids}
    component_depths = _longest_dag_depths(root_components, component_adjacency)
    node_depths = {
        node: component_depths.get(component_index[node], 0) for node in reachable
    }
    recursive = [
        sorted(component)
        for component in components
        if len(component) > 1
        or any(node in scoped_adjacency.get(node, set()) for node in component)
    ]
    function_nodes = tuple(
        node
        for node in graph.nodes
        if node.kind == NodeKind.FUNCTION and node.id in reachable
    )
    return GraphProjection(
        kind="call_depth_graph",
        nodes=function_nodes,
        edges=tuple(
            edge
            for edge in call_edges
            if edge.source in reachable and edge.target in reachable
        ),
        metadata={
            "roots": sorted(root_ids),
            "depth_by_node": dict(sorted(node_depths.items())),
            "maximum_depth": max(node_depths.values(), default=0),
            "recursive_components": sorted(recursive),
        },
    )


def module_dependency_graph(graph: KnowledgeGraph) -> GraphProjection:
    graph.validate()
    files = {node.id: node for node in graph.nodes if node.kind == NodeKind.FILE}
    owner_by_symbol = {
        edge.target: edge.source
        for edge in graph.edges
        if edge.kind == EdgeKind.CONTAINS and edge.source in files
    }
    evidence: dict[tuple[str, str], list[GraphEdge]] = defaultdict(list)
    for edge in graph.edges:
        if edge.kind == EdgeKind.INCLUDES:
            source_file = edge.source
            target_file = edge.target
        elif edge.kind == EdgeKind.CALLS:
            source_file = owner_by_symbol.get(edge.source)
            target_file = owner_by_symbol.get(edge.target)
        else:
            continue
        if source_file and target_file and source_file != target_file:
            evidence[(source_file, target_file)].append(edge)

    dependency_edges = []
    for (source, target), source_edges in sorted(evidence.items()):
        resolution = _least_resolved(source_edges)
        dependency_edges.append(
            GraphEdge(
                id=edge_id(EdgeKind.DEPENDS_ON, source=source, target=target),
                kind=EdgeKind.DEPENDS_ON,
                source=source,
                target=target,
                resolution=resolution,
                attributes={
                    "evidence_edge_ids": sorted(edge.id for edge in source_edges),
                    "evidence_kinds": sorted(
                        {edge.kind.value for edge in source_edges}
                    ),
                    "grouping": "file_as_module",
                },
            )
        )
    endpoint_ids = {
        identity
        for edge in dependency_edges
        for identity in (edge.source, edge.target)
    }
    return GraphProjection(
        kind="module_dependency_graph",
        nodes=tuple(files[identity] for identity in sorted(endpoint_ids)),
        edges=tuple(dependency_edges),
        metadata={"grouping": "file_as_module"},
    )


def dependency_impact_graph(
    graph: KnowledgeGraph,
    *,
    changed_nodes: Iterable[str],
) -> GraphProjection:
    graph.validate()
    nodes_by_id = {node.id: node for node in graph.nodes}
    changed = set(changed_nodes)
    missing = sorted(changed - nodes_by_id.keys())
    if missing:
        raise ValueError("Unknown changed node IDs: " + ", ".join(missing))

    dependencies: dict[str, set[str]] = defaultdict(set)
    relevant_edges = []
    for edge in graph.edges:
        if edge.kind in {EdgeKind.CALLS, EdgeKind.INCLUDES}:
            dependencies[edge.target].add(edge.source)
            relevant_edges.append(edge)
        elif edge.kind == EdgeKind.CONTAINS:
            dependencies[edge.target].add(edge.source)
            dependencies[edge.source].add(edge.target)
            relevant_edges.append(edge)

    distance = _impact_distances(changed, dependencies)
    impacted = set(distance)
    return GraphProjection(
        kind="dependency_impact_graph",
        nodes=tuple(nodes_by_id[identity] for identity in sorted(impacted)),
        edges=tuple(
            edge
            for edge in relevant_edges
            if edge.source in impacted and edge.target in impacted
        ),
        metadata={
            "changed": sorted(changed),
            "directly_impacted": sorted(
                identity for identity, depth in distance.items() if depth == 1
            ),
            "transitively_impacted": sorted(
                identity for identity, depth in distance.items() if depth > 1
            ),
            "distance_from_change": dict(sorted(distance.items())),
        },
    )


def _function_roots(graph: KnowledgeGraph, roots: Iterable[str]) -> set[str]:
    roots = set(roots)
    functions = {node.id for node in graph.nodes if node.kind == NodeKind.FUNCTION}
    invalid = sorted(roots - functions)
    if invalid:
        raise ValueError("Unknown or non-function roots: " + ", ".join(invalid))
    if not roots:
        raise ValueError("At least one function root is required")
    return roots


def _adjacency(edges: Iterable[GraphEdge]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        result[edge.source].add(edge.target)
    return result


def _forward_reachable(
    roots: Iterable[str], adjacency: dict[str, set[str]]
) -> set[str]:
    reachable = set(roots)
    pending = list(reachable)
    while pending:
        source = pending.pop()
        for target in adjacency.get(source, set()):
            if target not in reachable:
                reachable.add(target)
                pending.append(target)
    return reachable


def _strongly_connected_components(
    nodes: Iterable[str], adjacency: dict[str, set[str]]
) -> list[set[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[set[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in adjacency.get(node, set()):
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])
        if lowlinks[node] == indices[node]:
            component = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            components.append(component)

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return components


def _longest_dag_depths(
    roots: set[int], adjacency: dict[int, set[int]]
) -> dict[int, int]:
    depths = {root: 0 for root in roots}
    pending = deque(sorted(roots))
    while pending:
        source = pending.popleft()
        for target in sorted(adjacency.get(source, set())):
            proposed = depths[source] + 1
            if proposed > depths.get(target, -1):
                depths[target] = proposed
                pending.append(target)
    return depths


def _impact_distances(
    changed: set[str], dependencies: dict[str, set[str]]
) -> dict[str, int]:
    distances = {identity: 0 for identity in changed}
    pending = deque(sorted(changed))
    while pending:
        source = pending.popleft()
        for dependent in sorted(dependencies.get(source, set())):
            proposed = distances[source] + 1
            if dependent not in distances or proposed < distances[dependent]:
                distances[dependent] = proposed
                pending.append(dependent)
    return distances


def _least_resolved(edges: Iterable[GraphEdge]) -> RelationResolution:
    resolutions = {edge.resolution for edge in edges}
    if RelationResolution.UNRESOLVED in resolutions:
        return RelationResolution.UNRESOLVED
    if RelationResolution.EXTERNAL in resolutions:
        return RelationResolution.EXTERNAL
    return RelationResolution.COMPILER_DERIVED
