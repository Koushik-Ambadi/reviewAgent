# Run result contract

- Status: living
- Owner: project maintainer
- Last reviewed: 2026-10-06 at revision `c603a69`
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
```

Only `report.json` is currently written by the review pipeline. `remediation`
and `build_result` are fields on `RunResult`, but the current remediation and
build paths do not persist separate `remediation.json`, `build.json`, or a
generated `evidence-report.html`. Those artifacts are future extension points,
not current capabilities.

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
