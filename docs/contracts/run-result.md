# Run result contract

- Status: living
- Last reviewed: 2026-10-10
- Update trigger: serialized result, response envelope, identifier, or persistence
  contract change
- Related: [`architecture.md`](../engineering/architecture.md),
  [`testing-and-replay.md`](../engineering/testing-and-replay.md)

This document defines the prototype's canonical review run structure. The
serialized `RunResult` is the contract for a run. The review API, browser UI,
and agent-oriented response builders now consume this hierarchy; legacy
`sections` compatibility remains in the application service for older reports.

## Shape

```text
RunResult
├── run_id
├── metadata
├── policy_version
├── report_version
├── status
├── summary
├── stages[]
│   ├── inventory?
│   └── checks[]
│       └── cases[]
├── remediation[]
└── build_result
```

`stage_id`, `check_id`, and `case_id` identify their records. Display fields such as `StageResult.title`, `CheckResult.title`, and `CaseResult.name` are for presentation and must not be used as identifiers. Consumers should join related records and actions through IDs.

`policy_version` identifies the policy/schema revision used for the run. `report_version` identifies the serialized report contract version. `metadata` carries run context such as module name, policy name, generation time, and the policy-owned `profile` display data (domain, language, formatter, build adapter, and artifact types). `summary` carries aggregate counts; stage/check summaries do likewise at their level.

`remediation` is a list of remediation result objects. `build_result` is the result object for the run's build. Their detailed fields can evolve without changing the run/stage/check/case hierarchy.

### Analysis inventory

Report version `2.1` added an optional stage-level count projection. Report
version `2.2` retains those aggregate `items` and adds grouped individual
artifacts so every extracted record can enter an audit lifecycle:

```json
{
  "source_artifact": "analysis/symbols.json",
  "parsed_files": 2,
  "skipped_files": 1,
  "items": [
    {
      "inventory_id": "global_variables",
      "label": "Global variables",
      "identified": 14
    }
  ],
  "groups": [
    {
      "group_id": "global_variables",
      "label": "Global variables",
      "artifacts": [
        {
          "artifact_id": "deterministic-uuid5-hex",
          "name": "g_state",
          "location": "src/state.c:14",
          "evidence": ["Type: State", "Storage: static"],
          "audit_status": "not_audited",
          "audit_reason": null
        }
      ]
    }
  ],
  "audit": {
    "status": "inventory_initialized",
    "audited": 0,
    "pending_approval": 0,
    "not_audited": 14
  }
}
```

`identified` counts extracted records by family; it does not claim unique,
source-stable symbol identity or compliance. `parsed_files` counts file records
written to the symbol inventory. `skipped_files` counts exclusions and parse or
compile failures returned by the extractor, but does not yet persist their
individual paths/reasons.

Each 2.2 artifact begins as `not_audited`. Its deterministic prototype ID is
derived from group, source location, display name, and local ordinal. `evidence`
contains only AST/source facts already extracted, such as type, declaration,
storage, enum value, or macro replacement. `audit_reason` remains `null` because
the parser cannot infer design intent.

The current contract initializes the register but does not provide a write API,
reviewer identity, approval transition, or durable audit history. Production
audit identity must survive line movement and symbol refactoring; the 2.2 ID is
for report-local selection and comparison only. Reports before 2.1 omit
`inventory`; 2.1 reports omit `groups`; both remain valid.

## Current prototype persistence

Each run is stored under `workspace/runs/<run_id>/`:

```text
report.json             Canonical serialized RunResult
remediation.json        Recorded remediation suggestions for the run
remediation-calls.jsonl Append-only remediation turn/call evidence
remediation-metrics.jsonl Normalized per-model-call token and latency evidence
build.json              Latest serialized build result
build-remediation.json  Redacted build-remediation model trace and result
evidence-pack.html      Latest self-contained HTML handoff generated on request
```

`report.json` remains the canonical `RunResult`.
The report may include additive `analysis_intelligence` (schema 1.0). It points
to `analysis/code-intelligence.json` and `analysis/flow/summary.json`, reports
per-source CFG/DFD completion counts, and summarizes current-snapshot functions,
complexity outliers, recursion, shared values, exact clones and file cycles.
`status: unavailable` means the graph is absent; static priorities are not
defect findings or runtime observations. Older reports may omit this field.

New remediation writes maintain one plan root per check. Every failed check case
has one ordered `case_results` entry with status `not_requested`,
`candidate_ready`, `input_required`, or
`unsupported`; absent candidates are JSON `null`, not invented placeholder
names. A case request updates only that child. A later check request targets
only `not_requested` children, then merges them into the same plan. The legacy
top-level `suggestions`, `questions`, and `limitations` arrays remain derived
compatibility views. Existing artifacts without `case_results` are projected at
read/update time.

A continuation supplies the existing `remediation_id`, updates that plan's
latest projection, preserves its identity and original `generated_at`, and
appends the new immutable turn to `turns`. `latest_turn_id` identifies the
current leaf; each continuation turn points to the preceding leaf through
`parent_turn_id`. Request scope belongs to each turn; the persisted plan root is
check-scoped.
A build request overwrites `build.json` with the latest result and updates
`RunResult.build_result`. This keeps follow-up actions attached to the same run
without making the file layout part of the API contract.

Every remediation turn is also appended as one JSON object per line to
`remediation-calls.jsonl`. Each record carries the run/remediation IDs and the
complete turn: remediation request context, developer answers, preflight
decision, exact provider payload with sensitive fields redacted, transport
attempt status/latency/error response, raw provider response, parsed structured
output, validation outcome, and final suggestions/questions/limitations.
Preflight-only turns have `provider_call: null`. Transport or provider failures
are logged before the API error is returned. Authorization headers and API keys
are never serialized. The log is application-owned evidence; provider-side
retention remains disabled with `store: false`.

Successful model turns also append one normalized record to
`remediation-metrics.jsonl`: run/remediation/turn/check/case identities, model
and prompt profile IDs, response ID, input/output/reasoning/cached/total tokens,
attempt count, measured transport latency, and outcome status. This metrics log
supports later model and prompt comparisons; it is not itself an evaluation or
quality score.

`GET /api/runs/{run_id}/evidence-pack` reads the canonical `report.json`, renders
all review findings and atomic reasons plus current remediation/build extensions,
and returns the persisted `evidence-pack.html` as a download. Generation is
repeatable and timestamped; it does not mutate `RunResult`.

The file is a prototype store. A later manifest/database-backed store should
preserve or explicitly version the `RunResult` contract so consumers do not
depend on storage mechanism. Current reports do not record code revision, input
checksum, exact command, tool versions, or dirty-worktree state.

## Implementation status

The Python dataclasses in `src/repo_review/contracts/models.py` define these extension points. The review writer populates the run and version fields, stage/check IDs come from stable code identifiers, and case IDs are derived from the check identity, case location/name, and list index. Default values on the dataclasses keep non-pipeline construction sites working; pipeline-produced review records populate their IDs.

`RunStatus.COMPLETED` currently means that pipeline execution reached reporting;
failed compliance cases can still be present. The pipeline does not yet convert
stage exceptions into `PARTIAL` or `ERROR` results.

## Derived manager response envelopes

The manager endpoints are read-only projections over persisted `RunResult`
records. They are not additional fields in `RunResult`, do not write a second
report, and do not rerun or recalculate checks:

- `GET /api/manager/portfolio` selects the newest valid report for each unique
  module and aggregates its persisted summary/build/artifact/remediation data.
- `GET /api/manager/modules/{module_name}` returns that module's reports newest
  first plus the default latest-versus-previous comparison IDs.
- `GET /api/manager/modules/{module_name}/compare` accepts `base_run_id` and
  `target_run_id`; deltas are target minus base and both IDs must belong to the
  selected module.

Legacy reports that omit `run_id` use their run-directory name as the derived
identifier. Failed cases match by persisted `case_id`; legacy cases use a
fallback composed only from report-visible stage, check, location, name, and
case index. This fallback is suitable for prototype comparison, not permanent
source-symbol identity.

`workflow_preview`, `ownership_preview`, and placeholder `insights` are
explicitly non-authoritative and carry `persisted: false` or
`status: "preview"`. Their values do not represent real approvals, owners,
tickets, pull requests, CI state, or model output. The insight envelope reserves
stable presentation fields—identity, source, kind, scope, summary, evidence,
actions, and status—so deterministic remediation or a governed model provider
can replace placeholder content later without changing the manager layout.

## Review response envelope

`POST /api/review` returns the run identifier beside the canonical report:

```json
{
  "run_id": "20261005_...",
  "report": { "run_id": "20261005_...", "stages": [] }
}
```

The persisted `report.json` contains the `RunResult` itself. The API envelope gives clients a direct run key for follow-up actions while keeping report data under `report`.

## Follow-up response envelopes

`POST /api/runs/{run_id}/remediations` accepts `scope`, a failed `check_id`, and
an optional failed `case_id`. Optional `developer_context` is keyed by case ID
and can be supplied before the first call. A follow-up also sends the returned
`remediation_id` plus a `context_answers` object keyed by question ID. The
response remains a provider-independent envelope:

```json
{
  "run_id": "20261005_...",
  "remediation": {
    "remediation_id": "...",
    "scope": "check",
    "check_id": "function_names",
    "status": "candidate_ready",
    "case_results": [],
    "applicable_rules": [],
    "affected_cases": [],
    "suggestions": [],
    "questions": [],
    "limitations": [],
    "model": null
  }
}
```

`status` is `not_started`, `candidate_ready`, `input_required`, `partial`, or
`unsupported`.
Rules are represented once per check in `applicable_rules`; cases retain their
original atomic reasons in `affected_cases`. Suggestions carry current and
candidate names, confidence, policy-validation status, a concise note, and
verification guidance. Questions carry a stable ID, field, case, and prompt.
Limitations explain why no candidate is available. `model` records provider
response identity and token counts only when a model was called.

The default provider runs deterministic preflight first. It makes no model call
for known context-only or unsupported cases, then sends all eligible cases for
one check in one structured-output request. The service currently resolves only
the active default policy and rejects reports whose policy name/version differs;
reports do not yet embed an immutable policy snapshot. Provider output is a
proposal and never authorizes or performs source edits.

`POST /api/runs/{run_id}/build` returns the latest serialized build result. It
includes `format_step`, `build_step`, `return_code`, raw output,
`important_diagnostics`, `artifact_manifest`, and `intelligence_summary`.
`process_return_code` preserves the batch wrapper's exit code; `return_code` is
the normalized result after fatal output is checked, so a permissive wrapper
cannot report success after CMake/toolchain failure text.

`intelligence_summary` includes a deterministic `issue_code`, `primary_issue`,
`evidence`, and ordered `next_actions` when a known failure pattern is matched.
For failed builds, an optional `remediation` object contains the validated
model summary, root cause, actions, confidence, and verification text. The
complete model request/response trace is stored separately in the redacted
`build-remediation.json`; it is not repeated in the product report. Missing
credentials or invalid model output preserve the deterministic summary and
record an explicit unsupported remediation state.

`artifact_manifest` contains files produced by the current build using paths
relative to the module root. A failed build may also include
`artifact_references`: paths observed in a retained run with a representative
ELF/HEX/MAP output set. Each reference carries `source_run_id` and
`reference_only: true`; it must never be presented as a current-run artifact.

The report UI starts a background build with `background=true` and polls
`GET /api/runs/{run_id}/build/status` for persisted queued/running/completed
state and recent raw output. Calling `POST /build` without `background=true`
continues to return the final result synchronously.

Formatting is skipped unless requested and the uploaded repository provides a
repository-local `review-build.json` declaration such as:

```json
{ "format": { "script": "tools/format.bat" } }
```

The declared script must remain inside the uploaded repository and use `.bat`
or `.cmd`. Formatter output is captured in the same build result.
