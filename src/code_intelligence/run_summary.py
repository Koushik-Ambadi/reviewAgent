"""Compact current-run intelligence for the developer Analysis stage."""
from __future__ import annotations

import json
from pathlib import Path

from code_intelligence.exploration import Explorer


def build_run_summary(analysis_dir: Path) -> dict:
    graph_path = analysis_dir / "code-intelligence.json"
    flow_path = analysis_dir / "flow/summary.json"
    if not graph_path.is_file():
        return {"status": "unavailable", "reason": "No code graph artifact"}
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    analytics = Explorer(graph).analytics()
    flow = (json.loads(flow_path.read_text(encoding="utf-8")) if flow_path.is_file()
            else {"status": "not_generated", "sources": []})
    source_status = [item["status"] for item in flow.get("sources", [])]
    return {
        "schema_version": "1.0",
        "status": "available",
        "graph_artifact": "analysis/code-intelligence.json",
        "flow_artifact": "analysis/flow/summary.json", "flow_status": flow["status"],
        "flow_completed_sources": source_status.count("completed"),
        "flow_failed_sources": source_status.count("failed"),
        "flow_skipped_sources": source_status.count("skipped"),
        "functions": len(analytics["functions"]),
        "top_functions": [
            {k: f[k] for k in ("id", "name", "complexity", "callers", "callees", "review_score")}
            for f in analytics["functions"][:5]
        ],
        "complexity_outliers": len(analytics["complexity_outliers"]),
        "recursive_groups": len(analytics["recursive_groups"]),
        "shared_values": len(analytics["shared_state"]),
        "exact_clone_groups": len(analytics["clone_groups"]),
        "file_cycles": len(analytics["file_cycles"]),
        "boundary": "Current static snapshot. Investigation signals are not defects or runtime observations.",
    }
