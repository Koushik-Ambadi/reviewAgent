# D032 — Use flow-oriented, cycle-safe trace exploration

- Date: 2026-10-29
- Status: accepted
- Scope: trace semantics, progressive expansion, and layout
- Context: canonical `reads` and `writes` are accurate compiler observations,
  but they do not directly express the interface question a reader asks. A
  bidirectional expansion could also recreate the same call relation from each
  endpoint indefinitely, and the depth-only tree layout did not center parents
  or distinguish inputs/callers from outputs/callees.
- Decision: retain canonical relationship kinds as evidence and add a derived
  trace flow. Read variables and parameters flow into their function, written
  variables flow out, and calls flow caller-to-callee. Each trace instance keeps
  its canonical ancestry and traversed relationship IDs. Expansion suppresses a
  canonical node or relationship already present on that branch while allowing
  the same canonical symbol to appear on a different branch.
- Entry and exit semantics: functions with no observed direct callers are
  beginning candidates; functions with no observed direct callees are ending
  candidates. Transitive caller/callee counts communicate structural position,
  not a runtime stack or guaranteed application entry/termination.
- Layout: incoming roles use columns left of their expanded node and outgoing
  roles use columns to its right. A parent is vertically centered over its
  visible children. Parameters render as compact expandable ports. Curved edges
  test deterministic bend candidates against visible node boxes and choose the
  least-obstructed route; this is a heuristic, not a crossing-free guarantee.
- Evidence boundary: argument-to-parameter binding, constant/macro/global/call-
  result origin, return lineage, transformations, control order, and path
  feasibility remain unavailable until value-flow and CFG extraction exists.
  LUT tables may be attached later through a versioned evidence adapter; they
  are not inferred now.
- Consequences: the playground uses input/output language without changing the
  canonical graph, cannot bounce forever across one relation, and better
  communicates call position and branch direction. Overview graphs remain
  unchanged.
- Reconsideration trigger: validated interprocedural value flow replaces the
  derived interface projection, or a dedicated layout engine is justified by
  measured readability failures on representative modules.
- Implementation references: `app/services/graph_service.py`,
  `app/static/graph.js`, and `tests/test_graph_service.py`.
