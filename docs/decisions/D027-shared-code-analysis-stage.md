# D027 — Parse source once in a shared code-analysis stage

- Date: 2026-10-27
- Status: accepted; single-parse integration landed, compatibility migration in progress
- Scope: compilation-database parsing, AST fact extraction, review inventory,
  graph snapshots, and independent graph consumers
- Context: review currently owns compilation-database generation and a legacy
  symbol walk, while `code_intelligence` owns a second graph-oriented cursor
  walk. Future review and graph workflows may run together or independently.
- Observation or trigger: the project owner requires common analysis work to be
  performed once rather than reparsing the same translation unit for each
  consumer.
- Evidence: current `repo_review.analysis` implementation, D026, and the
  [graph capability matrix](../contracts/graph-capabilities.md).
- Constraints and decision drivers: preserve `symbols.json` compatibility;
  keep graph views independent of review; avoid coupling the shared core to HTTP
  or report DTOs; retain compile arguments, configuration, diagnostics, and
  producer provenance; support graph-only execution.
- Options considered: keep independent review and graph parsers; move graphs
  back under `repo_review.analysis`; make the shared stage part of the graph
  view package; or make `code_intelligence` own compiler facts while consumers
  project their own outputs.
- Decision: `src/code_intelligence` owns compilation-database loading, one parse
  per translation unit, normalized AST facts, canonical graph construction, and
  graph snapshots. `repo_review.analysis` becomes a consumer that derives its
  compatibility inventory/report projection from that shared result. Graph
  views consume the same canonical graph and never parse source themselves. A
  graph-only entry point may invoke the common stage without `repo_review`.
- Rejected alternatives and why: duplicate parsers can diverge and double cost;
  review ownership prevents independent graph use; view-owned parsing mixes
  source authority with derived presentation.
- Consequences and trade-offs: review and graph extraction now share one
  libclang translation-unit parse and write `symbols.json` plus
  `code-intelligence.json` in the same analysis increment. Two cursor projections
  remain temporarily: the legacy inventory walker and canonical graph extractor.
  Migration still requires a graph-to-inventory compatibility adapter before the
  legacy walker can be removed.
- Reconsideration trigger: the common stage cannot preserve legacy review
  behavior on representative fixtures, or a selected external analysis engine
  requires a different canonical ingestion boundary.
- Implementation references: `src/code_intelligence/analysis.py`,
  `src/code_intelligence/compiler.py`,
  `src/repo_review/analysis/symbol_inventory/extractor.py`, and D026.
- Observed impact and validation: a real temporary compilation database fixture
  produced the legacy inventory and schema 1.1 graph snapshot from one parsed
  translation unit. Independent graph-only orchestration remains pending.
