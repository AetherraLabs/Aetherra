#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Validate imports in the codebase against the canonical import map.

- Only flags legacy internal namespaces (aetherra_core.*, lyrixa_core.*).
- Allows third-party imports freely.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

DISALLOWED_PREFIXES = (
    "aetherra_core.",
    "lyrixa_core.",
)

# Also disallow importing the base legacy packages directly, e.g.:
#   from aetherra_core import X
#   import lyrixa_core
DISALLOWED_EXACT = {"aetherra_core", "lyrixa_core"}


def iter_py_files(root: Path):
    for p in root.rglob("*.py"):
        # Skip typical non-source folders
        skip = {".venv", "venv", "env", "node_modules", "__pycache__", "build", "dist"}
        if any(part in skip for part in p.parts):
            continue
        yield p


def is_disallowed(name: str) -> bool:
    return name in DISALLOWED_EXACT or any(
        name.startswith(pref) for pref in DISALLOWED_PREFIXES
    )


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
                if node.module and is_disallowed(node.module):
                    offenders.append((str(py), node.lineno, node.module))

    if offenders:
        print(
            "Non-canonical imports detected (use Aetherra.* instead of legacy namespaces):"
        )
        for file, line, name in offenders[:200]:
            print(f" - {file}:{line} -> {name}")
        if len(offenders) > 200:
            print(f" ... and {len(offenders) - 200} more")
        return 1

    print("Import map validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
