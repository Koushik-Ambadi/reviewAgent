# Documentation

This directory separates current engineering guidance from standards, contracts,
and historical artifacts. Start with the engineering evidence index for the
scope and confidence model used across the records.

## Engineering records

Current project knowledge lives in [`engineering/`](engineering/):

- [Evidence index](engineering/evidence-index.md) — documentation ownership,
  review scope, evidence labels, and repository facts.
- [Architecture](engineering/architecture.md) — current modules, interfaces,
  data structures, technology, and execution flow.
- [Project history](engineering/project-history.md) — append-only daily and
  commit chronology.
- [Decisions and lessons](engineering/decisions-and-lessons.md) — reconstructed
  rationale, alternatives, problems, and durable lessons.
- [Testing and replay](engineering/testing-and-replay.md) — verification status,
  retained runs, hashes, and isolated replay procedure.
- [Roadmap and gaps](engineering/roadmap-and-gaps.md) — current limitations and
  future gates.
- [Developer skills evidence](engineering/developer-skills-evidence.md) —
  evidence-backed strengths, growth, and learning goals.
- [Content sourcebook](engineering/content-sourcebook.md) — provenance-first
  story candidates for later blogs or portfolio work.

## Standards and coverage

[`standards/`](standards/) owns the coding-standard interpretation and
automation map:

- [Coding-standard rulebook](standards/coding-standard-rulebook.md) and its
  [machine-readable YAML](standards/coding-standard-rulebook.yaml).
- [Review check catalog](standards/review-check-catalog.md).
- [Naming policy audit](standards/naming-policy-audit.md).
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
- Move superseded material to `archive/` with an explanation; do not silently
  delete evidence.
- Store generated run output under `workspace/runs/`, not in this directory.
- Update this index and all affected relative links whenever a document moves.
