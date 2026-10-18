# Documentation

This directory separates current engineering guidance from standards, contracts,
and historical artifacts. Start with the engineering evidence index for the
scope and confidence model used across the records.

## Engineering records

Current project knowledge lives in [`engineering/`](engineering/):

- [Evidence index](engineering/evidence-index.md) -- documentation authority,
  review scope, evidence labels, and repository facts.
- [Architecture](engineering/architecture.md) -- current modules, interfaces,
  data structures, technology, constraints, and execution flow.
- [Remediation generation](engineering/remediation-generation.md) -- model
  prompt/output boundaries, local validation, extension points, and maturity.
- [Project history](engineering/project-history.md) -- append-only daily and
  commit chronology.
- [Decisions and lessons](engineering/decisions-and-lessons.md) -- reconstructed
  rationale, alternatives, problems, and durable lessons.
- [Testing and replay](engineering/testing-and-replay.md) -- verification status,
  retained runs, hashes, constraints, and isolated replay procedure.
- [Roadmap](engineering/roadmap.md) -- future gates, dependencies, priorities,
  and acceptance evidence derived from current engineering records.
- [Known issues](engineering/known-issues.md) -- authoritative status,
  evidence, selected remediation, and resolution proof for deferred defects.

## Module guides

[`modules/`](modules/) contains detailed local records for responsibilities
that change independently of the high-level architecture. Each guide starts
with its code entry points, inputs, consumers, contracts, verification, and
related decisions. It owns local mechanics; architecture summarizes the whole.

| Responsibility | Local guide | Code entry points | Upstream | Downstream | State |
|---|---|---|---|---|---|
| Review pipeline | [review-pipeline](modules/review-pipeline.md) | `repo_review.review`, `pipeline/`, `pipeline/stages/` | orchestration workspace and policy | analysis, checks, reporting | living |
| C/C++ analysis inventory | [analysis-inventory](modules/analysis-inventory.md) | `analysis/source_index`, `analysis/symbol_inventory`, `analysis/runner.py` | repository, CMake, YAML policy | symbol JSON, checks, inventory | living |
| Policy-driven checks | [policy-driven-checks](modules/policy-driven-checks.md) | `checks/`, `policies/default.yaml` | structure tree, symbol inventory, policy | typed check results and report stages | living |
| Result contract and reporting | [result-contract-and-reporting](modules/result-contract-and-reporting.md) | `contracts/`, `reporting/` | stage results and projections | report, API/UI/manager consumers | living |

The existing [remediation generation](engineering/remediation-generation.md)
record remains the detailed owner for the model-assisted workflow.

Current constraints remain with the architecture, module, testing, contract,
decision, operational, or standards record that demonstrates them. Skill views,
gap assessments, blog ideas, portfolio stories, and similar summaries are
generated from those authoritative records when needed; they are not maintained
as competing documents.

## Standards and coverage

[`standards/`](standards/) owns the coding-standard interpretation and
automation map:

- [Coding-standard rulebook](standards/coding-standard-rulebook.md) and its
  [machine-readable YAML](standards/coding-standard-rulebook.yaml).
- [Review check catalog](standards/review-check-catalog.md).
- [Naming policy audit](standards/naming-policy-audit.md).
- [LLM remediation input readiness audit](standards/llm-remediation-readiness.md).
- [`standards/sources/`](standards/sources/) contains the original Word source
  documents. Derived rulebooks and audits must remain traceable to these sources.

## Contracts and diagrams

- [Run result contract](contracts/run-result.md) documents the serialized
  Run/Stage/Check/Case hierarchy and current persistence boundary.
- [`diagrams/review-agent.drawio`](diagrams/review-agent.drawio) is the editable
  architecture diagram source.

## Archive

[`archive/`](archive/) contains superseded notes, prototypes, and ignored report
snapshots. These files are retained as historical evidence and are not current
instructions or active application modules. See the
[archive README](archive/README.md) before reusing them.

## Update rules

- Put current project-wide engineering truth under `engineering/`.
- Put source-standard interpretation and coverage under `standards/`.
- Put serialized interface definitions under `contracts/`.
- Keep each constraint in the record that proves it; keep only future work in
  the roadmap.
- Record a non-urgent defect once in `engineering/known-issues.md`; link its
  architectural constraint, decision, test evidence, and roadmap gate instead
  of copying the complete issue narrative into those records.
- Derive profiles, assessments, and narrative ideas on demand from authoritative
  records instead of maintaining parallel summaries.
- Competency evidence tracking is enabled as a compact section of the
  [engineering evidence index](engineering/evidence-index.md). Update it only
  for a milestone, material responsibility change, verified experiment,
  deployment, incident, or coverage-state change; it is not a per-task inventory.
- Write records in one project voice: describe what happened, why, evidence,
  and outcome. Git identity records authorship; do not add separate actor or
  assistant attribution fields.
- Move superseded material to `archive/` with an explanation; do not silently
  delete evidence.
- Store generated run output under `workspace/runs/`, not in this directory.
- Update this index and all affected relative links whenever a document moves.
