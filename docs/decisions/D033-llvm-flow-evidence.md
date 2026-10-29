# D033 — Add opt-in compiler flow evidence

- Date: 2026-10-29
- Status: Accepted, bounded implementation
- Trigger: working machine-readable CFG/DFD on a retained run is the success
  criterion; rendering is secondary and existing behavior must survive.
- Decision: matching Clang/LLVM 22, O0 debug IR and the LLVM C API. Add facts to
  the canonical graph and derive disposable projections. A separate CLI writes
  only to a fresh directory, preserving existing pipeline and UI behavior.
- Alternatives: Clang `debug.DumpCFG` worked on the public fixture, but its
  diagnostic text and expression references would need a parser and another
  memory-flow model. Native IR supplies successors/operands directly. AST-only
  reconstruction would require implementing C control/sequencing semantics.
  Joern/LibTooling were considered, not installed or experimentally compared.
- Evidence: LLVM 22.1.5 on retained Shunt emitted 9 CFGs. Branches, binary-search
  loop and arithmetic were manually aligned to source. Tests exercise switch,
  PHI, loop-carried local definitions, short-circuiting and pointer escapes.
- Trade-offs: lowered, configuration-specific IR and bounded local-memory flow;
  no full alias/interprocedural analysis. This optional compiler pass extends
  D027 explicitly; the default review still shares its single AST parse.
- Revisit: target ABI, full memory flow, large-run resource bounds, another LLVM
  major or UI integration. Widen claims only with new tests/source evidence.
- Owners: [flow contract](../contracts/flow-evidence.md),
  [verification](../engineering/testing-and-replay.md).
- References: [LLVM IR](https://llvm.org/docs/LangRef.html),
  [LLVM C terminators](https://llvm.org/doxygen/group__LLVMCCoreValueInstructionTerminator.html),
  [Clang debug CFG](https://clang.llvm.org/docs/analyzer/developer-docs/DebugChecks.html).
