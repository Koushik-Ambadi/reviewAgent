# Known Issues and Deferred Defects

- Status: living
- Created: 2026-10-13
- Last reviewed: 2026-10-13
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
