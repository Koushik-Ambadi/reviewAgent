# Engineering Roadmap

- Status: living
- Created: 2026-10-06
- Last reviewed: 2026-10-13
- Update trigger: priority, dependency, acceptance evidence, or gate status changes
- Source of truth for: future engineering gates and their ordering
- Does not own: current behavior, module constraints, test status, or rule-level
  coverage

This roadmap contains future work only. Its gates are derived from current facts
in the authoritative records below; those records must be updated when a fact
changes. Do not maintain a second project-wide gap inventory here.

## Evidence sources

- [`architecture.md`](architecture.md) owns current modules, interfaces, flows,
  technology, operational boundaries, and implementation constraints.
- [`testing-and-replay.md`](testing-and-replay.md) owns current verification,
  retained-run provenance, reproducibility constraints, and missing test layers.
- [`../contracts/run-result.md`](../contracts/run-result.md) owns the serialized
  result contract and compatibility boundary.
- [`../standards/review-check-catalog.md`](../standards/review-check-catalog.md)
  owns rule-by-rule coverage and implementation readiness.
- [`decisions-and-lessons.md`](decisions-and-lessons.md) owns accepted choices,
  unresolved decisions, problems, and their evidence.

## Roadmap gates

### G01 — Secure the ingestion and execution boundary

- Priority: P0 before untrusted or organizational multi-user exposure
- Goal: no uploaded path or script can escape its run sandbox or consume
  unbounded service resources.
- In scope: safe archive member validation, expanded-size/entry/file limits,
  strict run/policy identifiers, authentication/authorization, build isolation
  or disablement, timeouts, resource quotas, and security tests.
- Known defect: [BUG-001](known-issues.md#bug-001--windows-zip-extraction-fails-on-overlong-nested-git-paths)
  requires selective extraction, `.git` exclusion, Windows target-path
  preflight, bounded archive policies, partial-workspace cleanup, and typed 4xx
  error mapping.
- Out of scope: new coding-standard checks.
- Acceptance evidence: malicious archive/path test suite; build threat model;
  authorization tests; documented limits; container/OS sandbox proof.
- Enables: credible hosted use.

### G02 — Establish durable run provenance

- Priority: P0 for “proof of work” and replay use case
- Goal: every run can be mapped to input, code, policy, environment, command,
  output, and completion/failure.
- In scope: `run.json` manifest, hashes, tool versions, revision/dirty flag,
  stage timestamps/state, skipped files, errors, output hashes, atomic writes.
- Acceptance evidence: schema and contract tests; reconstruct a fresh run from
  manifest; explicitly mark non-reproducible external inputs.
- Enables: organizational audit, comparisons, regression baselines, traceable
  derived claims, and safe cleanup/export.

### G03 — Create an automated quality baseline

- Priority: P0 before broad check expansion
- Goal: current behavior is protected by fast local tests and one clean
  end-to-end fixture.
- In scope: repair/remove stale manual scripts, unit tests for atomic/specialized
  validators, policy schema, report contract, small CMake fixture, API tests,
  container smoke test, CI on supported platforms.
- Acceptance evidence: documented commands pass from a clean checkout; failures
  return nonzero; CI retains report/test artifacts.
- Enables: refactoring, dependency cleanup, new rule families.

### G04 — Finish result/error semantics and compatibility migration

- Priority: P1
- Goal: consumers can distinguish execution success, policy compliance, partial
  coverage, and failure without reading implementation details.
- In scope: stage diagnostics, `PARTIAL`/`ERROR` propagation, compliance outcome,
  report schema file, legacy consumer inventory and removal date, API response
  models.
- Acceptance evidence: contract tests for pass/fail/skip/error/partial and old
  report fixtures through the adapter.
- Enables: stable external integration and remote MCP versioning.

### G05 — Make operations explicit and portable

- Priority: P1
- Goal: review/build behavior is predictable on supported environments.
- In scope: absolute configuration-root resolution, development versus
  production Docker commands, health/readiness, job execution with cancellation
  and timeouts, workspace cleanup, structured logs, supported build adapters.
- Acceptance evidence: Windows/Linux support matrix and clean-container smoke
  tests; interrupted-run recovery; retention tests.
- Enables: production deployment and concurrent use.

### G06 — Reduce compatibility and dependency debt

- Priority: P1 after tests
- Goal: each concern has one owner and only required dependencies ship.
- In scope: split upload workflow from legacy/current report adapters, remove
  duplicate helpers, unify policy loading, correct stale comments, identify
  direct/optional dependencies, remove unused MCP stack from this service if the
  remote integration no longer needs it.
- Acceptance evidence: unchanged contract fixtures and passing end-to-end test;
  dependency import/license/security scan.
- Enables: easier maintenance and smaller attack surface.

### G07 — Activate remaining deterministic structure checks

- Priority: P2
- Goal: connect already-present structure capabilities through the typed result
  contract.
- Dependencies: G03/G04; confirm policy fields and expected semantics.
- In scope: forbidden paths/extensions, allowed extensions, file types, sizes,
  and tree limits.
- Acceptance evidence: one `CheckResult` per enabled capability; empty config
  means skipped/not configured, never false pass.
- Enables: higher repository-governance coverage with low semantic ambiguity.

### G08 — Expand source analysis foundations

- Priority: P2
- Goal: provide durable analysis artifacts required by the next rule families.
- In scope: token/comment inventory, include/dependency graph, call graph,
  control-flow graph, provenance for generated/third-party symbols, parse
  coverage diagnostics.
- Acceptance evidence: graph/schema contracts, representative C fixtures,
  coverage/diagnostic metrics, deterministic IDs.
- Enables: metrics, dead-code signals, impact analysis, interface checks, and
  semantic review assistance.

### G09 — Implement coding-standard families incrementally

- Priority: P2/P3 according to organizational value and evidence readiness
- Goal: expand beyond naming without claiming unsupported compliance.
- Sequence: deterministic lexical/file rules; declaration/type rules; function
  and control-flow rules; graph metrics; static-analysis imports; manual evidence
  workflows.
- Acceptance evidence per check: source rule mapping, applicability/exceptions,
  policy schema, hand-checkable fixtures, actionable atomic reasons, typed result,
  catalog/audit update.
- Detailed source: check catalog sections 4–11 and its definition of ready.

### G10 — Reconnect external agent integration through a versioned contract

- Priority: P3 unless an active consumer raises it
- Goal: document and test the HTTP/report interface expected by remote MCP.
- In scope: external consumer inventory, API/schema version, authentication,
  compact response contract, integration test, ownership/deployment link.
- Acceptance evidence: remote tool test pinned to service/report versions.
- Enables: reliable agent automation without re-bundling MCP concerns.

### G11 — Graduate planned workspace capabilities

- Priority: P3 after the supporting security, provenance, test, result-semantic,
  and operational gates are complete
- Goal: replace the inert Roadmap tab with trustworthy developer and manager
  workflows rather than disconnected prototype controls.
- Dependencies: G01–G05; G10 where an external agent performs an action.
- In scope: governed pull-request and approval workflow; multi-run/project
  comparison; validated selectable profiles and project-specific build adapters;
  optional model-assisted analysis for failures not covered by deterministic
  classifiers.
- Required boundaries: deterministic analysis remains first; model output keeps
  evidence and provider provenance; multi-run filters stay out of a single-run
  report; approvals require actor identity and authorization; profile selection
  requires schema/version ownership.
- Acceptance evidence: role and authorization tests, profile schema/fixtures,
  run-comparison contract, provider-independent assisted-analysis contract, and
  end-to-end UI tests proving planned labels are removed only when controls work.
- Current UI status: the developer Roadmap remains inert. A separate shallow
  manager preview now reads persisted reports and demonstrates portfolio,
  comparison, exception-selection, ownership/ticket, audit, and insight layouts.
  Its workflow values and actions are explicitly non-persistent placeholders;
  this does not satisfy the production acceptance evidence above.
- Remediation prototype status (2026-10-16): the developer report has a
  provider-independent candidate/context workflow with deterministic preflight,
  strict model output, persisted provenance, and explicit unsupported cases.
  This is a G11 experiment, not graduation. Source-context enrichment,
  immutable policy snapshots, supported-model selection and evaluations,
  repository-wide collision/reference discovery, authorization, approved patch
  generation, and end-to-end browser/provider tests remain gated work.

### G12 — Govern symbol inventory audits

- Priority: P3 after G02-G04 and the identity/authorization parts of G11
- Goal: turn identified symbol records into a durable, reviewable audit scope
  without weakening the distinction between extraction and compliance.
- Current baseline: report version 2.2 records parsed/skipped coverage,
  symbol-family counts, and individual grouped artifacts initialized as not
  audited. The register is read-only and has no actor or decision history.
- In scope: stable cross-run symbol identity, audit policy and scope, reviewer
  and approver roles, authorized state transitions, persisted decisions and
  evidence, inventory reconciliation, and manager aggregation.
- Required boundaries: declaration/definition duplicates must be resolved by an
  explicit identity rule; skipped-file causes remain visible; pending approval
  is not treated as audited; historical decisions retain actor and policy
  versions; aggregate totals derive from the same persisted records; large
  inventories use pagination or virtualization rather than an unbounded DOM.
- Acceptance evidence: identity fixtures across source changes, authorization
  and transition tests, replayable decision history, skipped-file reconciliation,
  and developer/manager end-to-end audit summaries.

## Product workflow evolution

The current product has two deliberately different scopes:

1. The developer workspace owns one active run: report, remediation, build, and
   evidence-pack actions remain attached to that run ID.
2. The manager workspace derives a cross-run portfolio from the same
   `report.json` records. It may compare runs and stage proposed work, but it
   cannot approve, assign, create a ticket, or mutate delivery state.

The next product gate is not another visual tab. It is a governed workflow
contract: authenticated roles, authorized transitions, durable owner/ticket and
approval records, external issue/PR/CI identities, audit events, idempotent
retries, pagination/retention behavior, and end-to-end verification. Only after
that gate should preview labels be removed or manager actions transmit data.

Intelligence should evolve through the existing insight wrapper: deterministic
classifiers and policy-derived remediation first, then optional model-generated
analysis with evidence, provider/model provenance, confidence/uncertainty, and
human-review boundaries. The canonical run record remains the evidence source;
the intelligence layer must not silently replace or recalculate it.

## Proposed priority order

```text
G01 security + G02 provenance
        |
        v
G03 automated baseline
        |
        +--> G04 result semantics --> G10 external agent contract
        +--> G05 operations/portability
        +--> G06 debt reduction
        +--> G07 structure checks --> G08 analysis foundations --> G09 rule expansion
        +--> G11 planned workspace capabilities (after G01-G05)
        `--> G12 symbol inventory audits (after G02-G04 and G11 identity/roles)
```

Security, provenance, and regression protection should precede a large increase
in check count. That ordering protects the project's strongest current asset—the
build-aware symbol/check pipeline—from becoming harder to trust as scope grows.
