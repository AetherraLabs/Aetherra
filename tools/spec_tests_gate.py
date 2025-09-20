#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Spec → Tests Gate

Enforces that when source files are changed, acceptance/unit tests are added or updated.
This is intended to run BEFORE applying patches in the autonomy loop, or as a task.

Logic:
- Determine changed files via git (staged first; fallback to HEAD working diff)
- If any non-doc, non-test source files changed (py, aether, ts/tsx/js) then require at least
  one changed file under tests/ (or docs changes that adjust acceptance specs)
- Exemptions can be configured via env IGNORED_PATHS (comma-separated substrings)

Exit code: 0 pass, 1 fail, 2 soft-skip (no git or no changes)
"""

from __future__ import annotations

# Standard library imports
import os
import subprocess
from pathlib import Path

SRC_EXTS = {".py", ".aether", ".ts", ".tsx", ".js", ".jsx"}


def git_diff(names_only: bool = True, staged: bool = True) -> list[str]:
    args = ["git", "--no-pager", "diff"]
    if staged:
        args.append("--cached")
    if names_only:
        args.append("--name-only")
    try:
        res = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        if res.returncode != 0:
            return []
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def classify(files: list[str]) -> tuple[list[Path], list[Path]]:
    code_changes: list[Path] = []
    test_changes: list[Path] = []
    ignored = [
        s.strip() for s in os.getenv("IGNORED_PATHS", "").split(",") if s.strip()
    ]
    for f in files:
        if any(ig in f for ig in ignored):
            continue
        p = Path(f)
        if p.is_dir():
            continue
        if "/tests/" in ("/" + f.replace("\\", "/") + "/") or f.startswith("tests/"):
            test_changes.append(p)
            continue
        if f.startswith("docs/"):
            # Docs don't force tests
            continue
        if p.suffix.lower() in SRC_EXTS:
            code_changes.append(p)
    return code_changes, test_changes


def main() -> int:
    # First try staged changes
    changed = git_diff(staged=True)
    if not changed:
        # Fallback to working diff vs HEAD
        changed = git_diff(staged=False)
    if not changed:
        print("[SPEC→TESTS] No changes detected (skip).")
        return 2

    code_changes, test_changes = classify(changed)
    if not code_changes:
        print("[SPEC→TESTS] No code changes requiring tests (pass).")
        return 0
    if test_changes:
        print(
            f"[SPEC→TESTS] OK: {len(test_changes)} test file(s) changed for {len(code_changes)} code file(s)."
        )
        return 0

    print(
        "[SPEC→TESTS] FAIL: Code changes detected without corresponding test updates."
    )
    for p in code_changes:
        print(f"  - {p}")
    print("Hint: add/update tests under tests/ or justify exemption.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
