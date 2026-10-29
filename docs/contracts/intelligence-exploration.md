# Current-snapshot exploration API

`GET /api/intelligence/catalog` lists latest graph-bearing runs, symbols, modes,
flow attachments and gates. `POST /api/intelligence/query` accepts `modules`
(names, at most 20), `mode`, `selected` (at most 20 catalog IDs), `depth` (1–12),
`limit` (1–300), and optional forbidden dependencies `rules: [{"from":"A","to":"B"}]`.
Empty modules selects nothing; omitted modules selects all.

Schema `1.0` returns nodes, edges, paths, analytics, coverage, notes, snapshot
hashes and flow evidence. IDs are run-qualified; `canonical_id` retains source
identity. Grouped edges retain evidence IDs. Cross-module edges retain
`declaration_target`; only unique exact public compiler USRs and compatible types
resolve. Same names, static symbols and ambiguous definitions never join.

Connection paths are undirected associations with original arrows. Influence
reverses calls/reads: caller depends on callee, reader on value. Writes propagate
to values. Neither establishes execution order. Search returns frontier, omitted
counts and budgets; `not_found_within_scope_and_budget` is not proof of absence.
CFG/DFD retain D033's lowered IR and bounded memory meanings.

`GET /api/intelligence/context?node_id=...` returns bounded source (300 lines /
24,000 characters), relationships and source-matched AST regions (500 regions /
12,000 cursors). Paths must resolve inside the selected repository, including
symlinks. Region IDs bind function, source hash, extent and kind. Nesting and
enclosing decision IDs describe containment, not true/false execution. Comparison
expressions produce boundary-test ideas, never executed or proven-feasible tests.

Attachments come from `workspace/runs/*/*/manifest.json`. Completed bundles must
name an input in the actual selected repository and match source, all compiler
inputs, graph, IR and preprocessed hashes. Conflicting configurations for one
source disable attachment. Same-configuration duplicates select latest manifest
mtime, then path. Integrity checks are separate from native LLVM semantic replay.
Legacy AST snapshots lack source-file hash binding; excerpts label this honestly.
No stored artifact is overwritten; attachment does not imply full module coverage.

Analytics: direct-call fan-in/out, SCC recursion, condensed longest call depth,
file cycles, readers/writers, exact token clones, compiler complexity, current
population IQR outliers, symbol-size sums and transparent review ordering.
Unknown metrics stay null. Depth is not stack depth; sizes are not target RAM;
shared writers are not races; scores are not defect probabilities. Architecture
violations require explicit supplied rules. Requirements are excluded; remaining
input gates and version analytics are in the roadmap.
