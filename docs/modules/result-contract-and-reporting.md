# Result Contract and Reporting

## Navigation

- Project index: [docs README](../README.md)
- Architecture: [contracts and reporting](../engineering/architecture.md#repo_reviewreporting)
- Code entry points: `contracts/models.py`, `contracts/builders.py`,
  `contracts/status.py`, `reporting/formatter.py`, `reporting/reporter.py`, and
  `reporting/serializers.py`
- Upstream: stage results plus optional remediation/build projections.
- Downstream: run-local `report.json`, HTTP/API adapters, UI, agents, managers,
  evidence packs, and remediation continuation.
- Contract and evidence: [run-result contract](../contracts/run-result.md),
  [D006](../engineering/decisions-and-lessons.md#d006--generate-one-full-report-and-derive-consumer-views), and [testing](../engineering/testing-and-replay.md)

## Responsibility and flow

`RunResult` contains ordered stages; stages contain checks; checks contain atomic
cases. `InventorySummary` supplements analysis; remediation and build data are
optional run projections. Builders traverse lists to derive totals rather than
store independently mutable counters. Reporting formats context into a report
dictionary and writes indented UTF-8 JSON in the run workspace.

## Data and implementation constructs

The contract uses dataclasses, typed lists, string IDs, enums, optional
inventory, and `default_factory`. Summary builders use generator expressions
with `sum`. The serializer recursively converts dataclasses, dictionaries,
lists, `Path`, and `Enum` to JSON-safe values; consumers must follow the
documented schema rather than assume in-memory objects persist unchanged.

## Boundaries and update trigger

The report is the durable handoff for one run but lacks full provenance such as
source checksum, exact revision, command, and environment fingerprint. Existing
compatibility behavior is deliberate migration debt. Update when hierarchy,
status, identifiers, serialization, report path, or consumer projection changes.
