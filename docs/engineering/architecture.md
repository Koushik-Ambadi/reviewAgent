# Current Architecture and Module Guide

- Status: living
- Created: 2026-10-06
- Last reviewed: 2026-10-27 for the shared code-analysis boundary
- Update trigger: module boundary, interface, data contract, dependency, or
  execution-flow change
- Source of truth for: current system shape and module responsibilities
- Does not own: historical chronology, future work, or individual rule wording

## System purpose and boundary

The system reviews an embedded C repository against a YAML policy. Its current
automated path covers required repository paths and eight symbol-naming check
families. It depends on the target project being CMake-configurable so it can
produce `compile_commands.json`, and on libclang being able to parse the
resulting translation units after compiler-argument sanitization.

The service also exposes a build trigger and a read-only manager projection.
Review and build share the ingested workspace, while the manager view derives
latest-per-module statistics and comparisons from the same persisted reports.
The build path is Windows-specific because it invokes `cmd /c cmake-build.bat`.

## Context and data flow

```text
Browser / API client
  |
  | ZIP + policy name fixed to default by service
  v
app.api.review -> app.services.review_service
  |
  v
orchestrator.prepare_review_run
  |-- creates workspace/runs/<timestamp>_<uuid8>/
  |-- extracts or copies one repository
  `-- returns workspace_path, repo_root, module_name
  |
  v
repo_review.run_review (facade)
  |
  v
PipelineContext -> structure -> analysis -> naming -> reporting
  |                |            |           |
  |                |            |           `-- report.json (RunResult v2.0)
  |                |            `-- checks read analysis/symbols.json
  |                `-- cmake_build/compile_commands.json
  |                    -> one libclang parse per translation unit
  |                    -> symbols.json + code-intelligence.json
  `-- stage_results accumulate typed results
  |
  +--> web UI renders stages/checks/cases
  +--> agent endpoints summarize failed/skipped cases
  +--> manager endpoints aggregate and compare persisted runs without writes
  |--> remediation endpoint reads failed cases and writes provider output
  `--> build endpoint resolves repo from report metadata and runs batch script
```

Dependency direction is mostly entry point -> orchestration -> review/build
domain packages. `repo_review` no longer owns uploads or source ingestion. That
boundary was introduced in `4217116` and is one of the clearest architectural
improvements in the history.

## Repository layout

```text
app/
  api/                 FastAPI route adapters, including read-only graph views
  services/            upload, policy, graph, and agent-response services
  static/              single-page HTML/CSS/JavaScript client
src/
  code_intelligence/     additive compiler-derived graph contracts and extraction
  orchestrator/        run workspace, source ingestion, review/build sequencing
  repo_build/          firmware build execution and result DTO
  repo_review/
    analysis/          compile database and libclang symbol inventory
    checks/            structure and naming policy evaluators
    contracts/         typed result/status model and aggregation builders
    pipeline/          mutable context and ordered stages
    policies/          active default YAML policy
    reporting/         stable IDs, serialization, report persistence
    tests/manual/      ad hoc manual scripts, not an automated suite
  tests/manual/        older pipeline scripts; currently stale
docs/                  indexed engineering, standards, contracts, diagrams, archive
skills/                ignored local lifecycle skill used to maintain records
workspace/runs/        ignored generated run inputs and evidence
```

`code_intelligence` is now an active analysis dependency. It owns libclang
configuration, compile-argument sanitization, and translation-unit parsing;
the review analysis stage passes each parsed cursor to both the compatibility
inventory walker and graph extractor, then merges deterministic graph fragments
into an invariant-checked canonical graph, atomically writes provenance-bearing
snapshots, and derives call/include, explicit-root reachability/call-depth,
file-module dependency, changed-node impact, variable-access, exact-clone,
complexity, and type-size memory-estimate projections. D026 selects it as
the eventual shared owner because review, build, and agent workflows may all consume
repository intelligence. The resulting `code-intelligence.json` snapshot is
persisted beside `symbols.json`; independent graph-only orchestration is not yet
wired into the application.

D027 fixes the boundary: `code_intelligence` parses every translation unit once.
Review inventory and graph extraction currently project the same cursor. The
legacy inventory cursor walker remains only to preserve `symbols.json`; removing
it requires a verified graph-to-inventory compatibility adapter.

## Public interfaces

### HTTP API

| Method and path | Input | Output | Owner |
|---|---|---|---|
| `POST /api/review` | Multipart `.zip` | `{run_id, report}` where report is serialized `RunResult` | `app/api/review.py` |
| `POST /api/agent/review` | Multipart `.zip` | Compact failed/skipped summary | `app/api/review.py`, service formatter |
| `GET /api/agent/review/{run_id}` | Run ID path value | Detailed agent-oriented failure text | `app/api/review.py`, service formatter |
| `GET /api/graphs/catalog` | None | Latest graph-bearing run per module | `app/api/graphs.py`, `app/services/graph_service.py` |
| `GET /api/runs/{run_id}/graphs` | Run, file/module scope, optional file and overlays | Read-only graph workspace projection | `app/api/graphs.py`, `app/services/graph_service.py` |
| `GET /api/graphs/inter-module` | Optional module names and overlays | Latest-per-module interactions and signal directions | `app/api/graphs.py`, `app/services/graph_service.py` |
| `POST /api/runs/{run_id}/build` | Run ID path value | Final `BuildResult`, or queued job with `background=true` | `app/api/build.py` |
| `GET /api/runs/{run_id}/build/status` | Run ID path value | Persisted build job state and recent raw output | `app/api/build.py` |
| `POST /api/runs/{run_id}/remediations` | Scope plus failed check/case IDs | `{run_id, remediation}` | `app/api/remediation.py` |
| `GET /api/manager/portfolio` | None | Latest run per module, portfolio aggregates, exceptions, and preview workflow data | `app/api/manager.py`, `manager_service.py` |
| `GET /api/manager/modules/{module_name}` | Module name | Ordered persisted run history, latest failures, and comparison defaults | `app/api/manager.py`, `manager_service.py` |
| `GET /api/manager/modules/{module_name}/compare` | Optional base and target run IDs | Target-minus-base summaries, check deltas, and new/resolved failures | `app/api/manager.py`, `manager_service.py` |
| `GET /api/policies/{policy_name}` | Policy name path value | Parsed YAML template | `app/api/policy.py` |

There are no explicit Pydantic request/response models, authentication,
authorization, upload-size limits, or exception translation around most domain
errors. Those are current limitations, not hidden features.

### Python facade

`repo_review.review.run_review(repo_root, workspace_path, module_name,
policy_name="default")` constructs a `PipelineContext`, runs the ordered stages,
and returns the context. The caller reads `context.report`, `report_path`, and
other accumulated state.

### Generated artifacts

| Path within run | Producer | Consumers | Retention status |
|---|---|---|---|
| `<module>/` | orchestrator ingestion | analysis, structure checks, build | Ignored generated copy |
| `analysis/cmake_build/compile_commands.json` | CMake source index | libclang compilation database | Ignored generated evidence |
| `analysis/symbols.json` | symbol inventory | naming checks, manual inspection | Ignored generated evidence |
| `analysis/code-intelligence.json` | canonical schema 1.1 graph plus provenance | graph views and future review/build/agent consumers | Ignored generated evidence |
| `report.json` | reporting stage | UI response, agent GET, build repo resolution | Ignored generated evidence |
| `remediation.json` | remediation service | Report drawer, later decision workflow | Ignored generated evidence |
| `remediation-calls.jsonl` | remediation service | Call diagnosis, retry audit, and turn replay | Ignored append-only generated evidence |
| `build.json` | build orchestration | Build result UI, later evidence export | Ignored generated evidence |
| `build-progress.json` | background build job | Live build status/output polling | Ignored generated evidence |

The report is the only persisted run metadata. There is no separate manifest
with source checksum, code revision, command, environment, or completion state.

## Core data structures

### `PipelineContext`

Mutable stage-carrier dataclass in `pipeline/context.py`.

- Inputs: `policy_name`, `workspace_path`, `repo_root`, `module_name`.
- Runtime state: parsed policy, ordered `stage_results`, diagnostics, report,
  and typed `run_result`.
- Invariant: analysis must run before naming because naming reads
  `workspace_path/analysis/symbols.json`.
- Side effects: stages create analysis directories and persist JSON.
- Constraint: `report_path` is assigned dynamically although it is not declared
  on the dataclass.

### Result contract

`contracts/models.py` defines dataclass DTOs:

- `CaseResult`: one checked item, status, name, location, stable case ID, reasons.
- `CheckResult`: check identity/title, completion status, summary, cases.
- `StageResult`: stage identity/title, completion status, summary, checks, and an
  optional typed inventory projection with aggregate items and grouped artifact
  records.
- `RunResult`: run metadata, policy/report versions, aggregate status/summary,
  stages, remediation, and optional build result.

`contracts/status.py` separates case outcomes (`SUCCESS`, `FAILED`, `SKIPPED`)
from check/stage execution state (`COMPLETED`, `ERROR`, `SKIPPED`) and run state
(`COMPLETED`, `PARTIAL`, `ERROR`). Aggregation in `contracts/builders.py` sums
case outcomes upward.

Observed semantic gap: the reporting stage always creates a `COMPLETED` run,
even when cases fail, and stages do not catch failures to create `ERROR` or
`PARTIAL` results. Current `COMPLETED` therefore means the pipeline finished,
not that compliance passed.

### Symbol inventory

Each `symbols.json` element represents one parsed source file and contains:

- relative file path and include names;
- defined and declared functions;
- global and local variables, including type, location, and recovered array
  suffixes;
- parameters;
- structs and fields;
- enums and constants;
- typedefs;
- user macros and their classification/replacement.

The inventory is a derived intermediate representation, not an authoritative
copy of source. A file without a compilation command is not represented. Report
version 2.2 persists aggregate parsed/skipped file coverage, extracted symbol
family counts, and individual grouped artifacts with report-local identities,
source evidence, and initial audit states. Individual skipped paths and reasons
remain outside `report.json`.

### `BuildResult`

`repo_build.models.BuildResult` records a run ID, format and build steps, status,
normalized and process return codes, repository root, script name, raw
stdout/stderr, selected diagnostics, current artifact manifest, retained-run
artifact references, deterministic intelligence summary, optional model
remediation, detected build log path, and UTC start/completion timestamps. The
build service writes `build.json`, optionally writes `build-remediation.json`,
and updates the canonical report.

### Structure tree types

`checks/structure/models.py` uses Pydantic models for a `FileNode` and legacy
`ValidationIssue`. The active required-path checker consumes `FileNode`; the
other structure validators still return legacy issue dictionaries and are not
included by the active runner.

## Module guide

The sections below are the project-level map. Detailed local mechanics and
direct context routes live in the [module guides](../modules/README.md): review
pipeline, analysis inventory, policy-driven checks, and result contract/reporting.
The existing [remediation generation](remediation-generation.md) record remains
the local owner for model-assisted behavior.

### `app/main.py`

- Responsibility: application composition.
- Inputs: imported routers and relative `app/static` directory.
- Outputs: `FastAPI(title="Review Agent")` instance.
- Side effects: mounts static files at `/`, after API routers.
- Technology: FastAPI/Starlette/Uvicorn.

### `app/api`

- `review.py` validates only the `.zip` filename suffix, then delegates upload
  and reporting work synchronously from async routes.
- `build.py` and `remediation.py` map invalid or missing run data to HTTP errors,
  then delegate to their application/domain services.
- `policy.py` loads a named YAML policy and maps missing files to HTTP 404.

These are thin adapters, consistent with the entry-point pattern. Long-running
CPU/subprocess work is not moved to a worker or thread pool.

### `app/services/review_service.py`

- Responsibility: save uploads, invoke orchestration/review, form HTTP response,
  and transform reports for agent consumers.
- Inputs: FastAPI `UploadFile`, run ID, legacy or `RunResult` report dict.
- Outputs: response envelopes or textual failure summaries.
- State: local upload directory and ignored run directory.
- Compatibility: contains both legacy `sections` report handling and new
  `stages` handling, reflecting the July-to-October contract migration.
- Debt: the file is more than 1,000 lines and defines `clean_report_path`,
  `humanize_rule`, and `normalize_status` twice. The old formatter remains in
  the same module as the current compatibility path.

### `app/services/policy_service.py`

Loads `src/repo_review/policies/<name>.yaml`. Its responsibility overlaps with
`pipeline/utils.py`, which independently resolves and loads the review policy.
The API returns templates; the pipeline owns execution-time loading.

### `app/services/manager_service.py`

- Responsibility: read valid `report.json` files and derive portfolio, module,
  exception, and comparison representations.
- Inputs: the configured run root plus optional module/base/target identifiers.
- Outputs: JSON-safe dictionaries; no generated artifact or persisted workflow
  state.
- Main flow: load reports, recover legacy run IDs from directory names, group by
  case-insensitive module name, sort by persisted generation time, select the
  latest report per module, and aggregate its already-persisted summaries.
- Comparison: target counts minus base counts, per-check summary deltas, and
  new/resolved failed cases matched by persisted case ID with a report-visible
  legacy fallback.
- Failure behavior: unreadable/non-object reports are counted as ignored in the
  portfolio source metadata; missing modules/runs and invalid run selections are
  translated by the API adapter.
- Prototype boundary: approval counts, owner/ticket actions, PR/CI status, and
  insight items are marked preview-only and are never written. A production
  workflow requires identity, authorization, durable state, and integration
  contracts before those controls can become active.
- Verification: `tests/test_manager_service.py` covers latest-per-module
  selection, ordering, default comparison IDs, deltas, and failure-set changes.

### `app/static`

- `index.html`: page structure and CSS for landing, setup/activity, report,
  build, remediation drawer, planned-capabilities, and manager views.
- `app.js`: POSTs the ZIP, renders the `RunResult` stage/check/case hierarchy,
  provides multi-select status/stage/check facets plus search, keeps Report and
  Build tabs on the active run ID, exposes the non-interactive Roadmap view,
  requests provider-independent remediation suggestions, and renders the
  structured build result.
- A stage is visible when it has compliance cases or inventory items. Analysis
  inventory therefore renders even when the stage has no cases. Stage and text
  filters apply to it; status and check facets exclude it because extracted
  records do not have compliance outcomes. Reports without `inventory` retain
  the previous behavior.
- The Analysis inventory keeps aggregate cards at the top and renders non-empty
  symbol families as collapsible audit groups. Each row shows the artifact name,
  source location, extracted evidence, audit state, and audit rationale slot.
  Report 2.1 count-only inventory remains readable and prompts for a rerun when
  detailed groups are absent.
- `manager.js`: owns manager-only client state, loads the read-only manager
  endpoints, switches the four manager tabs, renders latest module summaries,
  drills into module history, requests selected-run comparisons, groups/selects
  visible failed cases, and provides preview-only ownership/ticket feedback.
- The manager workspace is entered separately from the landing page; it is not a
  developer run tab and does not alter `currentRunId`, `currentReport`, the
  selected ZIP, or build polling state. Its internal tabs are Portfolio overview,
  Exception queue, Tickets and ownership, and Audit and delivery.
- Exception selection is client-local and limited to the first 120 rendered
  cases for a responsive prototype; group totals still reflect the complete
  latest-run portfolio. Owner, ticket, approval, PR, and CI controls only explain
  what would happen and make no request that writes state.
- Manager insight cards consume the provider-independent insight envelope from
  the API. Placeholder content is visibly labelled, allowing later deterministic
  remediation or governed model output to use the same visual wrapper.
- Both workspace tabs expose the run-scoped HTML evidence-pack download. New and
  re-run actions preserve the current architecture: re-run reuses the browser's
  selected ZIP, while new review returns to the upload/profile view.
- The upload view reads the default profile from `GET /api/policies/default` and
  uses the same explicit defaults as a display-only fallback if that read fails;
  no profile selector or multi-project behavior is implied.
- The workspace navigation contains navigation only. Review actions remain on
  the review page, build actions remain on the build page, and evidence download
  is available from both evidence-bearing views. Run/profile metadata is titled
  and collapsed by default because it is supporting context; its summary retains
  the selected profile and module.
- The Code graphs tab is the interactive engineering view over canonical run
  artifacts. It combines available overlays across file, module, and
  inter-module scopes, keeps a textual relationship fallback, and drills from
  high-level nodes to lower scopes. Disabled CFG/data-flow controls explain the
  missing engine instead of implying an empty result.
- File graphs are function-centric: parameters and locals remain owned details
  in the inspector unless explicitly expanded. Selection centers one node and
  dims unrelated facts; aggregate module edges expose bounded underlying symbol
  interactions. The dependency-ranked layout reduces crossings heuristically,
  without claiming a minimum-crossing solution.
- Edges are clipped to node boundaries. Different relationship kinds receive
  stable parallel lanes, while repeated occurrences of the same relationship
  aggregate with retained locations. File-projection symbols carry bounded
  cross-file declaration/definition and incoming/outgoing interaction evidence
  for side-panel inspection; these facts remain unordered.
- The graph workspace has two presentations over one canonical artifact:
  overview projections and an expandable trace playground. Trace expansion uses
  run-wide node-index and neighborhood projections; branch-local instance IDs
  may duplicate a canonical symbol visually but always retain `canonical_id`.
- Landing and setup use dynamic viewport sizing on normal desktop layouts. The
  setup configuration and activity panels share one height, while the activity
  log flexes inside its panel. Narrow or short displays retain page scrolling as
  an accessibility and content-safety fallback.
- The Roadmap tab is a static, staged description mapped to engineering gates
  G02/G08/G09/G11/G12 and proposed future gates G13–G15. It presents cross-module
  code/evidence graphs, requirements and test traceability, change impact,
  governed delivery workflows, and later evidence-grounded assistance. Engine
  and interchange options remain evaluations; no roadmap item is a callable
  action or an implemented capability. Approval, compliance, integration, and
  prediction claims remain gated by their documented evidence and authorization
  requirements.
- The progress display is explicitly simulated (`startFakeProgress`); it is not
  server-side stage telemetry. Its purpose is perceived activity during the
  current synchronous review request, not operational observability.
- HTML is escaped before report values are inserted into templates.

### `orchestrator`

- `workspace.py`: creates timestamp-plus-random run IDs under
  `Path.cwd()/workspace/runs`; creation is exclusive.
- `ingestion/ingestion_manager.py`: dispatches `local` or `zip` sources.
- `local_ingestion.py`: copies a source tree into the run directory.
- `zip_ingestion.py`: extracts the archive, requires exactly one top-level
  directory, deletes the uploaded ZIP where possible, and returns that directory.
- `runner.py`: facade joining workspace creation and ingestion; derives the
  module name from repository directory name.
- `run_store.py`: validates run IDs and centralizes canonical report JSON access.
- `build.py`: opens `report.json`, obtains `metadata.module_name`, reconstructs
  the repository path, writes `build.json`, and updates the canonical report.

The package implements orchestration/facade and adapter-dispatch patterns. ZIP
extraction currently uses `extractall` without member-path validation.
The resulting Windows long-path failure is tracked as
[BUG-001](known-issues.md#bug-001--windows-zip-extraction-fails-on-overlong-nested-git-paths);
the selected remediation remains unimplemented.
The ZIP adapter also unconditionally deletes its input even though ownership is
not part of its contract. The HTTP caller supplies a private temporary copy, but
direct callers may supply user-owned archives; this remains unfixed in
[BUG-003](known-issues.md#bug-003--zip-ingestion-deletes-caller-owned-archives).
Local directory ingestion is copy-only and does not delete its source.

### `repo_build`

- `builder.py`: checks repository-local batch wrappers and streams captured lines.
- `formatting.py`: reads an explicit optional `review-build.json` formatter wrapper.
- `models.py`: typed DTO.
- `parser.py`: maps return code to status, detects fatal output that a batch wrapper
  may mask, and probes two build-log locations.
- `reporter.py`: DTO-to-dict mapping.
- `runner.py`: timestamps and composes builder/parser/reporter.

`artifacts.py` restricts discovery to useful build outputs (`.elf`, `.hex`,
`.bin`, `.map`, logs, and generated reports). `intelligence.py` provides a
provider boundary, diagnostic selection, and deterministic classification for
known license, build-adapter, compiler-validation, and linker failures. Unknown
output retains an explicit generic fallback.

  `orchestrator/build_jobs.py` runs UI-started builds on a bounded worker pool and
  persists `build-progress.json`; progress read/modify/write operations are
  serialized per run because output callbacks and terminal state updates share
  an atomic replacement path on Windows. Persistence uses process-safe unique
  temporary files and short replacement retries, and live telemetry failures
  cannot abort the build. The final build still becomes
  `build.json` and `RunResult.build_result`. This lets the static UI poll live
  output without changing the synchronous API behavior used by callers that need
  a final result. Worker ownership is process-local; a queued/running snapshot
  left by a server restart is treated as stale and can be restarted.

### `repo_remediation`

Detailed implementation and extension boundaries are owned by
[Remediation generation](remediation-generation.md).

`repo_remediation/contracts.py` defines the provider-independent suggestion and
transport protocols. `providers.py` contains the OpenAI-backed and offline
workflow implementations; external HTTP transport lives in `adapters/`,
model-facing behavior in `generation/`, context gates in `context.py`, hierarchy
projection in `hierarchy.py`, report mapping in `results.py`, and call
evidence/metrics in `observability/`.

`RemediationProvider` defines a provider-independent suggestion boundary.
`OpenAIRemediationProvider` is the interactive default. It receives one failed
check, that check's active policy, and all selected failed cases. Deterministic
preflight partitions cases into model-eligible candidates, developer-context
questions, and unsupported limitations. One strict-schema Responses API call is
made only when eligible cases remain. The model-facing compiler sends only
current names, optional developer context, and readable atomic rules that
actually failed. Prompt-local `C1`/`R1` references replace persistent
case/rule IDs. Locations, validator fields, passing rules, and applicability
exclusions stay outside the prompt.

Ordinary naming candidates are validated again against the complete check
policy with the atomic-rule evaluator, including constraints omitted from the
compact prompt.
Global categorical repairs request trusted module/type/size/unit/meaning context
before generation; their candidates still cannot be fully revalidated without
symbol type. Required-path creation remains a limitation. Single-letter
parameters, ambiguous local names, symbolic array sizes, and absent semantic
descriptions request narrow context. A model may also request one question when
the visible name is ambiguous.

`OpenAIResponsesClient` reads `OPENAI_API_KEY`, disables response storage,
bounds output, uses minimal reasoning, applies a configurable timeout, and
retries one transient network/429/5xx failure. It never persists credentials.
The placeholder remains an offline compatibility provider, and the former
future-provider name is now an alias.

At startup, `app.local_env` loads only the three allow-listed remediation
settings from repository-root `.env.local`, without overriding process
environment values. The real local file is Git-ignored; `.env.local.example` is
the tracked shape. Placeholder and empty values are ignored, malformed or
unknown keys stop startup, and no loaded value is logged or added to run data.

The remediation service rejects policy-version drift and maintains one
check-scoped plan per run/check. Ordered `case_results` children preserve
candidate, context-required, limitation, and not-requested states. Case requests
update one child; later check requests exclude attempted children and fill only
missing ones. Optional per-case developer context can be supplied on the first
request. Continued questions retain immutable linked turns under the same plan.
The API also retains derived candidates, confidence, validation, questions,
limitations, usage, and rules for compatibility. Each request appends a redacted
turn to `remediation-calls.jsonl`, including the exact provider request, raw
response, retries, parsed output, validation outcome, and developer answers.
Successful model calls append normalized latency/token/profile evidence to
`remediation-metrics.jsonl`.
Transport/provider failures are recorded before their HTTP error is returned.
No provider edits source or treats a candidate as approved.

`app/static/app.js` renders that contract in the remediation drawer and posts
question answers with the existing plan ID. It replaces the matching in-memory
plan so badges count decisions rather than request turns. The evidence service
projects the same persisted state into escaped, self-contained HTML.

Prototype limitations remain explicit: reports reference rather than embed the
exact policy snapshot; repository collisions and references are not checked;
global candidates cannot be fully revalidated without symbol type; source
context is manual; and the inexpensive default model is a workflow-test choice,
not a production quality decision.

The trace persistence added for
[BUG-004](known-issues.md#bug-004--remediation-calls-lose-raw-requestresponse-and-turn-lineage)
is intentionally local and append-only. It records observable inputs, outputs,
transport evidence, and application validation; it does not claim access to
hidden model reasoning. Generated traces remain inside the ignored run workspace
and therefore still depend on the unresolved retention boundary in BUG-002.
Mechanical atomic failures are not transformed before model dispatch, allowing
an unchanged/empty model candidate to become an unsupported result; see
[BUG-005](known-issues.md#bug-005--mechanical-naming-failures-can-return-unsupported-model-output).

The separation is clean but small; it makes execution and result formation
independently replaceable. The concrete builder is Windows-only, while the
container is Linux-based.

### `repo_review.analysis.source_index`

`generator.py` creates a clean `analysis/cmake_build` directory and runs CMake
with Ninja, `AST_ANALYSIS=ON`, and compilation-database export. On POSIX it
forces GCC/G++, and injects configured compiler paths only if they exist.

Inputs are repository root, analysis directory, and policy. Output is a status
dictionary plus the generated database. A prior build directory is recursively
deleted, so the analysis directory must remain run-scoped.

### `repo_review.analysis.symbol_inventory`

- `libclang_resolver.py`: searches environment, package, Linux glob, and Windows
  candidates before failing with a configuration message.
- `compile_args.py`: removes output/dependency/vendor compiler flags and forces
  C99 parsing.
- `extractor.py`: loads the compilation database, restricts files to configured
  folders/extensions, deduplicates entries, parses each translation unit, and
  writes `symbols.json`.
- `analysis/runner.py`: derives the report inventory from the extractor's
  returned `results` without rereading source. One linear projection groups
  function definitions/declarations, global/local variables, parameters,
  structures and fields, enumerations and constants, type definitions, and
  macros. It creates deterministic report-local IDs, retains source evidence,
  records parsed/skipped coverage, and initializes every artifact
  `not_audited`.
- `ast_walker.py`: recursive cursor dispatcher, excluding nodes outside the
  repository and macros outside configured target folders.
- `symbol_extractors.py`: converts Clang cursors and source text into JSON-safe
  records, including array declarations and nested type information.

This is a compiler-assisted analysis design. It uses real build flags rather
than parsing C with regex alone, but applies targeted source-text recovery where
libclang cursors do not retain the exact desired spelling.

### `repo_review.checks.structure`

The folder contains validators for required/forbidden paths, extensions, file
types, size, and tree limits. The active `runner.py` currently executes only
`validate_required_paths`; imports of the other validators do not make them
active. Required paths support exact directories and `fnmatch`-style patterns,
with `{module}` expansion performed inside the validator.

This distinction matters: the check catalog labels several platform
capabilities as existing, but the current execution path proves only required
paths are wired into `RunResult`.

### `repo_review.checks.naming`

The runner reads `symbols.json` once and returns eight `CheckResult` objects:

1. functions;
2. value macros;
3. type names;
4. enum constants;
5. parameters;
6. local variables;
7. symbolic array dimensions;
8. globals.

`common_identifier.evaluate_atomic_rules` is the shared policy interpreter for
validators such as regex, min/max length, prefix/suffix, casing, and non-empty
description. Functions, macros, types, enums, locals, and parameters reuse it.
Global-variable naming remains a specialized grammar because it decomposes
type, size, module, unit, and description segments. Array-size checking remains
specialized because it classifies literal and expression forms.

The policy owns automatic/manual mode, source rule ID, reason text, expected
values, module casing, applicability, and pointer-depth conditions. Detailed
coverage belongs to the
[`naming-policy-audit.md`](../standards/naming-policy-audit.md).

### `repo_review.pipeline`

The ordered stages are hard-coded:

1. structure;
2. analysis;
3. naming;
4. reporting.

This is a simple pipeline pattern with a shared context. It makes stage order
explicit and was progressively simplified from a more generic stage framework
in May. The trade-off is no stage registry, conditional execution, rollback,
or structured error capture.

### `repo_review.reporting`

- `formatter.py` enriches `RunResult` with run/policy/report metadata and uses
  UUIDv5 over check ID, location, case name, and case index for deterministic
  case IDs.
- `serializer.py` recursively converts dataclasses, enums, paths, lists, and
  dictionaries.
- `reporter.py` writes indented JSON to the run root.

Case identity is deterministic only while check ID, location, name, ordering,
and extraction behavior remain unchanged. It is stable enough for one contract
version, not a permanent symbol identifier.

### Policy and standards

`policies/default.yaml` is version 4. It owns required paths, AST target folders
and extensions, automatic atomic naming rules, exclusions, manual-only source
requirements, the global-name vocabulary, and symbolic array patterns. The
rulebook YAML is the source-traceability inventory; the executable policy is the
runtime decision authority.

### Tests and generated workspaces

Tests are standalone scripts with local absolute paths or retained-run IDs.
There is no discovered pytest suite or CI workflow. Workspaces preserve useful
derived artifacts but are ignored by Git and lack a manifest. See
[`testing-and-replay.md`](testing-and-replay.md).

## Cross-module constraints

These constraints belong here because they describe the current system boundary.
Roadmap gates may link them, but must not become a duplicate constraint owner.

### Trust and execution boundary

- ZIP ingestion uses `ZipFile.extractall` without member-path, link, entry-count,
  or expanded-size validation; uploads are read fully into memory without a
  configured size limit. Deep archive members can also fail with Windows path
  error 206; see BUG-001.
- Run and policy identifiers become path components without a strict validated
  identifier contract.
- HTTP endpoints have no authentication or authorization.
- Firmware build executes a script from the reviewed repository with service
  permissions; workspaces may copy nested Git metadata, credentials, generated
  artifacts, or proprietary material without classification or redaction.

### Result and configuration boundary

- Pipeline exceptions abort the run instead of becoming typed `ERROR` results,
  and `RunStatus.COMPLETED` does not distinguish policy pass from failure.
- Skipped-file diagnostics exist during analysis but are not persisted in the
  report, so consumers cannot measure all missing coverage.
- Policy access uses raw mapping keys without schema validation.
- Case identity depends partly on ordering and source location.
- Legacy/current report compatibility has no recorded removal condition.

### Operations and portability boundary

- Workspace, upload, and static roots depend on the process working directory.
- Review analysis can run in the Linux image, while firmware build remains tied
  to Windows `cmd` and a batch script; the container command also enables reload.
- Filesystem, CMake, libclang, and build operations run synchronously in request
  handlers without a job queue, cancellation, timeout, or resource quota.
- Analysis recreates its build directory without an atomic completion marker.
- No health/readiness endpoint, structured telemetry, run-state API, workspace
  retention process, or disk-capacity policy is present.

### Maintenance boundary

- `review_service.py` combines upload flow, current and legacy report shaping,
  and duplicate helper responsibilities.
- Policy loading exists in both application and review layers.
- Some source headers still describe former paths.
- The dependency set retains the historical MCP environment and does not
  distinguish direct, optional, and transitive packages.
- Project metadata does not yet define a console entry point or an integrated
  formatter, linter, type-check, test, and CI contract.

## Design patterns evidenced by the code

| Pattern | Evidence | Why it fit | Trade-off visible now |
|---|---|---|---|
| Pipeline | Ordered stage functions over `PipelineContext` | Makes review phases and artifact dependencies explicit | Exceptions abort instead of becoming typed stage errors |
| Facade/orchestration | `run_review`, `prepare_review_run`, `execute_firmware_build` | Keeps entry points small and coordinates subsystems | Context and dictionaries remain loosely typed at boundaries |
| Policy/strategy by configuration | YAML chooses rule values and applicability | Standards change without rewriting every checker | No schema validation before use; missing keys fail at runtime |
| DTO plus builders | Dataclass results and aggregation helpers | One stable shape for UI, agents, and future checks | No runtime validation/version migration layer |
| Adapter dispatch | Local versus ZIP ingestion | Isolates source acquisition from review logic | Only two local adapters; Git/S3 plans were removed |
| Compatibility adapter | Legacy `sections` and current `stages` report paths | Allowed contract migration without immediately breaking agent clients | Large duplicate formatter surface remains |

## Technology stack

- Runtime: Python 3.11+ metadata; Docker currently uses Python 3.13.
- Web: FastAPI, Starlette, Uvicorn, multipart upload handling.
- Models/config: dataclasses, Pydantic, PyYAML.
- C analysis: CMake, Ninja, GCC/G++, Python Clang bindings, libclang.
- UI: static HTML/CSS and vanilla JavaScript.
- Packaging/deployment: `pyproject.toml`, fully pinned `requirements.txt`, Docker,
  Windows batch scripts.
- Historical agent integration: FastMCP/MCP was added locally and then removed
  in favor of a remote MCP boundary; MCP packages remain in dependencies.

There is no tracked LLM inference, model provider, prompt execution, retrieval,
embedding, or evaluation loop in the current service. “Agent” currently means
agent-oriented HTTP representations plus the historical/remote MCP boundary;
any model reasoning happens outside the evidence available in this repository.

Only FastAPI, Pydantic, PyYAML, and Clang are directly imported by current
application source. The dependency file includes the former MCP stack and its
transitive packages, so it behaves more like an environment freeze than a
minimal direct-dependency declaration.
