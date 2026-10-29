# Project Conversation Provenance and Design Evolution

- Status: living evidence map
- Created: 2026-10-27
- Last reviewed: 2026-10-27
- Source of truth for: saved-conversation provenance, extracted design evolution,
  superseded conversation proposals, and refresh limitations
- Does not own: current architecture, accepted decisions, roadmap priority, or
  implementation contracts
- Machine-readable source inventory: [conversation-sources.json](conversation-sources.json)

## Source and confidence boundary

The project owner identified the private ChatGPT project at the URL recorded in
the source inventory as the continuing design discussion for this repository.
On 2026-10-27 the authenticated project view listed ten conversations. Four
threads were selectively inspected: `Code Review Pipeline Design`,
`reviewHighLevel`, `Pipeline Stabilization Strategy`, and
`Code Intelligence Design Graphs`.

This is a partial capture. No authenticated export API or page-provided WebMCP
tool was available. The repository therefore retains stable conversation IDs,
titles, concise engineering conclusions, and an explicit completeness
boundary—not a transcript. Content hashes remain null until a user-authorized
ChatGPT export or normalized complete capture is passed through the
project-local refresh helper.

Conversation statements are classified as recorded user direction, assistant
proposal, observed implementation, or superseded direction. Current code,
tests, accepted decisions, and the latest user request remain authoritative.

## Evolution reconstructed from conversations and repository evidence

1. **Regex prototype to compiler-backed inventory.** The project began with
   source-pattern experiments and evolved into compilation-database-driven
   libclang extraction. D001 and D002 own the accepted current boundary.
2. **Monolith to responsibility-based pipeline.** The early pipeline discussion
   separated ingestion, isolated run workspaces, AST analysis, checks,
   reporting, and optional vendor build. The repository now implements these as
   `orchestrator`, `repo_review`, and `repo_build` rather than the exact draft
   folder names proposed in chat.
3. **Build remains optional and separate from review.** The early instruction
   to defer build was a sequencing choice, not abandonment. Build was later
   implemented under `repo_build`; compile-database generation remains analysis
   input rather than a firmware build.
4. **Local MCP proved the boundary, then left this repository.** Phase-one
   discussion recorded a working standalone adapter over HTTP. Git evidence and
   D007 show the bundled implementation was subsequently removed in favor of a
   remote boundary. The missing external implementation is not represented as
   current repository capability.
5. **Policy became both execution and guidance contract.** Conversation plans
   proposed exposing policy read-only to agents so code generation and review
   share one rule authority. Current policy/report work implements parts of
   that direction; remote MCP exposure remains a gated external integration.
6. **Remediation moved from deferred to implemented prototype.** Early design
   explicitly postponed remediation. Later repository work added bounded,
   observable model-backed candidates while retaining deterministic validation
   and keeping automatic source mutation out of scope.
7. **Inventory to code intelligence.** The `reviewHighLevel` thread proposed
   independent symbol, relationship, semantic, and flow layers. It first
   recommended separate graph artifacts and keeping the work inside
   `repo_review/analysis` until another consumer appeared.
8. **Unified graph superseded graph-specific storage.** The latest
   `Code Intelligence Design Graphs` direction rejected storing separate graph
   files as authorities. It selected one node/edge knowledge graph with
   graph-specific views, stable clang USRs where available, deterministic
   fallback identities, and an eventual shared `code_intelligence` capability.
   The current request confirms that this graph work is now active.

## Current vision carried forward

- Treat repository intelligence as a versioned asset; review and build are
  events that consume it.
- Preserve compiler-derived facts and their provenance. Do not let model output
  become source truth, compliance verdict, or graph authority.
- Store one canonical node/edge representation. Call, include, module,
  reachability, impact, and later semantic/flow graphs are deterministic
  projections or analyses over that representation.
- Start with a complete, meaningful path through files, functions, includes,
  and calls. Retain structs, enums, typedefs, globals, and macros as first-class
  nodes so the foundation does not repeat the old count-only limitation.
- Extend extraction without changing the existing symbol inventory contract.
  Adopt stable identities and explicit unresolved relations before adding
  higher-level graph claims.
- Defer semantics, control/data flow, scheduler/ISR interpretation,
  requirement/test traceability, timing, stack, failure propagation, cloning,
  and learned predictions until their required evidence is available.

## Superseded or abandoned directions

- One JSON authority per graph type is superseded by the unified graph.
- Names alone are rejected as symbol identity; use clang USR first and a
  deterministic kind/path/name fallback with an explicit stability limit.
- Copying the existing symbol-inventory implementation wholesale into a new
  package is rejected. Knowledge may be reused, while the existing inventory
  remains compatibility-owned by naming checks.
- A bundled local MCP package is historical. Remote MCP compatibility remains a
  future contract, not current functionality.
- Exact chat-proposed folder layouts were proposals. Current repository
  boundaries and accepted decisions control unless a new decision changes them.
- Time estimates from `Pipeline Stabilization Strategy` are historical planning
  artifacts and are not active commitments.

## Refresh procedure and limitation

The local `reviewer-conversation-context` skill owns the refresh workflow. Its
helper accepts a ChatGPT data export or normalized JSON capture, computes
canonical SHA-256 identities over normalized messages, and reports added,
changed, unchanged, and missing conversations. It deliberately does not scrape
or authenticate to ChatGPT. Browser enumeration is still required to discover
new project chats; a complete export is required before content hashes can be
used as reliable change detectors.

## 2026-10-29 shared discussion refresh

Read the user-provided shared conversation `Application Features Identified`
(`6ae36bdc-d418-83e8-9a64-5b3f1ff2ec66`) in the already-open browser tab. This
is rendered discussion evidence, not an authenticated project enumeration or
complete export. The original attachment was not imported. Current user direction
accepts graph/analytics exploration, excludes requirements workflows, and
explicitly defers version comparisons. Older suggestions to prioritize requirements
are therefore superseded for this increment. Runtime, tests, model mappings and
learned predictions still require their stated evidence; no results are invented.

Browser access became available later on 2026-10-29. The exact shared URL was
opened again and its current-snapshot feature list checked against the guided
workspace. The rendered discussion and the `Application Features Identified`
project chat agree on the graph/analytics categories. The attachment remains
unimported, so this is still a partial capture without a content hash.
