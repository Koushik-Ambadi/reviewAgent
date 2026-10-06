# Run result contract

- Status: living
- Last reviewed: 2026-10-06
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
│   └── checks[]
│       └── cases[]
├── remediation[]
└── build_result
```

`stage_id`, `check_id`, and `case_id` identify their records. Display fields such as `StageResult.title`, `CheckResult.title`, and `CaseResult.name` are for presentation and must not be used as identifiers. Consumers should join related records and actions through IDs.

`policy_version` identifies the policy/schema revision used for the run. `report_version` identifies the serialized report contract version. `metadata` carries run context such as module name, policy name, and generation time. `summary` carries aggregate counts; stage/check summaries do likewise at their level.

`remediation` is a list of remediation result objects. `build_result` is the result object for the run's build. Their detailed fields can evolve without changing the run/stage/check/case hierarchy.

## Current prototype persistence

Each run is stored under `workspace/runs/<run_id>/`:

```text
report.json             Canonical serialized RunResult
remediation.json        Recorded remediation suggestions for the run
build.json              Latest serialized build result
```

`report.json` remains the canonical `RunResult`. A remediation request appends
its result to both `remediation.json` and `RunResult.remediation`. A build
request overwrites `build.json` with the latest result and updates
`RunResult.build_result`. This keeps follow-up actions attached to the same run
without making the file layout part of the API contract.

The file is a prototype store. A later manifest/database-backed store should
preserve or explicitly version the `RunResult` contract so consumers do not
depend on storage mechanism. Current reports do not record code revision, input
checksum, exact command, tool versions, or dirty-worktree state.

## Implementation status

The Python dataclasses in `src/repo_review/contracts/models.py` define these extension points. The review writer populates the run and version fields, stage/check IDs come from stable code identifiers, and case IDs are derived from the check identity, case location/name, and list index. Default values on the dataclasses keep non-pipeline construction sites working; pipeline-produced review records populate their IDs.

`RunStatus.COMPLETED` currently means that pipeline execution reached reporting;
failed compliance cases can still be present. The pipeline does not yet convert
stage exceptions into `PARTIAL` or `ERROR` results.

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

`POST /api/runs/{run_id}/remediations` accepts a failed `check_id`, optionally
with a failed `case_id`, and returns a provider-independent envelope:

```json
{
  "run_id": "20261005_...",
  "remediation": {
    "remediation_id": "...",
    "scope": "check",
    "check_id": "function_names",
    "suggestions": []
  }
}
```

The current placeholder provider generates deterministic guidance from failed
case reasons. A future provider must preserve this response shape.

`POST /api/runs/{run_id}/build` returns the latest serialized build result. It
includes `format_step`, `build_step`, `return_code`, raw output,
`important_diagnostics`, `artifact_manifest`, and `intelligence_summary`.
`process_return_code` preserves the batch wrapper's exit code; `return_code` is
the normalized result after fatal output is checked, so a permissive wrapper
cannot report success after CMake/toolchain failure text.

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
