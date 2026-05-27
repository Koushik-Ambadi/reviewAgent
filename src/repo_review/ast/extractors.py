from __future__ import annotations
# src/repo_review/ast/extractors.py

import re
from pathlib import Path

from clang.cindex import CursorKind


def is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def is_user_macro(node, repo_root: Path) -> bool:
    if not node.location.file:
        return False

    macro_file = Path(str(node.location.file)).resolve()

    if not is_within_root(macro_file, repo_root):
        return False

    name = node.spelling

    if name.startswith("__") or name.startswith("_"):
        return False

    return True


def extract_function(node):
    return {
        "name": node.spelling,
        "return_type": node.result_type.spelling,
        "line": node.location.line,
        "is_definition": node.is_definition(),
        "storage_class": str(node.storage_class),
    }


def extract_variable(node, source_file: Path):
    tokens = [tok.spelling for tok in node.get_tokens()]
    raw_declaration = " ".join(tokens)

    full_decl = raw_declaration

    try:
        with open(source_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        line_text = lines[node.location.line - 1].strip()

        m = re.search(
            rf"\b{re.escape(node.spelling)}((?:\s*\[[^\]]*\])*)",
            line_text,
        )

        if m:
            suffix = m.group(1) or ""
            full_decl = raw_declaration + suffix

    except Exception:
        pass

    array_suffixes = re.findall(r"\[[^\]]*\]", full_decl)

    return {
        "name": node.spelling,
        "type": node.type.spelling,
        "raw_declaration": full_decl,
        "array_suffixes": array_suffixes,
        "line": node.location.line,
        "storage_class": str(node.storage_class),
    }


def extract_parameter(node):
    return {
        "name": node.spelling,
        "type": node.type.spelling,
        "line": node.location.line,
    }


def extract_struct(node):
    struct_data = {
        "name": node.spelling,
        "line": node.location.line,
        "fields": [],
    }

    for child in node.get_children():
        if child.kind == CursorKind.FIELD_DECL:
            struct_data["fields"].append(
                {
                    "name": child.spelling,
                    "type": child.type.spelling,
                    "line": child.location.line,
                }
            )

    return struct_data


def extract_enum(node):
    enum_data = {
        "name": node.spelling,
        "line": node.location.line,
        "constants": [],
    }

    for child in node.get_children():
        if child.kind == CursorKind.ENUM_CONSTANT_DECL:
            enum_data["constants"].append(
                {
                    "name": child.spelling,
                    "line": child.location.line,
                }
            )

    return enum_data


def extract_typedef(node):
    return {
        "name": node.spelling,
        "type": node.type.spelling,
        "line": node.location.line,
    }


def extract_macro(node):
    tokens = list(node.get_tokens())

    replacement = ""

    if len(tokens) > 1:
        replacement = " ".join(tok.spelling for tok in tokens[1:])

    macro_type = "conditional"

    if len(tokens) >= 4 and tokens[1].spelling == "(":
        close_idx = None

        for i in range(2, len(tokens)):
            if tokens[i].spelling == ")":
                close_idx = i
                break

        if close_idx is not None:
            param_tokens = tokens[2:close_idx]

            is_param_list = all(
                tok.kind.name == "IDENTIFIER" or tok.spelling == ","
                for tok in param_tokens
            )

            macro_type = "function" if is_param_list else "value"

    elif len(tokens) > 1:
        macro_type = "value"

    return {
        "name": node.spelling,
        "line": node.location.line,
        "type": macro_type,
        "replacement": replacement,
    }