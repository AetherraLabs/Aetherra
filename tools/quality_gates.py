#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Quality Gates Runner
- Dependency & security hygiene
- Tests with coverage & no-drop gate
- Optional architecture verification

Sequence:
 1. (Optional) Enforce dependency lock sync
 2. (Optional) Vulnerability scan (fails on severity threshold)
 3. Run tests with coverage & enforce no-drop
 4. (Optional) Architecture map verifier
 5. (Optional / non-fatal) License report artifact

Env/config:
    MIN_COVERAGE              : percentage (default 0; rely on no-drop unless overridden)
    COVERAGE_BASELINE_FILE    : path to store last coverage percent (default .coverage-baseline)
    TEST_TARGETS              : pytest target path(s). If unset, chooses existing from candidates.
    ARCH_CHECK                : 1 run architecture verifier (default 1)
    ARCH_CHECK_STRICT         : 1 fail gates if verifier non-zero (default 0)
    ARCH_PROBE_HUB            : 1 enable Hub probe (default 0)
    LOCK_ENFORCE              : 1 enforce requirements.lock drift check (default 1 if lock present)
    LOCK_FILE                 : path to lock file (default requirements.lock)
    VULN_SCAN                 : 1 run vulnerability scan (default 1 if lock present)
    VULN_FAIL_LEVEL           : severity threshold (default high) passed through to vuln_scan.py
    LICENSE_REPORT            : 1 generate license report (default 1)
    LICENSE_REPORT_JSON       : output JSON path (default licenses_report.json)
    LICENSE_DENY              : space/comma separated deny substrings (e.g. 'agpl GPL-2.0')
    LICENSE_FAIL_ON_UNKNOWN   : 1 to fail on UNKNOWN licenses (default 0)
    REQUIRE_THREAT_MODEL      : 1 require docs/THREAT_MODEL.md presence (default 1)
    REQUIRE_LICENSE_POLICY    : 1 require LICENSE_POLICY.md presence (default 1)
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


def run_optional_tool(label: str, args: list[str], fail_fatal: bool = True) -> bool:
    """Run a subordinate tool, printing output. Returns True if succeeded.

    If fail_fatal is False, failures are logged but do not abort gates.
    """
    print(f"[GATES] {label} -> {' '.join(args)}")
    code, out = run(args)
    print(out)
    if code != 0:
        msg = f"[GATES] {label} failed with exit {code}"
        if fail_fatal:
            print(msg)
            return False
        print(msg + " (non-fatal)")
    else:
        print(f"[GATES] {label} OK")
    return True


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
            "tests/failure_injection",
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

    # 0. Dependency lock enforcement & vulnerability scan (pre-test)
    lock_file = Path(os.getenv("LOCK_FILE", "requirements.lock"))
    lock_exists = lock_file.exists()

    enforce_lock = os.getenv("LOCK_ENFORCE", "1") == "1" and lock_exists
    if enforce_lock:
        tool = Path("tools/enforce_lock_sync.py")
        if tool.exists():
            ok = run_optional_tool(
                "Lock Sync", [sys.executable, str(tool), "--lock", str(lock_file)]
            )
            if not ok:
                return 1
        else:
            print(
                "[GATES] Lock enforcement requested but tool missing; failing for safety."
            )
            return 1
    elif os.getenv("LOCK_ENFORCE", "1") == "1" and not lock_exists:
        # user expected enforcement but file absent
        print(f"[GATES] LOCK_ENFORCE=1 but missing {lock_file}; failing.")
        return 1
    else:
        print("[GATES] Lock enforcement skipped (disabled or lock absent)")

    vuln_scan_enabled = os.getenv("VULN_SCAN", "1") == "1" and lock_exists
    if vuln_scan_enabled:
        tool = Path("tools/vuln_scan.py")
        if tool.exists():
            args_vs = [sys.executable, str(tool), "--lock", str(lock_file)]
            fail_level = os.getenv("VULN_FAIL_LEVEL")
            if fail_level:
                args_vs += ["--fail-level", fail_level]
            ok = run_optional_tool("Vulnerability Scan", args_vs)
            if not ok:
                return 1
        else:
            print(
                "[GATES] Vulnerability scan requested but tool missing; continuing (treat as warning)."
            )
    else:
        print("[GATES] Vulnerability scan skipped (disabled or lock absent)")

    # 1. Run pytest with coverage
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

    # 2. Optional: run Architecture Map verifier
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

    # 3. Optional: license report (can be fatal if policy set)
    if os.getenv("LICENSE_REPORT", "1") == "1":
        tool = Path("tools/license_report.py")
        if tool.exists() and lock_exists:
            json_out = os.getenv("LICENSE_REPORT_JSON", "licenses_report.json")
            deny_raw = os.getenv("LICENSE_DENY", "").replace(",", " ")
            deny_parts = [d for d in deny_raw.split() if d]
            args_lr = [
                sys.executable,
                str(tool),
                "--lock",
                str(lock_file),
                "--json",
                json_out,
            ]
            if deny_parts:
                args_lr += ["--deny", *deny_parts]
            fail_unknown = os.getenv("LICENSE_FAIL_ON_UNKNOWN", "0") == "1"
            if fail_unknown:
                args_lr.append("--fail-on-unknown")
            fatal = bool(deny_parts) or fail_unknown
            ok = run_optional_tool("License Report", args_lr, fail_fatal=fatal)
            if not ok and fatal:
                return 1
            # Run non-fatal policy enforcement right after report generation to surface UNKNOWN metrics.
            enforce_tool = Path("tools/enforce_license_policy.py")
            if enforce_tool.is_file():
                # Always pass through same JSON path; non-fatal (warn-only in alpha)
                args_enforce = [
                    sys.executable,
                    str(enforce_tool),
                    # report path picked up via env or default; set explicitly for clarity
                ]
                # Ensure env var for report path so script resolves correctly even if default changes later.
                os.environ["LICENSE_REPORT_JSON"] = json_out
                run_optional_tool(
                    "License Policy Enforcement", args_enforce, fail_fatal=False
                )
            else:
                print(
                    "[GATES] License enforcement script missing (tools/enforce_license_policy.py); skipping (non-fatal)"
                )
        else:
            print("[GATES] License report skipped (tool or lock missing)")

    # 4. Threat model presence enforcement
    if os.getenv("REQUIRE_THREAT_MODEL", "1") == "1":
        if not Path("docs/THREAT_MODEL.md").exists():
            print("[GATES] Missing docs/THREAT_MODEL.md (REQUIRE_THREAT_MODEL=1)")
            return 1

    # 5. License policy presence (non-negotiable for alpha governance transparency)
    if os.getenv("REQUIRE_LICENSE_POLICY", "1") == "1":
        if not Path("LICENSE_POLICY.md").exists():
            print("[GATES] Missing LICENSE_POLICY.md (REQUIRE_LICENSE_POLICY=1)")
            return 1

    # Placeholder for future strict enforcement (Beta toggle)
    if os.getenv("LICENSE_POLICY_STRICT", "0") == "1":  # future use
        print(
            "[GATES] LICENSE_POLICY_STRICT=1 set but strict implementation not yet available; proceeding (info)"
        )

    print("[GATES] All quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
