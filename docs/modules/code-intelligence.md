# Code Intelligence

## Guided exploration service

`app/services/intelligence_service.py` composes selected current module runs with
hash-verified flow bundles without rewriting stored graphs. The deterministic
`exploration.py` engine supplies connections, influence, calls/depth, data access,
file/module/interfaces, CFG/DFD, recursion, clones, metrics, calibration candidates
and root-bounded reachability. `regions.py` retrieves compiler source structure
and boundary-test ideas. The [API contract](../contracts/intelligence-exploration.md)
owns exact semantics and budgets. `tests/test_intelligence.py` covers traversal,
ambiguity, source containment, stale evidence and projection identity. Original
graph API and trace canvas remain compatible. This is static evidence, not
runtime, coverage, alias-complete or target-memory analysis.

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
- Inspectable example: [generated graphs](../examples/code-intelligence-graphs.md)
  and the adjacent canonical/projection JSON
- UI/API contract: [graph workspace API](../contracts/graph-workspace-api.md)
- Use-case owner: [graph use cases](../engineering/graph-use-cases.md)

## Responsibility and current maturity

This package defines a review-independent representation of repository code
facts and extracts one graph fragment from a clang translation-unit cursor. It
is an additive foundation: the existing `repo_review` symbol inventory remains
unchanged and continues to support naming checks and report inventory.

Current maturity is a shared analysis-stage and graph-foundation slice. It emits
file, function, type, global/scoped-variable, field, enum-constant, and macro
nodes; physical/scoped containment plus declaration/definition, include, call,
and conservative variable-access edges; stable USR-
first identity; repository-relative locations; and explicit external/unresolved
relations. Fragments merge into one invariant-checked graph, canonical
snapshots are written atomically with required replay provenance, and call,
include, explicit-root reachability/call-depth, file-module dependency, and
changed-node impact projections are available. Exact-token clone, versioned AST
complexity, and clearly labeled type-size memory estimates are also available.
The package owns the compilation-database parse primitive and the review stage
writes `analysis/code-intelligence.json` beside `symbols.json`. An opt-in
standalone LLVM flow entry point now exists; broader graph-only orchestration
remains pending.

The read-only application adapter projects a run graph at file or module scope
and aggregates the newest graph-bearing run per module for inter-module views.
It never rewrites the canonical artifact. Available overlays are calls, includes,
and conservative reads/writes/references; CFG and definition-use data flow remain
explicitly disabled evidence gates.

The UI projection is deliberately function-centric. Ownership facts still
travel in the payload, but parameters and locals are nested under their function
unless a user explicitly promotes those node kinds. Aggregate file edges expose
bounded source/target interaction evidence. This presentation does not add or
reinterpret compiler facts.

File projections enrich displayed symbols with bounded occurrence evidence from
the same canonical graph: declaration and definition sites plus incoming and
outgoing calls, reads, writes, and references. Repeated occurrences aggregate
for display while retaining locations. This avoids a second graph authority and
lets variable inspection cross file boundaries. Occurrence order is not control
flow.

The run-wide trace adapter exposes a semantic-node index and one-hop
neighborhood projection over the same graph. The UI may instantiate one
canonical symbol more than once in different trace branches; `canonical_id`
preserves identity and the duplicated instance is never persisted as analysis.
The adapter adds a presentation-only input/output flow over canonical access
edges and computes observed call-position summaries. Client instances retain
canonical ancestry so a branch cannot bounce across the same relationship or
cycle back to a prior symbol. Parameter ports are expandable to currently known
ownership/interactions, but concrete argument bindings remain outside the
extracted contract.

## Flow and invariants

```text
clang translation-unit cursor
  -> recursive source-owned traversal
  -> graph nodes with USR-first identity
  -> source-occurrence edges with resolution state
  -> deterministic GraphFragment ordering
  -> stable-identity merge and invariant validation
  -> canonical snapshot or deterministic graph projection
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
- Function metrics and clone fingerprints are computed during the same cursor
  traversal. Memory totals are type-size estimates only; exact stack, section,
  address, and heap claims require external build/runtime evidence.

## Known limits and next boundary

The fake-cursor unit fixtures prove extraction semantics without requiring a
machine-specific libclang installation. Pure graph fixtures prove deterministic
merge, definition preference, conflict/dangling-edge rejection, projections,
required provenance, repeatable atomic snapshot bytes, recursive call-depth
handling, reachability, file-module dependencies, and reverse impact traversal.
A real representative
C fixture and compilation-database runner remain the next integration gate.
Indirect calls, conditional-compilation coverage, configuration identity, and
cross-translation-unit semantic reconciliation beyond stable-ID merge remain
unimplemented.

The next safe semantic extension is conservative value-flow evidence for
call-site arguments, initializers/assignments, return expressions, and received
call results. Path-sensitive control dependence and pointer/alias resolution are
separate CFG/data-flow gates and must not be inferred from existing read/write
occurrences.

The accepted target is one common compiler-analysis stage owned here. Review
will derive its compatibility inventory from the shared result, while graph
views and graph-only execution consume the same snapshot. The current branch
has not completed that migration yet: `repo_review.analysis` still performs its
legacy parse separately.

## Optional LLVM flow command

`src/code_intelligence/flow.py` owns source selection, compiler invocation,
provenance and fresh-directory output. `extraction/llvm_api.py` owns verified
native LLVM 22 module access and disposal. `extraction/llvm_flow.py` joins AST
functions, traverses blocks/instructions/operands and solves reaching definitions
for direct non-escaping allocas. `views/flow.py` makes exact CFG/DFD projections.
The [flow contract](../contracts/flow-evidence.md) owns serialized meanings and
limitations; [D033](../decisions/D033-llvm-flow-evidence.md) owns engine rationale.

The command is a bounded C analysis capability, not full alias/interprocedural
flow. It does not enable the old UI overlays or modify old run artifacts.
Verification is in `tests/test_code_intelligence_flow.py` and retained-run evidence
in [testing and replay](../engineering/testing-and-replay.md).
