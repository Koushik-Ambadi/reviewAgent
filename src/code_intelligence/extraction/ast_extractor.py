from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

from code_intelligence.identity import (
    cursor_usr,
    edge_id,
    node_id,
    normalized_path,
)
from code_intelligence.models import (
    EdgeKind,
    GraphEdge,
    GraphFragment,
    GraphNode,
    NodeKind,
    RelationResolution,
    SourceLocation,
)


_SYMBOL_KINDS = {
    "FUNCTION_DECL": NodeKind.FUNCTION,
    "STRUCT_DECL": NodeKind.STRUCT,
    "ENUM_DECL": NodeKind.ENUM,
    "TYPEDEF_DECL": NodeKind.TYPEDEF,
    "MACRO_DEFINITION": NodeKind.MACRO,
    "PARM_DECL": NodeKind.PARAMETER,
    "FIELD_DECL": NodeKind.FIELD,
    "ENUM_CONSTANT_DECL": NodeKind.ENUM_CONSTANT,
}

_DECISION_KINDS = {
    "IF_STMT",
    "FOR_STMT",
    "WHILE_STMT",
    "DO_STMT",
    "CASE_STMT",
    "CONDITIONAL_OPERATOR",
}

_ASSIGNMENT_OPERATORS = {
    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "<<=",
    ">>=",
    "&=",
    "|=",
    "^=",
}


def _kind_name(cursor: Any) -> str:
    return str(getattr(getattr(cursor, "kind", None), "name", ""))


def _children(cursor: Any) -> Iterable[Any]:
    try:
        return cursor.get_children()
    except AttributeError:
        return ()


def _tokens(cursor: Any) -> tuple[str, ...]:
    try:
        return tuple(str(token.spelling) for token in cursor.get_tokens())
    except (AttributeError, RuntimeError):
        return ()


def _type_attributes(cursor: Any) -> dict[str, Any]:
    cursor_type = getattr(cursor, "type", None)
    attributes: dict[str, Any] = {}
    spelling = getattr(cursor_type, "spelling", None)
    if spelling:
        attributes["type"] = str(spelling)
    try:
        size = int(cursor_type.get_size())
    except (AttributeError, RuntimeError, TypeError, ValueError):
        size = -1
    if size >= 0:
        attributes["size_bytes"] = size
    return attributes


def _function_metrics(cursor: Any) -> dict[str, Any]:
    decisions = 0
    statements = 0
    pending = list(_children(cursor))
    while pending:
        child = pending.pop()
        kind_name = _kind_name(child)
        if kind_name in _DECISION_KINDS:
            decisions += 1
        if kind_name.endswith("_STMT") and kind_name != "COMPOUND_STMT":
            statements += 1
        if kind_name == "BINARY_OPERATOR":
            decisions += sum(token in {"&&", "||"} for token in _tokens(child))
        pending.extend(_children(child))
    tokens = _tokens(cursor)
    attributes: dict[str, Any] = {
        "complexity_method": "ast_cyclomatic_v1",
        "cyclomatic_complexity": 1 + decisions,
        "statement_count": statements,
    }
    if tokens:
        body_tokens = tokens[tokens.index("{") :] if "{" in tokens else tokens
        normalized = "\x1f".join(body_tokens)
        attributes["token_fingerprint_method"] = "clang_tokens_sha256_v1"
        attributes["token_fingerprint"] = hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()
        attributes["token_count"] = len(body_tokens)
    return attributes


def _path_from_file(file_value: Any) -> Path | None:
    if file_value is None:
        return None
    try:
        return Path(str(file_value)).resolve()
    except (OSError, RuntimeError, ValueError):
        return None


def _cursor_path(cursor: Any) -> Path | None:
    location = getattr(cursor, "location", None)
    return _path_from_file(getattr(location, "file", None))


def _location(cursor: Any, path: str) -> SourceLocation:
    location = getattr(cursor, "location", None)
    extent = getattr(cursor, "extent", None)
    end = getattr(extent, "end", None)
    return SourceLocation(
        path=path,
        line=getattr(location, "line", None) or None,
        column=getattr(location, "column", None) or None,
        end_line=getattr(end, "line", None) or None,
        end_column=getattr(end, "column", None) or None,
    )


def _is_definition(cursor: Any) -> bool | None:
    try:
        return bool(cursor.is_definition())
    except (AttributeError, RuntimeError):
        return None


class _FragmentBuilder:
    def __init__(self, repo_root: Path, translation_unit: Path) -> None:
        self.repo_root = repo_root.resolve()
        translation_path, _ = normalized_path(translation_unit, self.repo_root)
        self.fragment = GraphFragment(translation_unit=translation_path)
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}

    def add_node(self, node: GraphNode) -> GraphNode:
        existing = self._nodes.get(node.id)
        if existing is None or (node.is_definition and not existing.is_definition):
            self._nodes[node.id] = node
        return self._nodes[node.id]

    def add_edge(self, edge: GraphEdge) -> None:
        self._edges.setdefault(edge.id, edge)

    def file_node(self, path: Path, *, display_name: str | None = None) -> GraphNode:
        normalized, external = normalized_path(path, self.repo_root)
        node = GraphNode(
            id=node_id(NodeKind.FILE, name=normalized, path=normalized),
            kind=NodeKind.FILE,
            name=display_name or Path(normalized).name,
            location=SourceLocation(path=normalized),
            attributes={"path": normalized, "external": external},
        )
        return self.add_node(node)

    def unresolved_file_node(self, include_name: str) -> GraphNode:
        path = f"<include>/{include_name}"
        return self.add_node(
            GraphNode(
                id=node_id(NodeKind.FILE, name=include_name, path=path),
                kind=NodeKind.FILE,
                name=include_name,
                location=None,
                attributes={"path": include_name, "external": True, "unresolved": True},
            )
        )

    def symbol_node(
        self,
        cursor: Any,
        kind: NodeKind,
        *,
        scope: str | None = None,
    ) -> GraphNode | None:
        name = str(getattr(cursor, "spelling", "") or "")
        path_value = _cursor_path(cursor)
        if not name or path_value is None:
            return None
        path, external = normalized_path(path_value, self.repo_root)
        usr = cursor_usr(cursor)
        attributes: dict[str, Any] = {"external": external}
        if kind == NodeKind.FUNCTION:
            result_type = getattr(
                getattr(cursor, "result_type", None), "spelling", None
            )
            if result_type:
                attributes["return_type"] = str(result_type)
            if _is_definition(cursor):
                attributes.update(_function_metrics(cursor))
        elif kind in {
            NodeKind.GLOBAL_VARIABLE,
            NodeKind.PARAMETER,
            NodeKind.LOCAL_VARIABLE,
            NodeKind.FIELD,
        }:
            attributes.update(_type_attributes(cursor))
        if scope:
            attributes["scope"] = scope

        return self.add_node(
            GraphNode(
                id=node_id(kind, name=name, path=path, usr=usr, scope=scope),
                kind=kind,
                name=name,
                location=_location(cursor, path),
                usr=usr,
                is_definition=_is_definition(cursor),
                attributes=attributes,
            )
        )

    def reference_function(
        self, call_cursor: Any
    ) -> tuple[GraphNode | None, RelationResolution]:
        referenced = getattr(call_cursor, "referenced", None)
        if referenced is not None:
            node = self.symbol_node(referenced, NodeKind.FUNCTION)
            if node is not None:
                if node.attributes.get("external"):
                    return node, RelationResolution.EXTERNAL
                return node, RelationResolution.COMPILER_DERIVED

        name = str(
            getattr(call_cursor, "spelling", "")
            or getattr(call_cursor, "displayname", "")
            or ""
        )
        if not name:
            return None, RelationResolution.UNRESOLVED
        path = f"<unresolved>/{name}"
        return (
            self.add_node(
                GraphNode(
                    id=node_id(NodeKind.FUNCTION, name=name, path=path),
                    kind=NodeKind.FUNCTION,
                    name=name,
                    attributes={"external": False, "unresolved": True},
                )
            ),
            RelationResolution.UNRESOLVED,
        )

    def reference_variable(
        self,
        reference_cursor: Any,
        *,
        scope: str | None,
    ) -> GraphNode | None:
        referenced = getattr(reference_cursor, "referenced", None)
        if referenced is None:
            return None
        kind_name = _kind_name(referenced)
        kind = {
            "PARM_DECL": NodeKind.PARAMETER,
            "FIELD_DECL": NodeKind.FIELD,
            "ENUM_CONSTANT_DECL": NodeKind.ENUM_CONSTANT,
        }.get(kind_name)
        if kind_name == "VAR_DECL":
            parent_kind = _kind_name(getattr(referenced, "semantic_parent", None))
            kind = (
                NodeKind.GLOBAL_VARIABLE
                if parent_kind == "TRANSLATION_UNIT"
                else NodeKind.LOCAL_VARIABLE
            )
        if kind is None:
            return None
        reference_scope = scope if kind in {
            NodeKind.PARAMETER,
            NodeKind.LOCAL_VARIABLE,
        } else None
        semantic_parent = getattr(referenced, "semantic_parent", None)
        parent_kind = _SYMBOL_KINDS.get(_kind_name(semantic_parent))
        if kind in {NodeKind.FIELD, NodeKind.ENUM_CONSTANT} and parent_kind in {
            NodeKind.STRUCT,
            NodeKind.ENUM,
        }:
            parent_node = self.symbol_node(semantic_parent, parent_kind)
            if parent_node is not None:
                reference_scope = parent_node.id
        return self.symbol_node(referenced, kind, scope=reference_scope)

    def finish(self) -> GraphFragment:
        self.fragment.nodes = sorted(
            self._nodes.values(), key=lambda node: (node.kind.value, node.id)
        )
        self.fragment.edges = sorted(
            self._edges.values(), key=lambda edge: (edge.kind.value, edge.id)
        )
        return self.fragment


def _access_kinds(parent: Any | None, child_index: int | None) -> tuple[EdgeKind, ...]:
    parent_kind = _kind_name(parent)
    tokens = _tokens(parent) if parent is not None else ()
    if parent_kind == "BINARY_OPERATOR" and any(
        token in _ASSIGNMENT_OPERATORS for token in tokens
    ):
        if child_index == 0:
            compound = any(
                token != "=" for token in tokens if token in _ASSIGNMENT_OPERATORS
            )
            return (EdgeKind.READS, EdgeKind.WRITES) if compound else (EdgeKind.WRITES,)
        return (EdgeKind.READS,)
    if parent_kind == "UNARY_OPERATOR":
        if any(token in {"++", "--"} for token in tokens):
            return (EdgeKind.READS, EdgeKind.WRITES)
        if "&" in tokens:
            return (EdgeKind.REFERENCES,)
    return (EdgeKind.READS,)


def extract_translation_unit(
    cursor: Any,
    *,
    repo_root: Path,
    translation_unit: Path,
) -> GraphFragment:
    """Extract graph-ready compiler facts without mutating symbol inventory output."""

    builder = _FragmentBuilder(repo_root, translation_unit)
    builder.file_node(translation_unit)

    def visit(
        node: Any,
        current_function_id: str | None = None,
        current_owner_id: str | None = None,
        parent: Any | None = None,
        child_index: int | None = None,
    ) -> None:
        kind_name = _kind_name(node)
        cursor_path = _cursor_path(node)
        if cursor_path is not None:
            _, external = normalized_path(cursor_path, builder.repo_root)
            if external and kind_name not in {"INCLUSION_DIRECTIVE", "CALL_EXPR"}:
                return

        physical_file = builder.file_node(cursor_path) if cursor_path else None

        symbol_kind = _SYMBOL_KINDS.get(kind_name)
        if kind_name == "VAR_DECL":
            parent_kind = _kind_name(getattr(node, "semantic_parent", None))
            symbol_kind = (
                NodeKind.GLOBAL_VARIABLE
                if parent_kind == "TRANSLATION_UNIT"
                else NodeKind.LOCAL_VARIABLE
            )

        next_function_id = current_function_id
        next_owner_id = current_owner_id
        if symbol_kind is not None:
            nested = symbol_kind in {
                NodeKind.PARAMETER,
                NodeKind.LOCAL_VARIABLE,
                NodeKind.FIELD,
                NodeKind.ENUM_CONSTANT,
            }
            owner_id = current_function_id if symbol_kind in {
                NodeKind.PARAMETER,
                NodeKind.LOCAL_VARIABLE,
            } else current_owner_id
            symbol = builder.symbol_node(node, symbol_kind, scope=owner_id)
            if symbol is not None and physical_file is not None and not nested:
                relation_kind = (
                    EdgeKind.DEFINES if symbol.is_definition else EdgeKind.DECLARES
                )
                for edge_kind in (EdgeKind.CONTAINS, relation_kind):
                    builder.add_edge(
                        GraphEdge(
                            id=edge_id(
                                edge_kind,
                                source=physical_file.id,
                                target=symbol.id,
                            ),
                            kind=edge_kind,
                            source=physical_file.id,
                            target=symbol.id,
                            resolution=RelationResolution.COMPILER_DERIVED,
                            location=symbol.location,
                        )
                    )
            if symbol is not None and owner_id is not None and nested:
                relation_kind = {
                    NodeKind.PARAMETER: EdgeKind.PARAMETER_OF,
                    NodeKind.FIELD: EdgeKind.FIELD_OF,
                    NodeKind.ENUM_CONSTANT: EdgeKind.MEMBER_OF,
                }.get(symbol_kind, EdgeKind.CONTAINS)
                builder.add_edge(
                    GraphEdge(
                        id=edge_id(
                            relation_kind,
                            source=owner_id,
                            target=symbol.id,
                        ),
                        kind=relation_kind,
                        source=owner_id,
                        target=symbol.id,
                        resolution=RelationResolution.COMPILER_DERIVED,
                        location=symbol.location,
                    )
                )
                if (
                    symbol_kind == NodeKind.LOCAL_VARIABLE
                    and current_function_id is not None
                    and any(True for _ in _children(node))
                ):
                    builder.add_edge(
                        GraphEdge(
                            id=edge_id(
                                EdgeKind.WRITES,
                                source=current_function_id,
                                target=symbol.id,
                                discriminator=(
                                    f"initializer:{symbol.location.path}:"
                                    f"{symbol.location.line}:{symbol.location.column}"
                                ),
                            ),
                            kind=EdgeKind.WRITES,
                            source=current_function_id,
                            target=symbol.id,
                            resolution=RelationResolution.COMPILER_DERIVED,
                            location=symbol.location,
                            attributes={"context": "initializer"},
                        )
                    )
            if symbol_kind == NodeKind.FUNCTION and symbol is not None:
                next_function_id = symbol.id
                next_owner_id = symbol.id
            elif symbol_kind in {NodeKind.STRUCT, NodeKind.ENUM} and symbol is not None:
                next_owner_id = symbol.id

        if kind_name == "INCLUSION_DIRECTIVE" and physical_file is not None:
            included = None
            try:
                included = node.get_included_file()
            except (AttributeError, RuntimeError):
                pass
            included_path = _path_from_file(included)
            include_name = str(
                getattr(node, "displayname", "")
                or getattr(node, "spelling", "")
                or "unknown"
            )
            if included_path is None:
                target = builder.unresolved_file_node(include_name)
                resolution = RelationResolution.UNRESOLVED
            else:
                target = builder.file_node(included_path, display_name=include_name)
                resolution = (
                    RelationResolution.EXTERNAL
                    if target.attributes.get("external")
                    else RelationResolution.COMPILER_DERIVED
                )
            location_path, _ = normalized_path(cursor_path, builder.repo_root)
            location = _location(node, location_path)
            builder.add_edge(
                GraphEdge(
                    id=edge_id(
                        EdgeKind.INCLUDES,
                        source=physical_file.id,
                        target=target.id,
                        discriminator=str(location.line or ""),
                    ),
                    kind=EdgeKind.INCLUDES,
                    source=physical_file.id,
                    target=target.id,
                    resolution=resolution,
                    location=location,
                    attributes={"include": include_name},
                )
            )

        if kind_name == "CALL_EXPR" and current_function_id is not None:
            target, resolution = builder.reference_function(node)
            if target is not None:
                location_path = builder.fragment.translation_unit
                if cursor_path is not None:
                    location_path, _ = normalized_path(cursor_path, builder.repo_root)
                location = _location(node, location_path)
                builder.add_edge(
                    GraphEdge(
                        id=edge_id(
                            EdgeKind.CALLS,
                            source=current_function_id,
                            target=target.id,
                            discriminator=(
                                f"{location.path}:{location.line}:{location.column}"
                            ),
                        ),
                        kind=EdgeKind.CALLS,
                        source=current_function_id,
                        target=target.id,
                        resolution=resolution,
                        location=location,
                    )
                )

        if kind_name in {"DECL_REF_EXPR", "MEMBER_REF_EXPR"} and current_function_id:
            target = builder.reference_variable(node, scope=current_function_id)
            if target is not None:
                location_path = builder.fragment.translation_unit
                if cursor_path is not None:
                    location_path, _ = normalized_path(cursor_path, builder.repo_root)
                location = _location(node, location_path)
                for access_kind in _access_kinds(parent, child_index):
                    builder.add_edge(
                        GraphEdge(
                            id=edge_id(
                                access_kind,
                                source=current_function_id,
                                target=target.id,
                                discriminator=(
                                    f"{location.path}:{location.line}:"
                                    f"{location.column}"
                                ),
                            ),
                            kind=access_kind,
                            source=current_function_id,
                            target=target.id,
                            resolution=RelationResolution.COMPILER_DERIVED,
                            location=location,
                        )
                    )

        for index, child in enumerate(_children(node)):
            visit(child, next_function_id, next_owner_id, node, index)

    visit(cursor)
    return builder.finish()
