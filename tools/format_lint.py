#!/usr/bin/env python3
"""Unified formatter & linter runner for Aetherra.

Runs (in order): isort, black, ruff (lint only), mypy (optional), flake8 (optional).
Produces a concise summary for CI / Lyrixa Code Studio.

Env Flags:
  AETHERRA_LINT_FIX=0   -> if set to 1, attempts autofix (ruff --fix)
  AETHERRA_LINT_MYPY=1  -> include mypy type checking
  AETHERRA_LINT_FLAKE8=1 -> include flake8 pass

Exit codes:
  0 success / clean
  1 if any tool reports errors it cannot fix
"""

from __future__ import annotations

import os
import subprocess
import sys
from shutil import which

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def run(cmd: list[str]) -> tuple[int, str]:
    """Run a command capturing combined stdout/stderr as UTF-8, replacing undecodable bytes.

    Using explicit encoding avoids Windows cp1252 decode failures when tools emit
    Unicode characters outside the code page.
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
    )
    out, _ = proc.communicate()
    return proc.returncode, out


def tool_exists(name: str) -> bool:
    return which(name) is not None


def main() -> int:
    fix = os.getenv("AETHERRA_LINT_FIX", "0") == "1"
    want_mypy = os.getenv("AETHERRA_LINT_MYPY", "0") == "1"
    want_flake8 = os.getenv("AETHERRA_LINT_FLAKE8", "0") == "1"
    failures = 0
    steps: list[tuple[str, list[str]]] = []

    strict = os.getenv("AETHERRA_STRICT", "0") == "1"
    if tool_exists("isort"):
        # isort in normal (write) mode even in strict; could add --check-only later
        steps.append(("isort", ["isort", "."]))
    if tool_exists("black"):
        if strict:
            steps.append(("black", ["black", "--check", "."]))
        else:
            steps.append(("black", ["black", "."]))
    if tool_exists("ruff"):
        steps.append(("ruff", ["ruff", "--fix" if fix else "check", "."]))
    if want_mypy and tool_exists("mypy"):
        steps.append(("mypy", ["mypy", "Aetherra", "aetherra_coding"]))
    if want_flake8 and tool_exists("flake8"):
        steps.append(("flake8", ["flake8", "."]))

    for name, cmd in steps:
        code, out = run(cmd)
        print(f"[{name}] exit={code}")
        # print first 40 lines of output to keep logs concise
        lines = out.strip().splitlines()
        if lines:
            preview = lines[:40]
            print("\n".join(preview))
            if len(lines) > 40:
                print(f"... ({len(lines) - 40} more lines truncated)")
        if code != 0:
            failures += 1

    if failures:
        print(f"Formatting/Lint failures: {failures}")
    else:
        print("Formatting/Lint clean")
    return 0 if failures == 0 else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
