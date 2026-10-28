from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any, Iterable

from orchestrator.config import WORKSPACE_ROOT
from orchestrator.run_store import get_run_path, load_report


_VISIBLE_LAYERS = {"calls", "includes", "reads", "writes", "references"}
_LAYER_CATALOG = [
    {
        "id": "calls",
        "label": "Function calls",
        "available": True,
        "description": "Direct compiler-resolved and explicitly unresolved calls.",
    },
    {
        "id": "includes",
        "label": "Includes / dependencies",
        "available": True,
        "description": "Resolved, external, and unresolved include relationships.",
    },
    {
        "id": "reads",
        "label": "Signal reads",
        "available": True,
        "description": "Conservative AST-context variable reads.",
    },
    {
        "id": "writes",
        "label": "Signal writes",
        "available": True,
        "description": "Conservative AST-context variable writes.",
    },
    {
        "id": "references",
        "label": "Address / references",
        "available": True,
        "description": "Address-taking and other non-read/write references.",
    },
    {
        "id": "control_flow",
        "label": "Control flow inside functions",
        "available": False,
        "description": "Requires a validated CFG engine; not inferred from syntax.",
    },
    {
        "id": "data_flow",
        "label": "Definition-use data flow",
        "available": False,
        "description": "Requires CFG, alias, and interprocedural data-flow evidence.",
    },
]


class GraphArtifactNotFoundError(FileNotFoundError):
    """Raised when a run has no canonical graph artifact."""


def get_graph_catalog(
    *, workspace_root: Path = WORKSPACE_ROOT
) -> dict[str, Any]:
    records = _latest_graphs_by_module(workspace_root)
    modules = []
    for module_name, record in sorted(records.items()):
        graph = record["graph"]
        modules.append(
            {
                "module_name": module_name,
                "run_id": record["run_id"],
                "generated_at": record["generated"].isoformat(),
                "source_revision": (graph.get("provenance") or {}).get(
                    "source_revision"
                ),
                "nodes": len(graph.get("nodes") or []),
                "edges": len(graph.get("edges") or []),
            }
        )
    return {"modules": modules, "count": len(modules)}


def get_run_graph(
    run_id: str,
    *,
    scope: str = "module",
    selected_file: str | None = None,
    layers: Iterable[str] | None = None,
) -> dict[str, Any]:
    run_path = get_run_path(run_id)
    report = load_report(run_id)
    graph = _load_graph(run_path)
    module_name = str((report.get("metadata") or {}).get("module_name") or run_id)
    selected_layers = _selected_layers(layers)
    if scope == "file":
        payload = _file_projection(
            graph,
            selected_file=selected_file,
            selected_layers=selected_layers,
        )
    elif scope == "module":
        payload = _module_projection(graph, selected_layers=selected_layers)
    else:
        raise ValueError("Scope must be 'file' or 'module'.")
    return {
        "run_id": run_id,
        "module_name": module_name,
        "scope": scope,
        "layers": _LAYER_CATALOG,
        "selected_layers": sorted(selected_layers),
        "provenance": graph.get("provenance") or {},
        **payload,
    }


def get_run_graph_nodes(run_id: str) -> dict[str, Any]:
    run_path = get_run_path(run_id)
    graph = _load_graph(run_path)
    nodes = [
        _node_payload(node)
        for node in graph.get("nodes") or []
        if node.get("kind") != "translation_unit"
    ]
    nodes.sort(key=lambda node: (node["kind"], node["label"], node["id"]))
    return {"run_id": run_id, "nodes": nodes}


def get_run_graph_neighborhood(
    run_id: str,
    node_id: str,
    *,
    direction: str = "both",
    layers: Iterable[str] | None = None,
) -> dict[str, Any]:
    if direction not in {"incoming", "outgoing", "both"}:
        raise ValueError("Direction must be 'incoming', 'outgoing', or 'both'.")
    run_path = get_run_path(run_id)
    graph = _load_graph(run_path)
    nodes = {str(node["id"]): node for node in graph.get("nodes") or []}
    if node_id not in nodes:
        raise ValueError(f"Unknown graph node: {node_id}")
    selected_layers = _selected_layers(layers)
    center_kind = str(nodes[node_id].get("kind"))
    selected_edges = []
    included = {node_id}
    for edge in graph.get("edges") or []:
        kind = str(edge.get("kind"))
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        hierarchy_allowed = (
            kind == "contains" and center_kind == "file"
        ) or (
            kind == "parameter_of" and center_kind == "function"
        ) or (
            kind in {"contains", "parameter_of", "field_of", "member_of"}
            and target == node_id
        )
        if kind not in selected_layers and not hierarchy_allowed:
            continue
        if direction in {"outgoing", "both"} and source == node_id:
            selected_edges.append(edge)
            included.add(target)
        elif direction in {"incoming", "both"} and target == node_id:
            selected_edges.append(edge)
            included.add(source)
    evidence = _node_evidence(nodes, graph.get("edges") or [])
    return {
        "run_id": run_id,
        "node_id": node_id,
        "direction": direction,
        "nodes": [
            _node_payload(nodes[identity], evidence=evidence.get(identity))
            for identity in sorted(included)
        ],
        "edges": _aggregate_occurrence_edges(selected_edges, nodes),
        "limitations": _projection_limitations(),
    }


def get_inter_module_graph(
    *,
    module_names: Iterable[str] | None = None,
    layers: Iterable[str] | None = None,
    workspace_root: Path = WORKSPACE_ROOT,
) -> dict[str, Any]:
    selected_layers = _selected_layers(layers)
    selected_modules = {name for name in (module_names or []) if name}
    records = _latest_graphs_by_module(workspace_root)
    if selected_modules:
        records = {
            name: record
            for name, record in records.items()
            if name in selected_modules
        }

    owners: dict[str, set[str]] = defaultdict(set)
    for module_name, record in records.items():
        for node in record["graph"].get("nodes") or []:
            if _is_owned_definition(node):
                owners[str(node["id"])].add(module_name)

    aggregates: dict[tuple[str, str, str], dict[str, Any]] = {}
    inputs: dict[str, set[str]] = defaultdict(set)
    outputs: dict[str, set[str]] = defaultdict(set)
    for source_module, record in records.items():
        graph = record["graph"]
        nodes = {str(node["id"]): node for node in graph.get("nodes") or []}
        for edge in graph.get("edges") or []:
            kind = str(edge.get("kind"))
            if kind not in selected_layers:
                continue
            target_id = str(edge.get("target"))
            for target_module in sorted(owners.get(target_id, set())):
                if target_module == source_module:
                    continue
                target = nodes.get(target_id) or {}
                label = str(target.get("name") or target_id)
                key = (source_module, target_module, kind)
                aggregate = aggregates.setdefault(
                    key,
                    {
                        "id": "::".join(key),
                        "kind": kind,
                        "source": source_module,
                        "target": target_module,
                        "count": 0,
                        "signals": set(),
                        "interactions": [],
                        "resolution": str(
                            edge.get("resolution") or "compiler_derived"
                        ),
                    },
                )
                aggregate["count"] += 1
                aggregate["signals"].add(label)
                if len(aggregate["interactions"]) < 50:
                    aggregate["interactions"].append(
                        _interaction_payload(edge, nodes)
                    )
                if kind == "reads":
                    inputs[source_module].add(label)
                    outputs[target_module].add(label)
                elif kind == "writes":
                    outputs[source_module].add(label)
                    inputs[target_module].add(label)

    nodes = [
        {
            "id": name,
            "kind": "module",
            "label": name,
            "run_id": record["run_id"],
            "inputs": sorted(inputs.get(name, set())),
            "outputs": sorted(outputs.get(name, set())),
        }
        for name, record in sorted(records.items())
    ]
    edges = [
        {**edge, "signals": sorted(edge["signals"])}
        for edge in sorted(aggregates.values(), key=_edge_sort_key)
    ]
    return {
        "scope": "inter_module",
        "layers": _LAYER_CATALOG,
        "selected_layers": sorted(selected_layers),
        "available_modules": sorted(_latest_graphs_by_module(workspace_root)),
        "selected_modules": sorted(records),
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "modules": len(nodes),
            "relationships": len(edges),
            "signal_names": len(
                {signal for edge in edges for signal in edge["signals"]}
            ),
        },
        "limitations": [
            "Cross-module links require matching stable symbol identities.",
            "No relationship means unavailable or unobserved evidence, "
            "not proof of isolation.",
        ],
    }


def _load_graph(run_path: Path) -> dict[str, Any]:
    path = run_path / "analysis" / "code-intelligence.json"
    if not path.is_file():
        raise GraphArtifactNotFoundError(
            f"Code-intelligence graph not found for run: {run_path.name}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _selected_layers(layers: Iterable[str] | None) -> set[str]:
    selected = set(layers or _VISIBLE_LAYERS)
    invalid = sorted(selected - _VISIBLE_LAYERS)
    if invalid:
        raise ValueError("Unavailable graph layers: " + ", ".join(invalid))
    return selected


def _file_projection(
    graph: dict[str, Any],
    *,
    selected_file: str | None,
    selected_layers: set[str],
) -> dict[str, Any]:
    nodes = {str(node["id"]): node for node in graph.get("nodes") or []}
    edges = graph.get("edges") or []
    files = [
        node
        for node in nodes.values()
        if node.get("kind") == "file"
        and not (node.get("attributes") or {}).get("external")
    ]
    files.sort(key=lambda node: str((node.get("attributes") or {}).get("path")))
    available_files = [
        str((node.get("attributes") or {}).get("path")) for node in files
    ]
    if not available_files:
        return _empty_projection("No repository-owned files are present in this graph.")
    selected_file = selected_file or available_files[0]
    if selected_file not in available_files:
        raise ValueError(f"Unknown graph file: {selected_file}")
    file_node = next(
        node
        for node in files
        if (node.get("attributes") or {}).get("path") == selected_file
    )
    owned = _descendants(str(file_node["id"]), edges)
    owned.add(str(file_node["id"]))
    selected_occurrence_edges = []
    included_nodes = set(owned)
    for edge in edges:
        kind = str(edge.get("kind"))
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        if kind in selected_layers and source in owned:
            selected_occurrence_edges.append(edge)
            included_nodes.update((source, target))
    projected_edges = _aggregate_occurrence_edges(
        selected_occurrence_edges, nodes
    )
    hierarchy_edges = [
        _edge_payload(edge, nodes)
        for edge in edges
        if edge.get("kind") in {"contains", "parameter_of", "field_of", "member_of"}
        and str(edge.get("source")) in owned
        and str(edge.get("target")) in owned
    ]
    projected_edges.extend(hierarchy_edges)
    node_evidence = _node_evidence(nodes, edges)
    return {
        "selected_file": selected_file,
        "available_files": available_files,
        "nodes": [
            _node_payload(nodes[identity], evidence=node_evidence.get(identity))
            for identity in sorted(included_nodes)
        ],
        "edges": sorted(projected_edges, key=_edge_sort_key),
        "summary": _summary(included_nodes, projected_edges),
        "limitations": _projection_limitations(),
    }


def _module_projection(
    graph: dict[str, Any], *, selected_layers: set[str]
) -> dict[str, Any]:
    nodes = {str(node["id"]): node for node in graph.get("nodes") or []}
    edges = graph.get("edges") or []
    owner = _file_owners(nodes, edges)
    file_nodes = {
        identity: node
        for identity, node in nodes.items()
        if node.get("kind") == "file"
        and not (node.get("attributes") or {}).get("external")
    }
    aggregates: dict[tuple[str, str, str], dict[str, Any]] = {}
    for edge in edges:
        kind = str(edge.get("kind"))
        if kind not in selected_layers:
            continue
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        source_file = source if source in file_nodes else owner.get(source)
        target_file = target if target in file_nodes else owner.get(target)
        if (
            source_file not in file_nodes
            or target_file not in file_nodes
            or source_file == target_file
        ):
            continue
        key = (source_file, target_file, kind)
        aggregate = aggregates.setdefault(
            key,
            {
                "id": "::".join(key),
                "kind": kind,
                "source": source_file,
                "target": target_file,
                "count": 0,
                "signals": set(),
                "interactions": [],
                "resolution": str(edge.get("resolution") or "compiler_derived"),
            },
        )
        aggregate["count"] += 1
        if kind in {"reads", "writes", "references", "calls"}:
            target_name = (nodes.get(target) or {}).get("name") or target
            aggregate["signals"].add(str(target_name))
        if len(aggregate["interactions"]) < 50:
            aggregate["interactions"].append(
                _interaction_payload(edge, nodes)
            )
    result_edges = [
        {**edge, "signals": sorted(edge["signals"])}
        for edge in sorted(aggregates.values(), key=_edge_sort_key)
    ]
    endpoint_ids = {
        identity
        for edge in result_edges
        for identity in (edge["source"], edge["target"])
    }
    return {
        "available_files": sorted(
            str((node.get("attributes") or {}).get("path"))
            for node in file_nodes.values()
        ),
        "nodes": [
            _node_payload(file_nodes[identity]) for identity in sorted(endpoint_ids)
        ],
        "edges": result_edges,
        "summary": _summary(endpoint_ids, result_edges),
        "limitations": _projection_limitations(),
    }


def _descendants(root: str, edges: list[dict[str, Any]]) -> set[str]:
    hierarchy = {"contains", "parameter_of", "field_of", "member_of"}
    children: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge.get("kind") in hierarchy:
            children[str(edge.get("source"))].add(str(edge.get("target")))
    result: set[str] = set()
    pending = [root]
    while pending:
        source = pending.pop()
        for child in children.get(source, set()):
            if child not in result:
                result.add(child)
                pending.append(child)
    return result


def _file_owners(
    nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]
) -> dict[str, str]:
    parents = {
        str(edge.get("target")): str(edge.get("source"))
        for edge in edges
        if edge.get("kind") in {"contains", "parameter_of", "field_of", "member_of"}
    }
    owners: dict[str, str] = {}
    for identity in nodes:
        current = identity
        seen = set()
        while current in parents and current not in seen:
            seen.add(current)
            current = parents[current]
        if (nodes.get(current) or {}).get("kind") == "file":
            owners[identity] = current
    return owners


def _node_payload(
    node: dict[str, Any], *, evidence: dict[str, list[dict[str, Any]]] | None = None
) -> dict[str, Any]:
    attributes = node.get("attributes") or {}
    location = node.get("location") or {}
    payload = {
        "id": str(node["id"]),
        "kind": str(node.get("kind")),
        "label": str(node.get("name") or node["id"]),
        "path": str(attributes.get("path") or location.get("path") or ""),
        "line": location.get("line"),
        "external": bool(attributes.get("external")),
        "definition": node.get("is_definition"),
        "type": attributes.get("type"),
        "return_type": attributes.get("return_type"),
        "owner_id": attributes.get("scope"),
        "metrics": {
            key: attributes[key]
            for key in ("cyclomatic_complexity", "statement_count", "size_bytes")
            if key in attributes
        },
    }
    if evidence is not None:
        payload["declarations"] = evidence["declarations"]
        payload["definitions"] = evidence["definitions"]
        payload["incoming_interactions"] = evidence["incoming"]
        payload["outgoing_interactions"] = evidence["outgoing"]
    return payload


def _node_evidence(
    nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    evidence: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: {
            "declarations": [],
            "definitions": [],
            "incoming": [],
            "outgoing": [],
        }
    )
    for edge in edges:
        kind = str(edge.get("kind"))
        source_id = str(edge.get("source"))
        target_id = str(edge.get("target"))
        if kind in {"declares", "defines"}:
            location = edge.get("location") or {}
            source = nodes.get(source_id) or {}
            occurrence = {
                "owner_id": source_id,
                "owner_label": str(source.get("name") or source_id),
                "path": str(location.get("path") or ""),
                "line": location.get("line"),
            }
            key = "declarations" if kind == "declares" else "definitions"
            if len(evidence[target_id][key]) < 50:
                evidence[target_id][key].append(occurrence)
        if kind not in {"calls", "reads", "writes", "references"}:
            continue
        interaction = {"kind": kind, **_interaction_payload(edge, nodes)}
        if len(evidence[source_id]["outgoing"]) < 100:
            evidence[source_id]["outgoing"].append(interaction)
        if len(evidence[target_id]["incoming"]) < 100:
            evidence[target_id]["incoming"].append(interaction)
    for node_evidence in evidence.values():
        for key in ("declarations", "definitions"):
            node_evidence[key].sort(
                key=lambda item: (
                    item.get("path") or "",
                    item.get("line") or 0,
                )
            )
        for key in ("incoming", "outgoing"):
            node_evidence[key].sort(
                key=lambda item: (
                    item.get("path") or "",
                    item.get("line") or 0,
                    item.get("kind") or "",
                    item.get("source_label") or "",
                    item.get("target_label") or "",
                )
            )
    return evidence


def _edge_payload(
    edge: dict[str, Any], nodes: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    target = nodes.get(str(edge.get("target"))) or {}
    location = edge.get("location") or {}
    return {
        "id": str(edge.get("id")),
        "kind": str(edge.get("kind")),
        "source": str(edge.get("source")),
        "target": str(edge.get("target")),
        "count": 1,
        "signals": [str(target.get("name"))] if target.get("name") else [],
        "resolution": str(edge.get("resolution") or "compiler_derived"),
        "path": str(location.get("path") or ""),
        "line": location.get("line"),
    }


def _aggregate_occurrence_edges(
    edges: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    aggregates: dict[tuple[str, str, str], dict[str, Any]] = {}
    for edge in edges:
        key = (
            str(edge.get("source")),
            str(edge.get("target")),
            str(edge.get("kind")),
        )
        aggregate = aggregates.get(key)
        if aggregate is None:
            aggregate = _edge_payload(edge, nodes)
            aggregate["id"] = "::".join(key)
            aggregate["count"] = 0
            aggregate["occurrences"] = []
            aggregate["interactions"] = []
            aggregates[key] = aggregate
        aggregate["count"] += 1
        location = edge.get("location") or {}
        if len(aggregate["occurrences"]) < 100:
            aggregate["occurrences"].append(
                {
                    "path": str(location.get("path") or ""),
                    "line": location.get("line"),
                    "column": location.get("column"),
                }
            )
        if len(aggregate["interactions"]) < 50:
            aggregate["interactions"].append(
                _interaction_payload(edge, nodes)
            )
    for aggregate in aggregates.values():
        aggregate["occurrences"].sort(
            key=lambda item: (
                item.get("path") or "",
                item.get("line") or 0,
                item.get("column") or 0,
            )
        )
        aggregate["interactions"].sort(
            key=lambda item: (
                item.get("path") or "",
                item.get("line") or 0,
                item.get("source_label") or "",
                item.get("target_label") or "",
            )
        )
    return sorted(aggregates.values(), key=_edge_sort_key)


def _interaction_payload(
    edge: dict[str, Any], nodes: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    source = nodes.get(str(edge.get("source"))) or {}
    target = nodes.get(str(edge.get("target"))) or {}
    location = edge.get("location") or {}
    return {
        "source_id": str(edge.get("source")),
        "source_label": str(source.get("name") or edge.get("source")),
        "source_kind": str(source.get("kind") or "unknown"),
        "target_id": str(edge.get("target")),
        "target_label": str(target.get("name") or edge.get("target")),
        "target_kind": str(target.get("kind") or "unknown"),
        "path": str(location.get("path") or ""),
        "line": location.get("line"),
    }


def _summary(nodes: Iterable[str], edges: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "nodes": len(set(nodes)),
        "relationships": len(edges),
        "unresolved": sum(edge.get("resolution") == "unresolved" for edge in edges),
    }


def _projection_limitations() -> list[str]:
    return [
        "Reads and writes are conservative syntax-context facts, not full data flow.",
        "Control flow is unavailable until a validated CFG engine is integrated.",
        "Indirect calls and configuration coverage remain incomplete.",
    ]


def _empty_projection(message: str) -> dict[str, Any]:
    return {
        "available_files": [],
        "nodes": [],
        "edges": [],
        "summary": {"nodes": 0, "relationships": 0, "unresolved": 0},
        "limitations": [message],
    }


def _is_owned_definition(node: dict[str, Any]) -> bool:
    if (node.get("attributes") or {}).get("external"):
        return False
    return bool(node.get("is_definition")) or node.get("kind") == "file"


def _latest_graphs_by_module(workspace_root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    if not workspace_root.is_dir():
        return records
    for report_path in sorted(workspace_root.glob("*/report.json")):
        graph_path = report_path.parent / "analysis" / "code-intelligence.json"
        if not graph_path.is_file():
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        metadata = report.get("metadata") or {}
        module_name = str(metadata.get("module_name") or report_path.parent.name)
        generated = _timestamp(metadata.get("generated_at"))
        current = records.get(module_name)
        if current is None or generated >= current["generated"]:
            records[module_name] = {
                "run_id": report_path.parent.name,
                "generated": generated,
                "graph": json.loads(graph_path.read_text(encoding="utf-8")),
            }
    return records


def _timestamp(value: Any) -> datetime:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)


def _edge_sort_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (str(edge["source"]), str(edge["target"]), str(edge["kind"]))
