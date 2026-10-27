from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from code_intelligence.extraction import extract_translation_unit
from code_intelligence.models import EdgeKind, NodeKind, RelationResolution


@dataclass
class FakeKind:
    name: str


@dataclass
class FakeFile:
    path: Path

    def __str__(self) -> str:
        return str(self.path)


@dataclass
class FakePosition:
    file: FakeFile | None = None
    line: int = 0
    column: int = 0


@dataclass
class FakeExtent:
    end: FakePosition


@dataclass
class FakeType:
    spelling: str


class FakeCursor:
    def __init__(
        self,
        kind: str,
        *,
        path: Path | None = None,
        spelling: str = "",
        displayname: str = "",
        usr: str = "",
        definition: bool = False,
        line: int = 1,
        children: list["FakeCursor"] | None = None,
        referenced: "FakeCursor | None" = None,
        included_file: Path | None = None,
        semantic_parent_kind: str | None = None,
        type_spelling: str = "",
    ) -> None:
        self.kind = FakeKind(kind)
        self.spelling = spelling
        self.displayname = displayname
        self._usr = usr
        self._definition = definition
        self._children = children or []
        self.referenced = referenced
        self._included_file = included_file
        file_value = FakeFile(path) if path else None
        self.location = FakePosition(file_value, line, 2)
        self.extent = FakeExtent(FakePosition(file_value, line + 1, 1))
        self.semantic_parent = (
            FakeCursor(semantic_parent_kind) if semantic_parent_kind else None
        )
        self.type = FakeType(type_spelling)
        self.result_type = FakeType(type_spelling)

    def get_children(self):
        return iter(self._children)

    def get_usr(self) -> str:
        return self._usr

    def is_definition(self) -> bool:
        return self._definition

    def get_included_file(self):
        return FakeFile(self._included_file) if self._included_file else None


def test_ast_extracts_stable_nodes_and_relationships(tmp_path: Path):
    source = tmp_path / "src" / "control.c"
    header = tmp_path / "include" / "control.h"
    callee = FakeCursor(
        "FUNCTION_DECL",
        path=source,
        spelling="read_sensor",
        usr="c:@F@read_sensor",
        definition=True,
        line=3,
        type_spelling="int",
    )
    caller = FakeCursor(
        "FUNCTION_DECL",
        path=source,
        spelling="control_step",
        usr="c:@F@control_step",
        definition=True,
        line=8,
        type_spelling="void",
        children=[
            FakeCursor(
                "CALL_EXPR",
                path=source,
                spelling="read_sensor",
                referenced=callee,
                line=10,
            ),
            FakeCursor(
                "CALL_EXPR",
                path=source,
                spelling="missing_hook",
                referenced=None,
                line=11,
            ),
        ],
    )
    root = FakeCursor(
        "TRANSLATION_UNIT",
        children=[
            FakeCursor(
                "INCLUSION_DIRECTIVE",
                path=source,
                displayname="control.h",
                included_file=header,
                line=1,
            ),
            FakeCursor(
                "VAR_DECL",
                path=source,
                spelling="system_state",
                definition=True,
                semantic_parent_kind="TRANSLATION_UNIT",
                type_spelling="uint8_t",
                line=2,
            ),
            callee,
            caller,
        ],
    )

    fragment = extract_translation_unit(
        root,
        repo_root=tmp_path,
        translation_unit=source,
    )

    nodes = {node.id: node for node in fragment.nodes}
    kinds = {node.kind for node in nodes.values()}
    assert NodeKind.FILE in kinds
    assert NodeKind.FUNCTION in kinds
    assert NodeKind.GLOBAL_VARIABLE in kinds
    assert "function:usr:c:@F@control_step" in nodes
    assert nodes["function:usr:c:@F@control_step"].location.path == "src/control.c"

    edges_by_kind = {
        kind: [edge for edge in fragment.edges if edge.kind == kind]
        for kind in EdgeKind
    }
    assert len(edges_by_kind[EdgeKind.INCLUDES]) == 1
    assert len(edges_by_kind[EdgeKind.CALLS]) == 2
    assert len(edges_by_kind[EdgeKind.DEFINES]) == 3
    assert len(edges_by_kind[EdgeKind.CONTAINS]) == 3
    assert {edge.resolution for edge in edges_by_kind[EdgeKind.CALLS]} == {
        RelationResolution.COMPILER_DERIVED,
        RelationResolution.UNRESOLVED,
    }
    assert all(
        edge.source in nodes and edge.target in nodes for edge in fragment.edges
    )


def test_ast_ignores_symbols_owned_outside_repository(tmp_path: Path):
    source = tmp_path / "src" / "control.c"
    external = tmp_path.parent / "sdk" / "vendor.h"
    root = FakeCursor(
        "TRANSLATION_UNIT",
        children=[
            FakeCursor(
                "FUNCTION_DECL",
                path=external,
                spelling="vendor_internal",
                usr="c:@F@vendor_internal",
                definition=True,
            )
        ],
    )

    fragment = extract_translation_unit(
        root,
        repo_root=tmp_path,
        translation_unit=source,
    )

    assert [node.kind for node in fragment.nodes] == [NodeKind.FILE]
    assert fragment.edges == []


def test_fallback_identity_is_deterministic(tmp_path: Path):
    source = tmp_path / "src" / "control.c"
    root = FakeCursor(
        "TRANSLATION_UNIT",
        children=[
            FakeCursor(
                "MACRO_DEFINITION",
                path=source,
                spelling="CONTROL_LIMIT",
                line=2,
            )
        ],
    )

    first = extract_translation_unit(root, repo_root=tmp_path, translation_unit=source)
    second = extract_translation_unit(root, repo_root=tmp_path, translation_unit=source)

    assert first.to_dict() == second.to_dict()
    macro = next(node for node in first.nodes if node.kind == NodeKind.MACRO)
    assert macro.id == "macro:fallback:src/control.c:CONTROL_LIMIT"
