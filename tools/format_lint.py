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

# Standard library imports
import os
import subprocess
import sys
from shutil import which

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def run(cmd: list[str], timeout: float | None = None) -> tuple[int, str]:
    """Run a command and return (exit_code, output) with robust decoding and optional timeout.

    - Uses UTF-8 decoding with errors="replace" for Windows compatibility
    - On timeout, terminates the process and returns code 124 with a diagnostic message
    """
    try:
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            timeout=timeout,
        )
        return completed.returncode, completed.stdout
    except subprocess.TimeoutExpired as e:
        out = ""
        # Prefer .output (stdout) attribute; .stderr is None when merged
        if getattr(e, "output", None):
            out += str(e.output)
        if getattr(e, "stderr", None):
            out += "\n" + str(e.stderr)
        out += f"\n[TIMEOUT] Command exceeded {timeout}s: {' '.join(cmd)}"
        return 124, out


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
        ruff_cmd = ["ruff", "check"]
        if fix:
            ruff_cmd.append("--fix")
        ruff_cmd.append(".")
        steps.append(("ruff", ruff_cmd))
    if want_mypy and tool_exists("mypy"):
        steps.append(("mypy", ["mypy", "Aetherra", "aetherra_coding"]))
    if want_flake8 and tool_exists("flake8"):
        steps.append(("flake8", ["flake8", "."]))

    for name, cmd in steps:
        # Most formatters/linters should finish quickly; provide a generous but finite timeout
        code, out = run(cmd, timeout=600)
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
