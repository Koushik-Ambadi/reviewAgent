# Project-Specific Rules

- Status: living
- Project identity: repository review agent
- Last reviewed: 2026-10-26
- Shared baseline: `skills` `main` at `b800dfc` (locally resolved from
  `origin/main`; live fetch authentication was unavailable during this review)
- Reset policy: replace this file when a different project is initialized; do
  not copy these rules into another repository.

## Active rules

### PRJ-001 -- Keep the established engineering-record grouping during transition

- Status: active compatibility exception
- Added: 2026-10-26
- Source: root `AGENTS.md` documentation ownership rules and D024.
- Applies to: `docs/engineering/`, `docs/contracts/`, `docs/standards/`,
  `docs/modules/`, and all inbound documentation links.
- Shared rule and revision: `b800dfc` cross-project conformance and canonical
  documentation paths.
- Rule: retain the existing `docs/engineering/` owners for architecture,
  roadmap, testing/replay, known issues, evidence, and legacy decisions;
  `docs/decisions.md` remains the canonical decision entry point. Map the
  semantics in `docs/README.md` instead of creating duplicate top-level files.
- Rationale: these paths are explicitly named by the project policy and already
  own live records with inbound links. A mass relocation is unrelated to the
  current cleanup and would increase review and link-breakage risk.
- Owner: dedicated documentation-topology migration.
- Verification: the documentation index maps each owner; local Markdown links
  resolve; decisions link from `docs/decisions.md`; no duplicate active owner
  is created for the same fact.
- Review trigger: root policy changes, a dedicated migration is approved, or
  shared guidance introduces an incompatible semantic requirement.
- Related: [D024](decisions/D024-shared-skill-conformance.md) and
  [shared-skill conformance](README.md#shared-skill-conformance).

### PRJ-002 -- Reconcile saved project conversations when design context changes

- Status: active
- Added: 2026-10-27
- Source: current project-owner request.
- Applies to: architecture, feature planning, technical strategy, decisions,
  and project-history reconstruction.
- Rule: use the saved `reviewer` ChatGPT project as historical evidence when a
  task depends on prior design intent. Enumerate the project and compare the
  conversation manifest before re-reading unchanged threads; reconcile added or
  changed material into its normal documentation owner.
- Authority boundary: current user direction, current code and tests, and
  accepted decisions override older or conflicting chat proposals. Assistant
  suggestions remain proposals unless accepted or subsequently implemented.
- Privacy and retention: store stable source IDs, hashes, concise engineering
  extracts, and completeness limits. Do not commit full transcripts, secrets,
  credentials, or personal material.
- Verification: follow the repository-local
  `reviewer-conversation-context` skill and validate the manifest helper against
  a normalized fixture. Content-change detection requires a local export or
  complete capture; browser listing alone detects new conversation IDs only.
- Review trigger: the project link changes, a new conversation appears, a
  content hash changes, or ChatGPT exposes a supported authenticated export.
- Related: [conversation provenance](engineering/conversation-provenance.md).
