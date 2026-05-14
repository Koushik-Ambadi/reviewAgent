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

# compile_commands.json location
COMPILE_DB_DIR = str(
    REPO_ROOT / "build"
)

OUTPUT_FILE = "review_results.json"

# only scan these folders
TARGET_FOLDERS = [

    (REPO_ROOT / "app").resolve(),
    (REPO_ROOT / "src").resolve()
]

# ==========================================
# INIT
# ==========================================

print("\n====================")
print("REPO_ROOT =", REPO_ROOT)
print("COMPILE_DB_DIR =", COMPILE_DB_DIR)

compile_db_file = (
    Path(COMPILE_DB_DIR)
    / "compile_commands.json"
)

print("EXPECTED FILE =", compile_db_file)
print("FILE EXISTS =", compile_db_file.exists())
print("====================\n")

index = Index.create()

compdb = CompilationDatabase.fromDirectory(
    COMPILE_DB_DIR
)

# ==========================================
# ARG SANITIZER
# ==========================================

def sanitize_args(args):

    cleaned = []
    skip_next = False

    for arg in args:

        if skip_next:
            skip_next = False
            continue

        # skip output file handling
        if arg == "-o":
            skip_next = True
            continue

        # remove only build artifact flags
        if arg in ["-c", "-MD", "-MF"]:
            continue

        cleaned.append(arg)

    # safe mode only (does NOT break includes)
    cleaned.extend([
        "-x", "c",
        "-std=c99"
    ])

    return cleaned


"""
def sanitize_args(args):

    cleaned = []
    skip_next = False

    blocked_prefixes = (
        "-Xclang",
        "--misra",
        "--diag",
        "-fms-",
        "-Xassembler",
        "-W",
        "-O",
        "-g",
        "-DMCAL",
        "-DUSING_OS",
        "-D_DLL",
        "-D_MT"
    )

    blocked_exact = {
        "-c",
        "-o",
        "-MD",
        "-MF",
        "--dependent-lib=msvcrtd"
    }

    for arg in args:

        if skip_next:
            skip_next = False
            continue

        if arg in blocked_exact:
            continue

        if arg.startswith("-o"):
            skip_next = True
            continue

        if any(arg.startswith(p) for p in blocked_prefixes):
            continue

        cleaned.append(arg)

    # FORCE SAFE MODE FOR LIBCLANG
    cleaned.extend([
        "-x",
        "c",
        "-std=c99",
        "-D__clang__"
    ])

    return cleaned
"""


# ==========================================
# EXTRACTOR
# ==========================================

def extract_symbols(file_path):

    commands = compdb.getCompileCommands(
        str(file_path)
    )

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
            args=[
                "-x", "c",
                "-std=c99"
            ],
            options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        )

    except Exception as e:

        print(f"FAILED PARSE: {e}")
        return None

    result = {

        "file": str(file_path),

        "includes": [],

        "functions_defined": [],

        "functions_declared": [],

        "globals": [],

        "macros": []
    }

    # diagnostics
    for diag in tu.diagnostics:

        if diag.severity >= 3:

            print(f"DIAG: {diag}")

    walk_ast(
        tu.cursor,
        result,
        str(file_path)
    )

    return result

# ==========================================
# AST WALKER
# ==========================================

def walk_ast(node, result, source_file):

    # ignore nodes from other files
    if node.location.file:

        current_file = str(
            Path(str(node.location.file)).resolve()
        )

        if current_file != source_file:
            return

    # ======================================
    # INCLUDES
    # ======================================

    if node.kind == CursorKind.INCLUSION_DIRECTIVE:

        result["includes"].append(
            node.displayname
        )

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

            result["functions_defined"].append(
                function_data
            )

        else:

            result["functions_declared"].append(
                function_data
            )

    # ======================================
    # GLOBAL VARIABLES
    # ======================================

    elif node.kind == CursorKind.VAR_DECL:

        if (
            node.semantic_parent.kind
            == CursorKind.TRANSLATION_UNIT
        ):

            result["globals"].append({

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

    # recurse
    for child in node.get_children():

        walk_ast(
            child,
            result,
            source_file
        )

# ==========================================
# MAIN
# ==========================================

all_results = []

compile_commands_path = (
    REPO_ROOT
    / "build"
    / "compile_commands.json"
)

with open(compile_commands_path, "r") as f:

    compile_data = json.load(f)

processed_files = set()

for entry in compile_data:

    file_path = Path(
        entry["file"]
    ).resolve()

    # ======================================
    # DUPLICATE CHECK
    # ======================================

    if str(file_path) in processed_files:
        continue

    processed_files.add(str(file_path))

    # ======================================
    # ONLY app/ and src/
    # ======================================

    if not any(
        str(file_path).startswith(str(folder))
        for folder in TARGET_FOLDERS
    ):
        continue

    # ======================================
    # ONLY .c / .h
    # ======================================

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

output_path = (
    REPO_ROOT
    / OUTPUT_FILE
)

with open(output_path, "w") as f:

    json.dump(
        all_results,
        f,
        indent=2
    )

print("\n================================")
print("DONE")
print(f"Saved: {output_path}")
print("================================")
