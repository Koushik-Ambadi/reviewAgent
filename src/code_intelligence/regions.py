"""Bounded source-region retrieval from the same host compiler configuration."""
from __future__ import annotations

from code_intelligence.compiler import configure_libclang
from code_intelligence.exploration import identity

REGIONS = {"IF_STMT", "FOR_STMT", "WHILE_STMT", "DO_STMT", "SWITCH_STMT", "CASE_STMT",
           "DEFAULT_STMT", "RETURN_STMT", "BREAK_STMT", "CONTINUE_STMT", "CALL_EXPR",
           "BINARY_OPERATOR", "COMPOUND_ASSIGNMENT_OPERATOR", "DECL_STMT", "CONDITIONAL_OPERATOR"}
GUARDS = {"IF_STMT", "FOR_STMT", "WHILE_STMT", "DO_STMT", "SWITCH_STMT", "CASE_STMT", "CONDITIONAL_OPERATOR"}


def source_regions(path, node, manifest):
    from clang import cindex
    configure_libclang()
    tu = cindex.Index.create().parse(str(path), args=[*manifest["effective_arguments"], "-working-directory", manifest["directory"]])
    if any(d.severity >= cindex.Diagnostic.Error for d in tu.diagnostics):
        return {"regions": [], "notes": ["Source-region parsing failed; no approximate structure substituted."]}
    raw = path.read_bytes()
    def snippet(cursor, limit=600):
        return raw[cursor.extent.start.offset:cursor.extent.end.offset].decode("utf-8", errors="replace")[:limit]
    function = next((c for c in tu.cursor.get_children() if c.kind.name == "FUNCTION_DECL" and
                     c.get_usr() == node.get("usr") and c.is_definition() and c.location.file and
                     str(c.location.file).replace("\\", "/").lower() == str(path).replace("\\", "/").lower()), None)
    if function is None: return {"regions": [], "notes": ["Exact function definition not found in this compiler configuration."]}
    regions, suggestions = [], []
    pending = [(c, None, []) for c in reversed(list(function.get_children()))]
    seen = 0
    while pending and seen < 12000 and len(regions) < 500:
        cursor, parent, guards = pending.pop(); seen += 1
        kind = cursor.kind.name
        children = list(cursor.get_children())
        current = parent
        if kind in REGIONS:
            current = "region:" + identity(node["id"], manifest["source_sha256"], cursor.extent.start.offset, cursor.extent.end.offset, kind)
            content = snippet(cursor)
            condition = snippet(children[0], 300) if kind in GUARDS and children else None
            regions.append({"id":current,"kind":kind,"parent":parent,"line":cursor.extent.start.line,
                "end_line":cursor.extent.end.line,"text":content,"guard_context":guards,
                "condition_candidate":condition, "name":cursor.spelling or kind.lower().replace("_", " ")})
            if kind == "BINARY_OPERATOR":
                tokens = [t.spelling for t in cursor.get_tokens()]
                if any(t in {"<", ">", "<=", ">=", "==", "!="} for t in tokens):
                    suggestions.append({"region":current,"expression":content,
                        "suggestion":"Exercise both outcomes, equality and adjacent representable values; confirm types, units, guards and feasible inputs first.",
                        "status":"test_idea_not_executed_or_proven_feasible"})
        next_guards = guards + [current] if kind in GUARDS else guards
        pending.extend((c,current,next_guards) for c in reversed(children))
    return {"regions":regions,"boundary_test_ideas":suggestions,"regions_truncated":bool(pending),
            "notes":["Regions are compiler AST containment, not sequential execution. Guard context names enclosing decisions, not a proven true/false predicate."]}
