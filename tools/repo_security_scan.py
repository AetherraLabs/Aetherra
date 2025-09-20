#!/usr/bin/env python3
"""Lightweight repository security & hygiene scan.

Checks (non-exhaustive):
- Raw risky primitives: eval(, exec( occurrences
- subprocess. usage without comment containing 'guard' or 'capability'
- requests. usages (recommend wrapper) unless line mentions 'net_policy' or 'allowlist'
- Bare except: 'except: pass'
- Broad except Exception without a log or raise in same block line

Exit codes:
 0: No high-severity findings
 1: Findings detected

Environment:
 AETHERRA_SCAN_VERBOSE=1 to list all matches

This helper is additive; integrate into CI or quality gates as needed.
"""

from __future__ import annotations

# Standard library imports
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE_EXT = {".py"}
results: list[dict] = []
VERBOSE = os.environ.get("AETHERRA_SCAN_VERBOSE") == "1"

PATTERNS = {
    "eval": re.compile(r"\beval\s*\("),
    "exec": re.compile(r"\bexec\s*\("),
    "subprocess": re.compile(r"\bsubprocess\."),
    "requests": re.compile(r"\brequests\."),
    # Tightened to match code-only bare except patterns at start of a statement
    "bare_except_pass": re.compile(r"^\s*except\s*:\s*pass\b"),
    # Tightened to match code-only broad except patterns at start of a statement
    "broad_except": re.compile(r"^\s*except\s+Exception\b"),
}

IGNORE_DIRS = {"tests", "build", "dist", ".venv", "archive", "backup"}


def scan_file(path: Path) -> None:
    """Scan a single file for simple risky patterns.

    Heuristics:
    - Skip comments and docstrings/triple-quoted blocks to avoid false positives
    - Tighten except-patterns to only match at statement start
    """
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return

    in_triple: str | None = None  # Track triple-quoted blocks (""" or ''')
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip pure comments
        if stripped.startswith("#"):
            continue

        # Track and skip triple-quoted string blocks (docstrings)
        if in_triple is not None:
            # Toggle off when delimiter count is odd (start/end)
            if in_triple in line and line.count(in_triple) % 2 == 1:
                in_triple = None
            continue
        if '"""' in line or "'''" in line:
            # If a triple quote appears with an odd count, enter docstring mode
            if line.count('"""') % 2 == 1:
                in_triple = '"""'
                continue
            if line.count("'''") % 2 == 1:
                in_triple = "'''"
                continue

        for key, pat in PATTERNS.items():
            if pat.search(line):
                # Heuristics to downgrade/ignore
                if key == "subprocess" and (
                    "guard" in stripped or "capability" in stripped
                ):
                    continue
                if key == "requests" and (
                    "net_policy" in stripped or "allowlist" in stripped
                ):
                    continue
                if key == "broad_except" and (
                    "logger." in stripped or "raise " in stripped or "pass" in stripped
                ):
                    continue
                results.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "line": lineno,
                        "type": key,
                        "code": line.rstrip(),
                    }
                )


def main() -> int:
    for p in ROOT.rglob("*.py"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        scan_file(p)
    high = [r for r in results if r["type"] in {"eval", "exec", "bare_except_pass"}]
    payload = {"total": len(results), "high": len(high), "findings": results}
    if VERBOSE:
        print(json.dumps(payload, indent=2))
    else:
        print(f"[scan] findings={len(results)} high={len(high)}")
    if high:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
