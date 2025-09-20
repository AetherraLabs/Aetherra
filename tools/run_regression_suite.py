#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Unified regression suite runner.

Goals:
- Execute fast smoke + capability + failure-injection tests
- Optional: full suite when --full provided
- Emit summarized JSON report with pass/fail counts and coverage percent excerpt

Usage:
  python tools/run_regression_suite.py            # fast sets
  python tools/run_regression_suite.py --full     # full suite
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_FAST_TARGETS = [
    "tests/capabilities",
    "tests/failure_injection",
]

FULL_EXTRA = [
    "tests",
]


def run_pytest(targets: list[str]) -> tuple[int, str]:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-o",
        "addopts=",
        "--maxfail=1",
        "--disable-warnings",
        "--cov=.",
        "--cov-report=term",
    ] + targets
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out, _ = p.communicate()
    return p.returncode, out


def parse_coverage(text: str) -> float | None:
    m = re.search(r"^TOTAL.*?(\d+)%\s*$", text, re.MULTILINE)
    return float(m.group(1)) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="Run full test suite")
    ap.add_argument(
        "--report", default="regression_report.json", help="Write JSON summary"
    )
    args = ap.parse_args()

    targets = DEFAULT_FAST_TARGETS.copy()
    if args.full:
        # Extend with extra broad sets (avoid duplicate capability dir)
        for t in FULL_EXTRA:
            if t not in targets:
                targets.append(t)

    # Filter to existing
    targets = [t for t in targets if Path(t).exists()]
    if not targets:
        print("[REGRESSION] No targets found")
        return 2

    code, out = run_pytest(targets)
    print(out)
    cov = parse_coverage(out) or 0.0

    passed = len(re.findall(r"^.+::.+ PASSED$", out, re.MULTILINE))
    failed = len(re.findall(r"^.+::.+ FAILED$", out, re.MULTILINE))
    skipped = len(re.findall(r"^.+::.+ SKIPPED$", out, re.MULTILINE))

    report = {
        "targets": targets,
        "exit_code": code,
        "coverage": cov,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }
    try:
        Path(args.report).write_text(json.dumps(report, indent=2))
        print(f"[REGRESSION] Report written to {args.report}")
    except Exception as e:
        print(f"[REGRESSION] Failed to write report: {e}")

    return code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
