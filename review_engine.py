import json
from pathlib import Path
from clang.cindex import (
    Index,
    CursorKind,
    CompilationDatabase,
    TranslationUnit,
    TypeKind,
    Config
)

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
# ARG SANITIZER
# ==========================================

def sanitize_args(args):

    cleaned = []

    skip_next = False

    # flags that take a value after them
    consume_next = {
        "-o",
        "-MF",
        "-MT",
        "-MQ",
        "--output",
    }

    # unsupported embedded/compiler-specific flags
    skip_prefixes = (
        "--cpu=",
        "-mcpu=",
        "-mfpu=",
        "-mfloat-abi=",
        "--target=",
        "-fshort-enums",
        "-fshort-wchar",
        "--specs=",
        "-ffreestanding",
        "-fno-common",
        "-fmessage-length=",
        "-fcyclomatic-complexity",
        "-fstack-usage",
        "--diag_suppress",
        "--diag_warning",
        "--diag_error",
        "--gcc",
        "--gnu",
        "--abi",
        "--thumb",
    )

    # exact flags to skip
    skip_exact = {
        "-c",
        "-MD",
        "-MMD",
        "-MP",
        "-Winvalid-pch",
    }

    for arg in args:

        if skip_next:
            skip_next = False
            continue

        if arg in consume_next:
            skip_next = True
            continue

        if arg in skip_exact:
            continue

        if arg.startswith(skip_prefixes):
            continue

        cleaned.append(arg)

    # force language
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
    # RESULT STRUCTURE
    # ======================================

    result = {

        "file": str(file_path),

        "includes": [],

        "functions_defined": [],
        "functions_declared": [],

        "globals": [],
        "locals": [],
        "parameters": [],

        # parent-child hierarchy
        "structs": [],
        "enums": [],

        "typedefs": [],

        "macros": []
    }

    # diagnostics
    for diag in tu.diagnostics:
        if diag.severity >= 3:
            print(f"DIAG: {diag}")

    walk_ast(tu.cursor, result, str(file_path))

    return result



# ==========================================
# HELPER: IS USER MACRO
# ==========================================

def is_user_macro(node):

    if not node.location.file:
        return False

    macro_file = Path(str(node.location.file)).resolve()

    # must be inside repo
    try:
        macro_file.relative_to(REPO_ROOT)
    except ValueError:
        return False

    name = node.spelling

    # compiler/internal macros
    if name.startswith("__"):
        return False

    # reserved/private macros
    if name.startswith("_"):
        return False

    return True



# ==========================================
# AST WALKER
# ==========================================

def walk_ast(node, result, source_file):



    if node.location.file:

        current_file = Path(str(node.location.file)).resolve()

        # Skip files outside repo
        try:
            current_file.relative_to(REPO_ROOT)
        except ValueError:
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
    # VARIABLES
    # ======================================
    elif node.kind == CursorKind.VAR_DECL:

        import re

        parent = node.semantic_parent.kind

        tokens = [tok.spelling for tok in node.get_tokens()]

        raw_declaration = " ".join(tokens)

        # =====================================
        # RECOVER ARRAY DECLARATION TEXT
        # =====================================

        full_decl = raw_declaration

        try:

            with open(source_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            line_text = lines[node.location.line - 1].strip()

            m = re.search(
                rf"\b{re.escape(node.spelling)}((?:\s*\[[^\]]*\])*)",
                line_text
            )

            if m:
                suffix = m.group(1) or ""
                full_decl = raw_declaration + suffix

        except Exception:
            pass

        # =====================================
        # ARRAY SUFFIXES
        # =====================================

        array_suffixes = re.findall(
            r"\[[^\]]*\]",
            full_decl
        )

        # =====================================
        # MINIMAL RAW STRUCTURE
        # =====================================

        var_data = {

            # variable identifier
            "name": node.spelling,

            # original declaration text
            "raw_declaration": full_decl,

            # raw array dimensions
            "array_suffixes": array_suffixes,

            # source location
            "line": node.location.line,

            # static / extern etc.
            "storage_class": str(node.storage_class)
        }

        if parent == CursorKind.TRANSLATION_UNIT:
            result["globals"].append(var_data)
        else:
            result["locals"].append(var_data)












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
    # STRUCTS + FIELDS
    # ======================================

    elif node.kind == CursorKind.STRUCT_DECL:

        if node.spelling:

            struct_data = {
                "name": node.spelling,
                "line": node.location.line,
                "fields": []
            }

            for child in node.get_children():

                if child.kind == CursorKind.FIELD_DECL:

                    struct_data["fields"].append({
                        "name": child.spelling,
                        "type": child.type.spelling,
                        "line": child.location.line
                    })

            result["structs"].append(struct_data)

    # ======================================
    # ENUMS + CONSTANTS
    # ======================================

    elif node.kind == CursorKind.ENUM_DECL:

        if node.spelling:

            enum_data = {
                "name": node.spelling,
                "line": node.location.line,
                "constants": []
            }

            for child in node.get_children():

                if child.kind == CursorKind.ENUM_CONSTANT_DECL:

                    enum_data["constants"].append({
                        "name": child.spelling,
                        "line": child.location.line
                    })

            result["enums"].append(enum_data)

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

        if is_user_macro(node):

            tokens = list(node.get_tokens())

            replacement = ""

            if len(tokens) > 1:
                replacement = " ".join(
                    tok.spelling for tok in tokens[1:]
                )

            macro_type = "conditional"

            # ----------------------------------
            # FUNCTION MACRO DETECTION
            # ----------------------------------

            # actual function macro:
            # #define MAX(x) ...

            if (
                len(tokens) >= 4
                and tokens[1].spelling == "("
            ):

                close_idx = None

                for i in range(2, len(tokens)):
                    if tokens[i].spelling == ")":
                        close_idx = i
                        break

                if close_idx is not None:

                    param_tokens = tokens[2:close_idx]

                    # valid param list contains only:
                    # identifiers and commas

                    is_param_list = all(
                        tok.kind.name == "IDENTIFIER"
                        or tok.spelling == ","
                        for tok in param_tokens
                    )

                    if is_param_list:
                        macro_type = "function"
                    else:
                        macro_type = "value"

            elif len(tokens) > 1:
                macro_type = "value"

            result["macros"].append({
                "name": node.spelling,
                "line": node.location.line,
                "type": macro_type,
                "replacement": replacement
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