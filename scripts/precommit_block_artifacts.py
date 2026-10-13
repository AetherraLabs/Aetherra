#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Block staged runtime/generated artifacts, including bypasses of .gitignore."""

from __future__ import annotations

import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path

BLOCK_PATTERNS = ["*.log", "*.db", "*.sqlite", "*.pyc"]
FORBIDDEN_GLOBS = [
    "outbox/*.jsonl",
    "outbox/**/*.jsonl",
    "audit/*.jsonl",
    "audit/**/*.jsonl",
    "*audit*.json",
    "*report*.json",
    "aetherra_kernel_metrics.json",
    "data/aetherra_kernel_metrics.json",
    "ui_standards_report.md",
    "aether_static_report.md",
    "frontend/Lib/**",
    "frontend/Scripts/**",
    "deployments/local/tmp*/**",
    ".plugin_history/**",
    "*.log",
]


def get_staged_files() -> list[str]:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("Git is unavailable")
    result = subprocess.run(
        [git, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        capture_output=True,
        check=True,
        timeout=10,
    )
    # NUL delimiters preserve filenames containing whitespace or newlines.
    return [
        name.decode("utf-8", errors="surrogateescape")
        for name in result.stdout.split(b"\0")
        if name
    ]


def matches_forbidden(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(
        fnmatch.fnmatch(normalized, pattern)
        for pattern in [*BLOCK_PATTERNS, *FORBIDDEN_GLOBS]
    )


def matches(path: Path) -> bool:
    return matches_forbidden(path.as_posix())


def main() -> int:
    try:
        staged = get_staged_files()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(
            f"precommit_block_artifacts: failed to list staged files ({type(error).__name__})",
            file=sys.stderr,
        )
        return 1
    blocked = [path for path in staged if matches_forbidden(path)]
    if not blocked:
        return 0
    print("[BLOCKED] Staged runtime/generated artifacts:")
    for path in blocked:
        print(f"  - {path}")
    print("Unstage these artifacts; regenerate them outside source control.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
