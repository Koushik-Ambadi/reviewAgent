# Reconstructed Decisions, Problems, and Lessons

- Status: append-only reconstructed decision record
- Created: 2026-10-06
- Last reviewed: 2026-10-13
- Update trigger: accepted/superseded decision or stronger historical evidence
- Source of truth for: consequential technical rationale and durable problems
- Does not own: daily chronology, current architecture, or future priorities

These records were created after the implementation. “Confidence” describes
the evidence for the rationale, not confidence that the decision was optimal.
No motive is attributed where the repository does not support it.

## D001 — Use the real compilation database for C analysis

- Date: 2026-05-25
- Status: accepted
- Confidence: high for decision; medium for original rationale
- Scope: source analysis
- Context: early AST prototypes parsed C and incrementally added symbols, but an
  embedded repository depends on defines, include paths, generated headers, and
  compiler flags.
- Evidence: `9755213` added CMake/Ninja compilation database generation;
  `extractor.py` now queries libclang `CompilationDatabase` per file; retained
  runs contain `analysis/cmake_build/compile_commands.json`.
- Options evidenced: standalone parse existed before this commit; compilation
  database became the selected path. No evidence of Bear, intercept-build, or a
  custom command manifest being evaluated.
- Decision: configure the target with CMake and parse each file with its recorded
  compile command after sanitizing target-specific arguments.
- Why: Inferred—this preserves more compilation context than filename-only
  parsing and supports realistic embedded projects.
- Consequences: analysis now requires CMake/Ninja and a configuration path that
  successfully emits a database; vendor flags still require sanitization.
- Validation: generated databases survive in six complete retained runs; exact commit
  and environment provenance are absent.

## D002 — Use AST plus targeted source-text recovery

- Date: 2026-05-17
- Status: accepted
- Confidence: high
- Scope: symbol intermediate representation
- Context: array bracket spelling and some declaration details were not exposed
  in the desired form by the prototype's cursor tokens.
- Evidence: `5fd77db` opens the AST-located source line and recovers `[...]`;
  current `symbol_extractors.py` retains source-assisted extraction.
- Options evidenced: cursor token extraction alone preceded the change. A full C
  concrete-syntax tree or preprocessor-preserving parser is not evidenced.
- Decision: treat libclang as the structural authority, then recover narrow
  lexical details from source at known locations.
- Consequences: pragmatic and build-aware, but multiline/macro-generated
  declarations need explicit cases and tests.
- Validation: later `symbols.json` artifacts contain `array_suffixes`; current
  array checks consume them.

## D003 — Process an isolated copied workspace

- Date: 2026-05-27, refined 2026-05-31
- Status: accepted
- Confidence: high
- Scope: run lifecycle and source safety
- Context: compilation and analysis generate directories/files and should not
  mutate a user's authoritative repository.
- Evidence: `c5a35aa` created run-scoped source/analysis paths; `62f1792` added
  ZIP workspaces; current local ingestion copies and ZIP ingestion extracts into
  `workspace/runs/<run_id>`.
- Decision: every review receives a timestamp/random run directory and works on
  a copied or extracted repository.
- Rejected/previous approach: operate directly on the local source root and
  check generated analysis output into the project history.
- Consequences: safer analysis and build sharing, at the cost of storage,
  cleanup/retention requirements, and missing authoritative-source linkage.
- Validation: eight retained workspaces exhibit this layout.

## D004 — Separate orchestration, review, and build ownership

- Date: 2026-06-02
- Status: accepted
- Confidence: high; contemporary rationale survives
- Scope: package boundaries
- Context: review previously handled ingestion, workspace lifecycle, checks,
  reporting, and build execution.
- Evidence: `4217116` moved ingestion/workspace to `orchestrator`, build to
  `repo_build`, and narrowed `run_review`; the
  [archived daily log](../archive/daily_log.txt) explicitly
  records the ownership split and single-workspace goal.
- Decision: orchestration prepares runs and resolves sources; `repo_review`
  receives an existing repository/workspace; `repo_build` executes firmware
  builds.
- Why: prevent duplicate extraction/workspaces and let review remain source-type
  agnostic.
- Consequences: cleaner domain boundaries; orchestration/report metadata become
  critical integration contracts.
- Validation: current imports follow this direction, though build resolution is
  coupled to `report.json` rather than a dedicated run manifest.

## D005 — Prefer simple function stages over a generic stage framework

- Date: 2026-05-30
- Status: accepted
- Confidence: medium-high
- Scope: review pipeline design
- Context: `d653e0a` introduced a generic stage class and separate ingestion,
  compile, AST, validation, and reporting stages.
- Evidence: `f435aea` deleted the stage abstraction, combined compilation and
  AST work under analysis, and used a fixed list of `run(context)` functions.
- Decision: keep a small explicit ordered pipeline until replaceable/dynamic
  stage behavior is required.
- Rejected/previous approach: generalized stage base layer and finer-grained
  orchestration.
- Consequences: lower ceremony and easier reading; no conditional stage graph,
  structured recovery, or plugin registration.
- Validation: the current four-stage list remains small and direct.

## D006 — Generate one full report and derive consumer views

- Date: 2026-07-28, refined 2026-10-05
- Status: accepted
- Confidence: high
- Scope: web/agent reporting
- Context: humans/UI need the full hierarchy; agents need concise actionable
  failures; the local MCP layer had been removed.
- Evidence: `5984863` added compact/detailed agent endpoints while preserving
  persisted reports; `97084dd` added `RunResult` traversal; UI and agents both
  consume the same stored report.
- Decision: persist canonical full results and derive compact agent responses at
  the service boundary.
- Consequences: no duplicated analysis run; compatibility logic grew large and
  still supports legacy `sections` reports.
- Validation: current endpoints branch on `stages` and retained reports include
  both legacy and new schemas.

## D007 — Move MCP to a separate remote boundary

- Date: 2026-07-17
- Status: accepted, external implementation not present here
- Confidence: high for boundary; low for detailed rationale
- Scope: agent integration and deployment
- Context: local MCP server, tools, skills, client, and formatters were added on
  9 July.
- Evidence: `f0d40b9` deleted the complete `review_mcp` package with subject
  “seperated mcp layer moved to remote mcp.”
- Decision: keep this repository focused on the review HTTP service; host MCP
  elsewhere.
- Alternatives: bundled local MCP is evidenced by prior commits. No record of a
  plugin, sidecar, or shared package alternative.
- Consequences: deployment concerns can evolve independently; this repository
  cannot reproduce the complete agent stack, and stale MCP dependencies remain.
- Unknown: remote location, interface version, security model, and deployment
  evidence.

## D008 — Adopt hierarchical typed result contracts

- Date: 2026-08-07
- Status: accepted
- Confidence: high
- Scope: checks, reporting, UI, and agent interfaces
- Context: ad hoc issue dictionaries made check extension and consumer behavior
  unstable.
- Evidence: `095ae1a` created status enums, dataclass models, summary builders,
  and named stages; `4afee6b` added stable IDs; `97084dd` and `0269843` migrated
  application consumers.
- Decision: model results as Run -> Stage -> Check -> Case, separating execution
  state from pass/fail/skip outcomes.
- Consequences: new checks have a uniform extension contract and consumers can
  filter hierarchically. The migration required temporary dual schema support.
- Validation: six retained reports include one legacy schema and five
  hierarchical reports; current report version is `2.0`.

## D009 — Make atomic naming rules policy-owned and source-linked

- Date: 2026-10-05
- Status: accepted
- Confidence: high
- Scope: compliance semantics
- Context: checkers consumed some policy values while retaining hidden regexes,
  combined conditions, and reason text.
- Evidence: `b6792eb` moved rule IDs, validators, values/limits, module casing,
  applicability, and reasons into policy; `c603a69` audited automatic/manual
  source coverage.
- Decision: each automatically evaluated condition is an atomic rule in YAML;
  semantic/provenance rules stay explicitly manual until evidence exists.
- Alternatives: hard-coded validators and broad combined regexes are visible in
  earlier revisions.
- Consequences: policy diffs explain behavior changes and diagnostics cite rule
  IDs; policy now needs schema validation and versioned regression fixtures.
- Validation: policy v4 run artifacts show changed classifications; the current
  manual test is stale, so correctness is not fully protected.

## D010 — Keep deterministic case identity within the report contract

- Date: 2026-10-05
- Status: accepted with constraint
- Confidence: high
- Scope: report item identity
- Context: consumers need a stable key beyond display text.
- Evidence: `97084dd` uses UUIDv5 over check ID, case location, name, and list
  index.
- Decision: derive IDs deterministically from report-visible case identity.
- Consequences: IDs are reproducible for the same extraction/order but change
  when ordering or locations change. They are not permanent source-symbol IDs.
- Validation: current formatter implementation is deterministic; no explicit
  identity regression test exists.

## D011 — Keep one project voice and derive secondary views

- Date: 2026-10-06
- Status: accepted
- Scope: engineering documentation and historical records
- Trigger: actor-specific record fields and dedicated gap/content/profile files
  duplicated facts and made project evidence look like work by separate actors.
- Decision: describe what happened, why, evidence, and result in one project
  voice. Git identity records authorship. Keep constraints in the architecture,
  module, testing, contract, decision, operation, or standards record that proves
  them. Keep the roadmap limited to future gates. Generate gap assessments,
  skill views, and narrative ideas from those authoritative records on demand.
- Alternatives rejected: keeping actor fields for tools; keeping a living
  content-idea index; keeping a project-wide gap inventory beside the actual
  module and verification records.
- Consequences: fewer duplicate documents and less attribution noise; derived
  views require reading/linking the authoritative records when requested.
- Validation: dedicated content and skill-profile documents removed; roadmap
  narrowed and renamed; current constraints distributed to their factual owners;
  navigation and links updated.

## D012 — Deepen one run-scoped developer workspace before adding breadth

- Date: 2026-10-08
- Status: accepted
- Scope: build intelligence, remediation, report/build UI, and evidence export
- Trigger: the prototype already persisted review, remediation, and build data
  under one run ID, but generic failure text, separate-looking pages, and
  single-value filters obscured that continuity.
- Decision sequence: classify known build failures before any model boundary;
  produce remediation from policy-owned atomic reasons; expose Report and Build
  as tabs over the current JavaScript state; allow multi-select only for status,
  stage, and check; generate a self-contained HTML evidence pack from the
  canonical persisted report; serialize the default project profile from policy
  data without adding a selector.
- Why this order: deterministic intelligence improves the value of existing
  evidence without token cost; the workspace then makes the same evidence easier
  to use; the HTML pack gives that state a portable handoff format. A profile
  selector or multi-run workspace would add configuration claims the prototype
  cannot yet support.
- Fallbacks: unmatched build output is explicitly classified as an unclassified
  failure and keeps generic next actions; legacy reports without profile fields
  receive display defaults; an unbuilt run renders `not run`; empty remediation,
  diagnostics, and artifact sections remain valid evidence-pack sections; zero
  selected facet values means “all.”
- Alternatives rejected: replacing the page architecture; model-first build
  analysis; multi-select module/profile filters within one run; and a client-only
  evidence export that could diverge from persisted state.
- Consequences: current UI state remains lightweight and run-scoped; generated
  evidence can be handed off without server assets; deterministic pattern rules
  now require focused regression fixtures when new toolchains are added.
- Validation: focused assertion tests cover Green Hills classification, generic
  fallback, remediation templates, and escaped/self-contained evidence output;
  JavaScript syntax is checked separately. Full API startup remains dependent on
  the FastAPI runtime being installed.

## D013 — Separate workspace navigation, context, actions, and future intent

- Date: 2026-10-09
- Status: accepted
- Scope: landing/setup layout and developer-workspace information architecture
- Trigger: page-specific actions were mixed into the tab bar, run metadata had
  no heading or disclosure control, entry screens depended on browser zoom to
  fit, and deferred features had no honest product surface.
- Decision: keep the shared bar navigation-only; place review and build actions
  on their owning pages; show run/profile metadata under a titled disclosure
  collapsed by default; fit landing and setup into a normal desktop dynamic
  viewport; make the setup cards equal-height with a flexible activity log; and
  expose deferred capabilities in an inert Roadmap tab backed by roadmap G11.
- Rationale: tabs answer “where am I,” page actions answer “what can I do here,”
  and metadata answers “what context produced this result.” Separating those
  concerns improves discoverability without adding a new application shell.
- Fallbacks: short and narrow viewports may scroll rather than clip content;
  legacy reports use the existing profile display defaults; simulated activity
  remains clearly documented as non-telemetry; the Roadmap provides explanatory
  text only until its dependency gates are met.
- Alternatives rejected: hiding metadata completely; leaving metadata as a
  permanently expanded untitled card; keeping review actions in the tab bar;
  disabling scrolling at all sizes; and presenting future actions as clickable
  controls before their contracts exist.
- Consequences: entry pages are denser at 100% zoom, supporting context consumes
  less vertical space, and planned product scope is visible without confusing it
  with implemented behavior.
- Validation: focused HTML/CSS diff inspection and JavaScript syntax checks. No
  application start was performed solely for presentation changes.

## D014 — Keep the manager preview a read-only projection

- Date: 2026-10-09
- Status: accepted temporarily at prototype maturity
- Scope: manager aggregation, module comparison, and future workflow surfaces
- Trigger: managers need a portfolio and cross-run view, but approvals,
  ownership, ticketing, PR/CI integration, and model-assisted insights do not yet
  have identity, authorization, persistence, or provider contracts.
- Decision: create dedicated manager endpoints that read the same persisted
  `RunResult` records, aggregate only the latest run of each module, and compare
  any two runs within one module. Keep exception selection and workflow data in
  clearly labelled preview envelopes; do not add write endpoints or lifecycle
  states.
- Source authority: `report.json` remains canonical. Manager totals,
  comparisons, queues, and insight cards are derived and never recalculate
  checks or duplicate the build-report format.
- Tactical choices: recover missing legacy run IDs from directory names; order
  by persisted generation time; express every delta as target minus base; match
  failures by case ID with a report-visible legacy fallback; use a
  provider-independent insight wrapper.
- Alternatives rejected: client-only aggregation, a second manager database,
  fake persistent ticket/approval actions, and model-first insight generation.
- Consequences: the prototype can demonstrate portfolio navigation and
  comparison honestly, but concurrent storage, pagination, access control,
  retention, and durable workflow integration remain production gates.
- Exit criteria: before preview actions become active, add authenticated roles,
  authorized state transitions, a durable workflow store, auditable integration
  IDs, retry/idempotency behavior, and contract/end-to-end tests.
- Validation: focused service assertions and a read-only projection over 17
  retained reports; route/HTTP and JavaScript syntax checks cover the composed
  preview. The active Python environments lack pytest, so the same assertion
  function was invoked directly. Automated visual inspection was attempted but
  the computer-use helper failed during sandbox setup before a page opened.

## D015 — Represent analysis inventory as evidence, not compliance

- Date: 2026-10-10
- Status: accepted
- Scope: Analysis-stage result contract, developer report, and evidence pack
- Trigger: the Analysis stage already built and persisted a useful AST-derived
  symbol inventory, but the report hid the stage whenever it contained no
  compliance cases.
- Decision: add an optional typed stage inventory and derive its file coverage
  and symbol-family counts from the extractor result already in memory. Render
  it as identified evidence, outside pass/fail/skip totals and facets.
- Audit boundary: reserve nullable audited, pending-approval, and not-audited
  values under an explicit `not_tracked` status. Do not present unavailable
  governance data as zero.
- Alternatives rejected: fake successful cases, browser-side aggregation of
  `symbols.json`, hiding Analysis until an audit workflow exists, and mixing
  inventory counts into compliance totals.
- Consequences: report version 2.1 is backward compatible because inventory is
  optional. Extracted records may include both declarations and definitions and
  are not yet stable cross-run symbol identities.
- Validation: focused pure summary/serialization assertions, evidence-pack
  assertions, and JavaScript syntax validation. The machine-dependent full
  CMake/libclang pipeline was intentionally not rerun for this projection.

## D016 — Preserve every extracted artifact as an audit candidate

- Date: 2026-10-10
- Status: accepted; supersedes the count-only scope of D015
- Scope: Analysis-stage inventory contract, Governance Report, and evidence pack
- Trigger: aggregate counts made Analysis visible but did not satisfy the actual
  requirement that every symbol be inspectable and visibly audited or not.
- Decision: retain aggregate cards, then group every extracted function,
  variable, parameter, structure/field, enum/constant, typedef, and macro as an
  individual artifact. Initialize each record `not_audited` and expose parser
  evidence plus an empty audit-rationale slot.
- Identity boundary: use a deterministic UUID5 over category, location, name,
  and ordinal for report-local identity. Do not claim that it survives line
  movement or refactoring; production cross-run identity remains G12 work.
- Rationale boundary: AST evidence can describe what was declared, where, and
  with which type/value/replacement. It cannot explain why the design needs the
  artifact, so no rationale is synthesized.
- Alternatives rejected: converting artifacts to passed/failed compliance
  cases, showing counts without rows, and inventing design rationales from names.
- Consequences: report 2.2 may be substantially larger, and rendering all rows
  is a prototype trade-off. Large-repository pagination or virtualization must
  precede production scale.
- Validation: hand-checkable projection and serialization assertions,
  deterministic-ID assertion, evidence-pack assertion, and JavaScript syntax.

## D017 — Preflight and selectively extract review archives

- Date: 2026-10-13
- Status: accepted design; implementation deferred to G01
- Scope: ZIP ingestion for review workspaces
- Trigger: BUG-001 records a Windows `WinError 206` during `extractall` on a
  deeply nested `.git/refs/codex/turn-diffs/checkpoints/` member. Removing
  `.git` allowed the reported archive to extract.
- Evidence boundary: the failure and workaround are recorded from the supplied
  investigation; the two original ZIPs were not compared or replayed here.
- Decision: preflight the entire archive, exclude non-consumed `.git` metadata,
  enforce path and resource limits, and then extract approved members
  individually into the run workspace. Return typed ingestion failures as 4xx
  responses and retain exclusion/rejection reason counts for run provenance.
- Security requirements: reject traversal, absolute/drive/UNC, NUL, and
  link-like members; bound entry count, expanded size, compression ratio,
  nesting depth, and predicted resolved path length; clean partial output after
  failure.
- Alternatives rejected: enabling Windows long paths as the only remedy,
  continuing unrestricted `extractall`, silently ignoring write errors, and
  requiring every user to rebuild ZIPs manually without `.git`.
- Consequences: ingestion becomes more explicit and testable but needs a
  documented archive policy. Excluding `.git` means future checks that require
  repository history must obtain it through a separate governed source.
- Validation required: compact Windows long-path fixture; malicious-member and
  archive-limit tests; source equivalence with/without `.git`; cleanup test; API
  4xx smoke; and comparison of the two reported ZIP manifests if available.
- Implementation references: none yet. This decision is not a fix.
- Related: [BUG-001](known-issues.md#bug-001--windows-zip-extraction-fails-on-overlong-nested-git-paths), G01.

## D018 — Generate a candidate or ask one narrow context question

- Date: 2026-10-16
- Status: accepted prototype; production model/evaluation gate remains G11
- Scope: naming remediation provider, service/API contract, and persistence
- Trigger: most lexical, case, prefix, and length failures can produce a useful
  candidate from the symbol and policy, while semantic names and categorical
  global-name segments cannot be inferred honestly from that evidence.
- Decision: process one check as one batch. Run deterministic preflight first,
  send the policy once and only failed rule IDs per case, and require strict
  structured output. Return a candidate, one narrow developer question, or an
  explicit limitation. Continue the same remediation record after answers.
- Length boundary: maximum-length failures are eligible because conservative
  abbreviations can preserve visible meaning. Ambiguity becomes a question.
- Global boundary: never invent data-type, size, module, unit, or categorical
  segment values. Other global failures are eligible only when existing segments
  and semantic description are sufficient.
- Cost and privacy: deterministic no-call paths, one request per eligible check
  batch, concise prompts, minimal reasoning, bounded output, `store=false`,
  environment-only credentials, and one transient retry. Persist model/token
  evidence, never credentials.
- Alternatives rejected: ask before every case; call once per case; repeat rule
  prose per case; invent categorical globals; silently edit source; or append a
  new plan for each question/answer turn.
- Prototype model boundary: `gpt-5-nano` is the configurable cheapest workflow
  default and is deprecated in the current catalog. Production requires a
  supported-model decision, evaluation corpus, collision/source-context checks,
  and end-to-end tests.
- Contract limitation: historical reports do not embed immutable policy
  snapshots, so name/version drift is rejected and requires a new review run.
- Validation: payload assertions, no-call paths, context continuations, global
  deferral, candidate policy checking, retry/error behavior, persistence
  replacement, and Python syntax checks.

## Durable problem and learning ledger

### P001 — Compiler/preprocessor visibility changes what can be reviewed

- Symptom: source constructs can be absent or transformed before AST traversal,
  and later optimization/linking can remove compiled symbols.
- Evidence: the [archived daily log](../archive/daily_log.txt) records a three-layer visibility map covering
  preprocessing, compiler/AST optimization, and linker pruning.
- Response implemented: use the compilation database and detailed preprocessing
  records, then filter macros to project scope.
- Remaining risk: the tool reviews configured translation units, not every
  inactive conditional branch or linked binary property.
- Lesson: “present in source,” “present in AST,” and “present in final firmware”
  are different claims and require different evidence.

### P002 — Realistic embedded test corpora overwhelmed repository history

- Symptom: commits `4fe47df`, `9755213`, `c5a35aa`, and `62f1792` include
  million-line swings driven by firmware, generated build trees, and reports.
- Root cause: a real integration corpus was used as both test input and tracked
  project content.
- Resolution: generated run workspaces became ignored; a large run tree was
  removed in `62f1792`.
- Remaining risk: ignored runs are local-only and can disappear; no compact
  governed fixture/manifests replace them.
- Lesson: retain small licensed fixtures, manifests, hashes, and summaries in
  Git; keep large reproducible payloads in an artifact store.

### P003 — Path/workspace responsibility drifted during modularization

- Symptom: `d653e0a` recorded unresolved “pat issues”; subsequent diff passes
  repeatedly changed source root, copied workspace, analysis directory, compile
  database path, and report paths.
- Best explanation: Inferred—stages mixed authoritative and copied source paths.
- Resolution: run-scoped workspace plus explicit `repo_root`, `workspace_path`,
  and analysis artifacts; later ownership moved to orchestration.
- Remaining risk: `Path.cwd()` still controls workspace/static resolution, so
  launching outside repository root can break behavior.
- Lesson: path authority is an interface and should be explicit, typed, and
  tested from multiple working directories.

### P004 — Windows/Linux portability was solved unevenly

- Symptom: analysis needed Linux compiler/libclang fixes; current build still
  invokes `cmd` and `.bat` inside a Linux Docker image.
- Resolution: containerized review analysis with Linux tools and multi-location
  libclang discovery.
- Remaining risk: the build endpoint cannot execute natively in that container.
- Lesson: separate “service can review on Linux” from “all advertised workflows
  are cross-platform.” Add platform contract tests per path.

### P005 — Report migrations created compatibility debt

- Symptom: July agent formatters expected `sections`; August introduced typed
  `stages`; October added compatibility branches.
- Resolution: support both shapes while migrating UI/agent consumers.
- Remaining risk: a 1,000+ line service contains duplicated helpers and legacy
  formatters with no removal condition.
- Lesson: version contracts, add adapters at one boundary, test both versions,
  and define a deprecation/removal gate.

### P006 — Tests drifted behind policy design

- Symptom: the current naming manual test passes pre-atomic inline policy
  dictionaries to checkers that now require `rules`; executed on 6 October it
  failed with `KeyError: 'rules'`.
- Root cause: test data duplicated the configuration contract instead of loading
  the executable policy or a versioned fixture.
- Resolution so far: none in code; this record makes the gap explicit.
- Lesson: contract tests should validate policy schema and use small fixtures
  owned with the contract.

### P007 — Run artifacts lack enough provenance for faithful replay

- Symptom: reports record run ID, module, policy/report versions, and timestamp,
  but not code revision, input checksum, exact command, tool versions, or errors
  from partial runs.
- Impact: count differences can be observed but not causally attributed.
- Resolution proposed in the contemporary daily log: ORCH-002 lightweight run
  metadata. It was not implemented as a separate manifest.
- Lesson: capture provenance before generating derived artifacts; it cannot be
  reconstructed reliably afterward.

## Decisions that remain undocumented or unresolved

- Why `--reload` is used in the container command and whether the image is for
  development or production.
- Whether build execution is intentionally Windows-only or requires a Linux
  implementation.
- Whether legacy report compatibility still has active consumers.
- What policy schema/version migration guarantees are required.
- How generated runs are retained, expired, or exported as organizational proof.
- What threat model applies to uploaded ZIPs, embedded Git metadata, build
  scripts, and unauthenticated build execution.
- Which remote MCP contract replaced the deleted local implementation.
