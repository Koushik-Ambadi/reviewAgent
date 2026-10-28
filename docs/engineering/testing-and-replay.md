# Testing, Retained Runs, and Historical Replay

- Status: living
- Created: 2026-10-06
- Last reviewed: 2026-10-26
- Update trigger: test command, environment, artifact schema, retention, or replay
  contract changes
- Source of truth for: current verification status and reproducible inspection
- Does not own: detailed check semantics or historical narrative

## Verification status at this review

| Check | Command/approach | Result on 2026-10-06 | What it proves |
|---|---|---|---|
| Application import | `PYTHONPATH=src`, Python 3.13 venv, bytecode disabled, `import app.main` | Passed; title `Review Agent` | Current imports and FastAPI composition load in the local environment |
| Python syntax | Parsed every `.py` under `app` and `src` with `ast.parse` | Passed; 80 files | Current Python source is syntactically parseable |
| Naming manual script without environment | Run file directly | Failed: `ModuleNotFoundError: repo_review` | Test command needs `PYTHONPATH=src` or installation |
| Naming manual script with `PYTHONPATH=src` | `python -B src/repo_review/tests/manual/test_new_naming_checks.py` | Failed: `KeyError: 'rules'` in `type_names.py` | Inline test policies predate atomic rule schema and have drifted |
| Retained JSON parse | Parsed each retained `report.json` and `symbols.json` | Passed for six complete runs | Files are valid JSON and their top-level contracts can be inspected |

No end-to-end review was launched during this documentation pass because it
would copy a large external source, regenerate ignored workspaces, and depend on
machine-specific CMake/libclang inputs. No source code was modified.

### Manager projection verification — 2026-10-09

| Check | Result | What it proves |
|---|---|---|
| `python -m pytest -q tests/test_manager_service.py` | Not executed: active Python has no `pytest` module | Environment limitation is distinct from product behavior |
| Direct invocation of the same assertion function with a temporary directory | Passed | Latest-per-module selection, history ordering, preview boundary, selected-run deltas, and new/resolved failure sets |
| Read-only projection over retained reports | Passed: 2 modules, 17 valid reports; default `shunt` comparison selected the two newest runs | The service handles both legacy reports without top-level run IDs and current `RunResult` records |
| `node --check app/static/app.js` and `node --check app/static/manager.js` | Passed | Existing developer behavior and the isolated manager controller are syntactically valid |
| Local app route and HTTP smoke | Passed: application loaded all manager routes; `/` returned 200 with manager markup/script; portfolio returned 2 modules, 540 latest failures, and `persisted: false` | Static manager delivery and live read-only endpoint composition work together |
| Focused browser visual check | Not executed: computer-use helper exited twice during sandbox setup before opening a tab | Visual layout remains a manual acceptance item; no browser result is claimed |

The review/build pipeline was intentionally not rerun: the manager service only
reads persisted JSON and the focused real-data projection exercised that
integration boundary without regenerating machine-dependent artifacts.

### Analysis inventory verification — 2026-10-10

| Check | Result | What it proves |
|---|---|---|
| Direct invocation of `tests/test_analysis_inventory.py` assertions | Passed | The pure projection counts every supported symbol family, preserves parsed/skipped coverage, keeps audit values unavailable, and serializes report version 2.1 |
| Direct invocation of the updated evidence-pack assertion | Passed | Analysis inventory and its audit boundary appear in the self-contained handoff document |
| `node --check app/static/app.js` | Passed | The developer report controller remains syntactically valid after the inventory rendering path was added |

The follow-up 2.2 fixture also verifies grouped individual artifacts,
structure-field expansion, deterministic report-local IDs, initial
`not_audited` state, AST evidence, and the evidence-pack audit table. It uses the
same focused direct invocation because the active Python environment does not
provide pytest.

The full review/build pipeline was intentionally not rerun. The change is a pure
projection over the extractor result already returned in memory; regenerating
machine-specific CMake/libclang artifacts would be disproportionate. The
responsive card layout remains a focused visual check at normal browser zoom.

### Code-intelligence AST verification — 2026-10-27

The derived-view fixture in `tests/test_code_intelligence_derived_views.py`
verifies explicit-root reachability, unreachable classification,
recursive-SCC call depth, file-as-module dependency aggregation, reverse
direct/transitive impact, and invalid input rejection. It is a pure graph test
and does not require libclang.

The expanded AST fixture verifies scoped identities, type sizes, conservative
read/write classification, function metrics, and exact body-token fingerprints.
`tests/test_code_intelligence_analysis_views.py` verifies variable-access,
exact-clone, complexity, and explicitly non-authoritative memory estimates. A
real detailed-processing parse of `tests/fixtures/code_intelligence/sample.c`
with the installed libclang produced 13 nodes, 40 edges, 17 access occurrences,
one exact-clone edge, three complexity nodes, and a four-byte global-storage
estimate.
`PYTHONPATH=src python scripts/build_code_intelligence_example.py` regenerates
the checked-in JSON and Mermaid-backed Markdown example deterministically.
`tests/test_shared_analysis_stage.py` builds a temporary compilation database
and verifies that the review inventory and provenance-bearing schema 1.1 graph
snapshot are produced together from the common parse boundary.

### Graph workspace backend verification — 2026-10-28

`tests/test_graph_service.py` verifies file/module overlay projection and
cross-module signal direction over two synthetic run artifacts. The retained
`20261022_154215_6b44447a` shunt source was reparsed without replacing its legacy
`symbols.json`: two policy-owned translation units produced 309 nodes and 1,242
edges in 7.542 seconds. The module projection contains nine repository-owned
file nodes and 32 selected relationships; `src/shunt.c` contains 83 displayed
nodes and 236 selected/hierarchy relationships. Only shunt currently has a
graph artifact, so the inter-module result honestly contains one module and no
cross-module relationships.

`tests/test_graph_workspace_static.py` verifies the graph page, three scope
selectors, layer host, canvas, accessible relationship list, stylesheet/script
delivery, catalog loading, and double-click drill-down hooks. `node --check`
passes for `graph.js`, `app.js`, and `manager.js`. A local Uvicorn smoke returned
200 for the catalog, shunt module/file projections, inter-module projection,
HTML shell, and graph script. Browser visual verification was not executed
because local browser use is disabled in Work settings.

The function-centric readability increment adds focused assertions for bounded
module/inter-module aggregate interaction evidence, owned-detail controls, node
focus, edge
inspection, and hierarchy suppression from the default canvas. `node --check`
and direct invocation of the three focused graph tests passed. The refreshed
Uvicorn projection returned 7 module nodes/20 selected aggregate relationships
and 83 file nodes/236 selected-plus-hierarchy relationships. Browser binding was
again blocked by Work settings, so the user-visible localhost tab remains the
visual acceptance surface.

| Check | Result | What it proves |
|---|---|---|
| `venv313` direct invocation of the three functions in `tests/test_code_intelligence_ast.py` with temporary roots | Passed | USR-first and fallback identities are deterministic; file/function/global/macro nodes and contains/declares/defines/includes/calls edges are emitted; unresolved calls remain explicit; every edge endpoint exists; external declarations are excluded |
| `python -m pytest tests/test_code_intelligence_ast.py -q` | Not executed: `venv313` has no `pytest` module | Environment limitation is distinct from product behavior |
| `python -m black --check ...` | Not executed: `venv313` has no `black` module | Formatting command remains unavailable; focused diff and syntax checks are required before commit |
| `python -m ruff check ...` | Not executed: `venv313` has no `ruff` module | Lint tooling is unavailable in the supported environment; no lint pass is claimed |

The fixture intentionally uses fake cursor objects so the isolated contract can
be tested without machine-specific libclang. A real compilation-database
fixture is required when the runner and snapshot integration are added.

### Code-intelligence graph verification — 2026-10-27

| Check | Result | What it proves |
|---|---|---|
| `venv313` direct invocation of the five functions in `tests/test_code_intelligence_graph.py` | Passed | Definition facts win deterministic merge; call/include projections use the canonical graph; identity conflicts and dangling edges fail closed; snapshot bytes are repeatable and atomically replace the target; required replay provenance cannot be omitted |
| Python AST parse and 88-column scan over `src/code_intelligence` and both focused test modules | Passed | All new Python parses and the repository's configured line-length boundary is met |

Pytest, Black, and Ruff remain unavailable in `venv313`; the focused direct
assertions and deterministic byte comparison are the executed evidence.

## Current test inventory

### `src/repo_review/tests/manual/smoke_test.py`

- Intended level: end-to-end local ingestion and review.
- Dependency: hard-coded `D:/BMS_related_testing_data/bmsAlgo/soc`.
- Side effects: copies the repository into a new run, deletes/recreates the
  analysis CMake build directory, and writes `symbols.json`/`report.json`.
- Current limitation: not portable, has no assertions, and succeeds/fails only
  through exceptions.

### `src/repo_review/tests/manual/test_new_naming_checks.py`

- Intended level: focused check execution against retained symbols.
- Fixture: hard-coded run `20260727_131845_e479c8c0` and module `soc`.
- Current limitation: duplicates an older flat policy shape; current checkers
  expect `policy["rules"]`. It fails before producing results.

### `src/tests/manual/test_pipeline.py`

- Intended level: older pipeline smoke path.
- Current limitation: constructs `PipelineContext(source_path=...)`, but current
  context has no `source_path` field. It catches its own exception, so process
  exit status may not reliably indicate failure.

### `src/tests/manual/test_zip_pipeline.py`

- Intended level: older ZIP end-to-end path.
- Current limitation: imports removed `run_review_from_zip` and uses a hard-coded
  desktop ZIP. It is not runnable against the current facade.

### Missing automated layers

- Unit tests for policy validators and edge cases.
- Policy-schema validation and migration tests.
- Contract tests for serialized `RunResult`, stable IDs, and legacy adapter.
- Integration tests for CMake/libclang analysis on a compact fixture.
- API tests for uploads, report retrieval, invalid run IDs, policies, and build.
- Security tests for ZIP traversal, path traversal, upload limits, and execution.
- Browser tests for upload, filtering, result rendering, and build output.
- Linux/Windows matrix, container smoke test, and CI workflow.

## Retained run inventory

All run directories are ignored by Git. The table is a local snapshot, not a
durable repository guarantee.

| Run ID | Module | Completion | Contract | Policy | Summary | Evidence note |
|---|---|---|---|---:|---|---|
| `20260727_131845_e479c8c0` | `soc` | Complete | legacy report 1.0 | name `default`; no version | 129 pass, 103 fail, 15 exception, 247 total | Oldest retained report; 2 parsed files, 33 functions, 131 globals |
| `20260811_185957_7f1f6262` | `soc` | Complete | hierarchical, early v2 shape | version missing | 349 pass, 379 fail, 15 skip, 743 total | No stage/check IDs in artifact |
| `20260811_190348_9bc9b2f3` | `soc` | Complete | hierarchical, early v2 shape | version missing | 349 pass, 379 fail, 15 skip, 743 total | Symbol inventory byte-identical to prior run |
| `20261005_163038_ed3fe2a5` | `soe` | Partial | none | unknown | no report | Repository copy exists; no analysis/report evidence |
| `20261005_163217_06410f05` | `shunt` | Complete | `RunResult` 2.0 | 2 | 161 pass, 196 fail, 10 skip, 367 total | Baseline before policy refinements |
| `20261005_175650_96dd018a` | `shunt` | Complete | `RunResult` 2.0 | 3 | 197 pass, 168 fail, 2 skip, 367 total | Same symbol hash as v2 |
| `20261005_185929_2c0b2076` | `shunt` | Partial | none | unknown | no report | CMake directory exists; no compile DB/symbol/report retained |
| `20261005_190122_b4aae0eb` | `shunt` | Complete | `RunResult` 2.0 | 4 | 204 pass, 161 fail, 2 skip, 367 total | Same symbol hash as v2/v3 |

The report's run status is `COMPLETED` even when cases fail. It means execution
finished, not policy compliance.

## Artifact integrity snapshot

SHA-256 values were calculated on 6 October 2026. They let a future reviewer
detect local mutation of these ignored artifacts; they do not prove origin.

| Run ID | Artifact | Bytes | SHA-256 |
|---|---|---:|---|
| `20260727_131845_e479c8c0` | `report.json` | 83,249 | `39b1184c769109acaddb8e5c93d82e065b62df318723c6f8d68253a8d26d79ee` |
| same | `analysis/symbols.json` | 275,959 | `b5ab170918322a18d2413089e00289d8fb4118014a906bbc3ded26181fe1aa64` |
| `20260811_185957_7f1f6262` | `report.json` | 192,530 | `07302f9da616439c4f68cda9c402968943b8b4b316fbd9dfaa47117d5ebf0148` |
| same | `analysis/symbols.json` | 284,870 | `6bae234702a8ff84a3d73387df3fad90e0b4578afb7cad97de13e309381d1c03` |
| `20260811_190348_9bc9b2f3` | `report.json` | 192,530 | `077a210a9e5cdacf3a6137258174dbaad6870b2b94e285e94021ee84dde17b3f` |
| same | `analysis/symbols.json` | 284,870 | `6bae234702a8ff84a3d73387df3fad90e0b4578afb7cad97de13e309381d1c03` |
| `20261005_163217_06410f05` | `report.json` | 124,895 | `77ba1629840c398508a2e69ce1f746fa21f832fdb09b924a1a4071f8c714cd99` |
| same | `analysis/symbols.json` | 128,431 | `db8bade4eed3aa920dd63fe82e93d885e458d658c66c6232c6f33f19d0fd7616` |
| `20261005_175650_96dd018a` | `report.json` | 127,995 | `b06e200a27dc8a9639553a5f72b43cd66cb263eb196bb937de000370ab5f79ed` |
| same | `analysis/symbols.json` | 128,431 | `db8bade4eed3aa920dd63fe82e93d885e458d658c66c6232c6f33f19d0fd7616` |
| `20261005_190122_b4aae0eb` | `report.json` | 142,347 | `e7cd520349c2d72ed3e3a49743a88332d985629c1ba88fa02424de8da10fdc4e` |
| same | `analysis/symbols.json` | 128,431 | `db8bade4eed3aa920dd63fe82e93d885e458d658c66c6232c6f33f19d0fd7616` |

The byte-identical symbol inventories strengthen two limited observations:

- the two August runs repeated the same extracted input and produced identical
  aggregate results, although their report files differ because run metadata
  differs;
- the three October policy runs evaluate the same extracted symbol inventory,
  so their check-count changes are attributable to report/check/policy behavior
  after extraction, though a missing Git revision prevents precise code-level
  attribution.

## Current local setup

### Windows development launcher

```powershell
.\run.bat
```

The batch file activates `venv313`, sets `PYTHONPATH=src`, and runs:

```powershell
uvicorn app.main:app --reload
```

Run it from the repository root because workspace and static paths depend on the
current working directory.

### Manual equivalent

```powershell
$env:PYTHONPATH = 'src'
.\venv313\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Docker review service

```powershell
docker build -t review-agent .
docker run --rm -p 8000:8000 review-agent
```

This should be treated as a documented command, not a verified 6 October run.
The image combines Python 3.13, Clang/libclang 19, GCC/G++, CMake, and Ninja.
The build endpoint remains incompatible with Linux because it invokes `cmd`.

## Safe current verification commands

These checks avoid writing Python bytecode. They may still import modules that
create `app/temp/uploads` if missing.

```powershell
$env:PYTHONPATH = 'src'
$env:PYTHONDONTWRITEBYTECODE = '1'
.\venv313\Scripts\python.exe -B -c "import app.main; print(app.main.app.title)"
```

Before relying on the manual test files, repair them or copy their intent into a
disposable test; their current failures are documented above.

### Documentation navigation check

For a documentation-only increment, validate local Markdown targets after a
focused diff review. This checks documentation routing, not application behavior:

```powershell
python -c "from pathlib import Path; import re; root=Path('docs'); missing=[]; [missing.append((p, t)) for p in root.rglob('*.md') for t in re.findall(r'\[[^]]+\]\(([^)#]+)', p.read_text(encoding='utf-8')) if not t.startswith(('http://','https://','#','?:')) and not (p.parent / t).resolve().exists()]; print(missing); raise SystemExit(bool(missing))"
```

Run focused Python, JavaScript, API, or replay checks as well whenever runtime
behavior, contracts, policy, or generated artifacts change.

## Historical inspection without executing old code

Use this first. It has the lowest risk and reconstructs most design decisions.

```powershell
git show --stat 095ae1a
git show 095ae1a -- src/repo_review/contracts
git diff 5984863 095ae1a -- src/repo_review/reporting src/repo_review/pipeline
git show b6792eb:src/repo_review/policies/default.yaml
```

Useful replay points:

| Revision | Question |
|---|---|
| `bddb1a0` | What did the first structure/AST prototype own? |
| `5fd77db` | How were array dimensions recovered? |
| `9755213` | When did compile commands and build enter the system? |
| `d653e0a` | What did the first large modular split look like? |
| `f435aea` | Which abstractions were removed/simplified? |
| `4217116` | How did orchestrator/review/build ownership separate? |
| `6947306` | Which Linux/container fixes were applied? |
| `196e282` / `f0d40b9` | How was local MCP added and then removed? |
| `095ae1a` | How did the stable result contract begin? |
| `4afee6b` | How were new naming check families added? |
| `b6792eb` | How did rule logic move into policy? |

## Isolated historical execution

Old revisions include generated data, old dependencies, absolute paths, and
potentially large embedded assets. Never switch the active worktree or install
old requirements into the current venv. Create a detached worktree beside the
repository:

```powershell
$revision = '095ae1a'
$replayRoot = Join-Path (Split-Path (Get-Location) -Parent) "review-replay-$revision"
git worktree add --detach $replayRoot $revision
Set-Location $replayRoot
git status --short
```

Then inspect that revision's `requirements.txt`, `pyproject.toml`, test paths,
and Dockerfile before installing or executing anything. Prefer a disposable
container/virtual environment. Record:

- revision and branch;
- host/container OS and architecture;
- Python, Clang/libclang, CMake, Ninja, and compiler versions;
- exact command and environment variables;
- input path, size, and checksum;
- resulting artifact checksums and failure logs.

When finished, return to the main repository and remove the exact validated
worktree path:

```powershell
Set-Location D:\toolsHub\apps\review
git worktree list
git worktree remove $replayRoot
```

Do not use `git reset --hard`, `git clean`, or checkout old commits in the active
worktree; the documentation and any user changes must remain intact.

## Replaying policy behavior without rerunning CMake/libclang

The safest focused experiment is to use a copied retained `symbols.json` as the
fixed input and execute checkers from one chosen revision. Record the symbol
hash, policy hash/version, and code revision. This isolates policy/check behavior
from extraction changes.

For the October sequence, the fixed input hash is:

```text
db8bade4eed3aa920dd63fe82e93d885e458d658c66c6232c6f33f19d0fd7616
```

Do not overwrite the retained report. Write experimental output under a new
experiment/run directory and label it reconstructed, because the original
command and revision are not available.

## Required future test strategy

### Unit

- One hand-checkable fixture per atomic validator.
- Boundary cases for lengths, underscores, module casing, pointer depth,
  numerical literal formats, exclusions, and global-name segments.
- Pure aggregation and serialization tests.

### Contract

- Validate YAML before execution, including rule IDs/validators/required fields.
- Snapshot semantic fields of `RunResult` without overfitting formatting.
- Prove case IDs repeat under stable inputs and change under identity changes.
- Test legacy adapter only while a named consumer requires it.

### Integration

- Small licensed CMake C fixture producing a deterministic compile database.
- C and header cases, compile-command absence, target-folder filtering, parse
  failure, macros, multiline arrays, structs/enums/typedefs, pointers.
- ZIP and local ingestion with one/multiple top-level directories.

### End to end

- Upload -> workspace -> report -> UI/agent retrieval.
- Build on explicitly supported OS/build adapters.
- Container smoke test from a clean checkout.

### Security and operations

- Archive traversal and archive-bomb controls.
- Run/policy path traversal and invalid identifiers.
- Upload limits, authentication/authorization, and untrusted build isolation.
- Concurrent runs, cleanup, interruption, disk exhaustion, and partial outputs.

## Run metadata required for future proof

Every durable run should capture at least:

```yaml
run_id: stable-run-id
status: completed|failed|partial
started_at: ISO-8601
completed_at: ISO-8601
code_revision: full-git-sha
dirty_worktree: false
command: exact invocation
environment:
  python: version
  platform: value
  clang_bindings: version
  libclang: version-and-path
  cmake: version
  generator: version
inputs:
  source_identity: name-or-uri
  source_sha256: checksum
policy:
  path: path
  version: value
  sha256: checksum
outputs:
  report: path-and-sha256
  symbols: path-and-sha256
  compile_database: path-and-sha256
errors: []
```

This closes the largest gap between useful local artifacts and defensible,
repeatable organizational evidence.

## 2026-10-16 remediation workflow verification

The first candidate-or-context slice was verified without a live credential:

- Python AST parsing passed for provider, service, API, evidence renderer, and
  focused tests; `node --check app/static/app.js` passed.
- Eleven focused tests passed by direct invocation in the repository virtual
  environment. Coverage includes one-call batching, policy-once/rule-ID-only
  input, length shortening, deterministic no-call questions, developer and
  model-question continuations, global deferral, candidate policy validation,
  one transient retry, missing-key behavior, record replacement, and escaped
  evidence output.
- A file-backed replay used a temporary report and proved the question-to-answer
  continuation leaves one `candidate_ready` record in both persistence files.
- Retained run `20261013_160052_bd9a5d2b` was also used in place: its four
  one-letter parameters produced questions, three missing required paths
  produced limitations, and one malformed categorical global produced a
  limitation. All three requests made zero model calls.
- Uvicorn started successfully on a local test port. The static root, retained
  agent report, and generated evidence-pack routes returned HTTP 200; the
  evidence response contained the persisted developer-context section.

`pytest` was unavailable, so zero-argument focused tests were loaded and invoked
directly. This does not replace G03. A live Responses/browser smoke was not run
because `OPENAI_API_KEY` was absent from the app environment. When configured,
open the retained run, request a function-name remediation, answer any question,
and confirm plan count is unchanged after continuation. Never paste a credential
into a command or persist it in a run artifact.

Local credential loading was verified separately with two focused tests: an
allow-listed value loads, an existing process variable wins, the dummy
placeholder is ignored, and an unknown key fails closed. Importing `app.main`
with the checked-in dummy file succeeds and leaves `OPENAI_API_KEY` unset.
`git check-ignore -v .env.local` confirms the editable secret file is ignored.
The combined focused set contains 13 passing tests, and a fresh Uvicorn startup
with the dummy file returned HTTP 200 from the static root.

### Remediation call-trace increment

The append-only trace change is covered by focused direct tests in the repository
Python 3.13 virtual environment. The checks prove that a question/answer
continuation keeps one remediation root, appends two turns, links the second turn
to the first, and writes two JSONL records with the same remediation ID. The
model-backed turn retains its exact request payload, raw response, parsed
structured output, and developer answer. Separate assertions cover retry attempt
status/responses, missing-key failure traces, nested secret redaction, and the
observed unchanged-candidate path retaining the raw/parsed candidate beside the
derived limitation.

Verification command:

```powershell
$env:PYTHONPATH='src'
.\venv313\Scripts\python.exe -B -c "import tests.test_remediation_templates as m; tests=[(n,getattr(m,n)) for n in dir(m) if n.startswith('test_')]; [f() for n,f in tests]; print(f'{len(tests)} remediation tests passed')"
```

The system-Python attempt stopped at import because that interpreter does not
have `httpx`; no test executed in that attempt. The repository virtual
environment is the supported test runtime.

This evidence is committed with the trace implementation in `bbacefa`.

### Minimal single-case model smoke

`src/repo_remediation/manual_single_case_test.py` isolates prompt behavior from
the remediation workflow. It sends `Shunt_msgcountercheck_Init`, its source
location, only the failed lowercase rule and its actual policy definition, plus
the required three-field JSON output shape. It uses the same `gpt-5-nano` model,
loads the ignored `.env.local` credential through the supported loader, disables
provider storage, prints the raw model JSON, and highlights the returned rename.
It does not persist a run or call log.

```powershell
.\venv313\Scripts\python.exe src\repo_remediation\manual_single_case_test.py
```

Syntax/import verification does not make a network call. The live output is
user-run experimental evidence and must not be represented as a regression
pass until its actual result is retained.

On 2026-10-26 the tracked file was restored after an uncommitted deletion so
this narrow experiment remains reviewable. The local check imports the module,
exercises `_output_text` with a synthetic Responses payload, and verifies the
three required schema fields. It passed in `venv313` with `PYTHONPATH=src` and
bytecode disabled, making no provider call. An initial inline synthetic-JSON
command failed before import because PowerShell quoting malformed the fixture;
the corrected plain-text fixture passed. This is parser/import evidence only,
not model-quality or live API evidence.

### Compact model-input compiler

The model-facing refactor is verified by 14 focused remediation tests.
The payload contract assertion now proves that one function-name case contains
only readable failed `rules`, prompt-local case references, the current name,
and optional developer context. It asserts that module/check metadata,
persistent case IDs, locations, validators, full policy objects, and
applicability exclusions are absent. Existing assertions continue to cover strict output
parsing, private ID restoration through the provider flow, context questions,
full-policy candidate validation, logging, retries, and redaction.
Boundary-specific coverage also proves shared failed rules are emitted once per
batch and that missing, duplicate, or unknown prompt-local case references are
rejected before application IDs are restored.

The retained production prompt for `Shunt_msgcountercheck_Init` contains 3,103
developer/user message characters. The compiled equivalent contains 424, an
86% reduction in message characters. This is not a token-cost claim because the
structured output schema and API framing are not included in that comparison.

The first compilation command passed a literal `*.py` to Windows Python and
failed with `Errno 22`; it did not compile those files. Expanding the paths in
PowerShell and rerunning passed. A separate one-line prompt-inspection harness
had malformed quoting and stopped with `SyntaxError`; the corrected here-string
harness produced the compact payload above. A `pytest` command stopped before
collection because that package is not installed in the repository environment;
the first direct-harness retry also stopped before collection because `src` was
not on its import path. The supported virtual-environment harness with `src`
inserted passed all 14 tests.

### Hierarchical remediation and initial context

The 2026-10-17 increment extends the focused direct suite to 17 tests. New
filesystem-backed coverage proves that a case request creates a check plan with
one `candidate_ready` child and one `not_requested` child, then a later
full-check request sends only the missing case, retains one remediation ID,
produces two parent-linked turns, and persists one plan. A second test proves
optional developer context for a one-letter parameter reaches the first prompt
and avoids the context-question round trip.

Evidence-pack coverage verifies that the same per-case hierarchy renders both a
candidate and a `not_requested` case without inventing a candidate.

Existing tests now also cover global categorical context questions, normalized
model/prompt profile IDs, token evidence in `remediation-metrics.jsonl`, and the
legacy top-level compatibility views. Python compilation, application import,
and `node --check app/static/app.js` are the proportional syntax gates. No live
provider call or visual browser check is represented by these tests.

The first syntax command again passed a literal `*.py` path to Windows Python
and reported `Errno 22`; the direct suite still executed and passed. The command
was corrected to expand files with PowerShell before invoking `py_compile`.

### Build remediation and retained artifact references

The build remediation increment adds three direct tests. They validate strict
structured model output, preservation of captured diagnostic strings in the
model input, and relative artifact references sourced from a retained output
set containing ELF, HEX, and MAP files. A read-only replay against the current
workspace found three such references in retained run
`20261017_171649_abddbcc4`; no build command or network call was made.

No live model response was available because `OPENAI_API_KEY` is not configured
in the application environment. The retained Green Hills failure logs remain
the manual evidence fixture: deterministic classification identifies the
unreachable license host, while the model path is tested with a fake structured
response and remains explicitly unavailable until credentials are supplied.
