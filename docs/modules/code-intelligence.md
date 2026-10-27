# Code Intelligence

## Navigation

- Project index: [docs README](../README.md)
- Architecture: [current architecture](../engineering/architecture.md)
- Contract: [code-intelligence graph](../contracts/code-intelligence-graph.md)
- Capability matrix: [all discussed graphs and evidence gates](../contracts/graph-capabilities.md)
- Decision: [D026](../decisions/D026-unified-code-intelligence-graph.md)
- Shared-stage decision: [D027](../decisions/D027-shared-code-analysis-stage.md)
- Code entry points: `src/code_intelligence/models.py`,
  `src/code_intelligence/identity.py`, and
  `src/code_intelligence/extraction/ast_extractor.py`; merge/view/storage entry
  points under `src/code_intelligence/graph`, `views`, and `storage`
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

Current maturity is an isolated extraction and graph-foundation slice. It emits file,
function, struct, enum, typedef, global-variable, and macro nodes; physical
containment plus declaration/definition, include, and call edges; stable USR-
first identity; repository-relative locations; and explicit external/unresolved
relations. Fragments merge into one invariant-checked graph, canonical
snapshots are written atomically with required replay provenance, and call and
include projections are available. The package does not yet parse compilation
databases itself or write application run artifacts.

## Flow and invariants

```text
clang translation-unit cursor
  -> recursive source-owned traversal
  -> graph nodes with USR-first identity
  -> source-occurrence edges with resolution state
  -> deterministic GraphFragment ordering
  -> stable-identity merge and invariant validation
  -> canonical snapshot or call/include projection
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
- Conflicting facts for one stable identity and edges with absent endpoints fail
  closed rather than being silently overwritten.
- Snapshot persistence requires source revision, dirty state, producer, and
  producer version and uses same-directory atomic replacement.

## Known limits and next boundary

The fake-cursor unit fixtures prove extraction semantics without requiring a
machine-specific libclang installation. Pure graph fixtures prove deterministic
merge, definition preference, conflict/dangling-edge rejection, projections,
required provenance, and repeatable atomic snapshot bytes. A real representative
C fixture and compilation-database runner remain the next integration gate.
Indirect calls, conditional-compilation coverage, configuration identity, and
cross-translation-unit semantic reconciliation beyond stable-ID merge remain
unimplemented.

The accepted target is one common compiler-analysis stage owned here. Review
will derive its compatibility inventory from the shared result, while graph
views and graph-only execution consume the same snapshot. The current branch
has not completed that migration yet: `repo_review.analysis` still performs its
legacy parse separately.
