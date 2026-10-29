"""Compiler CFG, SSA operand flow and bounded local-memory reaching definitions."""
from __future__ import annotations

import hashlib
from pathlib import Path

from code_intelligence.graph import KnowledgeGraph
from code_intelligence.models import (
    EdgeKind, GraphEdge, GraphNode, NodeKind, RelationResolution, SourceLocation,
)
from .llvm_api import LLVM


def _id(*parts):
    return "llvm:" + hashlib.sha256("\x1f".join(map(str, parts)).encode()).hexdigest()


def add_llvm_flow(graph: KnowledgeGraph, ir: bytes, *, library: Path,
                  repo_root: Path, translation_unit: str, configuration: str) -> dict:
    api = LLVM(library)
    ast_symbols = graph.nodes
    scope = (translation_unit, configuration)
    summary = {"engine": "llvm_c_api", "version": api.version, "functions": 0,
               "blocks": 0, "instructions": 0, "memory_objects": 0,
               "memory_scope": "non_escaping_direct_allocas_only",
               "limitations": ["No interprocedural memory or alias analysis",
                   "Pointer/global/field memory contents are not resolved",
                   "CFG is lowered IR, not a one-to-one source statement graph",
                   "Reaching definitions are path-insensitive may-flow"]}

    def location(value):
        line = api.GetDebugLocLine(value)
        filename = api.debug_string(value, "Filename")
        if not line or not filename:
            return None
        path = Path(filename)
        if not path.is_absolute():
            path = Path(api.debug_string(value, "Directory")) / path
        try:
            relative = path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            relative = path.as_posix()
        return SourceLocation(relative, line, api.GetDebugLocColumn(value) or None)

    def edge(kind, source, target, **attrs):
        graph.add_edge(GraphEdge(_id(kind, source, target, sorted(attrs.items())),
            kind, source, target, RelationResolution.COMPILER_DERIVED,
            attributes={"engine": "llvm", **attrs}))

    with api.parse(ir) as module:
        for function in api.items(module, "Function"):
            blocks = list(api.items(function, "BasicBlock"))
            if not blocks:
                continue
            name, loc = api.name(function), location(function)
            matches = [n for n in ast_symbols if n.kind == NodeKind.FUNCTION
                       and n.name == name and n.is_definition and n.location and loc
                       and n.location.path == loc.path and n.location.line == loc.line]
            if len(matches) != 1:
                raise ValueError(f"Cannot uniquely join LLVM function to AST: {name} {loc}")
            function_id = matches[0].id
            summary["functions"] += 1
            prefix = (*scope, name)
            block_ids = {b: _id(*prefix, "block", i) for i, b in enumerate(blocks)}
            instructions = {b: list(api.items(b, "Instruction")) for b in blocks}
            ids = {v: _id(*prefix, "instruction", bi, i)
                   for bi, b in enumerate(blocks) for i, v in enumerate(instructions[b])}
            for i, param in enumerate(api.items(function, "Param")):
                ids[param] = _id(*prefix, "argument", i)
                graph.add_node(GraphNode(ids[param], NodeKind.IR_VALUE, api.name(param),
                    loc, attributes={"role": "argument", "index": i, "function": function_id}))
                edge(EdgeKind.CONTAINS, function_id, ids[param])

            def value_id(value):
                if value in ids:
                    return ids[value]
                if api.IsABasicBlock(value):
                    raise ValueError("Basic block used as a data operand")
                text = ("@" + api.name(value)) if api.IsAGlobalValue(value) else api.text(value)
                identity = _id(*prefix, "value", text)
                ids[value] = identity
                symbols = [n.id for n in ast_symbols
                           if api.IsAGlobalValue(value) and n.name == api.name(value)
                           and n.kind in {NodeKind.FUNCTION, NodeKind.GLOBAL_VARIABLE}]
                graph.add_node(GraphNode(identity, NodeKind.IR_VALUE, text,
                    attributes={"role": "global_or_callee" if api.IsAGlobalValue(value)
                                else "constant", "ir": text, "function": function_id,
                                "canonical_symbol": symbols[0] if len(symbols) == 1 else None}))
                if api.IsAConstantExpr(value):
                    for index in range(api.GetNumOperands(value)):
                        operand = api.GetOperand(value, index)
                        edge(EdgeKind.DEF_USE, value_id(operand), identity, operand_index=index)
                return identity

            opcodes = {inst: api.GetInstructionOpcode(inst)
                       for values in instructions.values() for inst in values}
            operands = {inst: [api.GetOperand(inst, i) for i in range(api.GetNumOperands(inst))]
                        for inst in opcodes}
            texts = {inst: api.text(inst) for inst in opcodes}
            safe = {v for v, op in opcodes.items() if op == 26}
            for inst, values in operands.items():
                for index, value in enumerate(values):
                    if value in safe and not (
                        (opcodes[inst] == 27 and index == 0 or opcodes[inst] == 28 and index == 1)
                        and " volatile " not in texts[inst] and " atomic " not in texts[inst]
                    ):
                        safe.remove(value)
            predecessors = {b: set() for b in blocks}
            for bi, block in enumerate(blocks):
                block_id = block_ids[block]
                terminator = api.GetBasicBlockTerminator(block)
                graph.add_node(GraphNode(block_id, NodeKind.BASIC_BLOCK,
                    api.name(api.BasicBlockAsValue(block)) or f"block{bi}",
                    attributes={"function": function_id, "entry": bi == 0,
                                "exit": api.GetNumSuccessors(terminator) == 0,
                                "order": bi, "configuration": configuration}))
                edge(EdgeKind.CONTAINS, function_id, block_id)
                for index, inst in enumerate(instructions[block]):
                    opcode = api.GetInstructionOpcode(inst)
                    attrs = {"ir": texts[inst], "opcode": opcode,
                             "block": block_id, "function": function_id, "order": index}
                    if opcode in {27, 28, 45, 5, 56, 57, 67}:
                        attrs["memory_boundary"] = "unresolved_memory_or_call_effect"
                    if opcode in {27, 28} and operands[inst][0 if opcode == 27 else 1] in safe:
                        attrs["memory_boundary"] = "local_reaching_definitions"
                    graph.add_node(GraphNode(ids[inst], NodeKind.INSTRUCTION,
                        api.name(inst) or f"instruction{index}", location(inst), attributes=attrs))
                    edge(EdgeKind.CONTAINS, block_id, ids[inst])
                count = api.GetNumSuccessors(terminator)
                for index in range(count):
                    target = api.GetSuccessor(terminator, index)
                    predecessors[target].add(block)
                    opcode = api.GetInstructionOpcode(terminator)
                    label = ("true" if index == 0 else "false") if opcode == 2 and count == 2 else "successor"
                    if opcode == 3:
                        label = "default" if index == 0 else api.text(api.GetSwitchCaseValue(terminator, index))
                    edge(EdgeKind.CONTROL_FLOW, block_id, block_ids[target],
                         successor_index=index, label=label, terminator=ids[terminator])
            for inst, values in operands.items():
                for index, operand in enumerate(values):
                    if api.IsABasicBlock(operand):
                        continue
                    attrs = {"operand_index": index}
                    if opcodes[inst] == 44:  # PHI operands carry predecessor identity.
                        attrs["incoming_block"] = block_ids[api.GetIncomingBlock(inst, index)]
                    edge(EdgeKind.DEF_USE, value_id(operand), ids[inst], **attrs)

            # Only track allocas used exclusively as direct load/store addresses.
            # Escapes, GEP, casts, calls, volatile/atomic accesses stay explicit boundaries.
            accesses = {i: ("load" if opcodes[i] == 27 else "store", vals[0 if opcodes[i] == 27 else 1])
                        for i, vals in operands.items() if opcodes[i] in {27, 28}
                        and vals[0 if opcodes[i] == 27 else 1] in safe}
            _memory_flow(blocks, instructions, predecessors, accesses, ids, edge)
            summary["blocks"] += len(blocks)
            summary["instructions"] += len(opcodes)
            summary["memory_objects"] += len(safe)
    graph.validate()
    return summary


def _memory_flow(blocks, instructions, predecessors, accesses, ids, edge):
    """Finite monotone reaching-definitions fixed point, including loop backedges."""
    reachable = {blocks[0]}
    while True:
        expanded = reachable | {b for b in blocks if predecessors[b] & reachable}
        if expanded == reachable:
            break
        reachable = expanded
    outgoing = {b: {} for b in blocks}

    def incoming(block):
        state = {}
        for pred in predecessors[block] & reachable:
            for address, defs in outgoing[pred].items():
                state.setdefault(address, set()).update(defs)
        return state

    changed = True
    while changed:
        changed = False
        for block in blocks:
            if block not in reachable:
                continue
            state = incoming(block)
            for inst in instructions[block]:
                if inst in accesses and accesses[inst][0] == "store":
                    state[accesses[inst][1]] = {inst}
            if state != outgoing[block]:
                outgoing[block] = state
                changed = True
    for block in blocks:
        if block not in reachable:
            continue
        state = incoming(block)
        for inst in instructions[block]:
            if inst not in accesses:
                continue
            kind, address = accesses[inst]
            if kind == "store":
                state[address] = {inst}
            else:
                for definition in sorted(state.get(address, ())):
                    edge(EdgeKind.MEMORY_FLOW, ids[definition], ids[inst],
                         memory_object=ids[address], certainty="may_reach",
                         method="direct_non_escaping_alloca_reaching_definitions_v1")
