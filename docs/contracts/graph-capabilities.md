# Graph Capability and Evidence Matrix

- Status: living implementation matrix
- Created: 2026-10-27
- Last reviewed: 2026-10-27
- Source of truth for: every graph capability discussed for this project, the
  evidence each graph requires, current extraction coverage, and the next
  implementation gate
- Does not own: canonical node/edge serialization, current package architecture,
  or roadmap priority
- Related: [code-intelligence graph contract](code-intelligence-graph.md),
  [D026](../decisions/D026-unified-code-intelligence-graph.md), and
  [D027](../decisions/D027-shared-code-analysis-stage.md)

## Status vocabulary

- `IMPLEMENTED`: extraction and a deterministic projection exist and have
  focused verification.
- `DERIVABLE`: the canonical graph already contains the required facts; the
  projection still needs implementation.
- `AST_EXPANSION`: source/compiler facts can be added to the common extraction
  stage without external evidence.
- `ENGINE_REQUIRED`: libclang Python cursors do not expose the required
  semantics reliably; a CFG/data-flow/static-analysis engine or compiler output
  must be selected and validated.
- `PROJECT_MODEL_REQUIRED`: syntax is insufficient; project configuration or
  explicit domain annotations are required.
- `EXTERNAL_EVIDENCE_REQUIRED`: requirements, tests, builds, measurements,
  linker artifacts, or safety evidence must be imported with provenance.

## Complete discussed graph list

| ID | Graph / aliases | Required evidence | Current coverage | Status | Next gate |
|---|---|---|---|---|---|
| GR-001 | Unified software knowledge graph / AI knowledge graph | Stable nodes and edges, source/configuration/tool provenance, unresolved relations | Canonical graph, AST fragments, deterministic merge, validation, snapshots | IMPLEMENTED | Connect real compilation database and run persistence |
| GR-002 | Call graph | Function identities and direct/indirect call sites | Direct calls and named unresolved calls; indirect target sets absent | IMPLEMENTED | Add indirect-call evidence and configuration coverage |
| GR-003 | Reachability / dead-code graph | Call graph plus explicit roots/exported entry points and configuration | Explicit-root projection classifies reachable/unreachable functions and exposes unresolved boundaries | IMPLEMENTED | Add project entry-point/configuration discovery |
| GR-004 | Call-depth graph | Call graph, roots, recursion/SCC handling | Explicit-root projection condenses recursive SCCs and reports bounded depth | IMPLEMENTED | Add project entry-point/configuration discovery |
| GR-005 | Control-flow graph (CFG) | Per-function basic blocks, branch/loop/switch/return edges, exceptional/unreachable exits | Function boundaries only | ENGINE_REQUIRED | Evaluate Clang CFG/LibTooling or a compatible CPG layer on embedded C |
| GR-006 | Data-flow / lineage graph | Definitions, uses, assignments, aliases, pointer targets, interprocedural flow, configuration | No def-use or alias model | ENGINE_REQUIRED | Build on validated CFG plus alias/data-flow engine |
| GR-007 | Variable-access / data-access graph | Variable identities, function scope, read/write/read-write/reference occurrences | Global nodes only; no access edges | AST_EXPANSION | Add parameter/local/field identities and conservative access edges |
| GR-008 | Include graph | Source file, include spelling, resolved target, configuration | Resolved, external, and unresolved include edges | IMPLEMENTED | Add translation-unit/configuration coverage summaries |
| GR-009 | Module-dependency / architecture graph | File ownership, file-to-symbol containment, include/call/data dependencies, module grouping policy | File-as-module projection groups call/include evidence into dependency edges | IMPLEMENTED | Add explicit module grouping and data dependencies |
| GR-010 | Dependency-impact / change-impact graph | Changed node set plus reverse/transitive typed dependencies and unresolved boundary | Reverse traversal reports direct/transitive impact over calls, includes, and containment | IMPLEMENTED | Add changed-line-to-node mapping and unresolved-boundary reporting |
| GR-011 | State-machine graph | State identities, transition guards/actions, initialization, generated-model mapping | Enums alone cannot prove states or transitions | PROJECT_MODEL_REQUIRED | Import annotations/configuration or evaluated Stateflow/generated-code mapping |
| GR-012 | Scheduler / task graph | Task identities, periods, priorities, activation/call relationships, RTOS configuration | Function/call facts only | PROJECT_MODEL_REQUIRED | Define task configuration/annotation contract and import it |
| GR-013 | Interrupt-interaction graph | ISR identities, priorities, shared data, masking/locking, task handoff | No ISR or concurrency semantics | PROJECT_MODEL_REQUIRED | Import target/compiler attributes and platform interrupt configuration |
| GR-014 | Requirement-traceability graph | Versioned requirements and explicit implementation links | No requirement source or link contract | EXTERNAL_EVIDENCE_REQUIRED | Define/import ReqIF or project mapping with revision provenance |
| GR-015 | Test-coverage graph | Test identities, test-to-code mapping, execution and coverage artifacts for exact revision/configuration | No test execution or coverage import | EXTERNAL_EVIDENCE_REQUIRED | Define coverage/test-result adapters and identity contract |
| GR-016 | Clone / duplicate-code graph | Function boundaries, normalized tokens/AST fingerprints, similarity method and threshold | Function boundaries available; fingerprints absent | AST_EXPANSION | Retain deterministic function token fingerprints, then start with exact clones |
| GR-017 | Complexity graph | Function boundaries and branch/decision facts; metric definition/version | Function boundaries available; metrics absent | AST_EXPANSION | Add versioned AST cyclomatic approximation and statement counts |
| GR-018 | Stack-usage graph | Call graph plus compiler stack-usage artifacts or ABI-aware local/frame calculation | Call graph available; exact frame sizes absent | EXTERNAL_EVIDENCE_REQUIRED | Import compiler `.su`/map evidence; allow clearly labeled local-storage estimate |
| GR-019 | Execution-time / timing graph | Measured or bounded timing by task/function/configuration/hardware | No runtime or WCET evidence | EXTERNAL_EVIDENCE_REQUIRED | Import SIL/HIL/profiler/WCET evidence with clock/configuration identity |
| GR-020 | Memory-usage graph | Symbol sizes/sections/addresses plus linker map and runtime heap evidence | Global identities available; sizes/sections absent | AST_EXPANSION | Add type-size estimates, then import linker map for authoritative placement |
| GR-021 | Failure-propagation graph | Failure modes, propagation rules, control/data dependencies, mitigations and safety assumptions | Call/include facts only; no failure semantics | EXTERNAL_EVIDENCE_REQUIRED | Import FMEA/safety model and join it to validated data/control flow |

## Extraction conclusions

The existing graph contains all source facts needed for the first reachability,
call-depth, file-module dependency, and dependency-impact views. Those views
are now implemented without reparsing source; their remaining gates concern
project configuration, richer grouping, changed-line mapping, and unresolved
boundaries rather than another AST walk.

The common AST layer must next add parameter, local-variable, field, and enum-
constant identities; conservative variable references/accesses; type/size
metadata; versioned per-function complexity facts; and deterministic token
fingerprints. These facts support GR-007, GR-016, GR-017, and the estimate-only
part of GR-020. They must be extracted in the same translation-unit traversal
used by review and graph generation.

CFG, interprocedural data flow, aliasing, requirements, tests, scheduler/ISR
semantics, timing, exact stack, linker memory, and failure propagation cannot be
made trustworthy by adding fields to a symbol table. They require named engines
or external evidence contracts. Until those inputs exist, corresponding graph
outputs must remain unavailable rather than empty or inferred as complete.
