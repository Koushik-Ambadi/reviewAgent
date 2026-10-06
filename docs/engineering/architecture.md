# Current Architecture and Module Guide

- Status: living
- Created: 2026-10-06
- Last reviewed: 2026-10-06 at revision `c603a69`
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

The service also exposes a build trigger. Review and build share the ingested
workspace, but the build path is Windows-specific because it invokes
`cmd /c cmake-build.bat`.

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
  |                `-- cmake_build/compile_commands.json -> symbols.json
  `-- stage_results accumulate typed results
  |
  +--> web UI renders stages/checks/cases
  +--> agent endpoints summarize failed/skipped cases
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
  api/                 FastAPI route adapters
  services/            upload, policy, and agent-response application services
  static/              single-page HTML/CSS/JavaScript client
src/
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

## Public interfaces

### HTTP API

| Method and path | Input | Output | Owner |
|---|---|---|---|
| `POST /api/review` | Multipart `.zip` | `{run_id, report}` where report is serialized `RunResult` | `app/api/review.py` |
| `POST /api/agent/review` | Multipart `.zip` | Compact failed/skipped summary | `app/api/review.py`, service formatter |
| `GET /api/agent/review/{run_id}` | Run ID path value | Detailed agent-oriented failure text | `app/api/review.py`, service formatter |
| `POST /api/runs/{run_id}/build` | Run ID path value | Serialized `BuildResult` | `app/api/build.py` |
| `POST /api/runs/{run_id}/remediations` | Scope plus failed check/case IDs | `{run_id, remediation}` | `app/api/remediation.py` |
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
| `report.json` | reporting stage | UI response, agent GET, build repo resolution | Ignored generated evidence |
| `remediation.json` | remediation service | Report drawer, later decision workflow | Ignored generated evidence |
| `build.json` | build orchestration | Build result UI, later evidence export | Ignored generated evidence |

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
- `StageResult`: stage identity/title, completion status, summary, checks.
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
copy of source. A file without a compilation command is not represented; parse
errors are recorded only in the return value's `skipped_files`, which is not
persisted into `symbols.json` or `report.json`.

### `BuildResult`

`repo_build.models.BuildResult` records a run ID, format and build steps, status,
return code, repository root, script name, raw stdout/stderr, selected
diagnostics, artifact manifest, placeholder intelligence summary, detected build
log path, and UTC start/completion timestamps. The build service writes
`build.json` and updates the canonical report.

### Structure tree types

`checks/structure/models.py` uses Pydantic models for a `FileNode` and legacy
`ValidationIssue`. The active required-path checker consumes `FileNode`; the
other structure validators still return legacy issue dictionaries and are not
included by the active runner.

## Module guide

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

### `app/static`

- `index.html`: page structure and CSS for setup, progress, report, and build
  views.
- `app.js`: POSTs the ZIP, renders the `RunResult` stage/check/case hierarchy,
  provides filters/search, requests provider-independent remediation suggestions,
  and renders the structured build result for the active run ID.
- The progress display is explicitly simulated (`startFakeProgress`); it is not
  server-side stage telemetry.
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

### `repo_build`

- `builder.py`: checks for a script and runs it with `cmd /c`, capturing output.
- `models.py`: typed DTO.
- `parser.py`: maps return code to status and probes two build-log locations.
- `reporter.py`: DTO-to-dict mapping.
- `runner.py`: timestamps and composes builder/parser/reporter.

`artifacts.py` restricts discovery to useful build outputs (`.elf`, `.hex`,
`.bin`, `.map`, logs, and generated reports). `intelligence.py` provides a
provider boundary and the current deterministic summary/diagnostic selection.

### `repo_remediation`

`RemediationProvider` defines a provider-independent suggestion boundary.
`PlaceholderRemediationProvider` groups failed check cases or combines one
case's reasons into a suggestion. `FutureOpenAIRemediationProvider` is reserved
for later implementation and must keep the same output contract. The provider
does not edit source files or persist developer decisions.

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
  configured size limit.
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
