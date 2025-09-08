# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import ast
import os
import sys

# Permit common first-party package prefixes and relative imports
ALLOWED_PREFIXES = (
    "Aetherra",
    "Lyrixa",
    "aetherra_core",
    "lyrixa_core",
    ".",
    "..",
)

# Exclude non-project folders (venvs, vendored libs, build artifacts, docs, tests)
EXCLUDE_DIR_NAMES = {
    ".git",
    ".github",
    "__pycache__",
    "build",
    "dist",
    "docs",
    "env",
    "venv",
    ".venv",
    "node_modules",
    "frontend",  # contains site-packages for GUI env in this repo
    "tests",  # tests import 3rd-party libs; skip for this validation
    "smart_cleanup_backup",  # legacy backup content – not part of active code
    "comprehensive_cleanup_backup",
    "final_organization_backup",
    "focused_cleanup_backup",
    "Discord Bot",
    "aetherra_os_web",
    "Aetherra",  # large legacy/alternate tree; excluded from import scope check
}

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


DISALLOWED_INTERNAL_ROOTS = {
    # Likely internal subpackages that must be prefixed by first-party roots
    "core",
    "kernel",
    "memory",
    "plugins",
    "plugin",
    "orchestration",
    "interpreter",
    "runtime",
    "web",
    "integration",
    "interfaces",
    "gui",
}


def is_valid_import(module: str | None) -> bool:
    """Return True if the import target should be considered valid.

    Rules:
    - Always allow None ("from . import ...")
    - Allow bare top-level module names (no dot) such as stdlib and 3rd-party
    - For dotted imports, require that they start with an allowed first-party prefix
    """
    if module is None:
        return True
    # Always allow relative imports and bare names (stdlib/3rd-party)
    if module.startswith((".", "..")) or "." not in module:
        return True

    first = module.split(".", 1)[0]

    # Only enforce prefixing rules for likely internal namespaces.
    # For all other dotted imports (third-party or stdlib like 'urllib.request'), allow.
    if first in DISALLOWED_INTERNAL_ROOTS:
        return module.startswith(ALLOWED_PREFIXES)

    return True


def check_file(filepath):
    with open(filepath, encoding="utf-8") as f:
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


def should_exclude_path(path: str) -> bool:
    # Exclude if any directory segment is in EXCLUDE_DIR_NAMES
    parts = set(os.path.normpath(path).split(os.sep))
    if parts & EXCLUDE_DIR_NAMES:
        return True
    # Exclude any site-packages or pip vendor content within the repo
    lowered = path.lower()
    if (
        "site-packages" in lowered
        or "pip/_vendor" in lowered
        or "pip\\_vendor" in lowered
    ):
        return True
    return False


def scan_directory(root):
    all_valid = True
    checked_files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories during traversal for efficiency
        dirnames[:] = [
            d for d in dirnames if not should_exclude_path(os.path.join(dirpath, d))
        ]

        if should_exclude_path(dirpath):
            continue

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, filename)
            if should_exclude_path(filepath):
                continue
            checked_files += 1
            if not check_file(filepath):
                all_valid = False
    print(f"Scanned {checked_files} Python files (excluded vendor/venv/tests/docs).")
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
