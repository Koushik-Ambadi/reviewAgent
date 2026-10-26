# D025 -- Retain Duplicate Historical Commits Through Archive Tags

- Date: 2026-10-26
- Status: accepted
- Scope: unreferenced commits `8040358f31481bdffff86ac6ef394307de11ecfb` and
  `971031425e8316e28cad07f7dda5d17efaf54d96`.
- Trigger: the objects would eventually become eligible for pruning, but need
  durable audit retention without replaying duplicate code.
- Evidence: [frozen review](../reviews/2026-10-26-unreachable-commits.md),
  `git show`, parent/tree comparison, and the archive refs below.

## Decision

Keep the historical objects by annotated tags and do not cherry-pick, merge,
reset to, or otherwise reintroduce their patches:

- `archive/2026-08-contract-prototype-reissue` -> `8040358`;
- `archive/2026-10-workspace-navigation-reissue` -> `9710314`.

Reachable commits `46e6e21` and `af5c71e` already retain the material
implementation with small follow-up refinements. Reapplying the earlier patches
would duplicate history and could remove those refinements.

## Options considered

1. Cherry-pick or merge: rejected because comparison shows duplicate delivery,
   not a missing feature.
2. Leave unreachable: rejected because reflog retention and garbage collection
   are not a durable evidence policy.
3. Delete/prune: rejected because this review establishes historical value.
4. Archive tags: selected; durable, inspectable, and no active product branch.

## Consequences

Archive tags are historical evidence only, not release bases. Future branch
cleanup follows the approved shared one-outcome guidance without rewriting old
history merely for naming or scope hygiene.

- Reconsideration trigger: a later audit finds an omitted functional change or
  retention requires another immutable archive medium.
- Validation: each tag resolves to its intended commit; the frozen review
  records comparisons; neither patch enters current code.
