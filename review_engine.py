import json
from pathlib import Path

from clang.cindex import Config

# ==========================================
# LLVM LIBCLANG
# ==========================================

Config.set_library_file(
    r"C:\Program Files\LLVM\bin\libclang.dll"
)

from clang.cindex import (
    Index,
    CursorKind,
    CompilationDatabase,
    TranslationUnit
)

# ==========================================
# CONFIG
# ==========================================

REPO_ROOT = Path(
    r"C:\Users\koushik\Desktop\review\soc"
).resolve()

COMPILE_DB_DIR = str(REPO_ROOT / "build")

OUTPUT_FILE = "review_results.json"

TARGET_FOLDERS = [
    #(REPO_ROOT / "app").resolve(),
    (REPO_ROOT / "src").resolve()
]

# ==========================================
# INIT
# ==========================================

print("\n====================")
print("REPO_ROOT =", REPO_ROOT)
print("COMPILE_DB_DIR =", COMPILE_DB_DIR)

compile_db_file = Path(COMPILE_DB_DIR) / "compile_commands.json"

print("EXPECTED FILE =", compile_db_file)
print("FILE EXISTS =", compile_db_file.exists())
print("====================\n")

index = Index.create()

compdb = CompilationDatabase.fromDirectory(COMPILE_DB_DIR)

# ==========================================
# ARG SANITIZER (KEEP AS IS)
# ==========================================

def sanitize_args(args):

    cleaned = []
    skip_next = False

    for arg in args:

        if skip_next:
            skip_next = False
            continue

        if arg == "-o":
            skip_next = True
            continue

        if arg in ["-c", "-MD", "-MF"]:
            continue

        cleaned.append(arg)

    cleaned.extend([
        "-x", "c",
        "-std=c99"
    ])

    return cleaned


# ==========================================
# EXTRACTOR
# ==========================================

def extract_symbols(file_path):

    commands = compdb.getCompileCommands(str(file_path))

    if not commands:
        print(f"SKIPPING: no compile command -> {file_path}")
        return None

    command = list(commands)[0]
    raw_args = list(command.arguments)[1:]
    args = sanitize_args(raw_args)

    print("\n================================")
    print(f"PROCESSING: {file_path}")
    print("================================")

    try:
        tu = index.parse(
            str(file_path),
            args=["-x", "c", "-std=c99"],
            options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        )

    except Exception as e:
        print(f"FAILED PARSE: {e}")
        return None

    # ======================================
    # EXPANDED RESULT STRUCTURE
    # ======================================

    result = {

        "file": str(file_path),

        "includes": [],

        "functions_defined": [],
        "functions_declared": [],

        "globals": [],
        "locals": [],              # NEW
        "parameters": [],          # NEW

        "structs": [],             # NEW
        "struct_fields": [],       # NEW

        "enums": [],               # NEW
        "enum_constants": [],      # NEW

        "typedefs": [],            # NEW

        "macros": []
    }

    # diagnostics
    for diag in tu.diagnostics:
        if diag.severity >= 3:
            print(f"DIAG: {diag}")

    walk_ast(tu.cursor, result, str(file_path))

    return result


# ==========================================
# AST WALKER (SAFE EXTENSION)
# ==========================================

def walk_ast(node, result, source_file):

    if node.location.file:

        current_file = str(Path(str(node.location.file)).resolve())

        if current_file != source_file:
            return

    # ======================================
    # INCLUDES
    # ======================================

    if node.kind == CursorKind.INCLUSION_DIRECTIVE:
        result["includes"].append(node.displayname)

    # ======================================
    # FUNCTIONS
    # ======================================

    elif node.kind == CursorKind.FUNCTION_DECL:

        function_data = {
            "name": node.spelling,
            "return_type": node.result_type.spelling,
            "line": node.location.line,
            "is_definition": node.is_definition(),
            "storage_class": str(node.storage_class)
        }

        if node.is_definition():
            result["functions_defined"].append(function_data)
        else:
            result["functions_declared"].append(function_data)

    # ======================================
    # GLOBAL VARIABLES
    # ======================================

    elif node.kind == CursorKind.VAR_DECL:

        parent = node.semantic_parent.kind

        var_data = {
            "name": node.spelling,
            "type": node.type.spelling,
            "line": node.location.line
        }

        if parent == CursorKind.TRANSLATION_UNIT:
            result["globals"].append(var_data)
        else:
            result["locals"].append(var_data)   # NEW

    # ======================================
    # PARAMETERS
    # ======================================

    elif node.kind == CursorKind.PARM_DECL:
        result["parameters"].append({
            "name": node.spelling,
            "type": node.type.spelling,
            "line": node.location.line
        })

    # ======================================
    # STRUCTS
    # ======================================

    elif node.kind == CursorKind.STRUCT_DECL:
        if node.spelling:
            result["structs"].append({
                "name": node.spelling,
                "line": node.location.line
            })

    # ======================================
    # STRUCT FIELDS
    # ======================================

    elif node.kind == CursorKind.FIELD_DECL:
        result["struct_fields"].append({
            "name": node.spelling,
            "type": node.type.spelling,
            "line": node.location.line
        })

    # ======================================
    # ENUMS
    # ======================================

    elif node.kind == CursorKind.ENUM_DECL:
        if node.spelling:
            result["enums"].append({
                "name": node.spelling,
                "line": node.location.line
            })

    elif node.kind == CursorKind.ENUM_CONSTANT_DECL:
        result["enum_constants"].append({
            "name": node.spelling,
            "line": node.location.line
        })

    # ======================================
    # TYPEDEFS
    # ======================================

    elif node.kind == CursorKind.TYPEDEF_DECL:
        result["typedefs"].append({
            "name": node.spelling,
            "type": node.type.spelling,
            "line": node.location.line
        })

    # ======================================
    # MACROS
    # ======================================

    elif node.kind == CursorKind.MACRO_DEFINITION:
        result["macros"].append({
            "name": node.spelling,
            "line": node.location.line
        })

    # ======================================
    # RECURSION
    # ======================================

    for child in node.get_children():
        walk_ast(child, result, source_file)


# ==========================================
# MAIN
# ==========================================

all_results = []

compile_commands_path = REPO_ROOT / "build" / "compile_commands.json"

with open(compile_commands_path, "r") as f:
    compile_data = json.load(f)

processed_files = set()

for entry in compile_data:

    file_path = Path(entry["file"]).resolve()

    if str(file_path) in processed_files:
        continue

    processed_files.add(str(file_path))

    if not any(
        str(file_path).startswith(str(folder))
        for folder in TARGET_FOLDERS
    ):
        continue

    if not (
        str(file_path).endswith(".c")
        or str(file_path).endswith(".h")
    ):
        continue

    result = extract_symbols(file_path)

    if result:
        all_results.append(result)


# ==========================================
# SAVE
# ==========================================

output_path = REPO_ROOT / OUTPUT_FILE

with open(output_path, "w") as f:
    json.dump(all_results, f, indent=2)

print("\n================================")
print("DONE")
print(f"Saved: {output_path}")
print("================================")