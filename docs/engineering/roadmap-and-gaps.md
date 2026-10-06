# Current Capabilities, Limitations, and Roadmap

- Status: living
- Owner: project maintainer
- Created: 2026-10-06
- Last reviewed: 2026-10-06
- Update trigger: gap resolved/discovered, user priority changes, or gate closes
- Source of truth for: current project-wide limitations and future engineering gates
- Does not own: rule-by-rule compliance backlog; see
  [`review-check-catalog.md`](../standards/review-check-catalog.md)

## Capability snapshot

| Area | Present now | Evidence | Boundary |
|---|---|---|---|
| Source ingestion | Local directory and ZIP into isolated run workspace | `orchestrator/ingestion`; commits `62f1792`, `4217116` | No Git/S3/Bitbucket adapter; ZIP safety controls absent |
| Repository structure | Tree construction and required-path cases | current structure stage | Other validator modules exist but are not wired into current runner |
| Build-aware analysis | CMake/Ninja compilation database | analysis source-index module; retained runs | Requires configurable CMake project and local tools |
| C symbol inventory | functions, variables, parameters, structs, enums, typedefs, macros, arrays | libclang modules; retained `symbols.json` | Only translation units in compile DB/target folders; limited diagnostics persistence |
| Naming checks | 8 families with atomic policy rules plus specialized global/array grammar | policy v4; check modules; `c603a69` audit | Manual semantic/provenance rules remain unresolved |
| Result contract | Typed Run/Stage/Check/Case hierarchy and JSON v2 | contracts/reporting; retained reports | No schema file/runtime validation/migration framework |
| Web UI | Upload, simulated progress, report filtering/search, build output | static UI; `0269843` | No automated browser test or real stage telemetry |
| Agent interface | Compact upload summary and detailed retained-run failures | agent API/service | Large legacy compatibility layer; remote MCP not in repo |
| Firmware build | Reuse reviewed run and capture batch output | build API and `repo_build` | Windows `.bat` only; no isolation/auth/persistence |
| Deployment | Linux Docker image for review service | Dockerfile; `6947306` | Uses reload; build endpoint incompatible with Linux container |
| Documentation | Rulebook, catalog, contract, policy audit, engineering evidence suite | `docs/` | Must be updated with future contract/architecture changes |

## Current limitations and risks

### Critical security boundary

- Uploaded ZIPs are extracted with `ZipFile.extractall` without validating
  member paths, absolute paths, links, entry counts, or expanded size.
- Uploads are read fully into memory and have no configured size limit.
- Run IDs and policy names become filesystem path components without strict
  identifier validation.
- The service has no authentication or authorization.
- The build endpoint executes a script from uploaded/untrusted repository
  content on the host with service permissions.
- Workspace copies can include `.git`, credentials, proprietary artifacts, or
  nested repositories; no redaction/classification is applied.

These are evidence-backed risk observations, not proof of exploitation. The
service should not be exposed to untrusted users until the boundary is designed
and tested.

### Correctness and contract gaps

- Pipeline exceptions abort rather than creating `ERROR` stage/run results.
- `RunStatus.COMPLETED` does not distinguish compliance failure from pass.
- Analysis produces skipped-file reasons in memory but does not persist them in
  the report; missing coverage can be invisible to consumers.
- The policy is accessed by raw dictionary keys with no schema validation.
- Case IDs include list index and source location, limiting long-term stability.
- Only required-path validation is active, despite additional structure modules.
- Global-name parsing has a specialized implementation separate from the atomic
  rule engine.
- Report compatibility supports both schemas but has no deprecation criteria.

### Reproducibility and evidence gaps

- No run manifest, code revision, input/policy checksum, exact command, tool
  version, or dirty-worktree flag.
- Ignored runs have no retention/cleanup/export policy.
- Two partial runs lack report/error logs.
- No compact version-controlled C fixture or expected report.
- Current manual tests are stale and machine-specific; no CI exists.

### Portability and operations gaps

- Workspace/static/upload roots depend on process working directory.
- Docker review path is Linux; build path is Windows-only.
- `--reload` is enabled in the container command.
- Request handlers execute blocking filesystem, CMake, libclang, and build work
  synchronously; there is no job queue, cancellation, timeout, or resource quota.
- CMake analysis deletes and recreates the run build directory without atomic
  completion markers.
- No health/readiness endpoint, structured logs, metrics, tracing, or run-state
  API.
- No cleanup for old workspaces/uploads and no disk-capacity policy.

### Maintainability gaps

- `review_service.py` owns upload flow plus two report generations and duplicate
  helper definitions.
- Policy loading exists in both application and review layers.
- Several source header comments still name former file locations.
- `requirements.txt` includes the historical MCP stack and transitive packages;
  direct versus optional dependencies are not separated.
- `pyproject.toml` contains minimal project metadata and no console entry point,
  dependency groups, formatter/linter/type/test configuration beyond Black and
  pytest path.

### Compliance coverage gaps

The active automation is a small subset of the 211-rule source inventory. The
authoritative detailed backlog is the check catalog. Major absent families are:

- file/module pairing, section order, and header/API quality;
- lexical formatting, whitespace, indentation, and comments;
- declarations, types, qualifiers, casts, and initialization;
- function design, function-like macro safety, and visibility;
- expressions, conditionals, switches, loops, and prohibited control flow;
- concurrency/ISR/hardware rules;
- call/control-flow/dependency graphs and code metrics;
- MISRA/static-analysis import and deviation evidence;
- process/governance evidence requiring human or external artifacts.

The existing catalog correctly separates deterministic, repository-level,
semantic, manual, configuration-dependent, and decision-blocked rules. New
checks should preserve that distinction.

## Roadmap gates

### G01 — Secure the ingestion and execution boundary

- Priority: P0 before untrusted or organizational multi-user exposure
- Goal: no uploaded path or script can escape its run sandbox or consume
  unbounded service resources.
- In scope: safe archive member validation, expanded-size/entry/file limits,
  strict run/policy identifiers, authentication/authorization, build isolation
  or disablement, timeouts, resource quotas, and security tests.
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
- Enables: organizational audit, comparisons, regression baselines, content
  claims, and safe cleanup/export.

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
        `--> G07 structure checks --> G08 analysis foundations --> G09 rule expansion
```

Security, provenance, and regression protection should precede a large increase
in check count. That ordering protects the project's strongest current asset—the
build-aware symbol/check pipeline—from becoming harder to trust as scope grows.
