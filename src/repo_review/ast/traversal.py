from __future__ import annotations

from pathlib import Path
from typing import Any

from clang.cindex import CursorKind

from repo_review.ast.extractors import (
    extract_enum,
    extract_function,
    extract_macro,
    extract_parameter,
    extract_struct,
    extract_typedef,
    extract_variable,
    is_user_macro,
    is_within_root,
)


def walk_ast(
    node,
    result: dict[str, Any],
    source_file: Path,
    repo_root: Path,
    target_folders: list[Path],
) -> None:

    if node.location.file:
        current_file = Path(str(node.location.file)).resolve()

        if not is_within_root(current_file, repo_root):
            return

    if node.kind == CursorKind.INCLUSION_DIRECTIVE:
        result["includes"].append(node.displayname)

    elif node.kind == CursorKind.FUNCTION_DECL:
        function_data = extract_function(node)

        if node.is_definition():
            result["functions_defined"].append(function_data)
        else:
            result["functions_declared"].append(function_data)

    elif node.kind == CursorKind.VAR_DECL:
        parent = node.semantic_parent.kind

        var_data = extract_variable(node, source_file)

        if parent == CursorKind.TRANSLATION_UNIT:
            result["globals"].append(var_data)
        else:
            result["locals"].append(var_data)

    elif node.kind == CursorKind.PARM_DECL:
        result["parameters"].append(extract_parameter(node))

    elif node.kind == CursorKind.STRUCT_DECL and node.spelling:
        result["structs"].append(extract_struct(node))

    elif node.kind == CursorKind.ENUM_DECL and node.spelling:
        result["enums"].append(extract_enum(node))

    elif node.kind == CursorKind.TYPEDEF_DECL:
        result["typedefs"].append(extract_typedef(node))

    elif node.kind == CursorKind.MACRO_DEFINITION:
        if not node.location.file:
            return

        macro_file = Path(str(node.location.file)).resolve()

        # ONLY this rule
        if not any(is_within_root(macro_file, folder) for folder in target_folders):
            return

        result["macros"].append(extract_macro(node))

    for child in node.get_children():
        walk_ast(
            child,
            result,
            source_file,
            repo_root,
            target_folders,
        )