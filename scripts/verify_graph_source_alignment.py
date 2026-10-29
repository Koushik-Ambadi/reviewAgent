from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


_TOKEN_CHECKED_EDGES = {"calls", "reads", "writes", "references"}


def verify_graph_source_alignment(
    graph_path: Path, source_root: Path
) -> dict[str, Any]:
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = {str(node["id"]): node for node in graph.get("nodes") or []}
    issues: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []
    occurrence_keys: list[tuple[Any, ...]] = []
    relation_counts: Counter[tuple[str, str, str]] = Counter()
    checked_locations = 0
    checked_node_locations = 0

    for node in nodes.values():
        attributes = node.get("attributes") or {}
        location = node.get("location") or {}
        path = str(location.get("path") or "")
        line = location.get("line")
        if attributes.get("external") or not path or not line:
            continue
        checked_node_locations += 1
        source_path = source_root / Path(path)
        if not source_path.is_file():
            issues.append(
                {
                    "code": "missing_node_source_file",
                    "node_id": node.get("id"),
                    "path": path,
                }
            )
            continue
        lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if not 1 <= int(line) <= len(lines):
            issues.append(
                {
                    "code": "invalid_node_source_line",
                    "node_id": node.get("id"),
                    "path": path,
                    "line": line,
                    "line_count": len(lines),
                }
            )
            continue
        name = str(node.get("name") or "")
        end_line = min(int(location.get("end_line") or line), len(lines))
        declaration_text = "\n".join(lines[int(line) - 1 : end_line])
        if name and name not in declaration_text:
            issues.append(
                {
                    "code": "node_name_not_at_location",
                    "node_id": node.get("id"),
                    "path": path,
                    "line": line,
                    "name": name,
                }
            )

    for edge in graph.get("edges") or []:
        source_id = str(edge.get("source"))
        target_id = str(edge.get("target"))
        kind = str(edge.get("kind"))
        if source_id not in nodes or target_id not in nodes:
            issues.append(
                {
                    "code": "dangling_endpoint",
                    "edge_id": edge.get("id"),
                    "source": source_id,
                    "target": target_id,
                }
            )
            continue
        location = edge.get("location") or {}
        path = str(location.get("path") or "")
        line = location.get("line")
        column = location.get("column")
        occurrence_keys.append((kind, source_id, target_id, path, line, column))
        relation_counts[(kind, source_id, target_id)] += 1
        if kind not in _TOKEN_CHECKED_EDGES or not path or not line:
            continue
        checked_locations += 1
        source_path = source_root / Path(path)
        if not source_path.is_file():
            issues.append(
                {
                    "code": "missing_source_file",
                    "edge_id": edge.get("id"),
                    "path": path,
                }
            )
            continue
        lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if not 1 <= int(line) <= len(lines):
            issues.append(
                {
                    "code": "invalid_source_line",
                    "edge_id": edge.get("id"),
                    "path": path,
                    "line": line,
                    "line_count": len(lines),
                }
            )
            continue
        target_name = str(nodes[target_id].get("name") or "")
        if target_name and target_name not in lines[int(line) - 1]:
            finding = (
                {
                    "code": "call_target_not_textual"
                    if kind == "calls"
                    else "target_name_not_at_location",
                    "edge_id": edge.get("id"),
                    "path": path,
                    "line": line,
                    "target_name": target_name,
                }
            )
            if kind == "calls":
                notes.append(finding)
            else:
                issues.append(finding)

    duplicate_occurrences = [
        {
            "kind": key[0],
            "source": key[1],
            "target": key[2],
            "path": key[3],
            "line": key[4],
            "column": key[5],
            "count": count,
        }
        for key, count in Counter(occurrence_keys).items()
        if count > 1
    ]
    repeated_relations = [
        {"kind": key[0], "source": key[1], "target": key[2], "count": count}
        for key, count in relation_counts.items()
        if count > 1
    ]
    return {
        "graph": str(graph_path),
        "source_root": str(source_root),
        "nodes": len(nodes),
        "edges": len(graph.get("edges") or []),
        "checked_semantic_locations": checked_locations,
        "checked_node_locations": checked_node_locations,
        "issues": issues,
        "notes": notes,
        "exact_duplicate_occurrences": duplicate_occurrences,
        "repeated_relations": repeated_relations,
        "consistent": not issues and not duplicate_occurrences,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-check canonical graph occurrences against retained source."
    )
    parser.add_argument("graph", type=Path)
    parser.add_argument("source_root", type=Path)
    parser.add_argument(
        "--summary", action="store_true", help="Print counts instead of full findings."
    )
    args = parser.parse_args()
    result = verify_graph_source_alignment(args.graph, args.source_root)
    if args.summary:
        output = {
            key: result[key]
            for key in (
                "graph",
                "source_root",
                "nodes",
                "edges",
                "checked_node_locations",
                "checked_semantic_locations",
                "consistent",
            )
        }
        output["issue_count"] = len(result["issues"])
        output["note_count"] = len(result["notes"])
        output["exact_duplicate_occurrence_count"] = len(
            result["exact_duplicate_occurrences"]
        )
        output["repeated_relation_group_count"] = len(result["repeated_relations"])
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["consistent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
