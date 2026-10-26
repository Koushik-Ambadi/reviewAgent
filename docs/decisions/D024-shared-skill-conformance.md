# D024 -- Adopt Published Shared-Skill Conformance

- Date: 2026-10-26
- Status: accepted
- Scope: documentation routing, shared-skill baseline, contribution feedback,
  and technical-skill activation for this repository.
- Trigger: the project indexed an earlier skills proposal (`b3a619d`) as its
  standard, while the shared repository had advanced to published `main`
  revision `d5b8fa3` containing that proposal plus cross-project conformance,
  technical-knowledge capture, and structured-LLM reliability guidance.
- Evidence: shared repository `main` at `d5b8fa3`; the project documentation
  index, root project policy, existing decision index, and current remediation
  module records.
- Constraints and decision drivers: preserve stable project links and decision
  IDs; adopt approved shared guidance rather than a proposal; avoid a broad
  documentation relocation during Git-branch consolidation; keep model output
  constrained by deterministic validation and evidence boundaries.
- Assumptions and unknowns: the existing `docs/engineering/` grouping is an
  intentional local convention because the root project policy names those
  owners. Its future migration cost has not been independently measured.
- Options considered: keep the proposal hash as the baseline; move every
  engineering record to the shared fallback paths now; or adopt published
  `main` and record a bounded compatibility mapping.
- Selection criteria: traceable baseline, no broken links or duplicated owners,
  minimal unrelated churn, and a clear route for reusable feedback.
- Decision: adopt `d5b8fa3` as the approved shared baseline. Keep
  `docs/decisions.md` as the canonical decision index, preserve D001-D023
  compatibility links, create `project/review-agent` as the persistent shared
  skills contribution branch, and record PRJ-001 for the existing engineering
  layout. Load `structured-llm-reliability` only for model-remediation changes.
- Rejected alternatives and why: proposal-only pinning was no longer current;
  a mass rename would add link and review risk without advancing the next
  engineering phase; applying the model skill to unrelated code would add
  unnecessary context.
- Consequences and trade-offs: future shared-skill updates require a scoped
  conformance check. The layout remains a documented compatibility variation
  until a dedicated migration is approved. Future reusable findings are proposed
  from the persistent contribution branch rather than written directly to shared
  `main`.
- Reconsideration trigger: root policy changes, a dedicated documentation-topology
  migration, a shared revision that removes this bounded variation, or a
  remediation/build-model change that exposes a missing shared reliability rule.
- Implementation references: [documentation index](../README.md#shared-skill-conformance),
  [project rules](../project-rules.md), and the shared
  [`structured-llm-reliability` skill](../../skills/structured-llm-reliability/SKILL.md).
- Validation: documentation-relative link validation and Git ancestry review;
  no application behavior changed.
- Supersedes / superseded by: replaces the project’s proposal-only baseline
  reference; does not supersede D001-D023.
