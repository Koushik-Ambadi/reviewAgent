# Project-Specific Rules

- Status: living
- Project identity: repository review agent
- Last reviewed: 2026-10-26
- Shared baseline: `skills` `main` at `d5b8fa3`
- Reset policy: replace this file when a different project is initialized; do
  not copy these rules into another repository.

## Active rules

### PRJ-001 -- Keep the established engineering-record grouping during transition

- Status: active compatibility exception
- Added: 2026-10-26
- Source: root `AGENTS.md` documentation ownership rules and D024.
- Applies to: `docs/engineering/`, `docs/contracts/`, `docs/standards/`,
  `docs/modules/`, and all inbound documentation links.
- Shared rule and revision: `d5b8fa3` cross-project conformance and canonical
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
