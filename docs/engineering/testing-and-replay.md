# Testing, Retained Runs, and Historical Replay

- Status: living
- Owner: project maintainer
- Created: 2026-10-06
- Last reviewed: 2026-10-06
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
