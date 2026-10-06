import os
import re

# Updated regex pattern to match C-style function definitions, including inline
function_pattern = re.compile(
    r'''
    ^                                       # start of line
    (?:static\s+)?                          # optional 'static'
    (?:inline\s+)?                          # optional 'inline'
    [a-zA-Z_][\w\s\*\(\)]+?                 # return type and optional pointers
    \s+                                     # at least one space
    [a-zA-Z_][\w]*                          # function name
    \s*\([^;]*?\)                           # parameter list (no semicolon = not declaration)
    \s*\{                                   # opening brace = function definition
    ''',
    re.MULTILINE | re.VERBOSE
)

def count_functions_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            matches = function_pattern.findall(content)
            return len(matches)
    except Exception as e:
        print(f"[Error] {filepath}: {e}")
        return 0

def traverse_and_count_functions(root_dir):
    total_count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.c', '.h')):
                path = os.path.join(root, file)
                count = count_functions_in_file(path)
                print(f"{path} -> {count} function(s)")
                total_count += count
    print(f"\n[Total Functions Found]: {total_count}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python count_functions.py <folder_path>")
    else:
        folder = sys.argv[1]
        if os.path.isdir(folder):
            traverse_and_count_functions(folder)
        else:
            print("Error: Provided path is not a valid directory.")
