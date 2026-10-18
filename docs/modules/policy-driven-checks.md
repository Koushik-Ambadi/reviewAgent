# Policy-Driven Checks

## Navigation

- Project index: [docs README](../README.md)
- Architecture: [structure and naming checks](../engineering/architecture.md#repo_reviewchecksstructure)
- Code entry points: `checks/structure/runner.py`, `checks/naming/runner.py`,
  check-family modules, and `policies/default.yaml`
- Upstream: repository tree or `analysis/symbols.json`, module name, and policy.
- Downstream: typed check/case results, report stages, UI, agent, and remediation consumers.
- Standards: [check catalog](../standards/review-check-catalog.md), [naming audit](../standards/naming-policy-audit.md), and [D009](../engineering/decisions-and-lessons.md#d009--make-atomic-naming-rules-policy-owned-and-source-linked)

## Responsibility and flow

Structure checks build a repository tree and currently return the required-path
result. Naming checks read analysis JSON once and invoke eight families:
functions, macros, types, enum constants, parameters, locals, array sizes, and
globals. Each family receives only its policy subsection and returns typed
outcomes with reasons.

YAML owns rule IDs, validator configuration, limits, exclusions, source links,
and user-facing reasons. Python owns validator application. Manual rules remain
manual; they are not presented as automated enforcement.

## Data and implementation constructs

Runners deserialize JSON into symbol dictionaries and return a fixed ordered
list of results. Individual check modules use policy dictionaries and reason
lists to preserve atomic failures. Shared result dataclasses and builders derive
pass/fail/skip totals from case statuses instead of maintaining copied counters.

## Boundaries and update trigger

Only the wired structure rule is current execution evidence; imported validators
are not proof of coverage. Naming automation is bounded by symbol extraction and
policy completeness. Update when check family, schema, rule semantics,
exclusion, source mapping, or automation/manual boundary changes.
