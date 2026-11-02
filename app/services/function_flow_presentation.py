"""Source-bound labels for an already verified compiler CFG projection."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


def _statement(lines: list[str], line: int) -> str | None:
    if not 1 <= line <= len(lines):
        return None
    # The debug line identifies the source statement. Keep a short continuation
    # for wrapped assignments, without claiming that it is a parsed expression.
    start = line - 1
    if "=" not in lines[start]:
        for previous in range(start - 1, max(-1, start - 3), -1):
            if ";" in lines[previous] or "{" in lines[previous]:
                break
            if re.search(r"(?<![=!<>])=(?!=)", lines[previous]):
                start = previous
                break
    text = " ".join(part.strip() for part in lines[start:line + 3])
    statement = " ".join(text.split()).split(";", 1)[0]
    return statement[:320] if re.search(r"(?<![=!<>])=(?!=)", statement) else None


def _condition(lines: list[str], line: int) -> str | None:
    if not 1 <= line <= len(lines):
        return None
    if not re.match(r"\s*(?:}\s*)?(?:else\s+)?if\s*\(", lines[line - 1]):
        return None
    text = " ".join(part.strip() for part in lines[line - 1:line + 5])
    match = re.search(r"\bif\s*\(", text)
    start, depth = match.end(), 1
    for position in range(start, min(len(text), start + 500)):
        if text[position] == "(":
            depth += 1
        elif text[position] == ")":
            depth -= 1
            if depth == 0:
                return " ".join(text[start:position].split())
    return None


def describe_cfg(nodes: list[dict], graph: dict, source: Path,
                 source_path: str) -> list[dict]:
    """Add display hints; canonical nodes, edges and LLVM evidence stay intact."""
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    operations = defaultdict(list)
    block_ids = {node["id"] for node in nodes if node["kind"] == "basic_block"}
    function_ids = {node.get("attributes", {}).get("function") for node in nodes
                    if node["kind"] == "basic_block"}
    function_ids.discard(None)
    function_ids |= {node.get("canonical_id") for node in graph["nodes"]
                     if node["id"] in function_ids}
    declarations = {}
    for node in graph["nodes"]:
        if node["kind"] == "instruction" and node.get("attributes", {}).get("block") in block_ids:
            operations[node["attributes"]["block"]].append(node)
        if node["kind"] in {"global_variable", "local_variable"}:
            if node["kind"] == "local_variable" and node.get("attributes", {}).get("scope") not in function_ids:
                continue
            location = node.get("location") or {}
            if location.get("path") == source_path and isinstance(location.get("line"), int):
                declarations[node["name"]] = location["line"]
    described = []
    for block in nodes:
        if block["kind"] != "basic_block":
            described.append(block)
            continue
        ordered = sorted(operations[block["id"]], key=lambda item: item["attributes"].get("order", 0))
        branches = [op for op in ordered if re.match(r"br i1\b", op.get("attributes", {}).get("ir", ""))]
        stores = [op for op in ordered if re.match(r"store\b", op.get("attributes", {}).get("ir", ""))]
        effects = []
        for op in stores:
            location = op.get("location") or {}
            line = location.get("line")
            statement = (_statement(lines, line) if location.get("path") == source_path
                         and isinstance(line, int) else None)
            effects.append({"source": statement, "line": line,
                            "ir": op["attributes"].get("ir")})
        branch = branches[-1] if branches else None
        branch_location = (branch.get("location") or {}) if branch else {}
        branch_line = branch_location.get("line")
        condition = (_condition(lines, branch_line) if branch_location.get("path") == source_path
                     and isinstance(branch_line, int) else None)
        inputs = []
        if condition:
            for name in dict.fromkeys(re.findall(r"\b[A-Za-z_]\w*\b", condition)):
                line = declarations.get(name)
                if line:
                    declaration = _statement(lines, line)
                    inputs.append({"name": name, "declaration": declaration, "line": line})
        structural_join = (not branch and not stores and not block["attributes"].get("exit")
                           and bool(ordered) and all(re.match(r"br label\b", op["attributes"].get("ir", ""))
                                                     for op in ordered))
        described.append({**block, "flow_summary": {
            "condition": condition, "condition_line": branch_line,
            "condition_inputs": inputs,
            "branch_ir": branch["attributes"].get("ir") if branch else None,
            "effects": effects, "structural_join": structural_join,
        }})
    return described
