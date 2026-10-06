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
