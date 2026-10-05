# Run result contract

This document defines the prototype's canonical review run structure. The serialized `RunResult` is the contract for a run; UI and API migrations will consume it in a later phase.

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

## Prototype persistence

Each run is stored under `workspace/runs/<run_id>/`:

```text
report.json             Canonical serialized RunResult
remediation.json        Remediation results for the run
build.json              Build result for the run
evidence-report.html    Downloadable, human-readable evidence
```

The JSON files are a file-backed prototype store. A later database-backed store should preserve the same `RunResult` contract so consumers do not depend on the storage mechanism.

## Implementation status

The Python dataclasses in `src/repo_review/contracts/models.py` define these extension points. The existing report writer and consumers still use the legacy report shape during this contract-freezing phase; migrating those paths is a subsequent phase. The identifier fields default to empty values to keep existing pipeline constructors working until ID assignment is wired through the pipeline. Before consumers rely on IDs, each produced record must receive a stable, non-display-derived identifier.
