# Historical Commit Review -- 2026-10-26

- Status: frozen
- Scope: the two commit objects reported by `git fsck --no-reflogs --unreachable`.
- Method: inspect metadata, parent identity, changed paths, and tree differences
  against reachable commits with matching subjects.
- Exclusions: unreachable blobs and trees are not catalogued separately; they
  remain available through the retained archive-tag trees.
- Outcome: retain both commits as archive tags; do not apply their patches.

## Evidence and disposition

| Unreachable commit | Observed comparison | Disposition |
|---|---|---|
| `8040358` (2026-08-07 14:28:39 +05:30) | Parent `095ae1a`; subject matches reachable `46e6e21`, which has the same parent and was recorded later that day. Trees differ only in two symbol-inventory files; the reachable version includes later path-normalization/import refinements. | Retain as `archive/2026-08-contract-prototype-reissue`; do not cherry-pick. |
| `9710314` (2026-10-08 19:39:28 +05:30) | Parent `6ffcc57`; subject and timestamp match reachable `af5c71e`. `app/static/app.js` is identical; the reachable tree removes a preliminary 29-line `AGENTS.md` and makes a one-line responsive CSS refinement. | Retain as `archive/2026-10-workspace-navigation-reissue`; do not cherry-pick. |

## Interpretation boundary

Matching metadata and near-identical trees demonstrate repeated delivery, not
why the first commits lost their references. The cause is **unknown**: no reset,
rebase, or branch-deletion claim is made without contemporary evidence.

## Options evaluated

- Reapply: duplicates reachable work and could overwrite follow-up refinements.
- Leave unreachable: does not survive eventual reflog expiry and garbage collection.
- Prune: removes inspectable evidence without a compensating archive.
- Archive tags: selected; named durable refs keep normal branches clean and
  allow isolated-worktree replay.

## Replay

```powershell
git show archive/2026-08-contract-prototype-reissue
git show archive/2026-10-workspace-navigation-reissue
```

Use a disposable worktree for source replay. Do not merge or cherry-pick into
`master` without comparing against the then-current implementation.

## Related owners

- Decision: [D025](../decisions/D025-retain-duplicate-history.md)
- Chronology: [project history](../engineering/project-history.md)
- Repository evidence: [engineering evidence index](../engineering/evidence-index.md)
