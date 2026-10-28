# Graph Workspace API Contract

- Status: living, initial read-only workspace contract
- Created: 2026-10-28
- Source of truth for: graph workspace scopes, layer availability, selector
  semantics, and API response boundaries
- Does not own: canonical graph serialization, extraction completeness, or UI
  visual styling
- Related: [canonical graph contract](code-intelligence-graph.md),
  [capability matrix](graph-capabilities.md), and
  [D028](../decisions/D028-layered-graph-workspace.md)

## Endpoints

`GET /api/graphs/catalog` lists the newest graph-bearing run for each module so
the workspace can inspect retained evidence without relying on browser session
state.

`GET /api/runs/{run_id}/graphs` returns a projection from one canonical run
artifact. Query parameters:

- `scope=module|file` selects the abstraction level;
- `file=<repository-relative-path>` selects a repository-owned file for file
  scope; omission selects the first deterministic path;
- repeated `layers=<id>` parameters select one or more available overlays.

`GET /api/graphs/inter-module` selects the newest graph-bearing run for each
module. Repeated `modules=<name>` parameters select a subset. Repeated `layers`
parameters use the same overlay vocabulary.

`GET /api/runs/{run_id}/graphs/nodes` returns the searchable graph-node index
for the expandable trace playground.

`GET /api/runs/{run_id}/graphs/neighborhood` accepts `node_id`,
`direction=incoming|outgoing|both`, and repeated `layers`. It returns the
canonical center, directly related canonical nodes, and aggregated occurrence
edges across the whole run graph, independent of an overview file selection.

Both endpoints are read-only. A missing run or graph returns 404. Unsafe run
IDs, unknown files, scopes, or unavailable layers return 400.

## Scope semantics

| Scope | Nodes | Relationships | Intended question |
|---|---|---|---|
| File | Functions by default; optional globals, parameters, locals, and macros | Selected call/access/include occurrences; ownership remains inspector structure | What is the file's functional skeleton and what does each function touch? |
| Module | Repository-owned files in one run | Aggregated call/include/read/write/reference evidence between files | Which internal files depend on or exchange signals with each other? |
| Inter-module | Latest graph-bearing run per selected module | Matching stable symbol identities observed across module boundaries | Which modules call, read, or write interfaces owned by another module? |

Module and inter-module edges contain an occurrence `count`, bounded signal
names, and up to 50
`interactions` naming the underlying source/target symbols and source location.
Inter-module nodes expose `inputs` and `outputs` derived from
cross-module reads and writes. These directions describe compiler observations,
not calibrated physical I/O or runtime timing.

## Layer contract

Available overlays are `calls`, `includes`, `reads`, `writes`, and `references`.
They may be combined. Relationship controls do not remove node kinds. Separate
file-detail controls can promote globals, parameters, locals, or macros to
canvas nodes; parameters and locals remain available under their owning
function when not promoted.

Selection is a focus operation: the selected node is centered, incident edges
and one-hop nodes retain emphasis, and unrelated nodes/edges are dimmed. A
selected aggregate module edge exposes its bounded underlying interactions.
Parallel relationship kinds use deterministic lanes and type-specific color or
dash styles. Identical source-kind-target occurrences aggregate into one edge
with a count and bounded location list. Arrowheads terminate at node boundaries;
hover exposes relation, direction, endpoints, and occurrence count.

File-projection node payloads may contain bounded `declarations`, `definitions`,
`incoming_interactions`, and `outgoing_interactions`. Each interaction includes
its relation kind, endpoint IDs/labels/kinds, and source location. These lists
are cross-file symbol evidence for inspection, not execution-ordered traces.

## Trace playground contract

The client may create multiple visual instances for one canonical node. Every
instance carries `canonical_id`; instance IDs are presentation-local and must
never be persisted as analysis identities. Double-click expansion is bounded to
depth 20 to prevent accidental cycling, but does not silently truncate a
neighborhood's relationship groups. Collapsing removes only the instance's
descendants. Edge direction and occurrence evidence remain canonical even when
the same symbol appears in several branches.

`control_flow` and `data_flow` are advertised with `available: false` and an
evidence-gate explanation. The workspace must render them disabled rather than
return an empty graph that could be mistaken for complete analysis. Current
reads/writes are conservative syntax-context facts, not definition-use data
flow.

## Completeness boundary

- Only canonical schema 1.1 graph artifacts are consumed.
- Cross-module matching requires identical stable symbol IDs. Missing matches
  are unavailable evidence, not proof that modules are isolated.
- Indirect calls, alternate preprocessor/build configurations, CFG, aliases,
  pointer targets, and runtime signal values remain incomplete or unavailable.
- Every response carries graph provenance or identifies the selected run so the
  source artifact remains inspectable.
