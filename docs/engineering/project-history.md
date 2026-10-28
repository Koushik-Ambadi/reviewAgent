# Project History and Daily Engineering Log

- Status: append-only reconstruction
- Created: 2026-10-06
- Evidence window: `bddb1a0` through `c603a69`
- Update trigger: new commit, recovered contemporary evidence, or explicit erratum
- Source of truth for: completed chronological engineering work
- Does not own: current architecture or future roadmap

## Reading this log

Each entry includes the outcome intended by the commit, what the diff proves,
the challenge signal available in the repository, the response, and the
verification boundary. `Observed`, `Recorded`, `Inferred`, and `Unknown` use the
definitions in [`evidence-index.md`](evidence-index.md).

Use `git show <hash>` to inspect an entire event. Statistics include generated
and third-party artifacts and must not be interpreted as effort or quality.

## 2026-10-28 — Validate retained source and expose graph workspace projections

- Ran schema 1.1 extraction against the retained shunt source and compilation
  database while preserving its existing compatibility inventory.
- Added read-only file, module, and inter-module API projections with selectable
  call/include/access overlays and explicit CFG/data-flow evidence gates.
- Recorded the graph workspace placement decision and a use-case/insight map.
- Added the developer Code graphs tab with retained-run selection, three scopes,
  combinable overlays, canvas pan/zoom, node inspection, accessible relationship
  fallback, and high-level-to-internal double-click drill-down.

## 2026-10-27 — First derived code-graph views

- Added deterministic reachability and recursive-SCC-aware call-depth views.
- Added file-as-module dependency aggregation backed by call/include evidence.
- Added changed-node reverse impact traversal over calls, includes, and
  containment, keeping it explicitly separate from test selection or proof of
  runtime impact.
- Extended the shared AST facts with scoped variables, conservative access,
  type-size estimates, versioned complexity, and exact body-token fingerprints;
  added their four initial projections and verified a real libclang fixture.
- Moved libclang setup, compile-argument sanitization, and translation-unit
  parsing into `code_intelligence`; the review stage now emits the legacy symbol
  inventory and canonical graph snapshot from the same parsed cursor.

## 2026-05-14 — Establish repository and AST foundations

### `bddb1a0` — Initial repository reviewer

- Outcome: first checked-in implementation of folder/file structure review and
  Clang AST extraction for defined and declared functions.
- Observed implementation: added `review_engine.py`, a YAML policy, early
  `repo_review` config/model/reporter/tree/validator modules, a sample `soc`
  repository, source standards, a Draw.io design, and initial report artifacts.
- Challenge signal: `review_engine.py` already combined compilation arguments,
  AST walking, extraction, and output, while parallel modular files handled
  structure checks. The boundary was exploratory rather than settled.
- Response: create a working vertical slice before decomposing it.
- Verification: 34 files and 11,238 inserted lines were committed; the subject
  records function extraction as working. No test command or environment was
  captured, so operational success is Recorded, not independently reproduced.
- Next transition: expand symbol categories and reduce noisy output.

### `888758f` — Add locals, globals, structs, and enums

- Outcome: broaden AST inventory beyond functions.
- Observed implementation: `review_engine.py` added parameter, field, enum
  constant, and typedef cursor handling; the retained working report changed.
- Challenge signal: the change removed substantially more report content than
  it added, suggesting output shape/noise was still being tuned.
- Response: attach extraction logic to specific `CursorKind` cases.
- Verification: the diff proves supported cursor branches; no automated
  assertions were retained.
- Next transition: make struct/enum nesting and macro provenance more accurate.

## 2026-05-15 — Filter AST noise and preserve nested metadata

### `47890d2` — Nested enums/structs and user-macro filtering

- Outcome: improve semantic grouping and remove system macro noise.
- Observed implementation: fields were collected beneath structs, constants
  beneath enums, and `is_user_macro` rejected macros outside the repository or
  with reserved underscore prefixes.
- Problem: detailed preprocessing records expose compiler and header macros,
  which can overwhelm project-owned results.
- Resolution: filter by source location and reserved naming before recording a
  macro.
- Limitation: repository containment and underscore heuristics do not establish
  true ownership for generated or vendored in-repository headers.

## 2026-05-17 — Classify macros and recover array syntax

### `1bf9299` — Distinguish macro kinds

- Outcome: classify conditional, function-like, and value macros and retain
  replacement text.
- Observed implementation: token inspection detects a parenthesized identifier
  parameter list; otherwise a non-empty replacement is treated as value-like.
- Problem: `MACRO_DEFINITION` alone does not convey the product-level category
  needed by later policy checks.
- Resolution: derive a small taxonomy from token spelling and kinds.
- Limitation: complex preprocessing constructs can exceed the heuristic.

### `5fd77db` — Recover array dimensions from source text

- Outcome: expose array suffixes for magic-number validation.
- Observed implementation: for variable declarations, the extractor reopened
  the source line, located the variable name, appended bracket suffixes to the
  tokenized declaration, and recorded each `[...]` dimension.
- Problem: the desired bracket spelling was not reliably present in the cursor
  token representation used by the prototype.
- Resolution: targeted source-text recovery around the AST-located declaration.
- Evidence correction: the subject says “used previous line”; the committed
  implementation reads `node.location.line - 1`, which is the cursor's current
  one-based source line converted to a zero-based list index.
- Limitation: multi-line declarations and macros can defeat single-line regex
  recovery.

### `4fe47df` — Record a working required-field inventory

- Outcome: checkpoint the inventory covering macros, globals, locals, structs,
  typedefs, and functions.
- Observed implementation: added a small function-name experiment and a very
  large embedded-system test corpus with models, documents, MIL/unit evidence,
  and reports.
- Challenge signal: meaningful source changes and more than one million lines
  of binary/generated/test artifacts were mixed in one commit.
- Response at the time: preserve a realistic corpus to validate extraction.
- Later lesson: realistic inputs were valuable, but committing the entire
  corpus made history heavy and obscured review-agent changes; much of it was
  removed on 31 May.

## 2026-05-18 — Convert extracted data into review outcomes

### `b9dd031` — Naming and array validators

- Outcome: add function-name, macro-name, and array magic-number validation.
- Observed implementation: renamed the prototype to `build_ast.py` and added a
  412-line `code_review_validators.py`.
- Architectural shift: the project moved from “inventory symbols” toward
  “evaluate policy over inventory.”
- Verification: implementation exists; no dedicated test suite was added.
- Next transition: connect the checks into an end-to-end pipeline and UI.

## 2026-05-19 — First full vertical slice

### `dc1ec4a` — Pipeline plus browser UI

- Outcome: Recorded as a working pipeline with frontend.
- Observed implementation: added declarative pipeline config, ingestion,
  pipeline orchestration, a static UI, and a lightweight server; moved AST work
  into `repo_review/ast_builder.py`; deleted the isolated function experiment.
- Problem: separate scripts and validators lacked one executable user journey.
- Resolution: compose ingestion, analysis, validation, reporting, and browser
  rendering into a vertical slice.
- Trade-off: a 1,668-line HTML file and mixed responsibilities made iteration
  fast but created later modularization pressure.

## 2026-05-25 — Use real compilation context and trigger builds

### `9755213` — Compilation database and firmware build

- Outcome: Recorded as a full pipeline with compile commands, build trigger,
  and working web application.
- Observed implementation: added CMake/Ninja compilation-database generation,
  a firmware build wrapper, frontend/server build trigger, and checked-in
  `analysis/cmake_build` output plus a large FreeRTOS/MCAL corpus.
- Problem: AST accuracy requires real include paths, defines, and target compile
  flags; standalone parsing is insufficient for embedded C.
- Resolution: configure the project with CMake and consume
  `compile_commands.json`.
- Repository problem introduced: 617 files and roughly 1.45 million inserted
  lines included derived build output and third-party source.
- Verification boundary: artifacts show CMake had run, but there is no recorded
  exact command/environment mapping the output to this revision.

## 2026-05-27 — Modularize the pipeline and stabilize run isolation

### `d653e0a` — Package-level decomposition

- Outcome: Recorded as a full pipeline with “pat issues” still present; the text
  is retained verbatim because the intended word is unknown.
- Observed implementation: replaced monolithic AST, validator, pipeline, and
  reporter modules with packages for AST extraction, compilation, ingestion,
  checks, reporting, and staged execution. Added a separate `repo_build`
  package and a manual pipeline script.
- Problem: multiple reasons to change were concentrated in large modules.
- Resolution: separate extractors, sanitizers, traversal, check families,
  stages, result models, and build responsibilities.
- Design evidence: this is the origin of the current role-oriented package
  structure, although several abstractions were simplified three days later.
- Verification: 70 relevant source files changed; no passing automated suite is
  retained.

### `c5a35aa` — Workspace and compilation stabilization

- Outcome: Recorded as a stable pipeline.
- Observed implementation: made analysis paths explicit, copied local source
  into a run workspace, created analysis/report/log/artifact/metadata folders,
  passed compile-database paths into AST extraction, introduced structure
  models, and improved error details.
- Likely problem (Inferred): earlier stages disagreed about original-source and
  workspace-relative paths, consistent with the prior “pat issues” subject.
- Response: establish the copied workspace as the processing root and pass
  derived paths explicitly.
- Limitation: stability remains a commit claim because no reproducible test log
  was committed.

## 2026-05-28 — Add project-specific global-name grammar

### `130745d` — Global variable validation

- Outcome: validate global names against type/size/module/unit/description
  segments and exclusions.
- Observed implementation: new 286-line checker, policy/rule wiring, and manual
  pipeline updates.
- Problem: common identifier checks could not express the organization's
  encoded global-variable schema.
- Resolution: implement a specialized parser driven by configured vocabularies.
- Trade-off: high policy specificity created a separate validation path that is
  still more complex than shared atomic naming rules.

## 2026-05-29 — Enrich extracted metadata

### `4ac4c8e` — Symbol detail expansion

- Outcome: expose metadata needed for more precise checks.
- Observed implementation: major additions in symbol extractors, argument
  sanitization, and AST builder; obsolete common issue models were removed.
- Problem: early name/location-only records were insufficient for pointer,
  array, struct, enum, storage, and later semantic rules.
- Resolution: make the symbol inventory a richer intermediate representation.
- Verification: current retained `symbols.json` artifacts demonstrate that a
  rich representation was produced in later runs.

## 2026-05-30 — Simplify responsibilities around analysis

### `f435aea` — Reframe AST/compilation as analysis

- Outcome: restructure workflow, context building, and orchestration.
- Observed implementation: renamed `ast` to
  `analysis/symbol_inventory`, compilation generation to
  `analysis/source_index`, collapsed compile/AST stages into an analysis stage,
  removed a generic stage class and ingestion models, centralized policy, and
  simplified reporting.
- Problem: the first decomposition introduced more abstractions and stages than
  the actual workflow needed.
- Resolution: organize by durable responsibility (“analysis”) and keep simple
  function stages.
- Design lesson: modularity improved by deleting abstractions as well as adding
  them; the current code retains this simpler pipeline shape.

## 2026-05-31 — Add ZIP/API delivery and remove checked-in run data

### `62f1792` — ZIP ingestion and history cleanup

- Outcome: add ZIP ingestion.
- Observed implementation: added archive extraction into a UUID/timestamp
  workspace and removed a checked-in run/source tree spanning 655 files and
  roughly 2.53 million lines.
- Problem: a service needs upload isolation, while committed run payloads made
  the repository enormous.
- Resolution: create generated workspaces and stop retaining the full run tree
  in the tracked source history.
- Limitation: archive-member path safety was not added.

### `64db5ad` — FastAPI review endpoint

- Outcome: implement the upload/review service path.
- Observed implementation: added `app/main.py`, `/api/review`, an application
  service, moved the UI under `app/static`, and adjusted ZIP ingestion.
- Problem: the previous standalone server was not a structured service API.
- Resolution: use FastAPI routes plus a service layer while reusing the pipeline.
- Hygiene follow-up: a sample upload ZIP was committed here and removed on
  2 June.

## 2026-06-02 — Separate orchestration, review, and build domains

### `4217116` — Ownership migration

- Outcome: integrated build, orchestration layer, and web UI.
- Observed implementation: moved ingestion from `repo_review` to
  `orchestrator`, moved build execution to `repo_build`, deleted review-owned
  ingestion/build stages, added `/api/runs/{run_id}/build`, persisted the run ID
  in the UI, and removed the standalone server/upload fixture.
- Contemporary rationale: the [archived daily log](../archive/daily_log.txt) says ingestion/workspace/run
  lifecycle belongs to orchestration, review should operate on an already
  prepared repository, and one workspace should serve review and build.
- Problem: duplicate ownership risk—review previously knew source type,
  extraction, workspace creation, checking, reporting, and build.
- Resolution: explicit package boundaries and a narrower review contract.
- Verification Recorded: the note says firmware build and finding rendering
  were verified; raw command/log is not retained.

## 2026-06-16 — Containerize and adapt analysis to Linux

### `6947306` — Docker/Linux review service

- Outcome: Recorded as a Dockerized service working on Linux.
- Observed implementation: added Python 3.13 slim image with Clang 19,
  libclang, CMake, Ninja, GCC/G++; added libclang resolution; changed compiler
  defaults from Windows LLVM paths to Linux GCC/G++; forced a safe POSIX
  compiler environment; reorganized docs and reformatted much of the tree.
- Explicit problem evidence: comments identify a `CC=C` environment problem and
  invalid compiler-path injection as fixes.
- Resolution: copy the environment, set valid compiler executables, inject paths
  only when present, and resolve libclang from configured Linux locations.
- Limitation: the review path became Linux-capable, but the build executor still
  calls Windows `cmd` and a `.bat` file.

## 2026-06-22 — Adjust hosted development command

### `63c8b90` — Enable Uvicorn reload

- Outcome: Recorded as “stable hosted.”
- Observed implementation: the only change adds `--reload` to the Docker CMD.
- Interpretation: this supports iterative hosted development, but reload is not
  evidence of production hardening and is normally not a production setting.
- Unknown: hosting provider, availability, smoke-test result, and deployment
  URL are not retained.

## 2026-07-09 — Explore local MCP and agent-oriented operation

### `196e282` — Local MCP integration

- Outcome: expose review through a local MCP server/tool.
- Observed implementation: added an HTTP review client, FastMCP server, tool,
  config, and test; extended dependencies.
- Problem: the web API shape alone was not optimized for tool-using agents.
- Resolution: wrap review as an MCP tool while retaining the HTTP service as the
  execution backend.
- Verification: a small test script exists in the commit; no execution record.

### `b69bfda` — Agent personas, skills, policy endpoint, compact reports

- Outcome: add agent context/reviewer/builder/optimizer guidance and adjust
  report consumption for agents.
- Observed implementation: introduced policy API/service, multiple MCP skill
  Markdown files, server resources/prompts, and a report formatter.
- Problem: raw review JSON was too verbose and lacked task-specific operating
  context for an agent.
- Resolution: provide compact formatting plus role-oriented instructions and
  policy retrieval.
- Trade-off: application and local MCP layer were coupled in the same repository.

## 2026-07-17 — Move MCP out of the service repository

### `f0d40b9` — Remote MCP boundary

- Outcome: separate the MCP layer and move it to a remote MCP deployment.
- Observed implementation: deleted the entire local `review_mcp` package and
  adjusted requirements.
- Decision signal: this is a deliberate reversal, not unfinished work—the
  commit subject names the new boundary.
- Likely rationale (Inferred): independent deployment and reduced service
  coupling; no contemporary alternatives analysis is retained.
- Current consequence: agent-oriented HTTP endpoints remain, while MCP code is
  absent. MCP-related packages still remain in the dependency freeze.

## 2026-07-28 — Make HTTP reports agent-consumable

### `5984863` — Agent endpoints and report shape

- Outcome: add agent-optimized endpoints after local MCP removal.
- Observed implementation: added `/api/agent/review` and
  `/api/agent/review/{run_id}`, built compact/detailed failure summaries, and
  changed reporting responsibilities. The service grew by roughly 961 lines.
- Problem: agents needed actionable failures without every passed case.
- Resolution: group failures dynamically by rule and separate skipped/excluded
  cases; persist the full report and derive compact views.
- Debt introduced: legacy formatting accumulated in one large service module.

## 2026-08-07 — Stabilize extensible contracts

### `095ae1a` — Typed check/stage/run result contract

- Outcome: establish a stable contract for adding checks.
- Observed implementation: added dataclass results/status enums/builders,
  replaced generic checks stage with named structure and naming stages, replaced
  old schemas/serializers, rewrote existing check outputs, added smoke test, and
  generated a 211-rule source rulebook.
- Problem: legacy report dictionaries and combined issues made check extension
  and multi-consumer stability difficult.
- Resolution: explicit `CaseResult -> CheckResult -> StageResult -> RunResult`
  hierarchy with separate execution and case statuses.
- Verification: two retained 11 August runs later use the hierarchical contract
  and produce identical 743-case summaries; they do not record code revision.

### `46e6e21` — Complete internal end-to-end migration

- Outcome: Recorded as the new contract working end to end, with web UI and
  agent interface still to update.
- Observed implementation: aligned analysis, symbol extraction, structure
  stages, and reporting with `StageResult`; strengthened libclang resolution;
  updated smoke test and added cache-clean script.
- Problem: the initial contract commit changed check/report types before every
  downstream producer/consumer was migrated.
- Resolution: complete internal pipeline propagation first and explicitly defer
  downstream presentation.
- Engineering strength: the commit message preserves incomplete scope rather
  than calling the entire migration done.

## 2026-10-05 — Extend checks, complete consumers, and move rule logic to policy

### `4afee6b` — New naming checks and documentation

- Outcome: add types, enum constants, parameters, and locals to the naming
  stage; extend contracts; document result/check behavior.
- Observed implementation: added four check modules, common identifier helpers,
  policy blocks, manual naming script, the current
  [run-result contract](../contracts/run-result.md), and the large
  implementation catalog. Added check/stage IDs and deterministic case-ID fields.
- Problem: the August contract made extension possible, but major symbol
  categories and consumer-facing documentation were still absent.
- Resolution: implement the new families against the symbol inventory and
  enumerate the broader standards backlog.
- Verification: manual script was added, but its inline policy shape later
  became stale.

### `97084dd` — Wire the `RunResult` API/agent response

- Outcome: make application services consume the new hierarchical report.
- Observed implementation: added stable IDs throughout existing checks/stages,
  enriched report metadata/versioning, and added `stages` compatibility branches
  in the agent summary/detail builders.
- Problem: 7 August explicitly left downstream agent/UI contracts behind.
- Resolution: preserve legacy `sections` support while adding `RunResult`
  traversal.
- Trade-off: compatibility avoided an immediate break but retained duplicate
  code paths.

### `0269843` — Render `RunResult` in the web UI

- Outcome: complete the other deferred downstream consumer.
- Observed implementation: extracted 475 lines of behavior into `app.js`,
  reduced/reworked inline HTML, and rendered/filter/searched stage/check/case
  results with build triggering.
- Problem: the old UI understood the legacy report shape.
- Resolution: make the UI contract-aware and separate JavaScript from markup.
- Verification boundary: code path exists; no browser automation is retained.

### `7322d77` — Refine policy-driven behavior

- Outcome: correct naming checks and policy handling before full policy
  extraction.
- Observed implementation: adjusted array literal parsing, enum/macro/global
  behavior, removed redundant pipeline policy expansion, updated catalog, and
  raised policy version from 2 to 3.
- Run evidence: `20261005_175650_96dd018a` records policy version 3 on the same
  retained `shunt`-shaped corpus used earlier that day: 367 total cases,
  168 failures, 2 skips versus version 2's 196 failures and 10 skips.
- Comparability limit: no source checksum or Git revision is in either report;
  this is an observed count change, not proof of quality improvement.

### `b6792eb` — Atomic rules fully owned by policy

- Outcome: move naming criteria and actionable reason text out of individual
  checkers and into policy.
- Observed implementation: expanded policy version 4 by 357 lines, centralized
  common validator execution, shortened several check modules, declared pointer
  suffixes and array literal patterns, and marked semantic/provenance rules
  manual instead of silently approximating them.
- Problem: policy fields existed, but hidden checker logic still determined
  several failures; combined regex failures were not source-traceable.
- Resolution: atomic rule records with ID, mode, validator, value/limit,
  applicability, and reason.
- Run evidence: `20261005_190122_b4aae0eb` records policy 4 with 367 cases,
  161 failures, and 2 skips. Type results changed from 0/24 pass/fail under v3
  to 8/16 under v4; function failures changed from 2 to 3.
- Interpretation: the policy change altered semantics as intended; totals alone
  do not tell whether every new classification is correct.

### `c603a69` — Audit source-rule coverage and blockers

- Outcome: document exactly what the naming policy automates, what remains
  manual, and which ambiguities/blockers remain.
- Observed implementation: added the file now maintained as
  [`naming-policy-audit.md`](../standards/naming-policy-audit.md) and corrected the check
  catalog's coverage/status claims.
- Problem: implementation without a source-to-rule map could overstate coding
  standard compliance.
- Resolution: link automatic outcomes to ABS rule IDs, retain manual rules, and
  name missing keyword/library inventories, provenance, and semantic review.
- Verification: documentation-only commit immediately follows implementation,
  giving the current branch an auditable policy rationale.

## 6 October 2026 — Consolidate documentation authority

- Outcome: make the engineering record read as one project history and remove
  secondary files that duplicated current facts.
- Change: removed actor/owner attribution fields, removed the dedicated content
  and developer-profile documents, renamed the roadmap, and limited it to future
  gates.
- Evidence preservation: deleted documents remain available in Git history;
  current security, contract, operations, portability, and maintenance
  constraints moved to the architecture record, while test/replay and standards
  records continue to own their existing detail.
- Decision: D011 records the single-voice and on-demand derivation rule.
- Verification target: no current links to removed files, all Markdown paths
  resolve, and no application source changes are present.

## 2026-10-18 — Make documentation routes explicit

### Time not captured — Add module-level context without duplicating authority

- Added a coverage map that routes the review pipeline, C/C++ analysis
  inventory, policy-driven checks, and result/reporting responsibilities to
  local technical guides, code entry points, direct inputs, consumers,
  contracts, and verification.
- Kept architecture, decisions, testing, issues, standards, and contracts as
  their existing owners. The local guides explain mechanics and link outward;
  they do not restate project history or the policy catalog.
- Recorded D022 and enabled compact evidence-only competency tracking. It
  distinguishes implemented project work from prototype limits and does not
  claim general proficiency.
- Verification is focused Markdown-link validation and Git diff review. No
  application code, policy, dependency, or generated run artifact changed.

## Evolution summary

| Phase | Starting form | Ending form | Durable lesson |
|---|---|---|---|
| Extraction | One AST prototype | Build-aware symbol intermediate representation | Real compiler context plus selective source recovery beats regex-only analysis |
| Workflow | Scripts and monoliths | Ordered stages with run workspace | Explicit artifact and responsibility boundaries make reruns understandable |
| Delivery | Standalone page/server | FastAPI, static UI, Docker, build API | One vertical slice exposes contract and platform mismatches early |
| Agent support | Local MCP bundled with service | Remote MCP boundary plus HTTP agent summaries | Consumer-specific views should derive from one full report |
| Extensibility | Ad hoc issue dictionaries | Typed case/check/stage/run DTOs | Stable contracts are prerequisite to adding checks safely |
| Policy | Logic embedded in validators | Atomic source-linked rules in YAML | Configuration is credible only when it owns criteria, reasons, and applicability |

## Errata and unresolved historical questions

- “pat issues” in `d653e0a` is not silently corrected to “path”; the intended
  issue and exact failure remain Unknown.
- “stable” and “working” in subjects are Recorded developer assessments. There
  are no contemporaneous CI or test logs proving those states.
- The exact reason for moving MCP remote is Inferred from the removal and
  subject; cost, security, deployment, and ownership alternatives are Unknown.
- The two 5 October partial runs without `report.json` show failed/interrupted
  attempts, but no error logs survive, so their root causes are Unknown.
- No run can be mapped conclusively to a commit because run metadata omitted
  `code_revision`.

## 2026-10-09 — Manager workspace preview

### 15:55:47 +05:30 — Open read-only manager projection gate

- Intended outcome: derive a latest-run portfolio, per-module history, and
  selectable two-run comparison from the canonical persisted run records, then
  expose them in a separate tabbed manager workspace.
- Starting state: branch `codex/atomic-naming-rules` at `449d329`; worktree and
  index clean; local branch six commits ahead of its upstream.
- Authority and records consulted: `AGENTS.md`, the repository
  `project-lifecycle-governance` skill, this history, architecture, run-result
  contract, testing record, roadmap, and decisions.
- Active implementation record: [`architecture.md`](architecture.md), especially
  the `app/api`, `app/services`, and `app/static` module sections.
- Source of truth: `workspace/runs/<run_id>/report.json`. Manager statistics,
  queues, comparisons, and insights are derived representations and must not
  recalculate review checks or build reports.
- In scope: read-only aggregation endpoints, latest-run-per-module statistics,
  module drill-down, arbitrary two-run comparison, preview-only approvals/PR/CI
  insight wrappers, grouped failed-case selection, owner selection, and ticket
  action affordances that do not persist.
- Explicitly excluded: approval lifecycle state, ticket storage/integration,
  ownership persistence, PR/CI integration, model calls, and a second report
  format.
- Intended maturity: prototype preview. Preview data and actions must be visibly
  labelled and must not imply durable workflow execution.
- Acceptance evidence: focused aggregation/comparison assertions using small
  temporary reports, Python/JavaScript syntax checks, and diff validation. No
  full review/build pipeline run is planned because the change only reads
  existing run artifacts.

### Read-only manager projection checkpoint — exact time not captured

- Implemented dedicated portfolio, module-history, and run-comparison endpoints
  over canonical reports. Legacy reports without top-level run IDs use their
  directory names; malformed reports are ignored and counted.
- Preserved the prototype boundary: approval, ownership, ticket, PR/CI, and
  intelligence data is explicitly preview-only and no workflow writes exist.
- Verification: pytest was unavailable in the active Python installation. The
  focused assertion function passed when invoked directly with a temporary
  workspace. A retained-data projection passed across 17 reports and selected
  the two newest `shunt` runs for the default comparison.
- Commit: `b867551` (`Add read-only manager run projections`).
- Decision: D014 records the read-only projection and the production exit
  criteria. Next gate: render the dedicated tabbed manager workspace over these
  endpoints without changing the developer workspace's run-scoped state.

### 16:12:56 +05:30 — Complete shallow manager UI gate

- Added a separate manager entry and four manager-only tabs: portfolio,
  exception queue, tickets and ownership, and audit and delivery. Developer
  Report/Build/Roadmap navigation and active-run state remain separate.
- Added module drill-down with latest-versus-previous defaults and arbitrary
  two-run selection; comparison calls the dedicated endpoint and labels deltas
  as target minus base.
- Added grouped and individual failed-case selection, owner choices, and ticket
  buttons. These controls return local preview notices only; no approval,
  ownership, or ticket data is persisted or transmitted.
- Added one reusable insight-card wrapper for current placeholders and later
  deterministic remediation or governed model-generated insight.
- Corrected the landing flow from `PR Automation` to `Delivery Evidence`; PR/CI
  status now appears only in the manager audit preview.
- Verification: JavaScript syntax and diff checks passed. The project runtime
  loaded the manager routes, and a local HTTP smoke returned the manager page,
  script, and live portfolio data. Computer-use browser setup failed twice before
  opening a tab, so no automated visual result is claimed.
- Next step: user checks the four manager tabs at normal browser zoom and reports
  pass/fail plus any overflow, unreadable state, or console error. Production
  workflow implementation remains gated by G11 and D014 exit criteria.

## 2026-10-10 — Analysis inventory visibility

### 14:51:22 +05:30 — Open analysis inventory gate

- Intended outcome: keep the completed Analysis stage visible in the developer
  report by summarizing the symbol inventory already produced by libclang.
- Starting state: branch `codex/atomic-naming-rules` at `325b7a5`; worktree and
  index clean; local branch eight commits ahead of its upstream.
- Authority and records consulted: `AGENTS.md`, the repository
  `project-lifecycle-governance` skill, architecture, run-result contract,
  testing record, roadmap, decisions, and this history.
- Active implementation record: [`architecture.md`](architecture.md), especially
  the result contract, symbol inventory, analysis runner, and static UI sections.
- Source of truth: `build_symbol_inventory`'s returned `results` list, which is
  the same content persisted as `analysis/symbols.json`. The report stores a
  deterministic count projection; it does not parse the source a second time.
- In scope: parsed/skipped file coverage, counts for extracted symbol families,
  an explicit untracked audit state, backward-compatible report serialization,
  and a non-case UI card for Analysis.
- Explicitly excluded: symbol-level audit identity, reviewer/approval state,
  persistence for audit decisions, and manager workflow aggregation.
- Acceptance evidence: one pure inventory-summary test, report serialization
  assertion, JavaScript syntax check, focused diff review, and no full
  CMake/libclang pipeline rerun.

### 15:02:09 +05:30 — Complete analysis inventory visibility gate

- Added the optional stage-level inventory contract and advanced the report
  version to 2.1. Older reports remain valid because the field is optional.
- Derived parsed/skipped coverage and ten symbol-family counts directly from the
  extractor result already returned to the Analysis runner; no source or
  `symbols.json` reread was added.
- Made Analysis visible without compliance cases and rendered responsive count
  cards in the developer report and HTML evidence pack. Status/check facets do
  not treat inventory as pass/fail data.
- Kept audit values nullable under `not_tracked`; no fake audited, pending, or
  approval totals are presented. Governed symbol identity and audit workflow are
  deferred to roadmap gate G12.
- Verification passed: focused inventory summary/serialization assertions,
  focused evidence-pack assertions, JavaScript syntax, and diff whitespace.
  The full CMake/libclang review pipeline was intentionally not rerun because
  this is a pure projection over the existing extractor result.
- Remaining visual check: confirm the Analysis count grid and coverage row at
  normal browser zoom with a newly generated 2.1 report.

### 15:49:06 +05:30 — Correct inventory scope to an artifact audit register

- Requirement clarification: aggregate counts are useful as a header, but the
  intended Analysis content is every extracted function, macro, variable, type,
  enum, parameter, and related symbol grouped for individual audit visibility.
- The 2.1 count-only projection is retained for compatibility but is not the
  completed product behavior. A new report must preserve per-artifact identity,
  source location, parser evidence, audit state, and an audit-reason slot.
- The AST can prove declaration facts such as location, type, storage, value, or
  replacement text. It cannot infer why a symbol exists, so design rationale
  remains explicitly unrecorded until supplied by a governed audit workflow.
- In scope: granular typed report projection, grouped Governance Report UI,
  evidence-pack output, focused contract tests, and synchronized records.
- Excluded: interactive audit transitions, reviewer identity, approvals, and
  durable audit writes. All newly identified artifacts start `not_audited`.

### 15:53:28 +05:30 — Complete granular Analysis audit register

- Advanced the additive report contract to 2.2 and preserved the 2.1 aggregate
  cards. The Analysis stage now contains non-empty groups for functions,
  variables, parameters, structures/fields, enums/constants, typedefs, and
  macros.
- Every record has a deterministic report-local ID, source location, extracted
  evidence, `not_audited` state, and an empty audit-rationale field. Aggregate
  audited/pending/not-audited totals derive from those same records.
- The Governance Report opens the first group and keeps the others collapsible;
  search matches artifact names, locations, evidence, and audit fields. The HTML
  evidence pack includes the same register.
- Focused projection/serialization assertions, deterministic-ID assertion,
  evidence-pack assertions, JavaScript syntax, and diff whitespace passed.
- The full CMake/libclang pipeline was intentionally not rerun because the
  extractor itself did not change. Visual confirmation requires a new or rerun
  review so report 2.2 data exists; old reports remain count-only or omit the
  Analysis inventory entirely.
- Production audit transitions, actors, approvals, history, stable cross-run
  identity, and large-inventory virtualization remain roadmap gate G12.

## 2026-10-13 — Deferred defect governance

### 16:23:45 +05:30 — Record ZIP long-path failure and open defect policy gate

- Recorded the supplied Windows `WinError 206` investigation as BUG-001 without
  changing ingestion code or manipulating either source ZIP.
- Starting state: branch `codex/atomic-naming-rules` at `bc1c403`; worktree and
  index clean.
- Evidence boundary: exception details, input paths, `.git` member location,
  source-edit note, and successful manual `.git` removal are recorded from the
  supplied report and were not independently replayed.
- Selected D017 as the deferred design: preflight and bound all members, exclude
  unused `.git` metadata, extract approved members individually, clean partial
  output, retain reason counts, and return typed 4xx ingestion errors.
- Added a project-wide issue owner, tracked agent policy, and workspace-local
  lifecycle-skill guidance so later non-urgent defects retain stable status,
  fixed/not-fixed truth, decisions, and closure evidence. The repository's
  `skills/` directory remains intentionally ignored.
- Authorization boundary: documentation and workflow policy only. No product
  fix, archive comparison, or test run is permitted in this increment. BUG-001
  is `PLANNED` because D017 is accepted under G01, but it remains explicitly not
  fixed.

### 16:31:15 +05:30 — Complete deferred defect record and policy increment

- BUG-001 is the first entry in the new authoritative known-issues register. Its
  summary and detail both state `PLANNED` and `Fixed: No`; the `.git` removal is
  retained only as a workaround.
- Architecture now links the current unsafe `extractall` boundary, D017 owns the
  selected remediation rationale, and G01 owns future implementation priority
  and acceptance scope.
- `AGENTS.md` now requires stable IDs, evidence confidence, explicit lifecycle
  states, and fixing commit/regression evidence before `RESOLVED`. The local
  lifecycle skill has matching routing and guidance under ignored `skills/`.
- Verification was documentation-proportional: referenced paths existed,
  BUG-001/D017/policy cross-links were found, and `git diff --check` passed with
  line-ending warnings only. No application tests or ZIP replay were run because
  no product code changed and the request explicitly deferred the fix.
- Next executable gate: when G01 starts, change BUG-001 to `IN_PROGRESS`, retain
  the compact failing fixtures, implement selective extraction and API mapping,
  then link the fixing commit and regression evidence before `RESOLVED`.

## 2026-10-16 — Model-assisted remediation prototype

### 13:14:36 +05:30 — Open candidate-or-context remediation gate

- Starting state: branch `codex/atomic-naming-rules` at `cb88b70`; worktree and
  index clean.
- Requirement: replace placeholder-only remediation with one conservative
  failed-check batch flow. Generate naming candidates where the current name
  and policy are sufficient; request narrow developer context where meaning is
  absent; do not attempt repository edits.
- Input boundary: send each check's policy once, failed rule IDs per case, and
  only user-supplied context in this increment. Source-code context enrichment,
  reference discovery, collision analysis, and automatic patching remain
  excluded.
- Cost boundary: use one structured model request per eligible batch, no model
  call for deterministically unsupported or context-required cases, concise
  output, and a configurable low-cost test model.
- Security boundary: read the API credential only from `OPENAI_API_KEY`; never
  persist or log it. The credential supplied in chat was not copied into a
  command or repository file. A live smoke requires the app process to receive
  the environment variable separately.
- Provider research: current official OpenAI documentation supports Responses
  API Structured Outputs. `gpt-5-nano` was selected temporarily for the cheapest
  workflow smoke; official documentation marks it deprecated, so production
  model selection remains an explicit exit condition.
- Intended maturity: prototype. Acceptance covers provider/service/API/UI
  contracts, focused fake-provider tests, JavaScript syntax, import smoke, and
  one optional live request. Accuracy evaluation, production retries,
  observability, authentication, and source mutation are not claimed.

### 13:29:59 +05:30 — Verify backend remediation contract before commit

- Implemented deterministic preflight, one-check structured model batching,
  atomic-rule candidate validation, narrow context questions, explicit
  limitations, transient retry/error mapping, and continuation upserts.
- Replayed retained run `20261013_160052_bd9a5d2b` directly from
  `workspace/runs`: parameter failures produced four context questions with no
  model call, required paths produced three limitations, and the selected
  categorical global failure produced one limitation. These generated plans are
  run artifacts and remain outside Git.
- Evidence-to-decision chain: retained atomic failures showed which context is
  actually absent; that drove deterministic preflight. Shared check policy and
  repeated rule text drove policy-once batching. The need to answer questions
  without inflating plan counts drove replace-by-`remediation_id` persistence.
- Options considered and rejected are owned by D018. The selected boundary
  favors low call count and truthful uncertainty over speculative names or
  automatic source mutation.
- Focused backend tests pass through direct invocation because `pytest` is not
  installed. This event closes the first backend commit boundary; UI/evidence
  presentation and final records remain the next increment.

### 13:32:58 +05:30 — Render remediation decisions as persisted evidence

- Added drawer states for candidates, confidence, policy validation, targeted
  questions, limitations, model token evidence, and check-level rules. Answering
  questions continues the same remediation instead of increasing plan count.
- Extended the self-contained evidence pack with the same candidate/question/
  limitation/provenance state and HTML-escaping assertions.
- Updated D018 with the explicit evidence-to-choice chain and corrected the
  earlier readiness audit: maximum length is candidate-eligible when visible
  semantics support conservative abbreviation.
- No reusable skill change was needed. The active lifecycle skill already owns
  incremental commits, retained-run evidence, experiment boundaries, decision
  rationale, and contemporaneous records; duplicating those rules would create
  two authorities.
- Verification passed: Python and JavaScript syntax, all eleven focused direct
  tests, application import, Uvicorn startup, and HTTP 200 responses for the
  static root, retained agent report, and evidence-pack routes.

### 13:35:30 +05:30 — Close committed prototype increments

- Commit `8a2981a` records the provider, service/API contract, persistence,
  focused tests, operating instructions, architecture, and D018 decision.
- Commit `406bc61` records the drawer, evidence export, readiness correction,
  roadmap/testing updates, and evidence-to-choice rationale.
- Problems and retries: the first combined delete/add patch was rejected before
  changing files; the provider was then replaced in supported patch steps. The
  first evidence renderer used an invalid nested f-string; AST verification
  caught it before execution, and an escaped helper replaced it. Initial Git
  staging was denied by the restricted `.git` sandbox and succeeded after the
  scoped approval. A trial `--renormalize` exposed the HTML file's pre-existing
  mixed line endings and inflated the staged diff; only that staged
  normalization was undone, the focused worktree edit was preserved, and the
  final diff used the repository's CR-at-EOL-aware whitespace check.
- Current state: tracked worktree clean after two independently verified
  commits. Generated remediation/evidence artifacts remain in the ignored
  retained run, as intended.
- Remaining experiment gate: the application environment still has no
  `OPENAI_API_KEY`, so no live Responses request or model-generated candidate is
  claimed. The credential shown in chat was never copied into commands, files,
  artifacts, or logs. Once the user configures the environment, run one retained
  function-name request and one question continuation, record response/token
  evidence, and rotate the disclosed credential.

### 15:16:52 +05:30 — Add one-place local credential configuration

- User workflow: edit repository-root `.env.local`, replace the dummy value,
  save, and restart `run.bat`. The tracked `.env.local.example` documents the
  same supported fields without containing a secret.
- Security choice: ignore the editable file in Git, load only three allow-listed
  remediation settings, preserve higher-priority process environment values,
  ignore empty/dummy values, reject unknown keys, and never log loaded values.
- Alternative considered: parse the file only in `run.bat`. Application-level
  loading was selected so direct Uvicorn and test launches behave consistently.
  Adding a dotenv dependency was unnecessary for the three-field contract.
- Verification: Python syntax, all 13 focused direct tests, application import,
  placeholder-not-loaded assertion, Git ignore evidence, fresh Uvicorn startup,
  and an HTTP 200 root smoke passed. The real key remains user-owned and was not
  copied from chat.

### 15:24:32 +05:30 — Record restored run-workspace data-loss event

- User reported that `workspace/runs` had been deleted and restored its contents
  from the Windows Recycle Bin. No deletion was performed as part of the
  remediation/configuration commands, and targeted source inspection found no
  application startup cleanup for the run root.
- Post-restore inventory contains 12 directories and 11 reports; one directory
  is empty, while the retained IDs used earlier in the remediation replay are
  absent. Recovery is therefore recorded as partial until reconciled.
- Opened BUG-002 with high retention priority, unknown initiator, observed versus
  user-supplied evidence separated, current workaround, and closure evidence.

### 16:42:30 +05:30 — Separate ZIP ownership defect from run loss

- Cause check found that local directory ingestion is copy-only, while ZIP
  ingestion unconditionally unlinks its input after successful extraction.
- Opened BUG-003 as unresolved: direct/local ZIP callers can lose a user-owned
  archive because the ingestion contract does not express ownership. The HTTP
  path happens to pass an application-owned temporary copy.
- This does not explain BUG-002: one ZIP-file `unlink` cannot recursively move
  `workspace/runs` to the Windows Recycle Bin. The run-loss initiator remains
  unknown.
- Per user direction, this increment records the defect and selected remediation
  but does not change runtime behavior or execute a destructive reproduction.

### 16:52:38 +05:30 — Diagnose unsupported live remediation and missing lineage

- Retained case `Shunt_getcurrent_ibatt_mA` failed only lowercase word-case, but
  the model-backed path returned no changed candidate and no question after 838
  input and 393 output tokens. The correct mechanical candidate is
  `Shunt_getcurrent_ibatt_ma`.
- Reconstructed the request from code, policy, report, and case data. The exact
  raw model output was not persisted. Read-only retrieval by response ID returned
  HTTP 404 because provider storage was disabled.
- Confirmed continuations overwrite the prior plan record and do not retain
  turn/parent IDs, earlier outputs, answers, or response IDs. Calls are stateless
  and do not use an OpenAI conversation or `previous_response_id`.
- Opened BUG-004 for append-only redacted call evidence and parent/child turns,
  and BUG-005 for deterministic mechanical remediation before model dispatch.
  Per user instruction, no runtime fix was made before design discussion.

### 17:25:44 +05:30 — Start observable remediation-call logging

- Scope was narrowed to logging only: no prompt adjustment, deterministic
  naming classifier, candidate fallback, or additional model-quality retry.
- Added immutable remediation turn records and append-only
  `remediation-calls.jsonl` evidence with redacted exact requests, transport
  attempts, raw responses, parsed output, validation outcomes, developer
  answers, and errors. Continued plans link each new turn to the prior
  `latest_turn_id` while retaining one stable remediation root.
- The first system-Python test attempt stopped before execution because `httpx`
  is absent. The supported `venv313` direct harness then passed all focused
  remediation tests, including continuation lineage, JSONL evidence, retries,
  redaction, missing-key traces, and the unchanged-candidate diagnostic path.
- Current interpretation remains deliberately unchanged: the historic live
  response cannot be recovered, and BUG-005 stays open until a new logged live
  call shows whether the model returned an empty name, the original name, or a
  candidate rejected by local validation.

### 17:28:12 +05:30 — Commit remediation trace and close BUG-004

- Commit `bbacefa` contains the append-only trace contract, linked turns,
  provider transport evidence, regression coverage, and owning documentation.
- BUG-004 is now resolved against 12 focused passing tests. BUG-005 remains open
  by design because this increment did not alter prompts or naming decisions.

### 23:06:43 +05:30 — Add isolated single-case model smoke

- Added one directly executable script under `src/repo_remediation/` that sends
  only a fixed failed function name, its location, the failed rule's actual
  policy definition, and the requested JSON output format to `gpt-5-nano`.
- The script prints raw structured output and highlights the proposed rename. It
  reuses the supported ignored local credential loader and Responses client but
  intentionally bypasses remediation preflight, validation, persistence, and
  call logging so prompt behavior can be observed in isolation.
- Scope excludes a live call; the user will run the script. Verification for
  this increment is syntax/import and focused payload inspection only.
- The first inline fake-client harness was malformed and stopped with a Python
  `SyntaxError` before importing or executing the script. A corrected in-memory
  fake response then exercised direct output parsing/highlighting and confirmed
  the payload contains only `failed_case`, `actual_policy`, and `output_format`.

### 23:42:12 +05:30 — Compile compact model-facing remediation input

- The retained production trace showed the model understood the lowercase rule
  but returned the unchanged name. The successful isolated smoke showed the
  same model could produce the correct name from a minimal request.
- Added `repo_remediation/llm/` boundaries for model settings, prompt
  compilation, structured output parsing/correlation, and full-policy candidate
  validation. The provider now delegates these responsibilities while retaining
  its external contract and trace behavior.
- Model input now omits persistent IDs, locations, rule IDs, modes, validators,
  operands, passing rules, and applicability exclusions. It sends readable
  failed-rule lines with private prompt-local references; application IDs are
  restored only after parsing.
- The example message content decreased from 3,103 to 424 characters. Fourteen
  focused tests pass without a live call; BUG-005 moved to `IN_PROGRESS` pending
  retained live evidence.
- Two verification harness errors were setup-only: Windows Python received an
  unexpanded `*.py` path, and a one-line inspection command had malformed
  quoting. Expanded paths and a PowerShell here-string both passed afterward.
- A later `pytest` attempt stopped before collection because the package is not
  installed; the first direct-test retry likewise stopped before collection
  because `src` was absent from its import path. The supported virtual
  environment with the path inserted passed all 14 focused tests.

## 2026-10-17 — Remediation hierarchy and developer-context workflow

### 01:07:56 +05:30 — Open modular remediation workflow increment

- Goal: give `repo_remediation` responsibility-based package boundaries, make
  one run/check/case/turn hierarchy explicit, avoid regenerating cases already
  covered when a full-check request follows a case request, and accept optional
  developer context before the first model call.
- Starting state: branch `codex/atomic-naming-rules` at `d0db8a1`, clean
  worktree, and 14 focused remediation tests passing in `venv313`.
- Authoritative records: `docs/contracts/run-result.md` owns persistence and API
  shape; `docs/engineering/remediation-generation.md` owns module behavior;
  architecture, decisions, testing, and this history own their respective facts.
- Compatibility boundary: preserve the existing response fields and append-only
  call evidence while adding a uniform per-case projection. Existing stored run
  artifacts must remain readable. No source-code rename application, repository
  context extraction, model comparison, or conversational candidate revision is
  included in this increment.
- Acceptance evidence: characterize existing behavior first; then prove package
  compatibility imports, check-level exclusion of already covered cases,
  question/answer parent-child turns, optional pre-call context, per-case empty
  states, token/latency metrics, and the affected UI request payload.

### 01:22:10 +05:30 — Establish check/case hierarchy and modular boundaries

- Replaced the technology-named `llm/` bucket with responsibility-based
  contracts, adapters, generation, context, hierarchy, result mapping, and
  observability modules. `providers.py` decreased from 768 to 316 lines and now
  composes those boundaries instead of owning HTTP, schemas, redaction,
  measurements, policy questions, and result mapping together.
- Added one check plan per run/check with ordered `case_results`. A case request
  leaves untouched siblings as `not_requested` with null candidates; a later
  full-check request excludes attempted children and merges only missing cases.
  Context answers retain the same remediation root and linked turn chain.
- Added optional case-keyed developer context before the first request,
  check-specific prompt profiles, trusted global-segment questions, and
  normalized `remediation-metrics.jsonl` token/latency/profile evidence.
- Added an initial-context form and case-coverage states to the remediation UI.
  Conversational candidate revision remains explicitly deferred.
- Verification reached 17 focused direct tests, Python compilation, application
  import, evidence-pack hierarchy rendering, and JavaScript syntax. No live
  model call or visual UI claim was made. A literal
  Windows `*.py` compilation attempt failed with `Errno 22`; expanded file paths
  passed afterward.

## 2026-10-21 — Browser verification observations and build-network block

### 12:34:18 +05:30 — Record remediation hardening direction

- User verification confirmed that model-generated remediation candidates are
  now returned and rendered correctly in the browser.
- The review identified five follow-up directions: check-specific prompt
  builders; normalized ownership of product reports versus traces, model
  configuration, telemetry, prompts, calls, and metrics; responsibility-based
  modules/classes/contracts with deprecated smoke paths removed or quarantined;
  documented model and token-setting rationale; and full applicable-policy
  validation after compact failed-rule prompting.
- These are recorded as proposed D023 and roadmap gate G11.1. No implementation
  claim is made in this entry; the next gate requires retained-run inventory and
  evaluation evidence.
- Build/artifact verification is currently blocked by a user-reported VPN
  failure. BUG-006 records the boundary, uncertainty, workaround, and closure
  evidence required before treating the build path as verified.

### 13:07:09 +05:30 — Add build remediation and artifact provenance path

- Added failure-only model remediation after deterministic build classification.
  Full stdout/stderr remains in `build.json`; the bounded model prompt contains
  diagnostic evidence, and the redacted request/response plus validated model
  result is stored in `build-remediation.json`.
- Added retained-run artifact references for failed builds. The current run's
  `artifact_manifest` remains reserved for files it produced; references carry
  `source_run_id`, relative module paths, and `reference_only: true`.
- Verification passed three direct build tests, Python compilation, JavaScript
  syntax, application import, and a read-only scan of retained artifacts. No
  build command or live model call was made while VPN access is unavailable.

## 2026-10-22 — Expand the engineering roadmap into a cross-module evidence graph

### 14:41:38 +05:30 — Update the roadmap view and owning engineering records

- Request: make the front-end Roadmap describe the proposed cross-module graph
  platform, future use cases, integrations, and optional AI extensions.
- Starting point: branch `codex/atomic-naming-rules` at `59d759b`, two commits
  ahead of its upstream. A pre-existing deletion of
  `src/repo_remediation/manual_single_case_test.py` was present and remains
  untouched.
- Changed: replaced four broad roadmap cards with staged sections for code graph
  and evidence foundations, requirements/verification/delivery workflows, and
  later evidence-grounded assistance and prediction experiments. Candidate
  integrations are labeled for evaluation; no future action is presented as
  implemented.
- Owning records: `docs/engineering/roadmap.md` defines gates G13–G15 and
  expands G08/G09; `docs/engineering/architecture.md` describes the current
  static Roadmap surface; D013 now records its staged informational behavior.
- Evidence boundary: current roadmap facts are descriptive plans. Joern/CPG,
  SARIF, ReqIF, and ASAM XIL references were checked against official
  specifications/documentation on 2026-10-22; compatibility, licensing and
  embedded-project fit remain unverified.
- Verification: focused source/diff inspection only; no tests or application
  startup were run for this static content/presentation update.
- Next state: inspect the complete diff, commit only the five roadmap-owned
  paths, and preserve the unrelated pre-existing deletion.

## 2026-10-26 — Reconcile shared-skill governance before repository consolidation

### 17:10:05 +05:30 — Adopt published shared baseline and preserve local layout safely

- Audited all local and remote project branches plus the separate skills
  repository. The active feature branch contains `master` and is 27 commits
  ahead; its work can be retained through a fast-forward integration.
- Found that the project had recorded proposal `b3a619d` as its skills baseline.
  The shared repository now publishes it through `main` revision `d5b8fa3` with
  cross-project conformance, technical-knowledge capture, and structured-LLM
  reliability guidance.
- Adopted D024, created the persistent `project/review-agent` skills branch,
  and recorded PRJ-001. The repository keeps its established
  `docs/engineering/` grouping as a bounded compatibility mapping because root
  policy and existing links bind those paths; no bulk documentation move occurs.
- `structured-llm-reliability` is now the routed technical skill for future
  changes to remediation/build-model contracts, retries, fallbacks, trace
  retention, or model evaluation. No model or application behavior changed in
  this governance increment.
- The uncommitted deletion of `src/repo_remediation/manual_single_case_test.py`
  predates this work and remains untouched. It blocks a fully clean working tree
  until its owner chooses to restore or commit it.

## 2026-10-26 — Retain duplicate historical commits and restore test evidence

### Time not captured — Resolve unreferenced history without rewriting it

- Reviewed two unreachable commit objects. `8040358` and `9710314` each have a
  reachable reissue with the same parent, timestamp, and subject (`46e6e21`
  and `af5c71e`). Tree comparison found only follow-up refinements in the
  reachable versions, so no missing feature should be merged.
- The cause of the lost references is unknown. No reset, rebase, or deletion is
  asserted because no contemporary evidence establishes one.
- D025 retains the original objects as archive tags rather than cherry-picking
  duplicate patches or allowing eventual garbage collection. The frozen review
  records the alternatives, exact refs, and isolated replay boundary.
- The shared skills checkout advanced from `d5b8fa3` to locally resolved
  `b800dfc`. Its one-outcome branch guidance applies forward without rewriting
  retained history. Live fetch authentication was unavailable, so currency
  beyond the tracked revision remains unknown.

## 2026-10-27 — Reconcile saved design conversations and start graph foundations

### Time not captured — Establish authenticated conversation provenance

- Opened the project-owner-supplied private ChatGPT project and enumerated ten
  saved conversations. Selectively inspected the original pipeline design,
  high-level code-intelligence design, stabilization estimate, and latest graph
  design threads.
- Reconciled the evolution from regex/AST inventory through modular review,
  isolated ingestion, optional build, removed local MCP, policy-guided agent
  use, remediation, and the current unified knowledge-graph direction.
- Added PRJ-002 and the repository-local `reviewer-conversation-context` skill.
  The helper normalizes a user-authorized local export/capture and computes
  content SHA-256 values; it does not scrape or authenticate to ChatGPT.
- Current capture is explicitly partial because the project page exposed no
  export or WebMCP tool. No full transcript, secret, or personal content was
  copied into the repository, and null content hashes are not presented as
  change evidence.
- Next state: validate and commit the provenance increment, then extend the AST
  as a separate compatibility-safe code-intelligence package before building
  graph projections.

### Time not captured — Add the compatibility-safe AST graph fact boundary

- Added an independent `code_intelligence` contract and extractor rather than
  changing the established `symbols.json` shape consumed by naming and report
  inventory.
- D026 accepts one canonical node/edge graph with USR-first identities,
  deterministic fallbacks, repository-relative locations, and explicit
  compiler-derived, external, and unresolved relation states.
- The initial extractor covers file, function, struct, enum, typedef, global,
  and macro nodes plus contains, declares, defines, includes, and calls edges.
  It keeps named unresolved targets as labeled nodes so no edge dangles.
- Three focused pure-Python scenarios passed by direct invocation. The supported
  environment lacks both pytest and Black; those command attempts were recorded
  as environment limitations rather than passes.
- Next state: merge translation-unit fragments into one deterministic snapshot,
  persist it atomically, and implement call/include views over that authority.

### Time not captured — Implement the first unified graph and projections

- Added stable-identity fragment merge with deterministic ordering and explicit
  failure on incompatible node/edge facts or dangling endpoints. Definition
  metadata wins over declaration-only metadata for a shared symbol identity.
- Added canonical snapshot serialization with required source revision, dirty
  state, producer, and producer-version provenance. Writes flush a sibling
  temporary file and atomically replace the target; failures remove the partial
  temporary file.
- Added call and include projections that select nodes and edges from the
  canonical graph and expose unresolved-edge totals without writing separate
  graph authorities.
- Five focused graph scenarios and the three AST scenarios pass by direct
  invocation; Python syntax and the configured 88-column boundary also pass.
- Next state: connect a compilation database and real libclang translation units
  to the package, capture configuration/tool provenance, then write one graph
  snapshot under the run analysis directory.

### Time not captured — Inventory all discussed graphs and choose shared analysis ownership

- Re-enumerated the authenticated project conversation list; the same ten
  conversation IDs remain, so no new thread required import.
- Consolidated aliases into 21 distinct graph capabilities and recorded the
  exact source, engine, project-model, or external evidence each requires.
- Confirmed that reachability, call depth, file-module dependency, and initial
  dependency impact are derivable from the current canonical graph. Variable
  access, exact-clone candidates, complexity, and memory estimates require a
  bounded AST expansion. CFG/data flow, requirements, tests, timing, exact
  stack, and failure propagation cannot be made complete from symbol fields.
- D027 assigns compilation-database parsing and normalized AST facts to the
  shared `code_intelligence` package. Review and graph workflows will consume
  one analysis result; the existing duplicate review parse remains a truthful
  migration limitation until compatibility is verified.
- Next state: commit the capability contract, then implement current-fact views
  before expanding AST facts and moving compilation-database parsing.
