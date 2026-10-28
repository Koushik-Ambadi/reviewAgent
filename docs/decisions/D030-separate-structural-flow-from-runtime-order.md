# D030 — Separate structural interaction from runtime-ordered flow

- Date: 2026-10-28
- Status: accepted
- Scope: symbol inspection, edge routing, function interfaces, and memory claims
- Context: users need to follow how functions and variables interact without
  confusing source occurrences with execution order or AST type sizes with
  object-code and stack measurements.
- Decision: preserve bounded declaration, definition, incoming-interaction, and
  outgoing-interaction evidence on file-projection nodes. Function inspection
  presents parameters, reads/references, writes, callers, callees, return type,
  complexity, and observed parameter/local object-size sums as structured side
  panels. Variable and macro inspection presents declaration/definition sites
  and all recorded direct interactions, independent of the selected file, but
  does not order those interactions without control-flow evidence.
- Rendering decision: parallel relationship kinds between one node pair receive
  deterministic side-by-side lanes, type-specific color/dash styles, boundary-
  clipped arrowheads, and hover labels. Identical source-kind-target occurrences
  aggregate into one relationship with a count and retained source locations.
  A three-sweep barycentric heuristic reduces crossings between dependency
  ranks; it is not a crossing-minimality guarantee.
- Evidence boundary: function code size requires object or linker-map evidence.
  Exact frame size and maximum caller-chain stack require ABI-aware compiler
  stack reports, validated indirect-call targets, recursion handling, and call-
  path composition. AST `size_bytes` sums remain labeled object-size estimates.
- Consequences: the workspace provides a useful unordered program skeleton now
  while leaving argument/value transformation and runtime ordering for the
  conservative value-flow and CFG gates recorded in D029.
- Reconsideration trigger: toolchain map/stack adapters or validated CFG/value-
  flow engines become available.
- Implementation references: `app/services/graph_service.py`,
  `app/static/graph.js`, and `docs/contracts/graph-workspace-api.md`.
