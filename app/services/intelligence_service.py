"""Read-only composition of run snapshots and source-matched compiler evidence."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from code_intelligence.exploration import Explorer, MODES, identity
from orchestrator.config import WORKSPACE_ROOT
from app.services.graph_service import _latest_graphs_by_module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Source path leaves the selected repository")
    return path


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


GATES = [
    {"feature": "Version comparison, change impact and architecture drift", "status": "roadmap", "requires": "Two comparable source snapshots and stable configuration identities"},
    {"feature": "Regression-test selection and coverage", "status": "needs_evidence", "requires": "Imported tests and source-to-test coverage mappings"},
    {"feature": "State-machine and scheduler views", "status": "needs_evidence", "requires": "Explicit state/transition and task/interrupt mappings; CFG branches alone do not establish these"},
    {"feature": "Signal / CAN / model traceability", "status": "needs_evidence", "requires": "DBC, interface dictionaries or model-to-code mappings"},
    {"feature": "Observed execution, timing, stack, races and safety", "status": "needs_evidence", "requires": "Runtime traces, target/linker evidence and relevant verification results"},
    {"feature": "AI semantic explanations and vector retrieval", "status": "roadmap", "requires": "A separately evaluated model/index with evidence-linked answers"},
]


class Workspace:
    def __init__(self, modules=None, root=WORKSPACE_ROOT):
        self.root = Path(root).resolve()
        records = _latest_graphs_by_module(self.root)
        if modules is not None and (len(modules) > 20 or any(m not in records for m in modules)):
            raise ValueError("Select at most 20 available modules")
        self.records = {m: r for m, r in records.items() if modules is None or m in modules}
        self.roots, self.bundles, self.evidence, self.warnings = {}, {}, [], []
        nodes, edges = {}, {}
        manifests = sorted(self.root.glob("*/*/manifest.json"))
        hash_cache = {}
        def cached_sha(path):
            path = Path(path).resolve()
            if path not in hash_cache: hash_cache[path] = sha(path)
            return hash_cache[path]
        for module, record in sorted(self.records.items()):
            run = self.root / record["run_id"]
            repo = inside(run, module)
            self.roots[module] = repo
            graph = deepcopy(record["graph"])
            local_nodes = {n["id"]: n for n in graph["nodes"]}
            local_edges = {e["id"]: e for e in graph["edges"]}
            candidates = defaultdict(list)
            for path in manifests:
                try:
                    manifest = read(path)
                    if manifest.get("status") != "completed" or not manifest.get("flow"): continue
                    source = inside(repo, manifest["source"])
                    # Match the actual repository, not just identical filenames or bytes.
                    if str(source) not in manifest.get("input_hashes", {}): continue
                    if cached_sha(source) != manifest["source_sha256"]: raise ValueError("source changed")
                    for input_path, expected in manifest["input_hashes"].items():
                        if cached_sha(Path(input_path)) != expected: raise ValueError("compiler input changed")
                    for name, key in (("code-intelligence.json", "graph_sha256"), ("source.ll", "ir_sha256"), ("source.i", "preprocessed_sha256")):
                        if cached_sha(path.parent / name) != manifest[key]: raise ValueError("bundle hash mismatch")
                    candidates[manifest["source"]].append((path, manifest))
                except (ValueError, KeyError, OSError) as exc:
                    self.warnings.append({"bundle": path.relative_to(self.root).as_posix(), "reason": str(exc)})
            for source, variants in sorted(candidates.items()):
                if len({m["configuration"] for _, m in variants}) > 1:
                    self.warnings.append({"source": source, "reason": "Conflicting compiler configurations; no automatic flow overlay"})
                    continue
                path, manifest = max(variants, key=lambda pair: (pair[0].stat().st_mtime_ns, str(pair[0])))
                flow = read(path.parent / "code-intelligence.json")
                for n in flow["nodes"]:
                    # Matching compiler bundle supplies current AST metrics as well as flow.
                    if n["id"] not in local_nodes or n.get("is_definition") or n["kind"] in {"basic_block", "instruction", "ir_value"}:
                        local_nodes[n["id"]] = n
                local_edges.update({e["id"]: e for e in flow["edges"]})
                self.bundles[(module, source)] = manifest
                self.evidence.append({"module": module, "source": source,
                    "bundle": path.parent.relative_to(self.root).as_posix(),
                    "configuration": manifest["configuration"], "graph_sha256": manifest["graph_sha256"],
                    "source_sha256": manifest["source_sha256"], "flow": manifest["flow"],
                    "status": "inputs_and_bundle_hashes_verified"})
            prefix = record["run_id"] + "::"
            for key, n in local_nodes.items():
                n = deepcopy(n)
                n.update(id=prefix + key, canonical_id=key, module=module, run_id=record["run_id"])
                for attr in ("function", "block", "canonical_symbol"):
                    if n.get("attributes", {}).get(attr) in local_nodes: n["attributes"][attr] = prefix + n["attributes"][attr]
                nodes[n["id"]] = n
            for key, e in local_edges.items():
                e = deepcopy(e)
                e.update(id=prefix + key, source=prefix + e["source"], target=prefix + e["target"], canonical_id=key)
                for attr in ("function", "terminator", "memory_object", "incoming_block"):
                    if e.get("attributes", {}).get(attr) in local_nodes: e["attributes"][attr] = prefix + e["attributes"][attr]
                edges[e["id"]] = e
        # Only exact public compiler identities with a unique definition may join modules.
        definitions = defaultdict(list)
        for n in nodes.values():
            if (n.get("usr") or "").startswith("c:@") and n.get("is_definition") and n["kind"] in {"function", "global_variable"}:
                definitions[(n["kind"], n["usr"])].append(n)
        resolved = {}
        for n in nodes.values():
            matches = definitions.get((n["kind"], n.get("usr")), [])
            if not n.get("is_definition") and len(matches) == 1 and matches[0]["module"] != n["module"]:
                target = matches[0]
                if n.get("attributes", {}).get("type") != target.get("attributes", {}).get("type"): continue
                resolved[n["id"]] = target["id"]
                key = "resolve:" + identity(n["id"], target["id"])
                edges[key] = {"id": key, "source": n["id"], "target": target["id"], "kind": "resolves_to", "resolution": "unique_public_usr", "attributes": {}}
        for e in list(edges.values()):
            if e["kind"] in {"calls", "reads", "writes", "references"} and e["target"] in resolved:
                # Replace the projection endpoint but retain its exact original evidence ID.
                e["declaration_target"] = e["target"]
                e["target"] = resolved[e["target"]]
                e["resolution"] = "unique_public_usr"
        self.graph = {"nodes": list(nodes.values()), "edges": list(edges.values())}
        self.explorer = Explorer(self.graph)

    def catalog(self):
        return {"modules": [{"module_name": m, "run_id": r["run_id"]} for m,r in self.records.items()],
                "modes": [{"id": k, "label": v} for k,v in MODES.items()],
                "symbols": [n for n in self.graph["nodes"] if n["kind"] not in {"instruction", "basic_block", "ir_value"}],
                "evidence": self.evidence, "warnings": self.warnings, "gates": GATES}

    def query(self, **kwargs):
        result = self.explorer.query(**kwargs)
        if kwargs.get("mode") == "skeleton" and kwargs.get("selected"):
            contexts = [self.context(k) for k in kwargs["selected"]]
            result["structures"] = contexts
            result["notes"].append("Source skeletons show containment; use CFG for branch order. Several selected functions are inspected together.")
        result.update(schema_version="1.0", evidence=self.evidence, warnings=self.warnings, gates=GATES,
                      snapshots=[{"module":m, "run_id":r["run_id"], "provenance":r["graph"].get("provenance"),
                                  "graph_sha256": sha(self.root / r["run_id"] / "analysis" / "code-intelligence.json")}
                                 for m,r in self.records.items()])
        return result

    def context(self, node_id):
        node = self.explorer.nodes.get(node_id)
        if not node: raise ValueError("Unknown node")
        location = node.get("location") or {}
        result = {"node": node, "relationships": [e for e in self.explorer.edges if node_id in (e["source"],e["target"])],
                  "source": None, "regions": [], "notes": []}
        if not location.get("path"):
            result["notes"].append("No source location supplied by the compiler")
            return result
        try:
            path = inside(self.roots[node["module"]], location["path"])
            text = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except (ValueError, OSError):
            result["notes"].append("Source is unavailable inside this repository")
            return result
        start = max(1, location.get("line", 1)); end = min(len(text), location.get("end_line") or start, start + 299)
        source = "\n".join(f"{i+1}: {text[i]}" for i in range(start-1, end))
        manifest = self.bundles.get((node["module"], location["path"]))
        result["source"] = {"path":location["path"], "start":start,"end":end,"text":source[:24000],
                            "sha256":sha(path), "match":"verified_flow_input" if manifest else "current_file_snapshot_not_hash_bound",
                            "truncated":end < (location.get("end_line") or start) or len(source)>24000}
        if node["kind"] == "function" and manifest:
            from code_intelligence.regions import source_regions
            result.update(source_regions(path, node, manifest))
        else: result["notes"].append("Compiler regions require a matching flow bundle for this function. Source excerpts remain available.")
        return result
