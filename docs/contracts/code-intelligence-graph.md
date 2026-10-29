# Code Intelligence Graph Contract

- Status: living, initial extraction contract
- Schema version: `1.1` for AST snapshots; `1.2` for opt-in LLVM flow
- Last reviewed: 2026-10-27
- Source of truth for: node, edge, identity, resolution, and source-location
  semantics for compiler-derived repository intelligence
- Does not own: review result schema, symbol inventory compatibility, graph
  persistence lifecycle, or higher-level semantic claims
- Capability coverage: [graph capability and evidence matrix](graph-capabilities.md)

## Canonical shape

The graph authority is one deterministic node/edge collection. Call, include,
module, reachability, call-depth, impact, and future views are projections; they
are not separate authoritative stores.

```json
{
  "schema_version": "1.1",
  "nodes": [],
  "edges": []
}
```

The AST boundary produces one `GraphFragment` per translation unit. Fragments
identify their translation unit and carry nodes, edges, and extraction
diagnostics. `KnowledgeGraph` merges fragments by stable identity, rejects
incompatible facts or dangling edges, and sorts all retained facts before
serialization.

## Nodes

The optional [flow evidence extension](flow-evidence.md) adds `basic_block`,
`instruction`, and `ir_value` nodes and `control_flow`, `def_use`, and
`memory_flow` edges. Existing AST-only serialization remains version 1.1.

Node kinds are `file`, `function`, `struct`, `enum`, `typedef`,
`global_variable`, `parameter`, `local_variable`, `field`, `enum_constant`, and
`macro`. Each node records:

- stable ID;
- kind and source spelling;
- optional source location and clang USR;
- definition state where clang exposes it;
- bounded attributes such as return/variable type, compiler-reported type size,
  external status, unresolved status, or versioned function metrics.

Function definitions retain `ast_cyclomatic_v1` complexity, statement count,
and a SHA-256 fingerprint over their exact clang body-token stream. These are
source estimates and clone candidates, not CFG complexity or semantic clone
proof. Anonymous symbols without a stable spelling are not emitted.

## Identity

Use a non-empty clang USR as the primary symbol identity:

```text
<kind>:usr:<clang-usr>
```

When clang supplies no USR, use:

```text
<kind>:fallback:<repository-relative-path>:[<scope>:]<name>
```

The fallback is deterministic but may not survive a rename or move. It is an
explicit compatibility boundary, not a claim of permanent semantic identity.
File nodes use normalized paths. External and unresolved references are labeled
and must not be mistaken for repository-owned definitions.

## Edges

Source and derived edge kinds are:

- `contains`: physical file ownership of a symbol occurrence;
- `declares`: file contains a non-definition declaration;
- `defines`: file contains a definition;
- `calls`: caller function invokes a referenced or unresolved callee;
- `includes`: source file includes a resolved or unresolved file.
- `parameter_of`, `field_of`, and `member_of`: scoped symbol ownership;
- `reads`, `writes`, and `references`: conservative AST-context access;
- `depends_on` and `clone_of`: projection-derived relationships.

Every edge references existing node IDs. Edge IDs are SHA-256 identities over
kind, source, target, and a source-occurrence discriminator. Resolution is one
of `compiler_derived`, `external`, or `unresolved`. Source location identifies
the observed occurrence; it is provenance, not part of symbol identity.

## Snapshot and views

The canonical snapshot contains schema version, sorted translation units,
nodes, edges, diagnostics, and caller-supplied provenance. Snapshot writing
requires `source_revision`, `dirty`, `producer`, and `producer_version`, writes
deterministic JSON bytes to a sibling temporary file, flushes them, and then
atomically replaces the target.

The review analysis stage writes the snapshot to
`analysis/code-intelligence.json` from the same parsed translation-unit cursors
used for the compatibility `symbols.json` inventory.

Call, include, reachability/depth, file-module dependency, changed-node impact,
variable access, exact-token clone, complexity, and memory-estimate views derive
from the canonical graph. They are runtime projections and are not written as
competing authorities.

## Compatibility and limits

This contract does not change `analysis/symbols.json`, which remains owned by
the existing naming and inventory workflow. The new extractor is additive.
Schema 1.1 does not claim complete indirect-call resolution, preprocessing
configuration equivalence, cross-translation-unit header deduplication,
CFG/data flow, semantic roles, authoritative linker/stack memory, final-binary
reachability, or an application runner that supplies snapshot provenance.
