#!/usr/bin/env python3
"""
Quality Gates Runner
- Runs tests with coverage
- Fails if coverage drops below configured threshold or below previous baseline
- Optional: enforce no-drop policy via last stored coverage percent

Env/config:
- MIN_COVERAGE: percentage (default 0; rely on no-drop unless overridden)
- COVERAGE_BASELINE_FILE: path to store last coverage percent (default .coverage-baseline)
- TEST_TARGETS: pytest target path(s). If unset, picks existing from ["tests/capabilities", "tests"].
- ARCH_CHECK: 1 to run Architecture Map verifier as part of gates (default 1)
- ARCH_CHECK_STRICT: 1 to fail gates if verifier reports any FAIL (default 0)
- ARCH_PROBE_HUB: 1 to enable optional Hub HTTP probe as part of verifier (default 0)
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> tuple[int, str]:
    """Run a command and return (exit_code, stdout+stderr) decoded as UTF-8.

    Using explicit UTF-8 decoding avoids Windows cp1252 decode errors when
    the child process emits Unicode (e.g., emojis, checkmarks).
    """
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
    """
    Parse coverage percent from pytest-cov terminal report.
    Handles formats with columns:
    - Stmts  Miss  Cover
    - Stmts  Miss  Branch  BrPart  Cover
    """
    # Prefer the TOTAL line and capture the last percentage
    m = re.search(r"^TOTAL\b.*?(\d+)%\s*$", text, re.IGNORECASE | re.MULTILINE)
    if not m:
        # Fallback: overall 'coverage: 97%'
        m = re.search(r"coverage[:\s]+(\d+)%", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def main() -> int:
    # Note: default 0 so we don't fail purely on threshold; we still enforce no-drop vs baseline.
    min_cov = float(os.getenv("MIN_COVERAGE", "0"))
    baseline_file = Path(os.getenv("COVERAGE_BASELINE_FILE", ".coverage-baseline"))
    raw_targets = os.getenv("TEST_TARGETS", "").strip()
    if raw_targets:
        targets = raw_targets.split()
    else:
        # Default: capabilities suite plus focused AAR/Outbox tests if present
        candidates = [
            "tests/capabilities",
            "tests/test_outbox_unit.py",
            "tests/test_aar_outbox.py",
            "tests/test_agent_pipeline_smoke.py",
        ]
        targets = [t for t in candidates if Path(t).exists()]
        # Fallback to tests/capabilities or tests if nothing found
        if not targets:
            targets = [
                t for t in ["tests/capabilities", "tests"] if Path(t).exists()
            ] or ["tests"]

    # Run pytest with coverage
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
        # Explicitly pass fail-under to override any config (pyproject/coverage) that might enforce a different value
        f"--cov-fail-under={int(min_cov)}",
        "--cov-report",
        "term",
    ] + targets
    code, out = run(cmd)
    print(out)
    if code != 0:
        print("[GATES] Tests failed; gate failed.")
        return code

    cov = parse_coverage(out)
    if cov is None:
        print("[GATES] Could not parse coverage; failing to be safe.")
        return 1

    print(f"[GATES] Coverage: {cov}% (min {min_cov}%)")
    if cov < min_cov:
        print("[GATES] Coverage below minimum threshold.")
        return 1

    # Coverage no-drop gate
    prev = None
    if baseline_file.exists():
        try:
            prev = float(baseline_file.read_text().strip())
        except Exception:
            prev = None
    if prev is not None and cov < prev:
        print(f"[GATES] Coverage dropped: prev {prev}% -> now {cov}%")
        return 1

    # Update baseline to latest
    try:
        baseline_file.write_text(str(cov))
    except Exception as e:
        print(f"[GATES] Warning: failed to write baseline: {e}")

    # Optional: run Architecture Map verifier
    if os.getenv("ARCH_CHECK", "1") == "1":
        strict = os.getenv("ARCH_CHECK_STRICT", "0") == "1"
        probe = os.getenv("ARCH_PROBE_HUB", "0") == "1"
        args = [sys.executable, "-X", "utf8", "tools/verify_architecture_map.py"]
        if strict:
            args.append("--strict")
        if probe:
            args.append("--probe-hub")
        print("[GATES] Running Architecture Map verifier...")
        code_arch, out_arch = run(args)
        print(out_arch)
        if code_arch != 0 and strict:
            print("[GATES] Architecture verifier failed in strict mode.")
            return code_arch

    print("[GATES] All quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
