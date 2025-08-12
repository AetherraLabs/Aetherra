#!/usr/bin/env python3
"""
Validate imports in the codebase against the canonical import map.
Fails with exit code 1 if non-canonical imports are detected.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

CANONICAL_ROOT = ("Aetherra",)
DISALLOWED_PREFIXES = (
    "aetherra_core.",
    "lyrixa_core.",
)


def iter_py_files(root: Path):
    for p in root.rglob("*.py"):
        # skip virtualenvs and hidden
        parts = {".venv", "venv", "env", "node_modules", "__pycache__"}
        if any(part in parts for part in p.parts):
            continue
        yield p


def is_disallowed(name: str) -> bool:
    return any(name.startswith(pref) for pref in DISALLOWED_PREFIXES)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    offenders: list[tuple[str, int, str]] = []

    for py in iter_py_files(root):
        try:
            src = py.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src, filename=str(py))
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if is_disallowed(name):
                        offenders.append((str(py), node.lineno, name))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    name = node.module
                    if is_disallowed(name):
                        offenders.append((str(py), node.lineno, name))

    if offenders:
        print("Non-canonical imports detected (use Aetherra.*):")
        for file, line, name in offenders:
            print(f" - {file}:{line} -> {name}")
        return 1

    print("Import map validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
