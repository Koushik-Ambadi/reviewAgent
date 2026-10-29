# Compiler flow evidence

Implemented bounded LLVM 22 C evidence; reviewed 2026-10-29.
See [D033](../decisions/D033-llvm-flow-evidence.md) for engine selection.

`python -m code_intelligence.flow` takes one source, repository root, a fresh
output directory, matching Clang/LLVM 22 library, and optional compilation
database directory. Exactly one database entry must match. The database's shell
command/compiler is never executed. Arguments use the existing sanitized host
C99 policy, not target ABI or firmware-build settings; both argument sets survive.

The command preprocesses into `source.i`, emits O0 debug IR to `source.ll`,
parses AST facts and reads verified IR through LLVM's native C API. It checks
input drift by re-preprocessing (normalizing CRLF/LF only for comparison).
Compiler calls time out after 120 seconds; native graph traversal currently has
no separate resource/time limit. Failed diagnostics/manifests are retained.
Existing output directories are rejected, including existing review artifacts.

## Authority and provenance

- `code-intelligence.json`: canonical AST plus flow graph, schema 1.2 when
  blocks exist. Normal review `symbols.json` and AST snapshots are unchanged.
- `control_flow.json` and `data_flow.json`: disposable exact node/edge subsets,
  each naming the canonical file SHA-256. They are not independent authorities.
- `manifest.json`: completion/failure, source/include hashes, preprocessed/IR/
  graph hashes, implementation hashes, arguments, commands, working directory,
  compiler/library versions and coverage. `source_revision` is a source-content
  `sha256:` identity; `dirty: null` means Git cleanliness is unknown. `source.i`
  is the IR replay input; the retained verification record supplies the Git
  revision. Compiler diagnostic files are retained even when empty.

Functions join AST IDs by exact name, debug path and definition line; ambiguous
or missing joins fail closed. Coverage means emitted definitions in one TU,
not all AST declarations, all source configurations or a whole repository.

## Added facts

- `basic_block`: function, ordinal, entry/exit flags, configuration. Exit means
  no successors: inspect the terminator to distinguish return/unreachable.
  Function-to-block and block-to-instruction ownership uses `contains`.
- `instruction`: numeric LLVM opcode, full instruction text, block/function,
  ordinal, available debug location. Synthetic instructions may lack locations;
  multiple instructions can map to one line. These are not exact source ranges.
- `ir_value`: argument, constant or global/callee operand. `canonical_symbol`
  links a unique matching AST global/function; null is unresolved. This is not
  a call-argument-to-callee-parameter binding.
- `control_flow`: block to actual successor, terminator, successor ordinal,
  true/false, typed switch case/default or generic successor label.
- `def_use`: producer/value to consuming instruction or constant expression,
  operand index and PHI predecessor. Addresses/callees are operands too; an
  operand edge alone does not claim memory-content flow.
- `memory_flow`: store to load on direct non-escaping allocas, memory object ID,
  `may_reach` certainty and versioned fixed-point method. Branch joins and loop
  backedges participate; intervening stores kill older local definitions.
  Unreachable blocks do not contribute.

LLVM IDs hash TU path, effective configuration/input identity, function and IR
ordinal/value. They are repeatable for unchanged inputs, not stable across code
edits or compilers. Existing AST USR semantics remain unchanged. All graph and
projection endpoints must exist.

## Limits

SSA operand references are exact; memory coverage is partial. Escaping allocas,
GEP/cast-based memory, volatile/atomic accesses, globals, fields, arrays, pointers
and call effects remain unresolved memory boundaries. Aliasing, interprocedural
memory, uninitialized-path detection and path feasibility are not implemented.
Missing memory edges never prove absence of dependencies. Intrinsic/call
operations retain operands without inferred hidden effects.

IR is lowered: source constructs may fold/expand even at O0. This is neither a
runtime trace nor a source-level CFG, frequency estimate or safety proof.
C++ exceptions, other LLVM majors and target builds have not been validated.
The normal pipeline and graphical CFG/DFD controls remain unchanged; the CLI
and JSON projections are the implemented delivery surface.
