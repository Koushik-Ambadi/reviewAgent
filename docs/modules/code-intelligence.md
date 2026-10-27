# Code Intelligence

## Navigation

- Project index: [docs README](../README.md)
- Architecture: [current architecture](../engineering/architecture.md)
- Contract: [code-intelligence graph](../contracts/code-intelligence-graph.md)
- Decision: [D026](../decisions/D026-unified-code-intelligence-graph.md)
- Code entry points: `src/code_intelligence/models.py`,
  `src/code_intelligence/identity.py`, and
  `src/code_intelligence/extraction/ast_extractor.py`
- Upstream: repository root, compilation database, translation-unit cursor, and
  libclang source/reference facts
- Downstream: graph merger, snapshot persistence, deterministic graph views,
  later review/build/agent consumers
- Verification: `tests/test_code_intelligence_ast.py`

## Responsibility and current maturity

This package defines a review-independent representation of repository code
facts and extracts one graph fragment from a clang translation-unit cursor. It
is an additive foundation: the existing `repo_review` symbol inventory remains
unchanged and continues to support naming checks and report inventory.

Current maturity is an isolated, pure extraction slice. It emits file,
function, struct, enum, typedef, global-variable, and macro nodes; physical
containment plus declaration/definition, include, and call edges; stable USR-
first identity; repository-relative locations; and explicit external/unresolved
relations. It does not yet parse compilation databases itself or write run
artifacts.

## Flow and invariants

```text
clang translation-unit cursor
  -> recursive source-owned traversal
  -> graph nodes with USR-first identity
  -> source-occurrence edges with resolution state
  -> deterministic GraphFragment ordering
```

- Repository-owned declarations outside the configured repository root are
  ignored, while externally referenced callees/includes may appear as labeled
  targets.
- A function context is propagated down the AST so each `CALL_EXPR` is attached
  to its caller without writing graph edges into the old symbol inventory.
- Every emitted edge resolves to an emitted node, including placeholders for
  named but unresolved callees and includes.
- Duplicate observations inside one translation unit are collapsed by stable
  node/edge ID. Definitions replace declaration-only node metadata when both
  share an ID.
- Output ordering is deterministic and contains no timestamp or random UUID.

## Known limits and next boundary

The fake-cursor unit fixtures prove extraction semantics without requiring a
machine-specific libclang installation. A real representative C fixture and
compilation-database runner remain the next integration gate. Cross-translation-
unit merge, snapshot provenance, call/include projections, indirect calls,
conditional compilation coverage, and configuration identity are not yet
implemented.
