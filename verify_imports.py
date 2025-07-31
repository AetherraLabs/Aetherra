import ast
import os
import sys

ALLOWED_PREFIXES = ("Aetherra", "Lyrixa", "aetherra_core", "lyrixa_core", ".", "..")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def is_valid_import(module):
    if module is None:
        return True
    return module.startswith(ALLOWED_PREFIXES)


def check_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception as e:
            print(f"[ERROR] Could not parse {filepath}: {e}")
            return False
    valid = True
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not is_valid_import(alias.name):
                    print(f"[INVALID IMPORT] {alias.name} in {filepath}:{node.lineno}")
                    valid = False
        elif isinstance(node, ast.ImportFrom):
            if node.module and not is_valid_import(node.module):
                print(
                    f"[INVALID FROM IMPORT] from {node.module} import ... in {filepath}:{node.lineno}"
                )
                valid = False
    return valid


def scan_directory(root):
    all_valid = True
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                if not check_file(filepath):
                    all_valid = False
    return all_valid


if __name__ == "__main__":
    print("Scanning for invalid imports...")
    result = scan_directory(PROJECT_ROOT)
    if result:
        print("All imports are valid.")
        sys.exit(0)
    else:
        print("Some invalid imports found.")
        sys.exit(1)
