# Code-intelligence graph example

Generated from `tests/fixtures/code_intelligence/sample.c` by
`scripts/build_code_intelligence_example.py`. The JSON beside this file
contains the canonical graph and every currently executable projection.

## Call graph

```mermaid
flowchart LR
  n4f48f2298349["function: control_step"]
  n3be38939021d["function: duplicate_step"]
  naf54d34d764f["function: read_state"]
  n4f48f2298349 -->|calls| naf54d34d764f
  n3be38939021d -->|calls| naf54d34d764f
```

## Variable-access graph

```mermaid
flowchart LR
  n4f48f2298349["function: control_step"]
  n3be38939021d["function: duplicate_step"]
  naf54d34d764f["function: read_state"]
  nb6c72fe45daf["global_variable: system_state"]
  n5f6c9577a92b["local_variable: next"]
  n4b3cec8bd9a0["local_variable: next"]
  nf64cb294fa38["parameter: request"]
  n5ff072e7af50["parameter: request"]
  n4f48f2298349 -->|writes| nb6c72fe45daf
  n4f48f2298349 -->|reads x3| n5f6c9577a92b
  n4f48f2298349 -->|writes x2| n5f6c9577a92b
  n4f48f2298349 -->|reads x2| nf64cb294fa38
  n3be38939021d -->|writes| nb6c72fe45daf
  n3be38939021d -->|reads x3| n4b3cec8bd9a0
  n3be38939021d -->|writes x2| n4b3cec8bd9a0
  n3be38939021d -->|reads x2| n5ff072e7af50
  naf54d34d764f -->|reads| nb6c72fe45daf
```

## Exact-token clone graph

```mermaid
flowchart LR
  n4f48f2298349["function: control_step"]
  n3be38939021d["function: duplicate_step"]
  n3be38939021d -->|clone_of| n4f48f2298349
```

## Complexity

| Function | Cyclomatic estimate | Statements | Method |
|---|---:|---:|---|
| control_step | 2 | 3 | ast_cyclomatic_v1 |
| duplicate_step | 2 | 3 | ast_cyclomatic_v1 |
| read_state | 1 | 1 | ast_cyclomatic_v1 |

## Memory estimate

- Global typed storage: 4 bytes.
- Local/parameter totals are compiler type-size sums, not stack frames.
- Linker sections, addresses, padding, heap, and runtime peaks remain
  unavailable.

## Evidence boundary

CFG, data flow, state/scheduler/interrupt semantics, requirements/tests,
timing, exact stack/linker memory, and failure propagation remain gated
by the engines or external evidence named in
`docs/contracts/graph-capabilities.md`.
