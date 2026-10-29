"""Check persisted projections against canonical facts, retained IR and source."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from code_intelligence.extraction.llvm_api import LLVM


def verify_flow_evidence(directory: Path, repo: Path, library: Path) -> dict:
    def read(name):
        return json.loads((directory / name).read_text(encoding="utf-8"))

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    manifest = read("manifest.json")
    require(manifest["status"] == "completed", "Run did not complete")
    for name, key in (("source.i", "preprocessed_sha256"), ("source.ll", "ir_sha256"),
                      ("code-intelligence.json", "graph_sha256")):
        require(sha(directory / name) == manifest[key], f"Hash mismatch: {name}")
    require(sha(repo / manifest["source"]) == manifest["source_sha256"], "Source changed")
    for path, expected in manifest["input_hashes"].items():
        require(sha(Path(path)) == expected, f"Input changed: {path}")
    graph = read("code-intelligence.json")
    nodes = {n["id"]: n for n in graph["nodes"]}
    edges = {e["id"]: e for e in graph["edges"]}
    require(len(nodes) == len(graph["nodes"]) and len(edges) == len(graph["edges"]), "Duplicate IDs")
    require(all(e["source"] in nodes and e["target"] in nodes for e in edges.values()), "Dangling edge")
    for name, node_kinds, edge_kinds in (
        ("control_flow", {"basic_block"}, {"control_flow"}),
        ("data_flow", {"instruction", "ir_value"}, {"def_use", "memory_flow"}),
    ):
        projection = read(name + ".json")
        require(projection["canonical_graph_sha256"] == manifest["graph_sha256"], "Wrong projection authority")
        require(projection["nodes"] == [n for n in graph["nodes"] if n["kind"] in node_kinds], "Node projection drift")
        require(projection["edges"] == [e for e in graph["edges"] if e["kind"] in edge_kinds], "Edge projection drift")
    located = 0
    for node in nodes.values():
        if node["kind"] != "instruction" or not node["location"]:
            continue
        loc = node["location"]
        path = repo / loc["path"]
        require(path.is_file(), f"Missing source: {path}")
        require(1 <= loc["line"] <= len(path.read_text(encoding="utf-8", errors="replace").splitlines()), "Bad source line")
        located += 1

    api = LLVM(library)
    block_count = instruction_count = successor_count = operand_count = 0
    cfg = {(e["source"], e["attributes"]["successor_index"]): e
           for e in edges.values() if e["kind"] == "control_flow"}
    uses = {(e["target"], e["attributes"]["operand_index"]): e
            for e in edges.values() if e["kind"] == "def_use" and nodes[e["target"]]["kind"] == "instruction"}
    with api.parse((directory / "source.ll").read_bytes()) as module:
        for function in api.items(module, "Function"):
            blocks = list(api.items(function, "BasicBlock"))
            if not blocks:
                continue
            candidates = [n for n in nodes.values() if n["kind"] == "function"
                          and n["name"] == api.name(function) and n["is_definition"]]
            require(len(candidates) == 1, "Ambiguous IR function")
            function_id = candidates[0]["id"]
            owned = [n for n in nodes.values() if n["attributes"].get("function") == function_id]
            ordered = sorted((n for n in owned if n["kind"] == "basic_block"), key=lambda n: n["attributes"]["order"])
            require(len(ordered) == len(blocks), "Block count differs from IR")
            block_ids = {b: n["id"] for b, n in zip(blocks, ordered)}
            values = {}
            for index, param in enumerate(api.items(function, "Param")):
                values[param] = next(n["id"] for n in owned if n["attributes"].get("role") == "argument"
                                     and n["attributes"]["index"] == index)
            pending = []
            for block in blocks:
                insts = list(api.items(block, "Instruction"))
                serialized = sorted((n for n in owned if n["kind"] == "instruction"
                                     and n["attributes"]["block"] == block_ids[block]), key=lambda n: n["attributes"]["order"])
                require(len(serialized) == len(insts), "Instruction count differs from IR")
                for inst, node in zip(insts, serialized):
                    values[inst] = node["id"]
                    require(node["attributes"]["ir"] == api.text(inst), "Instruction differs from IR")
                    pending.append(inst)
                term = api.GetBasicBlockTerminator(block)
                count = api.GetNumSuccessors(term)
                for index in range(count):
                    edge = cfg[(block_ids[block], index)]
                    require(edge["target"] == block_ids[api.GetSuccessor(term, index)], "CFG differs from IR")
                    successor_count += 1
                instruction_count += len(insts)
            for inst in pending:
                for index in range(api.GetNumOperands(inst)):
                    operand = api.GetOperand(inst, index)
                    if api.IsABasicBlock(operand):
                        continue
                    edge = uses[(values[inst], index)]
                    if operand in values:
                        require(edge["source"] == values[operand], "SSA def-use differs from IR")
                    else:
                        text = "@" + api.name(operand) if api.IsAGlobalValue(operand) else api.text(operand)
                        require(nodes[edge["source"]]["attributes"]["ir"] == text, "Operand differs from IR")
                    operand_count += 1
            block_count += len(blocks)
    require(successor_count == len(cfg), "Extra CFG edges")
    require(operand_count == len(uses), "Extra instruction operand edges")
    return {"consistent": True, "canonical_sha256": manifest["graph_sha256"],
            "nodes": dict(Counter(n["kind"] for n in nodes.values())),
            "edges": dict(Counter(e["kind"] for e in edges.values())),
            "verified_blocks": block_count, "verified_instructions": instruction_count,
            "verified_successors": successor_count, "verified_instruction_operands": operand_count,
            "source_located_instructions": located,
            "boundary": "Serialization/IR/source-location alignment; semantic source checks and memory-flow tests are separate"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--llvm-library", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify_flow_evidence(args.directory, args.repo, args.llvm_library), indent=2, sort_keys=True))
