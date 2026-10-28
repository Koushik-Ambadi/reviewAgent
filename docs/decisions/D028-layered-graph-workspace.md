# D028 — Put layered code graphs in the developer workspace

- Date: 2026-10-28
- Status: accepted
- Scope: graph UI placement, abstraction levels, overlay selection, and evidence
  gating
- Context: the project now produces a canonical graph per review run. Users need
  file, module, and multi-module views with selectable internal detail while
  preserving the distinction between available access facts and unavailable
  CFG/data-flow evidence.
- Decision: add a `Code graphs` tab to the developer run workspace. One workspace
  switches between file, module, and inter-module scopes and combines available
  overlays. File scope supports symbol-level drill-down; module scope aggregates
  file relationships; inter-module scope selects multiple latest module graphs
  and exposes input/output signal names. Control-flow and definition-use data-
  flow controls remain visible but disabled until their evidence engines exist.
- Rejected alternatives and why: placing graphs only on the roadmap hides an
  implemented run artifact; placing the interactive explorer in the manager
  workspace mixes engineering evidence with portfolio summaries; separate pages
  per graph duplicate selectors and make combined overlays difficult.
- Consequences and trade-offs: the developer workspace owns interactive graph
  inspection. Manager views may later consume derived summaries, not the full
  explorer. Canvas rendering is a bounded first implementation and must retain
  textual summaries/limitations for accessibility and large-graph fallback.
- Reconsideration trigger: graph workloads require server-side layout/search or
  a manager/auditor workflow needs a materially different projection.
- Implementation references: `app/api/graphs.py`,
  `app/services/graph_service.py`, and the graph workspace UI.
- Observed impact and validation: backend projections are verified against pure
  fixtures and the retained shunt run. The developer workspace now provides the
  three scopes, combined overlays, pan/zoom, selection, text fallback, and
  double-click drill-down. HTTP/static smoke passed; browser visual review is
  pending because local browser use is disabled in Work settings.
