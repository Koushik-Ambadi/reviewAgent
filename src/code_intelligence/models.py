from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class NodeKind(StrEnum):
    FILE = "file"
    FUNCTION = "function"
    STRUCT = "struct"
    ENUM = "enum"
    TYPEDEF = "typedef"
    GLOBAL_VARIABLE = "global_variable"
    PARAMETER = "parameter"
    LOCAL_VARIABLE = "local_variable"
    FIELD = "field"
    ENUM_CONSTANT = "enum_constant"
    MACRO = "macro"
    BASIC_BLOCK = "basic_block"
    INSTRUCTION = "instruction"
    IR_VALUE = "ir_value"


class EdgeKind(StrEnum):
    CONTAINS = "contains"
    CALLS = "calls"
    INCLUDES = "includes"
    DECLARES = "declares"
    DEFINES = "defines"
    DEPENDS_ON = "depends_on"
    PARAMETER_OF = "parameter_of"
    FIELD_OF = "field_of"
    MEMBER_OF = "member_of"
    READS = "reads"
    WRITES = "writes"
    REFERENCES = "references"
    CLONE_OF = "clone_of"
    CONTROL_FLOW = "control_flow"
    DEF_USE = "def_use"
    MEMORY_FLOW = "memory_flow"


class RelationResolution(StrEnum):
    COMPILER_DERIVED = "compiler_derived"
    EXTERNAL = "external"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class SourceLocation:
    path: str
    line: int | None = None
    column: int | None = None
    end_line: int | None = None
    end_column: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GraphNode:
    id: str
    kind: NodeKind
    name: str
    location: SourceLocation | None = None
    usr: str | None = None
    is_definition: bool | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kind"] = self.kind.value
        return payload


@dataclass(frozen=True, slots=True)
class GraphEdge:
    id: str
    kind: EdgeKind
    source: str
    target: str
    resolution: RelationResolution
    location: SourceLocation | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kind"] = self.kind.value
        payload["resolution"] = self.resolution.value
        return payload


@dataclass(slots=True)
class GraphFragment:
    translation_unit: str
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "translation_unit": self.translation_unit,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "diagnostics": list(self.diagnostics),
        }
