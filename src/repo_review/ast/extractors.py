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

    storage_class = (
        str(node.storage_class)
        .replace(
            "StorageClass.",
            "",
        )
        .lower()
    )

    parameters = []

    for child in node.get_children():

        if (
            child.kind
            == CursorKind.PARM_DECL
        ):

            parameters.append(
                {
                    "name":
                        child.spelling,

                    "type":
                        child.type.spelling,
                }
            )

    return {

        "name":
            node.spelling,

        "return_type":
            node.result_type.spelling,

        "line":
            node.location.line,

        "end_line":
            node.extent.end.line,

        "is_definition":
            node.is_definition(),

        "storage_class":
            storage_class,

        "parameter_count":
            len(parameters),

        "parameters":
            parameters,
    }


def extract_variable(node, source_file: Path):

    tokens = [
        tok.spelling
        for tok in node.get_tokens()
    ]

    raw_declaration = " ".join(tokens)

    full_decl = raw_declaration

    try:

        with open(
            source_file,
            "r",
            encoding="utf-8",
        ) as f:

            lines = f.readlines()

        line_text = (
            lines[node.location.line - 1]
            .strip()
        )

        m = re.search(
            rf"\b{re.escape(node.spelling)}((?:\s*\[[^\]]*\])*)",
            line_text,
        )

        if m:

            suffix = m.group(1) or ""

            full_decl = (
                raw_declaration + suffix
            )

    except Exception:
        pass

    #
    # Array extraction
    #

    array_suffixes = re.findall(
        r"\[[^\]]*\]",
        full_decl,
    )

    #
    # Canonical type
    #

    canonical_type = (
        node.type
        .get_canonical()
        .spelling
    )

    #
    # Pointer analysis
    #

    pointer_depth = 0

    clang_type = node.type

    while (
        clang_type.kind.spelling
        == "POINTER"
    ):

        pointer_depth += 1

        clang_type = (
            clang_type.get_pointee()
        )

    is_pointer = (
        pointer_depth > 0
    )

    #
    # Qualifiers
    #


    is_const = (
        node.type
        .is_const_qualified()
    )

    is_volatile = (
        node.type
        .is_volatile_qualified()
    )

    #
    # Type metadata
    #

    canonical_type = (
        node.type
        .get_canonical()
        .spelling
    )

    type_kind = (
        node.type.kind.spelling
    )

    #
    # Pointer analysis
    #

    pointer_depth = 0

    clang_type = node.type

    while (
        clang_type.kind.spelling
        == "POINTER"
    ):

        pointer_depth += 1

        clang_type = (
            clang_type.get_pointee()
        )

    is_pointer = (
        pointer_depth > 0
    )

    #
    # Qualifiers
    #

    is_const = (
        node.type
        .is_const_qualified()
    )

    is_volatile = (
        node.type
        .is_volatile_qualified()
    )

    #
    # Arrays
    #

    is_array = bool(
        array_suffixes
    )

    #
    # Normalized storage class
    #

    storage_class = (
        str(node.storage_class)
        .replace(
            "StorageClass.",
            "",
        )
        .lower()
    )



    #
    # Arrays
    #

    is_array = bool(
        array_suffixes
    )

    return {

        "name":
            node.spelling,

        "type":
            node.type.spelling,

        "canonical_type":
            canonical_type,

        "type_kind":
            type_kind,

        "raw_declaration":
            full_decl,

        "array_suffixes":
            array_suffixes,

        "is_array":
            is_array,

        "pointer_depth":
            pointer_depth,

        "is_pointer":
            is_pointer,

        "is_const":
            is_const,

        "is_volatile":
            is_volatile,

        "line":
            node.location.line,

        "storage_class":
            storage_class,
    }

def extract_parameter(node):
    return {
        "name": node.spelling,
        "type": node.type.spelling,
        "line": node.location.line,
    }


def extract_struct(node):

    struct_data = {

        "name":
            node.spelling,

        "line":
            node.location.line,

        "fields": [],
    }

    for child in node.get_children():

        if (
            child.kind
            == CursorKind.FIELD_DECL
        ):

            canonical_type = (
                child.type
                .get_canonical()
                .spelling
            )

            type_kind = (
                child.type.kind.spelling
            )

            pointer_depth = 0

            clang_type = child.type

            while (
                clang_type.kind.spelling
                == "POINTER"
            ):

                pointer_depth += 1

                clang_type = (
                    clang_type.get_pointee()
                )

            is_pointer = (
                pointer_depth > 0
            )

            is_const = (
                child.type
                .is_const_qualified()
            )

            is_volatile = (
                child.type
                .is_volatile_qualified()
            )

            struct_data["fields"].append(
                {

                    "name":
                        child.spelling,

                    "type":
                        child.type.spelling,

                    "canonical_type":
                        canonical_type,

                    "type_kind":
                        type_kind,

                    "pointer_depth":
                        pointer_depth,

                    "is_pointer":
                        is_pointer,

                    "is_const":
                        is_const,

                    "is_volatile":
                        is_volatile,

                    "line":
                        child.location.line,
                }
            )

    return struct_data



def extract_enum(node):

    enum_data = {

        "name":
            node.spelling,

        "line":
            node.location.line,

        "underlying_type":
            node.enum_type.spelling
            if node.enum_type
            else "",

        "constants": [],
    }

    current_value = 0

    for child in node.get_children():

        if (
            child.kind
            == CursorKind.ENUM_CONSTANT_DECL
        ):

            try:
                value = child.enum_value
                current_value = value

            except Exception:
                value = current_value

            enum_data["constants"].append(
                {

                    "name":
                        child.spelling,

                    "value":
                        value,

                    "line":
                        child.location.line,
                }
            )

            current_value += 1

    return enum_data



def extract_typedef(node):

    underlying_type = ""

    try:

        underlying_type = (
            node
            .underlying_typedef_type
            .spelling
        )

    except Exception:
        pass

    canonical_type = (
        node.type
        .get_canonical()
        .spelling
    )

    type_kind = (
        node.type.kind.spelling
    )

    return {

        "name":
            node.spelling,

        "type":
            node.type.spelling,

        "underlying_type":
            underlying_type,

        "canonical_type":
            canonical_type,

        "type_kind":
            type_kind,

        "line":
            node.location.line,
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

