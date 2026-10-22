# Known Issues and Deferred Defects

- Status: living
- Created: 2026-10-13
- Last reviewed: 2026-10-21
- Update trigger: a defect is observed, triaged, mitigated, scheduled, fixed,
  verified, accepted, or superseded
- Source of truth for: project-wide non-urgent and deferred defect state
- Does not own: current architecture, decision rationale, test strategy, or
  roadmap priority; those records link back here when triggered
- Related: [architecture](architecture.md),
  [decisions](decisions-and-lessons.md), [testing](testing-and-replay.md), and
  [roadmap](roadmap.md)

This register distinguishes observed symptoms, current explanations, selected
remediation, and verified resolution. A workaround or design decision does not
make an issue fixed. Status changes require dated evidence in the issue entry.

## Status model

- `OPEN`: observed and not resolved.
- `PLANNED`: accepted remediation has an implementation gate.
- `IN_PROGRESS`: implementation has started in the current worktree or issue.
- `MITIGATED`: impact is reduced, but the root problem remains.
- `RESOLVED`: the fix and proportional regression evidence are committed.
- `ACCEPTED`: the behavior is intentionally retained with documented risk.
- `SUPERSEDED`: another issue owns the remaining scope.

## Current register

| ID | Summary | Status | Fixed? | Current priority | Owner/gate |
|---|---|---|---|---|---|
| BUG-001 | Windows ZIP extraction fails on overlong nested Git paths | PLANNED | No | Deferred for local prototype; required before untrusted/multi-user use | G01 ingestion security |
| BUG-002 | Ignored run workspace was moved to the Windows Recycle Bin | OPEN | No | High until deletion source and backup boundary are known | G02 provenance and retention |
| BUG-003 | ZIP ingestion deletes caller-owned archives | OPEN | No | High for direct/local ZIP callers | G01 ingestion ownership |
| BUG-004 | Remediation calls lose raw request/response and turn lineage | RESOLVED | Yes | Closed by `bbacefa` | G11 remediation evidence |
| BUG-005 | Mechanical naming failures can return unsupported model output | IN_PROGRESS | No | High for remediation reliability and cost | G11 prompt/evaluation remediation |
| BUG-006 | VPN-dependent build environment is unavailable | OPEN | No | Blocks build/artifact verification | G05 operations and build portability |
| BUG-007 | Build worker can report failure after producing firmware artifacts | IN_PROGRESS | No | High for build result/artifact routing | G05 build orchestration |

## BUG-007 — Build worker can report failure after producing firmware artifacts

- Status: IN_PROGRESS
- Fixed: No
- First observed: 2026-10-22 in run `20261022_150752_17220702`
- Last updated: 2026-10-22
- Affected paths: `src/orchestrator/build_jobs.py`,
  `src/orchestrator/run_store.py`, build status API, and the browser build
  fallback renderer
- Impact: concurrent progress writes can leave `build-progress.json` in
  `failed` state without a normalized `build.json`; the UI then shows a worker
  failure, does not receive the build result or artifact manifest, and cannot
  persist/display model build remediation.
- Evidence confidence: independently reproduced by inspecting the retained run;
  the progress error is `[WinError 5] Access is denied` while replacing the
  temporary progress file, while `shunt/build.log` ends with `Done` and the
  current run contains `app.hex`, `shunt-component.elf`, and
  `shunt-component.map`.
- Work started: per-run serialization was added around progress read/modify/
  replace operations, and stale process-local `running` snapshots can now be
  restarted after an application reload. Output collection also has a bounded
  post-process drain for inherited Windows pipe handles; regression evidence is
  pending because this environment does not have the project test dependencies
  installed.

### Smallest known reproduction and boundary

- Start the background build for the retained run and poll its status while
  output callbacks are appending lines.
- The retained status is `state=failed` with the atomic-replace error on
  `build-progress.json.tmp`; no `build.json` or `build-remediation.json` was
  persisted, and `report.json` still has an empty `build_result` object.
- The compiler/linker exit code is not available because normalization did not
  complete. The artifacts and terminal `Done` marker are evidence of build
  progress/completion, not a persisted normalized pass result.

### Workaround, selected follow-up, and closure evidence

- Workaround: inspect the run's build log and artifact files directly; do not
  treat the browser's synthetic worker-failure card as the compiler result.
- Follow-up: serialize progress writes per run or use a collision-safe append/
  snapshot strategy, then ensure worker exceptions still persist a normalized
  result (or an explicit worker-failure result) before the status endpoint and
  UI render it.
- Closure requires a regression test that exercises concurrent output/status
  updates, persists `build.json`/artifact references on successful completion,
  preserves remediation on normalized failures, and verifies the browser route
  for both paths.

## BUG-006 — VPN-dependent build environment is unavailable

- Status: OPEN
- Fixed: No
- First observed: 2026-10-21 during browser verification of the remediation
  workflow and preparation to verify build/artifact integration
- Last updated: 2026-10-21
- Environment: user-reported VPN configuration required by the build
  environment; exact client, endpoint, and error are not yet recorded
- Affected paths: build execution and associated artifact linking; remediation
  remains independently usable for the current run
- Impact: build and artifact verification cannot start until the VPN is
  available, so build-dependent acceptance evidence is incomplete
- Evidence confidence: user-reported observation; not independently reproduced

### Smallest known reproduction and boundary

- Attempt to start the build from the existing run while the required VPN is
  unavailable.
- The exact command, endpoint, connection error, and whether the failure is
  network, credential, routing, or build-adapter related are unknown.
- No source or run artifact was changed as part of recording this issue.

### Workaround, selected follow-up, and closure evidence

- Workaround: continue remediation/UI verification, which does not require the
  build network path. This does not establish build correctness.
- Follow-up: once the VPN is available, capture the build request, adapter
  status, failure/output, artifact paths, and run ID before changing code.
- Closure requires a successful VPN-dependent build or a reproducible local
  substitute, linked artifact evidence, and a regression/portability check that
  distinguishes network setup failure from build implementation failure.

## BUG-005 — Mechanical naming failures can return unsupported model output

- Status: IN_PROGRESS
- Fixed: No
- First observed: 2026-10-16 in run `20261016_153027_9ab948dc`
- Last updated: 2026-10-17T01:22:10+05:30
- Affected paths: `src/repo_remediation/providers.py`,
  `src/repo_remediation/generation/`, function-name remediation
- Impact: an atomic, mechanically solvable case can consume a model call and
  finish `unsupported` with no candidate and no question
- Evidence confidence: independently reproduced from retained report/remediation
  artifacts; raw model output is unavailable due BUG-004

### Observed case and cause boundary

- Case `44638082d7e35f6ea9643697d68394ff` failed only
  `ABS-POLICY-FUNCTION-WORD-CASE`: `Shunt_getcurrent_ibatt_mA` must use lowercase
  letters after `Shunt_`.
- The policy-implied candidate is `Shunt_getcurrent_ibatt_ma`; no semantic
  question is required.
- Current preflight sends every otherwise eligible case to the model. The result
  mapper emits “The model did not produce a changed candidate” only when the
  structured candidate is empty or identical to the current name.
- The persisted response used 838 input and 393 output tokens but produced no
  actionable result.

### Current decision and closure evidence

The trace proved the model understood the lowercase rule but returned the
unchanged name. The current implementation compiles only readable failed-rule
lines into the prompt, explicitly requires a changed candidate, keeps IDs and
validator metadata local, and reruns the full policy after generation. Focused
offline tests pass, but no post-change live call has verified model behavior.
Closure requires retained live evidence for the observed lowercase cases,
unchanged-candidate and policy-pass measurements, proportional call/token
evidence, and the fixing commit. A bounded corrective retry or deterministic
fallback remains a later decision based on that evidence.

## BUG-004 — Remediation calls lose raw request/response and turn lineage

- Status: RESOLVED
- Fixed: Yes
- First observed: 2026-10-16 in run `20261016_153027_9ab948dc`
- Last updated: 2026-10-16T17:28:12+05:30
- Affected paths: `src/repo_remediation/providers.py`,
  `app/services/remediation_service.py`, `remediation.json`
- Impact: a response ID and token counts exist, but the exact returned structured
  output, request snapshot, retry events, developer answers, and parent/child
  call relationship cannot be audited after the call
- Evidence confidence: independently observed in source and retained artifacts

### Recorded evidence

- The provider posts `store: false`, parses the returned response in memory, and
  persists only model metadata plus the derived suggestions/questions/
  limitations.
- A retrieval attempt for response
  `resp_0882a5ce90b4029b016ad206863ee487d188851e4e2eba293e` returned HTTP 404.
- The request was reconstructed from current code and retained inputs, but no
  persisted artifact proves the exact original bytes or raw model output.
- Continuation uses the same `remediation_id` and replaces the prior record,
  preserving only its original `generated_at`. It does not retain a turn ID,
  parent turn, prior question/output, answer event, or prior response ID.
- The implementation does not use an OpenAI conversation or
  `previous_response_id`; each call is stateless and rebuilt from policy, cases,
  and current developer answers.

### Selected remediation and closure evidence

Keep one stable remediation-plan root and append immutable call turns. Each turn
needs `turn_id`, `parent_turn_id`, request timestamp/hash/sanitized payload,
developer answers, transport attempts, raw provider response, parsed output,
validation decisions, latency, token/model metadata, and errors. Secrets and
authorization headers must never be logged. Keep `store: false`; application-
owned evidence, not provider retention, is authoritative. Derive the plan's
current state from its turns rather than overwriting history. Closure requires
contract, persistence, API/UI/evidence, retry/error, redaction, and multi-turn
regression tests plus the fixing commit.

### Implementation state

Commit `bbacefa` implements the selected append-only evidence and linked-turn
contract. Twelve focused remediation tests pass in `venv313`, including exact
request/raw response and parsed-output capture, retry evidence, secret
redaction, developer-answer lineage, missing-key failure traces, and the
unchanged-candidate path. This resolves the audit/lineage defect. It does not
resolve BUG-005 naming quality or BUG-002 run-directory retention.

## BUG-003 — ZIP ingestion deletes caller-owned archives

- Status: OPEN
- Fixed: No
- First observed: 2026-10-16 during BUG-002 cause investigation
- Last updated: 2026-10-16T16:42:30+05:30
- Environment: all platforms using the orchestration ingestion API
- Affected path: `src/orchestrator/ingestion/zip_ingestion.py`
- Affected callers: direct `prepare_review_run(..., source_type="zip")` and any
  future caller that passes a user-owned archive
- Impact: a successfully extracted input ZIP is unconditionally unlinked even
  when the ingestion layer does not own that file
- Severity: high data-loss defect for direct/local ZIP ingestion; currently
  masked in the HTTP upload flow because that flow first creates a private
  temporary copy
- Current priority: unresolved; establish ownership and regression coverage
- Related gate: G01 ingestion security and ownership

### Observed code evidence

- `ingest_zip_source` converts its argument to `Path`, extracts it, detects the
  repository root, then calls `zip_path.unlink()` inside an ignored `OSError`
  handler. Its signature has no ownership/delete flag.
- `review_uploaded_zip` writes the browser upload into an application-owned UUID
  file under `app/temp/uploads`, passes that file to ingestion, and attempts a
  second cleanup afterward. Deleting that private temporary file is appropriate,
  but ownership is not represented at the ingestion boundary.
- `ingest_local_source` does not delete the source directory. It resolves the
  path and copies it into the run workspace with `shutil.copytree`.
- The manual local smoke script uses `source_type="local"`, so it does not enter
  the destructive ZIP branch.

Evidence confidence: independently observed directly in current source. No
destructive runtime reproduction was performed because the code path and target
are unambiguous and reproducing it against user data would add risk.

### Relationship to BUG-002

This defect deletes one ZIP file; it does not recursively delete or move
`workspace/runs`. It therefore does not explain the recovered run-directory
event. BUG-002 remains open with an unknown deleting process.

### Smallest known reproduction

Create a disposable ZIP outside `app/temp/uploads`, call
`prepare_review_run(source_path=zip_path, source_type="zip")`, and observe that
the original archive no longer exists after successful extraction. This
reproduction is specified but intentionally not executed in this
documentation-only triage.

### Selected remediation and closure evidence

- Remove source deletion from `ingest_zip_source`; ingestion must treat its
  input as caller-owned.
- Make the HTTP upload service solely responsible for deleting the private
  temporary copy in a `finally` block, covering preparation and review failures.
- Add tests proving a direct caller's ZIP survives success and failure while an
  HTTP temporary upload is cleaned on success and failure.
- Link the fix commit and passing regression evidence before marking resolved.

## BUG-002 — Ignored run workspace was moved to the Windows Recycle Bin

- Status: OPEN
- Fixed: No
- First observed: 2026-10-16; exact deletion time and initiator unknown
- Last updated: 2026-10-16T15:24:32+05:30
- Environment: Windows local checkout
- Affected path: `workspace/runs/`
- Impact: retained reports and source/run evidence became unavailable until the
  user restored directories from the Windows Recycle Bin
- Severity: high data-retention risk; no evidence currently attributes the
  deletion to application code or to a particular user/tool action
- Current priority: investigate before relying on ignored runs as durable proof
- Related gate: G02 provenance and retention

### Recorded symptom and evidence

- The user reported that `workspace/runs` had been deleted and subsequently
  restored its contents from the Windows Recycle Bin.
- After restoration, the directory exists with 12 run directories; 11 contain
  `report.json`. `20261005_185929_2c0b2076` is empty.
- The run IDs observed during the earlier remediation replay, including
  `20261013_160052_bd9a5d2b`, are not in the restored set currently visible.
- `git status --ignored` reports `workspace/` as ignored, so Git history and
  checkout operations do not provide a recovery source for these artifacts.
- Targeted source search found no startup or retention routine that removes
  `workspace/runs`; the only recursive product deletion found is the run-local
  analysis build directory in `generator.py`.
- Local ingestion copies its source directory and does not delete it. ZIP
  ingestion has a separate caller-owned-file deletion defect (BUG-003), but its
  single-file `unlink` cannot explain recursive removal of the run root.
- During the remediation work, no `Remove-Item`, `rm`, `git clean`, recursive
  workspace deletion, or reset command was issued. A test used Python's system
  temporary directory and restored the monkeypatched run-store root in `finally`.

Evidence confidence: deletion and Recycle Bin recovery are user-supplied and
high confidence. The post-restore inventory is independently observed. The
deleting process, trigger, and exact pre-deletion inventory are unknown.

### Smallest known reproduction

No reproduction exists. Starting/importing the application and exercising the
focused remediation tests did not intentionally remove the run workspace.

### Workaround and recovery boundary

Restoring from the Windows Recycle Bin recovered 12 directories, but one is
empty and the earlier observed retained IDs remain absent. This is a partial
recovery, not a fix. Copy important run artifacts outside the ignored workspace
before further cleanup, checkout, IDE maintenance, or automated housekeeping.

### Unknowns and selected next action

- Identify whether an IDE, synchronization/cleanup tool, manual action, security
  product, or unobserved application process moved the directory to Recycle Bin.
- Compare the Recycle Bin/restored inventory with any external backup or known
  run manifest; the repository currently has no authoritative inventory.
- Add explicit retention/export behavior and a run manifest under G02 before
  treating ignored workspaces as durable evidence.
- Consider filesystem auditing or a narrow watcher during the next reproduction
  attempt so the deleting process and timestamp are captured.

### Closure evidence required

- Deleting process and trigger identified or a reproducible product path found.
- Retention/export policy implemented and tested, or the external backup owner
  documented and verified.
- Missing/empty runs reconciled against an authoritative inventory.
- Fix/mitigation commit and proportional recovery/regression evidence linked
  before changing this issue to `RESOLVED` or `MITIGATED`.

## BUG-001 — Windows ZIP extraction fails on overlong nested Git paths

- Status: PLANNED
- Fixed: No
- First observed: 2026-10-13; exact occurrence time not recorded
- Last updated: 2026-10-13T16:23:45+05:30
- Environment: Windows, Python 3.13, FastAPI, Uvicorn
- Affected path: `src/orchestrator/ingestion/zip_ingestion.py`
- Affected endpoint: `POST /api/review`
- Impact: the review request returns HTTP 500 before analysis when extraction
  creates a destination path beyond the Windows-supported path boundary
- Severity: medium availability defect in the trusted local workflow; high-risk
  ingestion boundary before untrusted or multi-user exposure
- Current priority: non-urgent for the trusted local prototype; blocking before
  uploaded archives are accepted from untrusted or multi-user sources
- Related gate: [G01 — Secure the ingestion and execution boundary](roadmap.md#g01--secure-the-ingestion-and-execution-boundary)
- Related decision: [D017 — Preflight and selectively extract review archives](decisions-and-lessons.md#d017--preflight-and-selectively-extract-review-archives)

### Recorded symptom and evidence

- A `shunt.zip` upload reached `ZipFile.extractall(workspace_path)` and raised
  `FileNotFoundError: [WinError 206] The filename or extension is too long`.
- The reported failing member was below
  `.git/refs/codex/turn-diffs/checkpoints/` and combined deep directories with
  long hash-based names.
- Removing `.git` from the initially failing archive allowed extraction to
  complete. This is a successful manual workaround, not a product fix.
- The following archives were reported as test inputs:
  - `D:\BMS_related_testing_data\shunt.zip`
  - `D:\BMS_related_testing_data\bmsAlgo\shunt.zip`
- Some `.c` files below `src/` differed because naming issues were corrected.
  Those source edits are not a credible direct cause of WinError 206, but the
  two original ZIPs have not been compared and that conclusion is not verified.

Evidence confidence: the exception, failing area, tested paths, and workaround
are recorded from the investigation report supplied on 2026-10-13. They were
not independently reproduced during this documentation-only increment.

### Best current explanation

The most likely immediate cause is the expanded destination path length created
by deeply nested Git metadata. The current implementation calls `extractall`
without archive-member filtering, target-path preflight, or a typed ingestion
error. Windows then rejects a member path and the unhandled exception becomes
HTTP 500.

This explanation is strong but remains `recorded/inferred`, not reproduced.
Separate risks already visible in the same extraction boundary include path
traversal, absolute/drive-qualified members, links, excessive entry counts,
expanded-size or compression-ratio abuse, and partial workspaces after failure.

### Selected remediation design

Implement D017 within G01:

1. Inspect every `ZipInfo` before writing any member.
2. Normalize archive paths and reject absolute, drive-qualified, UNC, NUL,
   traversal, and link-like entries.
3. Exclude repository metadata that review does not consume, beginning with a
   complete top-level `.git/` subtree, and record exclusion counts/reasons.
4. Enforce configured limits for entry count, per-file and total expanded size,
   compression ratio, nesting depth, and predicted resolved target-path length.
5. Replace `extractall` with controlled per-member extraction into the run
   workspace, and remove partial extracted content if validation or writing
   fails.
6. Return an actionable typed ingestion error and map invalid/unsupported ZIPs
   to a 4xx response instead of HTTP 500. Do not expose sensitive absolute host
   paths in the client message.
7. Persist an ingestion summary in the future run manifest: included, excluded,
   and rejected entries plus reason codes and configured limits.

The service must not rely on enabling Windows long-path support as its only fix.
That setting is environment-dependent and does not address unsafe or unbounded
archive contents. Asking users to remove `.git` remains a temporary workaround.

### Verification required before `RESOLVED`

- A compact Windows-focused archive fixture reproduces an overlong `.git` member
  without depending on the private source ZIPs.
- The same source tree with and without `.git` produces an equivalent reviewable
  repository after governed exclusions.
- Tests cover traversal, absolute/drive paths, link entries, entry/size/ratio/
  depth limits, long resolved paths, multiple top-level roots, cleanup after
  failure, and 4xx error mapping.
- The two reported ZIPs are compared by member manifest or hash when they are
  available; source changes and archive-structure differences are recorded
  separately.
- A Windows API smoke demonstrates that a valid archive completes review and an
  invalid archive returns the documented error without a traceback response.
- The fixing commit and test command/results are linked here.

### Resolution tracking

- [x] Failure and workaround recorded.
- [x] Remediation design accepted in D017.
- [ ] Reproduction fixture retained.
- [ ] Safe selective extractor implemented.
- [ ] API error mapping implemented.
- [ ] Security and Windows regression checks passed.
- [ ] Fix commit linked and status changed to `RESOLVED`.

### Reusable lesson

Archive extraction is an input-security and resource-governance boundary, not a
filesystem convenience call. Ignoring VCS metadata reduces noise and path depth,
but validation and bounded extraction are still required.
