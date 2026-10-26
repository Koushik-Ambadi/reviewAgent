# Decisions

- Status: living index with legacy compatibility links
- Canonical standard: `docs/decisions.md` is the project decision entry point;
  substantial records belong under `docs/decisions/`.
- Shared proposal: `b3a619d2ae6347d64433b60bd80e7037df308555`
  on `project/skills-repository`.
- Migration state: D001-D023 retain their existing IDs and remain in the legacy
  combined record until each owning area is changed and migrated safely.

| ID | Decision | Status | Record |
|---|---|---|---|
| D001 | Use the real compilation database for C analysis | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D002 | Use AST plus targeted source-text recovery | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D003 | Process an isolated copied workspace | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D004 | Separate orchestration, review, and build ownership | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D005 | Prefer simple function stages over a generic stage framework | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D006 | Generate one full report and derive consumer views | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D007 | Move MCP to a separate remote boundary | Accepted; external implementation absent | [Legacy record](engineering/decisions-and-lessons.md) |
| D008 | Adopt hierarchical typed result contracts | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D009 | Make atomic naming rules policy-owned and source-linked | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D010 | Keep deterministic case identity within the report contract | Accepted with constraint | [Legacy record](engineering/decisions-and-lessons.md) |
| D011 | Keep one project voice and derive secondary views | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D012 | Deepen one run-scoped developer workspace before adding breadth | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D013 | Separate workspace navigation, context, actions, and future intent | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D014 | Keep the manager preview a read-only projection | Accepted temporarily at prototype maturity | [Legacy record](engineering/decisions-and-lessons.md) |
| D015 | Represent analysis inventory as evidence, not compliance | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D016 | Preserve every extracted artifact as an audit candidate | Accepted; supersedes part of D015 | [Legacy record](engineering/decisions-and-lessons.md) |
| D017 | Preflight and selectively extract review archives | Accepted design; implementation deferred | [Legacy record](engineering/decisions-and-lessons.md) |
| D018 | Generate a candidate or ask one narrow context question | Accepted prototype | [Legacy record](engineering/decisions-and-lessons.md) |
| D019 | Observe model remediation before optimizing its decisions | Accepted prototype | [Legacy record](engineering/decisions-and-lessons.md) |
| D020 | Compile report policy into a minimal model-facing view | Accepted prototype | [Legacy record](engineering/decisions-and-lessons.md) |
| D021 | Persist remediation as run → check → case → turn hierarchy | Accepted prototype | [Legacy record](engineering/decisions-and-lessons.md) |
| D022 | Route documentation from a high-level index to local module owners | Accepted | [Legacy record](engineering/decisions-and-lessons.md) |
| D023 | Proposed remediation hardening and evidence ownership | Proposed | [Legacy record](engineering/decisions-and-lessons.md) |
| D024 | Adopt published shared-skill conformance | Accepted | [Record](decisions/D024-shared-skill-conformance.md) |

New substantial decisions use `docs/decisions/DNNN-short-title.md` and are linked
from this table. Small decisions may be recorded directly here when a separate
lifecycle would add no value. Problems, lessons, tests, and chronology remain in
their own authoritative records.
