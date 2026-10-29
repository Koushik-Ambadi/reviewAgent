"""Deterministic current-snapshot exploration. No runtime or defect predictions."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
import hashlib
import statistics


RELATIONS = {"calls", "reads", "writes", "references", "includes", "resolves_to"}
FLOW = {"control_flow", "def_use", "memory_flow"}
MODES = {
    "connections": "How are my selections connected?",
    "upstream": "What could influence this?",
    "downstream": "What could this affect?",
    "calls": "Who calls whom?", "signals": "Who produces and uses data?",
    "call_depth": "How deep can the call chain go?",
    "files": "How do files depend on one another?",
    "modules": "How do modules connect?", "interfaces": "What crosses a boundary?",
    "skeleton": "What is inside this function?",
    "cfg": "Which decision can happen next?", "dfd": "Where do values come from?",
    "reachability": "What can the selected entry points reach?",
    "cycles": "Where do calls or dependencies loop?",
    "clones": "Where is the same implementation repeated?",
    "metrics": "Where should I investigate first?",
    "calibrations": "Where are constants and tables used?",
}


def identity(*parts):
    return hashlib.sha256("\x1f".join(map(str, parts)).encode()).hexdigest()[:24]


def components(ids, adjacency):
    """Iterative Kosaraju: safe for long generated-code call chains."""
    visited, order = set(), []
    reverse = defaultdict(set)
    for source, targets in adjacency.items():
        for target in targets:
            reverse[target].add(source)
    for root in sorted(ids):
        if root in visited:
            continue
        stack = [(root, False)]
        while stack:
            node, done = stack.pop()
            if done:
                order.append(node)
            elif node not in visited:
                visited.add(node)
                stack.append((node, True))
                stack.extend((n, False) for n in sorted(adjacency.get(node, ()), reverse=True) if n not in visited)
    visited, groups = set(), []
    for root in reversed(order):
        if root in visited:
            continue
        group, pending = set(), [root]
        while pending:
            node = pending.pop()
            if node in visited:
                continue
            visited.add(node)
            group.add(node)
            pending.extend(reverse[node] - visited)
        groups.append(sorted(group))
    return sorted(groups)


class Explorer:
    def __init__(self, graph):
        self.nodes = {n["id"]: n for n in graph["nodes"]}
        self.edges = sorted(graph["edges"], key=lambda e: e["id"])
        if len(self.nodes) != len(graph["nodes"]) or len({e["id"] for e in self.edges}) != len(self.edges):
            raise ValueError("Duplicate graph identities")
        if any(e["source"] not in self.nodes or e["target"] not in self.nodes for e in self.edges):
            raise ValueError("Graph has missing endpoints")
        self.semantic = [e for e in self.edges if e["kind"] in RELATIONS]
        self.calls = [e for e in self.edges if e["kind"] == "calls"]
        self.functions = {k for k, n in self.nodes.items() if n["kind"] == "function"}
        self.adjacency = self.adj(self.calls)
        self.recursive = [g for g in components(self.functions, self.adjacency)
                          if len(g) > 1 or g[0] in self.adjacency.get(g[0], ())]

    def call_depths(self):
        groups = components(self.functions, self.adjacency)
        group_of = {k:i for i,g in enumerate(groups) for k in g}
        successors, parents = defaultdict(set), defaultdict(set)
        for e in self.calls:
            a,b = group_of[e["source"]], group_of[e["target"]]
            if a != b: successors[a].add(b); parents[b].add(a)
        remaining = {i:len(successors[i]) for i in range(len(groups))}
        depths = {i:0 for i in range(len(groups))}
        pending = deque(i for i in remaining if remaining[i] == 0)
        while pending:
            child = pending.popleft()
            for parent in parents[child]:
                depths[parent] = max(depths[parent], depths[child]+1)
                remaining[parent] -= 1
                if remaining[parent] == 0: pending.append(parent)
        return {k:depths[group_of[k]] for k in self.functions}

    @staticmethod
    def adj(edges, undirected=False):
        result = defaultdict(set)
        for e in edges:
            result[e["source"]].add(e["target"])
            if undirected:
                result[e["target"]].add(e["source"])
        return result

    def influence_edges(self):
        # Calls imply a caller depends on its callee, not an execution chronology.
        return [{**e, "source": e["target"], "target": e["source"],
                 "direction_reason": {"reads": "reader depends on value", "calls": "caller depends on callee",
                                      "includes": "including file depends on included file", "resolves_to": "declaration depends on implementation"}[e["kind"]],
                 "display_relation": {"reads": "may affect a reader", "calls": "may affect a caller",
                                      "includes": "may affect an including file", "resolves_to": "implements"}[e["kind"]]}
                if e["kind"] in {"reads", "calls", "includes", "resolves_to"} else e
                for e in self.semantic if e["kind"] != "references"]

    def grouped(self, level):
        def owner(node):
            return node.get("module", "unknown") if level == "modules" else (
                node.get("module", "unknown") + "/" + (node.get("location") or {}).get("path", "external"))
        names = {k: owner(n) for k, n in self.nodes.items()
                 if n["kind"] not in {"instruction", "basic_block", "ir_value"}}
        groups = defaultdict(list)
        for e in self.semantic:
            if e["source"] not in names or e["target"] not in names: continue
            if names[e["source"]] != names[e["target"]]:
                groups[(names[e["source"]], names[e["target"]], e["kind"])].append(e["id"])
        selected = sorted(set(names.values()))
        nodes = [{"id": "group:" + identity(level, n), "name": n, "kind": level[:-1],
                  "module": n.split("/")[0], "attributes": {}, "members": sorted(k for k,v in names.items() if v == n)} for n in selected]
        ids = {n["name"]: n["id"] for n in nodes}
        edges = [{"id": "group:" + identity(*key), "source": ids[key[0]], "target": ids[key[1]],
                  "kind": key[2], "evidence": evidence, "count": len(evidence), "resolution": "derived"}
                 for key, evidence in sorted(groups.items())]
        return nodes, edges

    def analytics(self, rules=()):
        callers, callees, readers, writers = (defaultdict(set) for _ in range(4))
        external = Counter()
        for e in self.semantic:
            s, t = e["source"], e["target"]
            if e["kind"] == "calls":
                callers[t].add(s); callees[s].add(t)
                if not self.nodes[t].get("is_definition") or self.nodes[t].get("attributes", {}).get("external"):
                    external[s] += 1
            if e["kind"] == "reads": readers[t].add(s)
            if e["kind"] == "writes": writers[t].add(s)
        rows, fingerprints = [], defaultdict(list)
        call_depth = self.call_depths()
        for key in sorted(self.functions):
            n = self.nodes[key]; attrs = n.get("attributes") or {}
            shared = [v for v, ws in writers.items() if key in ws and self.nodes[v]["kind"] == "global_variable"]
            complexity = attrs.get("cyclomatic_complexity")
            score = (complexity or 0) + 2 * len(callers[key]) + len(callees[key]) + 3 * len(shared)
            rows.append({"id": key, "name": n["name"], "module": n.get("module"),
                         "complexity": complexity, "method": attrs.get("complexity_method"),
                         "callers": len(callers[key]), "callees": len(callees[key]),
                         "shared_writes": len(shared), "external_calls": external[key],
                         "call_depth_scc_edges": call_depth[key], "definition_available": bool(n.get("is_definition")),
                         "review_score": score, "statement_count": attrs.get("statement_count")})
            if attrs.get("token_fingerprint"):
                fingerprints[(attrs.get("token_fingerprint_method"), attrs["token_fingerprint"])].append(key)
        rows.sort(key=lambda r: (-r["review_score"], r["id"]))
        values = [r["complexity"] for r in rows if isinstance(r["complexity"], (int, float))]
        threshold = None
        if len(values) >= 4:
            q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
            threshold = q3 + 1.5 * (q3 - q1)
        shared = [{"variable": v, "writers": sorted(ws), "readers": sorted(readers[v]),
                   "multiple_writers": len(ws) > 1} for v, ws in sorted(writers.items())
                  if self.nodes[v]["kind"] == "global_variable"]
        file_nodes, file_edges = self.grouped("files")
        adj = self.adj(file_edges)
        file_cycles = [g for g in components([n["id"] for n in file_nodes], adj) if len(g) > 1]
        module_nodes, module_edges = self.grouped("modules")
        module_names = {n["id"]: n["name"] for n in module_nodes}
        findings = [{"rule": rule, "edge": e["id"], "evidence": e["evidence"]}
                    for rule in rules for e in module_edges
                    if module_names[e["source"]] == rule["from"] and module_names[e["target"]] == rule["to"]]
        storage = [n for n in self.nodes.values() if n["kind"] in {"global_variable", "local_variable", "parameter"}]
        return {"functions": rows, "recursive_groups": self.recursive,
                "file_cycles": file_cycles, "file_nodes": file_nodes,
                "shared_state": shared, "clone_groups": sorted(sorted(g) for g in fingerprints.values() if len(g) > 1),
                "complexity_outliers": [r["id"] for r in rows if threshold is not None and (r["complexity"] or 0) > threshold],
                "outlier_threshold": threshold, "outlier_method": "current_population_Q3_plus_1.5_IQR" if threshold is not None else "insufficient_population",
                "score_formula": "complexity + 2×unique callers + unique callees + 3×globals written; review ordering, not defect probability",
                "call_depth_boundary": "Longest path in the SCC-condensed direct-call graph; recursive groups collapse to one step. This is not runtime stack depth; unresolved calls and callbacks remain boundaries.",
                "storage_estimate_bytes": sum((n.get("attributes") or {}).get("size_bytes", 0) for n in storage if isinstance((n.get("attributes") or {}).get("size_bytes"), int)),
                "storage_unknown_symbols": sum((n.get("attributes") or {}).get("size_bytes") is None for n in storage),
                "storage_boundary": "Sum of symbol type sizes, not target RAM, stack frame or simultaneous lifetime",
                "architecture": {"status": "checked" if rules else "needs_rules", "findings": findings},
                "boundaries": ["Multiple writers are review candidates, not proven races.", "No callers does not prove dead code; configure roots and account for callbacks.",
                               "Static paths are possible relationships, not observed execution or fault causes."]}

    def query(self, *, mode="connections", selected=(), depth=3, limit=100, rules=()):
        if mode not in MODES: raise ValueError("Unknown analysis mode")
        if not 1 <= depth <= 12 or not 1 <= limit <= 300: raise ValueError("Depth 1–12 and node limit 1–300 required")
        selected = sorted(set(selected))
        if len(selected) > 20 or any(k not in self.nodes for k in selected): raise ValueError("Select at most 20 known nodes")
        if len(selected) > limit: raise ValueError("Node limit must include every selection")
        metrics = self.analytics(rules)
        notes, paths, visited, frontier = [], [], {}, set()
        nodes, edges = list(self.nodes.values()), self.semantic
        if mode in {"files", "modules"}: nodes, edges = self.grouped(mode)
        elif mode == "interfaces":
            edges = [e for e in self.semantic if self.nodes[e["source"]].get("module") != self.nodes[e["target"]].get("module")
                     or (self.nodes[e["source"]].get("location") or {}).get("path") != (self.nodes[e["target"]].get("location") or {}).get("path")]
        elif mode in {"calls", "reachability", "call_depth"}:
            edges = self.calls
            nodes = [self.nodes[k] for k in sorted(self.functions)]
        elif mode == "signals":
            edges = [{**e, "source": e["target"], "target": e["source"], "direction_reason": "value to reader", "display_relation": "is read by"} if e["kind"] == "reads" else e
                     for e in self.semantic if e["kind"] in {"reads", "writes", "resolves_to"}]
            endpoints = {v for e in edges for v in (e["source"], e["target"])}
            nodes = [n for n in nodes if n["id"] in endpoints]
        elif mode in {"upstream", "downstream"}: edges = self.influence_edges()
        elif mode in {"cfg", "dfd", "skeleton"}:
            kinds = {"control_flow"} if mode == "cfg" else {"def_use", "memory_flow"}
            owned = {k for k,n in self.nodes.items() if n.get("attributes", {}).get("function") in selected}
            if mode == "skeleton":
                owned.update(selected)
                edges = [e for e in self.edges if e["kind"] == "contains" and e["source"] in owned and e["target"] in owned
                         and self.nodes[e["target"]]["kind"] in {"basic_block", "ir_value"}]
            else: edges = [e for e in self.edges if e["kind"] in kinds and (not selected or e["source"] in owned or e["source"] in selected or e["target"] in selected)]
            nodes = [n for n in nodes if n["id"] in {v for e in edges for v in (e["source"], e["target"])} or
                     n["id"] in owned and n["kind"] == "basic_block" and mode == "cfg"]
            if not nodes: notes.append("No compiler flow evidence for this selection. Generate or attach a matching flow bundle; structural access is not data flow.")
        elif mode == "cycles":
            recursive = {k for group in self.recursive for k in group}
            edges = [e for e in self.calls if e["source"] in recursive and e["target"] in recursive]
            nodes = [self.nodes[k] for k in sorted(recursive)]
            notes.append("Call recursion is distinct from CFG loops. File dependency cycles are listed in the analytics panel.")
        elif mode == "clones":
            ids = {k for g in metrics["clone_groups"] for k in g}
            nodes = [self.nodes[k] for k in sorted(ids)]
            edges = [{"id": "clone:" + identity(a,b), "source": a, "target": b, "kind": "same_tokens", "resolution": "derived"}
                     for g in metrics["clone_groups"] for a,b in zip(g,g[1:])]
        elif mode == "metrics":
            nodes = [self.nodes[r["id"]] for r in metrics["functions"]]; edges = self.calls
        elif mode == "calibrations":
            candidates = {k for k,n in self.nodes.items() if n["kind"] in {"global_variable", "macro"}}
            if selected: candidates &= set(selected)
            edges = [e for e in self.semantic if e["target"] in candidates]
            nodes = [self.nodes[k] for k in sorted(candidates)] + [self.nodes[e["source"]] for e in edges]
            notes.append("Storage and macros are candidates, not verified calibrations. Inspect source initializers, units and table bounds.")

        traversed_modes = {"connections", "upstream", "downstream", "calls", "call_depth", "signals", "reachability", "interfaces"}
        if mode in traversed_modes and selected:
            if mode == "reachability" and any(k not in self.functions for k in selected): raise ValueError("Reachability roots must be functions")
            adj = self.adj(edges, undirected=mode in {"connections", "interfaces"})
            if mode == "upstream": adj = self.adj([{**e,"source":e["target"],"target":e["source"]} for e in edges])
            visited = {k: 0 for k in selected}; pending = deque(selected)
            while pending:
                current = pending.popleft()
                for target in sorted(adj[current]):
                    if target in visited: continue
                    if visited[current] >= depth or len(visited) >= limit:
                        frontier.add(target); continue
                    visited[target] = visited[current] + 1; pending.append(target)
            included = set(visited)
            if mode == "connections" and len(selected) > 1:
                included = set(selected)
                for i, start in enumerate(selected):
                    parents = {start: None}; queue = deque([(start, 0)])
                    while queue:
                        current, distance = queue.popleft()
                        if distance == depth: continue
                        for target in sorted(adj[current]):
                            if target not in parents and target in visited:
                                parents[target] = current; queue.append((target, distance+1))
                    for end in selected[i+1:]:
                        if end not in parents:
                            paths.append({"from":start,"to":end,"status":"not_found_within_scope_and_budget","nodes":[]});continue
                        path=[end]
                        while path[-1] != start: path.append(parents[path[-1]])
                        path.reverse();included.update(path)
                        paths.append({"from":start,"to":end,"status":"association_path","nodes":path})
                notes.append("Connection search can traverse either direction. Arrows retain relationship meaning; association does not prove causality.")
            nodes = [self.nodes[k] for k in sorted(included)]
            if mode == "reachability":
                notes.append(f"{len(self.functions - set(visited))} functions not reached within this scope/budget; not a dead-code verdict.")
        elif mode in {"upstream", "downstream", "reachability"}:
            nodes, edges = [], []; notes.append("Select a starting symbol (functions for entry-point reachability).")
        elif mode == "connections" and not selected:
            nodes = [self.nodes[r["id"]] for r in metrics["functions"]]
            notes.append("Select two or more items to show connecting paths, or one to see its neighborhood.")
        if mode == "interfaces":
            endpoints = {v for e in edges for v in (e["source"],e["target"])}
            nodes = [n for n in nodes if n["id"] in endpoints]
        unique = {n["id"]: n for n in nodes}
        ordered = sorted(unique, key=lambda k:(k not in selected, visited.get(k,0), unique[k].get("name",""),k))
        if mode in {"cfg", "dfd"}:
            # Preserve a connected neighborhood when the full IR exceeds the display budget.
            adj = self.adj(edges, undirected=True)
            rank, seen = [], set()
            roots = sorted(unique, key=lambda k:(unique[k].get("attributes", {}).get("function", ""),
                           unique[k].get("attributes", {}).get("order", 0), k))
            for root in roots:
                if root in seen: continue
                pending = deque([root]); seen.add(root)
                while pending:
                    key = pending.popleft(); rank.append(key)
                    for other in sorted(adj[key]):
                        if other in unique and other not in seen: seen.add(other); pending.append(other)
            ordered = rank
        displayed = set(ordered[:limit]); omitted = len(ordered)-len(displayed)
        result_edges = [e for e in edges if e["source"] in displayed and e["target"] in displayed]
        return {"mode":mode,"title":MODES[mode],"nodes":[unique[k] for k in ordered[:limit]],
                "edges":result_edges,"selected":selected,"paths":paths,"analytics":metrics,
                "coverage":{"displayed":len(displayed),"eligible":len(unique),"omitted":omitted,
                            "frontier":sorted(frontier-set(visited)),"depth":depth,"limit":limit,
                            "complete_within_scope":not omitted and not (frontier-set(visited))},
                "notes":notes + ["Evidence describes possible static relationships. It does not prove a runtime cause, race, timing or safety result."]}
