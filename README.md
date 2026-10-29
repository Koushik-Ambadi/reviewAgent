# Review Agent

Review Agent is a policy-driven repository review service for embedded C
projects. It accepts a repository ZIP, creates an isolated run workspace,
generates a CMake compilation database, extracts C symbols with libclang,
applies repository-structure and naming checks, persists a versioned JSON
report plus canonical code graph, and renders the result in a FastAPI-hosted
web UI. A separate endpoint
can invoke the uploaded firmware repository's `cmake-build.bat`.

The current checkout documents 31 linear commits from 14 May through
5 October 2026. The engineering record was reconstructed on 6 October 2026
from Git history, current code, retained run artifacts, manual tests, and the
existing project notes. Claims that cannot be proved are explicitly marked as
recorded, inferred, or unknown.

## Start here

- [Documentation index](docs/README.md)
- [Engineering evidence index](docs/engineering/evidence-index.md)
- [Project history and daily log](docs/engineering/project-history.md)
- [Current architecture and module guide](docs/engineering/architecture.md)
- [Decisions, problems, and lessons](docs/engineering/decisions-and-lessons.md)
- [Testing, retained runs, and replay](docs/engineering/testing-and-replay.md)
- [Engineering roadmap](docs/engineering/roadmap.md)

Current constraints, demonstrated skills, learning opportunities, and material
for later narratives are derived from the architecture, history, decisions,
testing, standards, runs, and commits rather than maintained in parallel files.

Existing domain references remain authoritative for their narrower subjects:

- [Review check catalog](docs/standards/review-check-catalog.md)
- [Naming policy audit](docs/standards/naming-policy-audit.md)
- [RunResult contract](docs/contracts/run-result.md)
- [Coding-standard rulebook](docs/standards/coding-standard-rulebook.md)

## Current execution path

```text
POST /api/review (ZIP)
  -> app service
  -> orchestrator workspace and ingestion
  -> repo_review structure -> analysis -> naming -> reporting
  -> workspace/runs/<run_id>/report.json
  -> workspace/runs/<run_id>/analysis/code-intelligence.json
  -> browser or agent-oriented response
```

The landing page’s **Explore code graphs** action opens retained graph-bearing
runs. The developer **Code graphs** tab switches between file, module, and
inter-module scopes; call/include/read/write/reference overlays can be combined.
Double-click a module or file node to drill down. Control-flow and true data-flow
overlays are visible but disabled until their required analysis engines exist.
File scope starts with functions as the readable skeleton; parameters and locals
are nested in function inspection and can be expanded explicitly. Selecting a
node centers and isolates its one-hop neighborhood, while selecting a module
edge lists the concrete function or signal interactions it summarizes.
Parallel relationship kinds are separated into styled lanes and explain
themselves on hover; repeated occurrences aggregate with their count and source
locations. Function and variable inspectors show recorded declaration,
definition, incoming, and outgoing evidence. Storage totals are type-size
estimates; code size and call-chain stack remain toolchain-gated.
Choose **Expandable trace playground** to start from any file or symbol and
progressively expand or collapse incoming/outgoing branches. A canonical symbol
can appear in
multiple branches for readability; double-clicking an instance changes only its
local branch, not the underlying graph evidence. The playground labels observed
reads/parameters as inputs and writes as outputs while preserving their original
evidence, places incoming roles left and outgoing roles right, and prevents one
branch from bouncing repeatedly through the same call. Beginning/ending filters
use observed no-caller/no-callee functions; they are structural candidates, not
proven runtime entry or termination points.

The supported development launcher is `run.bat`, which activates `venv313`,
sets `PYTHONPATH=src`, and starts Uvicorn with reload. Reproduction constraints,
safer historical replay commands, and known platform mismatches are documented
in [Testing, retained runs, and replay](docs/engineering/testing-and-replay.md).

## Model-assisted remediation prototype

Open `.env.local` in the repository root and replace
`replace_with_your_openai_api_key` with the real key, then restart `run.bat`.
The file is ignored by Git and loaded automatically at application startup. Do
not put the key in `.env.local.example`, a run artifact, or a browser request.
The tracked example documents the supported fields. `OPENAI_REMEDIATION_MODEL`
optionally overrides the prototype default (`gpt-5-nano`), and
`OPENAI_REMEDIATION_TIMEOUT_SECONDS` overrides the 30-second request timeout.

The remediation drawer proposes names; it never edits uploaded source. It asks
for narrowly scoped developer context when a failed case does not reveal its
meaning. Global-variable type, size, module, unit, and other categorical segment
repairs are deliberately unavailable until those values can come from trusted
code or developer context. The inexpensive default model is for workflow
testing only and must be replaced and evaluated before production use.

Each remediation request writes its current plan to `remediation.json` and
appends a diagnostic turn to `remediation-calls.jsonl` inside that run's
`workspace/runs/<run_id>/` directory. The turn records the redacted provider
payload, raw response, retries, parsed result, validation outcome, and
parent/child linkage. API keys and authorization headers are never written.

To make one isolated call with the same `gpt-5-nano` model, a fixed failed case,
its location, its actual policy rule, and an explicit JSON output format, run:

```powershell
.\venv313\Scripts\python.exe src\repo_remediation\manual_single_case_test.py
```

The script loads the ignored `.env.local` key, prints the model's JSON, and
highlights the returned remediation. It does not create or modify run artifacts.

## Generate CFG and DFD evidence

With matching Clang/LLVM 22 and the existing Python dependencies, run from the
repository root (PowerShell):

```powershell
$env:PYTHONPATH = 'src'
venv313/Scripts/python.exe -m code_intelligence.flow --repo workspace/runs/20261022_154215_6b44447a/shunt --source workspace/runs/20261022_154215_6b44447a/shunt/src/shunt_model.c --compile-db workspace/runs/20261022_154215_6b44447a/analysis/cmake_build --output workspace/runs/my-flow-evidence --llvm-library 'C:/Program Files/LLVM/bin/LLVM-C.dll'
```

Choose a **new** output directory. It contains the canonical
`code-intelligence.json`, derived `control_flow.json` and `data_flow.json`,
compiler IR, preprocessed source, diagnostics and a hashed manifest. Existing
review artifacts are preserved. These are host-analysis CFGs and bounded DFDs;
pointer/global/interprocedural memory flow is unresolved. See the
[flow contract](docs/contracts/flow-evidence.md). Rendering is not required.

## Explore relationships and analytics

Open **Code graphs** in the developer workspace:

1. Choose one or more modules and search for functions, shared values or files.
2. Check multiple items, choose a question, then **Explore selection**. Start
   with “How are my selections connected?” or “What could this affect?”
3. Inspect a card to see source, relationships and its structure. Add further
   items to the selection. For functions with verified compiler evidence, choose
   the decision-flow or value-flow question to inspect CFG/DFD.
4. Open **Analytics and investigation priorities** for complexity, coupling,
   call depth, shared writes, exact clones and cycles. Download the current
   analysis as JSON when sharing evidence.

The interface explains static possibilities, not observed runtime causes.
Hidden/frontier counts indicate incomplete searches. Existing overview and
trace tools are retained behind their toggle. Source-matched flow bundles are
discovered read-only under `workspace/runs/*/*/manifest.json`; use the flow
command above to generate additional bundles in fresh directories.

Requirements features are excluded. Version comparisons remain on the roadmap.
State/task, test coverage, model/CAN mapping, target memory/timing and learned
predictions require evidence absent from these runs and are shown as unavailable.
See [exploration contract](docs/contracts/intelligence-exploration.md).
