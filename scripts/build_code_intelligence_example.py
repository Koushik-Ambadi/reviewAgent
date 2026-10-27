from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from clang import cindex

from code_intelligence.compiler import configure_libclang
from code_intelligence.extraction import extract_translation_unit
from code_intelligence.graph import KnowledgeGraph
from code_intelligence.models import NodeKind
from code_intelligence.views import (
    call_depth_graph,
    call_graph,
    complexity_graph,
    dependency_impact_graph,
    exact_clone_graph,
    include_graph,
    memory_estimate_graph,
    module_dependency_graph,
    reachability_graph,
    variable_access_graph,
)


def _mermaid(projection, names: dict[str, str]) -> list[str]:
    lines = ["```mermaid", "flowchart LR"]
    identifiers = {
        node.id: "n" + hashlib.sha256(node.id.encode("utf-8")).hexdigest()[:12]
        for node in projection.nodes
    }
    for node in projection.nodes:
        lines.append(
            f'  {identifiers[node.id]}["{node.kind.value}: {names[node.id]}"]'
        )
    relationships = Counter(
        (edge.source, edge.target, edge.kind.value) for edge in projection.edges
    )
    for (source, target, kind), count in sorted(relationships.items()):
        suffix = f" x{count}" if count > 1 else ""
        lines.append(
            f"  {identifiers[source]} -->|{kind}{suffix}| {identifiers[target]}"
        )
    if len(lines) == 2:
        lines.append('  empty["No relationships in this projection"]')
    lines.append("```")
    return lines


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "tests" / "fixtures" / "code_intelligence" / "sample.c"
    output_dir = root / "docs" / "examples"
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_libclang()
    translation_unit = cindex.Index.create().parse(
        str(source),
        args=["-std=c11", f"-I{source.parent}"],
        options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
    )
    fragment = extract_translation_unit(
        translation_unit.cursor,
        repo_root=root,
        translation_unit=source,
    )
    graph = KnowledgeGraph.from_fragments([fragment])
    functions = {
        node.name: node.id
        for node in graph.nodes
        if node.kind == NodeKind.FUNCTION
    }
    roots = [functions["control_step"]]
    projections = [
        call_graph(graph),
        include_graph(graph),
        reachability_graph(graph, roots=roots),
        call_depth_graph(graph, roots=roots),
        module_dependency_graph(graph),
        dependency_impact_graph(graph, changed_nodes=[functions["read_state"]]),
        variable_access_graph(graph),
        exact_clone_graph(graph),
        complexity_graph(graph),
        memory_estimate_graph(graph),
    ]
    payload = {
        "source": source.relative_to(root).as_posix(),
        "graph": graph.to_dict(),
        "projections": {
            projection.kind: projection.to_dict() for projection in projections
        },
    }
    json_path = output_dir / "code-intelligence-graphs.json"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    names = {node.id: node.name for node in graph.nodes}
    by_kind = {projection.kind: projection for projection in projections}
    memory = by_kind["memory_estimate_graph"].metadata
    complexity = by_kind["complexity_graph"].metadata["metrics_by_function"]
    markdown = [
        "# Code-intelligence graph example",
        "",
        "Generated from `tests/fixtures/code_intelligence/sample.c` by",
        "`scripts/build_code_intelligence_example.py`. The JSON beside this file",
        "contains the canonical graph and every currently executable projection.",
        "",
        "## Call graph",
        "",
        *_mermaid(by_kind["call_graph"], names),
        "",
        "## Variable-access graph",
        "",
        *_mermaid(by_kind["variable_access_graph"], names),
        "",
        "## Exact-token clone graph",
        "",
        *_mermaid(by_kind["exact_clone_graph"], names),
        "",
        "## Complexity",
        "",
        "| Function | Cyclomatic estimate | Statements | Method |",
        "|---|---:|---:|---|",
    ]
    ordered_metrics = sorted(complexity.items(), key=lambda item: names[item[0]])
    for identity, metrics in ordered_metrics:
        markdown.append(
            f"| {names[identity]} | {metrics['cyclomatic_complexity']} | "
            f"{metrics['statement_count']} | {metrics['method']} |"
        )
    markdown.extend(
        [
            "",
            "## Memory estimate",
            "",
            f"- Global typed storage: {memory['global_storage_estimate_bytes']} bytes.",
            "- Local/parameter totals are compiler type-size sums, not stack frames.",
            "- Linker sections, addresses, padding, heap, and runtime peaks remain",
            "  unavailable.",
            "",
            "## Evidence boundary",
            "",
            "CFG, data flow, state/scheduler/interrupt semantics, requirements/tests,",
            "timing, exact stack/linker memory, and failure propagation remain gated",
            "by the engines or external evidence named in",
            "`docs/contracts/graph-capabilities.md`.",
            "",
        ]
    )
    markdown_path = output_dir / "code-intelligence-graphs.md"
    markdown_path.write_text("\n".join(markdown), encoding="utf-8")
    print(f"wrote {json_path.relative_to(root)}")
    print(f"wrote {markdown_path.relative_to(root)}")


if __name__ == "__main__":
    main()
