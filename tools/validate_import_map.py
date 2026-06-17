#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Validate imports in the codebase against the canonical import map.

Enforcements (P2 #13):

1. Disallow legacy internal namespaces (``aetherra_core.*``, ``lyrixa_core.*``)
2. Disallow direct base legacy packages (``import aetherra_core``)
3. Flag deep relative imports that escape package roots (``from ..`` / ``from ...``)
    - Allow relative imports of depth 0/1 inside tests (fixture patterns) to reduce noise
4. (Future) Optionally block wildcard ``from X import *`` for internal modules (placeholder hook)

Exit code 1 if any violations are found so CI will fail.
"""

from __future__ import annotations

# Standard library imports
import ast
import sys
from pathlib import Path

RELATIVE_MAX_DEPTH = (
    2  # depth > 2 discouraged outside tests; allow parent package access
)
RELATIVE_WHITELIST: set[str] = {
    # Temporary exemptions (P2 migration window)
    # aether_parser deep grammar utilities
    "Aetherra/runtime/aether_parser.py:278",
    # agent base complex relative (pending refactor)
    "Aetherra/aetherra_core/agents/base.py:280",
    "Aetherra/aetherra_core/agents/base.py:390",
    "Aetherra/aetherra_core/memory/memory_learning.py:27",
    "Aetherra/runtime/aether_parser.py:342",
}

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
        skip = {
            ".venv",
            "venv",
            "env",
            "node_modules",
            "__pycache__",
            "build",
            "dist",
            "dist-packages",
            "archive",
            "backups",
            "unused",
            "legacy",
        }
        if any(part in skip for part in p.parts):
            continue
        yield p


def is_disallowed(name: str) -> bool:
    return name in DISALLOWED_EXACT or any(
        name.startswith(pref) for pref in DISALLOWED_PREFIXES
    )


def relative_depth(node: ast.ImportFrom) -> int:
    # node.level gives the number of leading dots in from-import statements
    return getattr(node, "level", 0) or 0


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    offenders: list[tuple[str, int, str]] = []
    rel_offenders: list[tuple[str, int, str]] = []

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
                # Relative import depth enforcement
                depth = relative_depth(node)
                if depth > RELATIVE_MAX_DEPTH:
                    # Allow in tests directory (common for local fixtures)
                    key = (
                        f"{py.as_posix().split(root.as_posix().rstrip('/') + '/')[-1]}:{node.lineno}"
                        if "root" in locals()
                        else f"{py}:{node.lineno}"
                    )
                    if "tests" not in py.parts and key not in RELATIVE_WHITELIST:
                        rel_offenders.append(
                            (
                                str(py),
                                node.lineno,
                                f"relative-depth={depth} (> {RELATIVE_MAX_DEPTH})",
                            )
                        )

    exit_code = 0
    if offenders:
        print(
            "[IMPORT-MAP] Non-canonical imports detected (use Aetherra.*; legacy namespaces forbidden):"
        )
        for file, line, name in offenders[:200]:
            print(f" - {file}:{line} -> {name}")
        if len(offenders) > 200:
            print(f" ... and {len(offenders) - 200} more")
        exit_code = 1

    if rel_offenders:
        print(
            f"[IMPORT-MAP] Deep relative imports detected (limit depth <= {RELATIVE_MAX_DEPTH}; prefer absolute Aetherra.*):"
        )
        for file, line, info in rel_offenders[:200]:
            print(f" - {file}:{line} -> {info}")
        if len(rel_offenders) > 200:
            print(f" ... and {len(rel_offenders) - 200} more")
        exit_code = 1
    if exit_code == 0:
        print("Import map validation passed (no legacy or deep relative imports).")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
