# D026 — Adopt a unified code-intelligence graph without changing symbol inventory

- Date: 2026-10-27
- Status: accepted; initial AST extraction implemented
- Scope: code-intelligence package, graph contract, AST extraction, and future
  graph projections
- Context: the existing symbol inventory is a stable input to naming checks and
  audit projections, but it does not represent calls, include targets, stable
  semantic identity, or other relationships. Saved design conversations moved
  from separate relationship/semantic/flow artifacts to one unified graph.
- Observation or trigger: the current request explicitly activates graph work
  and requires the AST to be extended safely before graph implementation.
- Evidence: current `repo_review.analysis.symbol_inventory` consumers; G08;
  [conversation provenance](../engineering/conversation-provenance.md); focused
  fake-cursor extraction tests.
- Constraints and decision drivers: preserve current naming/report behavior;
  do not duplicate graph authorities; retain compiler provenance; make
  unresolved/external relations honest; allow later review, build, and agent
  consumers without coupling the core representation to one workflow.
- Options considered: add calls and graph lists directly to `symbols.json`;
  store one independent JSON file per graph; keep all new work under
  `repo_review.analysis`; create a standalone graph foundation and integrate it
  incrementally.
- Decision: create `src/code_intelligence` as an additive package. Extract
  normalized nodes and edges from clang cursors without changing
  `symbols.json`. Use clang USR as primary identity and deterministic
  kind/path/name fallback otherwise. Store one canonical node/edge graph;
  graph-specific outputs are projections. Begin with files, functions, core
  declared symbol kinds, includes, calls, and source ownership.
- Rejected alternatives and why: extending `symbols.json` would couple graph
  evolution to naming compatibility; independent graph stores would duplicate
  nodes and provenance; retaining the capability permanently inside
  `repo_review` would make a future second consumer depend on review internals.
- Consequences and trade-offs: the repository temporarily has two AST-derived
  representations with separate contracts. The new package needs a compilation-
  database runner, cross-translation-unit merge, snapshot provenance, and
  migration/integration tests before review or build consumes it.
- Reconsideration trigger: a representative embedded-C fixture disproves the
  identity or edge model; indirect-call requirements need a richer target
  contract; or an evaluated external CPG engine provides a demonstrably safer
  canonical representation.
- Implementation references: `src/code_intelligence/`,
  `tests/test_code_intelligence_ast.py`, and
  `docs/contracts/code-intelligence-graph.md`.
- Observed impact and validation: three pure extraction scenarios pass by
  direct assertion invocation in the supported Python 3.13 environment. Pytest
  Black, and Ruff are not installed, so their attempted commands were
  environment failures and are not reported as passes.
