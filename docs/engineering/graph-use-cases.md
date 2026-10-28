# Graph Use Cases and Insight Boundaries

- Status: living product/engineering map
- Created: 2026-10-28
- Source of truth for: problems the graph workspace is intended to solve, the
  current evidence behind each insight, and unavailable conclusions
- Does not own: canonical graph schema, API response fields, or roadmap priority
- Related: [graph capability matrix](../contracts/graph-capabilities.md) and
  [graph workspace API](../contracts/graph-workspace-api.md)

## Implemented or initially supported

| Problem or use case | View and evidence | Insight available now | Boundary |
|---|---|---|---|
| Understand an unfamiliar file | File ownership plus declarations, definitions, calls, and variable access | Functions/types/data owned by the file and the boundary symbols they touch | Macro expansion and conditional configurations are incomplete |
| Understand internal module architecture | Module aggregation over file ownership, calls, includes, reads, and writes | File coupling, dependency direction, shared-state traffic, and high-fan relationship candidates | Files are the initial grouping policy; architectural components need explicit grouping |
| Understand multiple modules | Latest graph-bearing run per module plus stable identity matching | Cross-module calls and named signals read from or written to another module | Requires two or more graph artifacts and matching USRs/IDs |
| Trace signal producers and consumers | `writes` and `reads` overlays | Candidate writers, readers, input/output direction, and shared-global coupling | Not runtime values, rates, units, calibration, or full data flow |
| Follow direct call paths | Call graph, reachability, SCC-aware depth | Direct callers/callees, unreachable candidates from chosen roots, recursion groups, and bounded depth | Indirect calls and root/configuration discovery remain incomplete |
| Estimate change impact | Reverse calls/includes/containment | Direct and transitive code areas to inspect after a changed node | Not proof of runtime impact or sufficient test selection |
| Find complexity hotspots | Versioned AST cyclomatic approximation and statement counts | Functions that deserve review or decomposition attention | Must be compared with a CFG-backed metric before compliance use |
| Find exact duplicate bodies | Exact clang body-token fingerprint | Exact-token clone candidates for consolidation review | Near/semantic clones are not detected |
| Inspect storage estimates | Compiler type sizes for globals, locals, and parameters | Approximate typed storage and unknown-size symbols | Not linker placement, padding, exact stack frames, heap, or peak usage |
| Detect dependency hygiene issues | Include and module/file dependency views | Excessive coupling, unexpected layer direction, and external dependency exposure | Architecture rules and allowed-direction policy are not yet configured |
| Support code review explanations | Source locations, provenance, selected overlays | Evidence-backed explanation of why a symbol/file is relevant | Graph facts do not decide compliance or approve changes |

## Valuable but evidence-gated

| Problem | Required evidence before claiming the insight |
|---|---|
| Statement-level branch/path inspection | Validated per-function CFG with basic blocks and exits |
| Definition-use lineage and “where did this value come from?” | CFG plus alias/pointer and interprocedural data-flow engine |
| Automatic regression-test selection | Versioned tests, coverage, results, requirements, and measured precision/recall |
| Task/ISR interference and race analysis | Scheduler, priority, ISR, masking/locking, and shared-data configuration |
| Timing bottlenecks or WCET | Hardware/configuration-specific measurement or bounded timing evidence |
| Exact stack and memory placement | Compiler stack reports, linker map, ABI, sections, and runtime heap evidence |
| Requirement-to-code/test coverage | Versioned requirement source and explicit trace links |
| Failure propagation and safety impact | FMEA/safety model joined to validated control/data flow |

## UI interpretation rules

- Empty means no relationship was observed in the selected evidence, never that
  no relationship can exist.
- Disabled layers explain their missing engine or evidence.
- High-level nodes may be expanded into available internal overlays, but the UI
  must not label read/write access as data flow or call hierarchy as control flow.
- Counts summarize occurrences; users can drill down to named targets and source
  paths rather than treating node size or color as a verdict.
- Parameters are input bindings owned by a function; locals are storage owned by
  a function. They can share a type or name but are not the same semantic role.
- In module scope, a file-to-file call edge means one or more named functions in
  the source file call functions in the target file. Selecting the edge reveals
  those pairs. A read/write edge similarly reveals the underlying function and
  variable rather than claiming the whole file performed one opaque operation.
- Function inspection can currently show ownership, callers, callees, reads,
  writes, parameter declarations, local declarations, and return type. Showing
  where each argument value originated or how it influences a returned value is
  gated on the value-flow relations in D029.
- Symbol inspection shows recorded declaration/definition sites and direct
  incoming/outgoing call, read, write, and reference occurrences across files.
  Their order is deliberately unspecified until CFG evidence exists.
- Parameter and local type-size sums are useful storage estimates, not function
  code size, exact stack-frame size, or maximum caller-chain stack. Those claims
  require object/map and ABI-aware compiler stack evidence as recorded in D030.
- Use overview graphs for architectural shape and the trace playground for one
  progressively disclosed investigation. Repeated visual instances reduce
  crossings but always refer back to one canonical symbol; their tree order is
  navigation order, not runtime order.
