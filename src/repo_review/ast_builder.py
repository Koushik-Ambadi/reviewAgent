from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from clang.cindex import Config, CursorKind, CompilationDatabase, Index, TranslationUnit


def configure_libclang(libclang_path: str | None) -> None:
    if not libclang_path:
        return

    try:
        if Path(libclang_path).exists():
            Config.set_library_file(libclang_path)
    except Exception:
        pass


def _sanitize_args(args: list[str], sanitize_rules: dict[str, Any]) -> list[str]:
    cleaned: list[str] = []
    skip_next = False
    consume_next = set(sanitize_rules.get("consume_next", []))
    skip_exact = set(sanitize_rules.get("skip_exact", []))
    skip_prefixes = tuple(sanitize_rules.get("skip_prefixes", []))

    for arg in args:
        if skip_next:
            skip_next = False
            continue

        if arg in consume_next:
            skip_next = True
            continue

        if arg in skip_exact:
            continue

        if skip_prefixes and arg.startswith(skip_prefixes):
            continue

        cleaned.append(arg)

    force_language = sanitize_rules.get("force_language", "c")
    language_standard = sanitize_rules.get("language_standard", "c99")

    cleaned.extend(["-x", force_language, f"-std={language_standard}"])
    return cleaned


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_user_macro(node, repo_root: Path) -> bool:
    if not node.location.file:
        return False

    macro_file = Path(str(node.location.file)).resolve()
    if not _is_within_root(macro_file, repo_root):
        return False

    name = node.spelling
    if name.startswith("__") or name.startswith("_"):
        return False

    return True


def _walk_ast(node, result: dict[str, Any], source_file: Path, repo_root: Path) -> None:
    if node.location.file:
        current_file = Path(str(node.location.file)).resolve()
        if not _is_within_root(current_file, repo_root):
            return

    if node.kind == CursorKind.INCLUSION_DIRECTIVE:
        result["includes"].append(node.displayname)
    elif node.kind == CursorKind.FUNCTION_DECL:
        function_data = {
            "name": node.spelling,
            "return_type": node.result_type.spelling,
            "line": node.location.line,
            "is_definition": node.is_definition(),
            "storage_class": str(node.storage_class),
        }
        if node.is_definition():
            result["functions_defined"].append(function_data)
        else:
            result["functions_declared"].append(function_data)
    elif node.kind == CursorKind.VAR_DECL:
        parent = node.semantic_parent.kind
        tokens = [tok.spelling for tok in node.get_tokens()]
        raw_declaration = " ".join(tokens)
        full_decl = raw_declaration

        try:
            with open(source_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            line_text = lines[node.location.line - 1].strip()
            m = re.search(rf"\b{re.escape(node.spelling)}((?:\s*\[[^\]]*\])*)", line_text)
            if m:
                suffix = m.group(1) or ""
                full_decl = raw_declaration + suffix
        except Exception:
            pass

        array_suffixes = re.findall(r"\[[^\]]*\]", full_decl)
        var_data = {
            "name": node.spelling,
            "type": node.type.spelling,
            "raw_declaration": full_decl,
            "array_suffixes": array_suffixes,
            "line": node.location.line,
            "storage_class": str(node.storage_class),
        }

        if parent == CursorKind.TRANSLATION_UNIT:
            result["globals"].append(var_data)
        else:
            result["locals"].append(var_data)
    elif node.kind == CursorKind.PARM_DECL:
        result["parameters"].append(
            {
                "name": node.spelling,
                "type": node.type.spelling,
                "line": node.location.line,
            }
        )
    elif node.kind == CursorKind.STRUCT_DECL and node.spelling:
        struct_data = {"name": node.spelling, "line": node.location.line, "fields": []}
        for child in node.get_children():
            if child.kind == CursorKind.FIELD_DECL:
                struct_data["fields"].append(
                    {
                        "name": child.spelling,
                        "type": child.type.spelling,
                        "line": child.location.line,
                    }
                )
        result["structs"].append(struct_data)
    elif node.kind == CursorKind.ENUM_DECL and node.spelling:
        enum_data = {"name": node.spelling, "line": node.location.line, "constants": []}
        for child in node.get_children():
            if child.kind == CursorKind.ENUM_CONSTANT_DECL:
                enum_data["constants"].append({"name": child.spelling, "line": child.location.line})
        result["enums"].append(enum_data)
    elif node.kind == CursorKind.TYPEDEF_DECL:
        result["typedefs"].append(
            {
                "name": node.spelling,
                "type": node.type.spelling,
                "line": node.location.line,
            }
        )
    elif node.kind == CursorKind.MACRO_DEFINITION and _is_user_macro(node, repo_root):
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
                    tok.kind.name == "IDENTIFIER" or tok.spelling == "," for tok in param_tokens
                )
                macro_type = "function" if is_param_list else "value"
        elif len(tokens) > 1:
            macro_type = "value"

        result["macros"].append(
            {
                "name": node.spelling,
                "line": node.location.line,
                "type": macro_type,
                "replacement": replacement,
            }
        )

    for child in node.get_children():
        _walk_ast(child, result, source_file, repo_root)


def _extract_symbols(
    file_path: Path,
    repo_root: Path,
    index: Index,
    compdb: CompilationDatabase,
    ast_config: dict[str, Any],
) -> dict[str, Any] | None:
    commands = compdb.getCompileCommands(str(file_path))
    if not commands:
        return None

    command = list(commands)[0]
    raw_args = list(command.arguments)[1:]
    if raw_args:
        try:
            if Path(raw_args[-1]).resolve() == file_path:
                raw_args = raw_args[:-1]
        except Exception:
            pass
    args = _sanitize_args(raw_args, ast_config.get("sanitize", {}))
    parse_options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    try:
        tu = index.parse(str(file_path), args=args, options=parse_options)
    except Exception:
        return None

    result = {
        "file": str(file_path),
        "includes": [],
        "functions_defined": [],
        "functions_declared": [],
        "globals": [],
        "locals": [],
        "parameters": [],
        "structs": [],
        "enums": [],
        "typedefs": [],
        "macros": [],
    }

    _walk_ast(tu.cursor, result, file_path, repo_root)
    return result


def build_ast_review_results(source_path: Path | str, config: dict[str, Any]) -> dict[str, Any]:
    source_root = Path(source_path).resolve()
    ast_config = config.get("ast", {})
    libclang_path = ast_config.get("libclang_path")
    configure_libclang(libclang_path)

    compile_db_dir = source_root / ast_config.get("compile_db_dir", "build")
    compile_db_path = compile_db_dir / "compile_commands.json"
    target_folders = [
        (source_root / folder).resolve() for folder in ast_config.get("target_folders", ["src"])
    ]
    target_extensions = set(ast_config.get("target_extensions", [".c", ".h"]))

    output_path = Path(
        source_root / config.get("runtime", {}).get("review_results_filename", "review_results.json")
    )

    artifact = {
        "status": "pending",
        "source_root": str(source_root),
        "compile_db_path": str(compile_db_path),
        "output_path": str(output_path),
        "processed_files": 0,
        "skipped_files": [],
        "results": [],
    }

    if not compile_db_path.exists():
        artifact["status"] = "missing_compile_db"
        artifact["error"] = f"Compile database not found: {compile_db_path}"
        return artifact

    index = Index.create()
    compdb = CompilationDatabase.fromDirectory(str(compile_db_dir))

    with open(compile_db_path, "r", encoding="utf-8") as f:
        compile_data = json.load(f)

    processed_files: set[str] = set()
    all_results: list[dict[str, Any]] = []
    skipped_files: list[dict[str, str]] = []

    for entry in compile_data:
        file_path = Path(entry["file"]).resolve()

        if str(file_path) in processed_files:
            continue

        processed_files.add(str(file_path))

        if not any(_is_within_root(file_path, folder) for folder in target_folders):
            skipped_files.append({"file": str(file_path), "reason": "outside_target_folder"})
            continue

        if file_path.suffix.lower() not in target_extensions:
            skipped_files.append({"file": str(file_path), "reason": "unsupported_extension"})
            continue

        result = _extract_symbols(file_path, source_root, index, compdb, ast_config)
        if result:
            all_results.append(result)
        else:
            skipped_files.append({"file": str(file_path), "reason": "parse_or_compile_error"})

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=True)

    artifact.update(
        {
            "status": "success",
            "processed_files": len(all_results),
            "skipped_files": skipped_files,
            "results": all_results,
            "written": output_path.exists(),
        }
    )
    return artifact
