# Engineering Evidence Index

- Status: frozen review plus living navigation
- Created: 2026-10-06
- Last reviewed: 2026-10-13 for living documentation navigation
- Review revision: `c603a69ddf97a9b8c9970e2e922c289209e0d591`
- Scope: all 31 commits reachable from all local refs, current tracked source,
  existing documentation, manual tests, and retained `workspace/runs` artifacts
- Does not own: detailed check semantics, source-standard wording, or generated
  run output

## What this documentation proves

This record connects each engineering claim to inspectable evidence. It is
designed for organizational review, reflection, safe historical replay,
onboarding, and later on-demand derivation of other views.

The reconstruction found a linear history from `bddb1a0` (14 May 2026) to
`c603a69` (5 October 2026), across 19 active calendar dates. The history shows
five broad phases:

1. AST and repository-structure exploration.
2. Pipeline, UI, build, ingestion, and modularization.
3. Orchestration boundaries, container hosting, and agent interfaces.
4. Stable typed result contracts and check extensibility.
5. Atomic, policy-owned naming rules with source traceability.

## Evidence vocabulary

| Label | Meaning | Appropriate claim |
|---|---|---|
| Observed | Directly demonstrated by a diff, current file, retained artifact, or command executed during this review | "The commit added `contracts/models.py`." |
| Recorded | Stated by a contemporary commit message or note but not reproduced here | "The commit message recorded the pipeline as stable." |
| Inferred | Likely explanation derived from ordering and changes; uncertainty remains | "The split probably reduced the monolith's change surface." |
| Unknown | No reliable evidence | Original local command, exact failure text, or unrecorded alternative |

Commit subjects are evidence of intent, not proof that a feature was stable.
Retained reports prove executions occurred, but none records the Git revision,
input checksum, exact command, or environment; therefore they cannot be used as
fully reproducible benchmark evidence.

## Documentation ownership

| Area | Authoritative document | Responsibility | Update trigger |
|---|---|---|---|
| Project purpose and entry points | [`../../README.md`](../../README.md) | Short current overview and navigation | User-facing boundary changes |
| Documentation navigation | [`../README.md`](../README.md) | Folder ownership and document map | Document added, moved, or superseded |
| Historical chronology | [`project-history.md`](project-history.md) | Append-only dates, commits, challenges, responses, evidence | Commit or recovered historical evidence |
| Current architecture | [`architecture.md`](architecture.md) | Present modules, interfaces, flows, data structures, and technology | Boundary or contract change |
| Decisions and durable lessons | [`decisions-and-lessons.md`](decisions-and-lessons.md) | Reconstructed decisions with confidence, alternatives, consequences | Decision accepted, superseded, or better evidence recovered |
| Verification and reproduction | [`testing-and-replay.md`](testing-and-replay.md) | Test status, run inventory, commands, isolation, provenance | Test/run/environment contract changes |
| Future gates | [`roadmap.md`](roadmap.md) | Prioritized future work, dependencies, and acceptance evidence derived from current records | Priority, dependency, evidence, or gate status changes |
| Deferred defects | [`known-issues.md`](known-issues.md) | Status, evidence, remediation selection, and closure proof for non-urgent project-wide bugs | Defect observed, triaged, mitigated, scheduled, fixed, verified, accepted, or superseded |
| Check coverage and backlog | [`../standards/review-check-catalog.md`](../standards/review-check-catalog.md) | Rule-by-rule implementation map | Check coverage changes |
| Policy/source mapping | [`../standards/naming-policy-audit.md`](../standards/naming-policy-audit.md) | Naming automation versus source rule | Naming rule implementation changes |
| LLM remediation readiness | [`../standards/llm-remediation-readiness.md`](../standards/llm-remediation-readiness.md) | Failed-check solvability, missing context, and proposed model-input contract | Report, check, policy, or remediation input changes |
| Result schema | [`../contracts/run-result.md`](../contracts/run-result.md) | `RunResult` field and persistence contract | Schema or envelope changes |
| Module coverage map | [`../README.md#module-guides`](../README.md#module-guides) | Routes material responsibilities to code entry points and local owners | Module boundary, entry point, or local owner changes |
| Local module behavior | [`../modules/README.md`](../modules/README.md) | Detailed inputs, outputs, constructs, verification, and operational posture | Material module behavior or integration changes |

## Competency evidence configuration

- Status: enabled, living, evidence-only index.
- Owner: this section; local technical facts remain with linked module,
  architecture, contract, test, decision, issue, history, and commit records.
- Scope: responsibilities demonstrated by the review engine. It does not assert
  transferable proficiency, maintain a separate gap register, or turn planned
  work into completed experience.
- Update triggers: a milestone, material responsibility or coverage change,
  verified experiment, deployment, incident, maintenance cycle, or historical
  correction. Routine edits and formatting do not trigger an update.

| Role lens | Evidenced responsibility | Coverage | Direct evidence | Evidence boundary |
|---|---|---|---|---|
| Software architecture | Separate orchestration, review, build, and reporting | implemented; prototype limits remain | [architecture](architecture.md), [D004](decisions-and-lessons.md#d004--separate-orchestration-review-and-build-ownership), [module map](../README.md#module-guides) | Deployment and release-operation depth is not demonstrated. |
| Backend / application engineering | Expose typed review results to API, UI, manager, and remediation consumers | implemented with compatibility constraints | [run-result contract](../contracts/run-result.md), [reporting guide](../modules/result-contract-and-reporting.md), [testing](testing-and-replay.md) | No production-scale traffic or authentication claim. |
| Static-analysis engineering | Build compilation context and extract a C/C++ symbol inventory | implemented with parsing and portability limits | [analysis guide](../modules/analysis-inventory.md), [D001](decisions-and-lessons.md#d001--use-the-real-compilation-database-for-c-analysis), [P001](decisions-and-lessons.md#p001--compilerpreprocessor-visibility-changes-what-can-be-reviewed) | Symbols do not prove full preprocessor, linker, or binary coverage. |
| Rules / data engineering | Encode review behavior as YAML policy and produce atomic typed outcomes | implemented for recorded structure and naming families | [checks guide](../modules/policy-driven-checks.md), [D009](decisions-and-lessons.md#d009--make-atomic-naming-rules-policy-owned-and-source-linked), [policy audit](../standards/naming-policy-audit.md) | Manual rules and stale fixtures remain explicit limits. |
| AI application engineering | Constrain model remediation with validation, evidence, and scoped prompts | prototype, partially verified | [remediation guide](remediation-generation.md), [D018](decisions-and-lessons.md#d018--generate-a-candidate-or-ask-one-narrow-context-question), [BUG-005](known-issues.md#bug-005--mechanical-naming-failures-can-return-unsupported-model-output) | No claim of production model quality or source mutation. |

## Review method

- Enumerated all refs, branch tips, parents, dates, messages, changed
  paths, and short statistics with `git log`, `git rev-list`, and `git show`.
- Inspected patches for every material commit, including removed approaches and
  renames rather than only the current tree.
- Traced the monolithic `review_engine.py` into the current `analysis`,
  `checks`, `pipeline`, `contracts`, `reporting`, `orchestrator`, and
  `repo_build` packages.
- Read the current Python, policy, frontend, container, batch, and manual-test
  files; no application source was edited.
- Inspected eight retained run directories, six reports/symbol inventories,
  and two partial runs without a report.
- Executed a no-bytecode application import and parsed all 80 current Python
  files successfully. Executed the naming manual test and retained its failure
  as evidence of contract drift.

## Repository and branch facts at review time

- Remote: `origin`, repository `Koushik-Ambadi/reviewAgent`.
- Local branch tips: `contracts-branch` at `4afee6b`, `master` at `0269843`,
  and the review branch at `c603a69`.
- `origin/master` and `origin/contracts-branch` both pointed to `4afee6b`.
- Local `master` was two commits ahead of `origin/master`; the current branch
  carried the later policy-refinement and audit commits and had no configured
  upstream.
- The tracked worktree was clean before this documentation work. `workspace/`,
  `skills/`, `run.bat`, HTML report snapshots, uploads, caches, and the virtual
  environment were ignored and therefore are not durable Git evidence.

## Important evidence boundaries

- The two large Word documents and embedded-project artifacts were inventoried,
  but this review relied on the already generated rulebook/audit for detailed
  standard interpretation.
- Conversation transcripts were not present in an inspectable, project-owned
  path. No claim is attributed to a conversation.
- There is no issue tracker export, pull-request history, CI log, release tag,
  benchmark definition, or deployment log in the repository.
- Historical commit statistics are distorted by vendored firmware, generated
  build trees, reports, and later mass deletion. They demonstrate repository
  events, not developer productivity.
- Some old commits contain paths and generated evidence that no longer exist on
  the current branch. Replay must use an isolated worktree.

## Quick evidence commands

```powershell
git log --reverse --date=iso-strict --pretty=format:'%H`t%ad`t%an`t%s' --all
git show --stat <commit>
git show <commit> -- <path>
git diff <older> <newer> -- <path>
git branch -a -vv
git status --short --ignored
```

For full replay guidance, including old revisions and retained report checks,
use [`testing-and-replay.md`](testing-and-replay.md).
