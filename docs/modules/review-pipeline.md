# Review Pipeline

## Navigation

- Project index: [docs README](../README.md)
- Architecture: [pipeline overview](../engineering/architecture.md#repo_reviewpipeline)
- Code entry points: `src/repo_review/review.py`, `pipeline/pipeline.py`,
  `pipeline/context.py`, and `pipeline/stages/`
- Upstream: orchestration supplies `workspace_path`, `repo_root`, module name,
  and selected policy name.
- Downstream: structure, analysis, naming, reporting, and persisted `report.json`.
- Contracts and evidence: [run result](../contracts/run-result.md),
  [D005](../engineering/decisions-and-lessons.md#d005--prefer-simple-function-stages-over-a-generic-stage-framework), and [testing](../engineering/testing-and-replay.md)

## Responsibility and flow

`run_review` creates a `PipelineContext`; `run_pipeline` loads the named YAML
policy and executes structure, analysis, naming, and reporting functions in
order. Every stage receives and returns the same context; `stage_results`
accumulates typed `StageResult` values before reporting serializes them.

The explicit list in `pipeline.py` is a deliberately small orchestration
pattern, not a generic plugin framework. Its order shows dependencies: analysis
creates `analysis/symbols.json`; naming consumes it; reporting persists the
accumulated results.

## Data and implementation constructs

`PipelineContext` is a Python `@dataclass` with optional `Path` workspace
fields, a policy dictionary, and lists/dictionaries created with
`default_factory` so no run shares mutable state. Stages use ordinary function
calls and return the context; error handling is owned by the calling boundary.

## Boundaries and update trigger

The pipeline assumes orchestration already made an isolated workspace. It is
synchronous and file-backed, not a job queue or concurrent worker system.
Update this guide when stage order, context ownership, policy loading,
cross-stage artifacts, or error propagation changes.
