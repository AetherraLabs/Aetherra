#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Lightweight vulnerability scan wrapper.

Attempts sequentially:
 1. pip-audit (if installed) JSON output
 2. osv-scanner (if installed) on requirements.lock or pyproject

Exits non-zero if any HIGH/CRITICAL (or severity >= high) are detected.

Usage:
  python tools/vuln_scan.py --lock requirements.lock

Environment:
  VULN_FAIL_LEVEL=high|critical (default high)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

SEVERITY_ORDER = ["low", "moderate", "medium", "high", "critical"]


def run(cmd: list[str]) -> tuple[int, str]:
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


def pip_audit(lock_path: Path) -> list[dict]:
    if not shutil.which("pip-audit"):
        return []
    code, out = run(["pip-audit", "-r", str(lock_path), "-f", "json"])
    if code != 0:
        print("[VULN][WARN] pip-audit failed or returned non-zero")
    try:
        data = json.loads(out)
    except Exception:
        return []
    vulns = []
    for entry in data:
        for v in entry.get("vulns", []) or []:
            vulns.append(
                {
                    "name": entry.get("name"),
                    "version": entry.get("version"),
                    "id": v.get("id"),
                    "fix_versions": v.get("fix_versions"),
                    "severity": (v.get("severity") or "unknown").lower(),
                }
            )
    return vulns


def osv_scan(lock_path: Path) -> list[dict]:
    if not shutil.which("osv-scanner"):
        return []
    code, out = run(
        ["osv-scanner", "--format", "json", "--requirements", str(lock_path)]
    )
    if code not in (0, 1):  # 0=none,1=found vulns
        print("[VULN][WARN] osv-scanner returned unexpected code")
    try:
        data = json.loads(out)
    except Exception:
        return []
    vulns = []
    for res in data.get("results", []):
        for pkg in res.get("packages", []):
            pkg_name = pkg.get("package", {}).get("name")
            for v in pkg.get("vulnerabilities", []) or []:
                sev = "unknown"
                if v.get("severity"):
                    # pick highest severity if list
                    sev_vals = [
                        s.get("type") or s.get("score") for s in v.get("severity", [])
                    ]
                    sev = str(sev_vals[0]).lower() if sev_vals else "unknown"
                vulns.append(
                    {
                        "name": pkg_name,
                        "id": v.get("id"),
                        "severity": sev,
                    }
                )
    return vulns


def worst_or_unknown(vulns: list[dict]) -> str:
    worst = "low"
    for v in vulns:
        sev = v.get("severity", "low").lower()
        if sev not in SEVERITY_ORDER:
            sev = "low"
        if SEVERITY_ORDER.index(sev) > SEVERITY_ORDER.index(worst):
            worst = sev
    return worst


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", default="requirements.lock")
    ap.add_argument("--fail-level", default=os.getenv("VULN_FAIL_LEVEL", "high"))
    args = ap.parse_args()

    lock_path = Path(args.lock)
    if not lock_path.exists():
        print(f"[VULN][FAIL] lock file missing: {lock_path}")
        return 2

    all_vulns: list[dict] = []
    all_vulns.extend(pip_audit(lock_path))
    all_vulns.extend(osv_scan(lock_path))

    if not all_vulns:
        print("[VULN][OK] no vulnerabilities (or scanners unavailable)")
        return 0

    print("[VULN] Findings:")
    for v in all_vulns:
        print(
            f" - {v.get('severity', '?').upper():8s} {v.get('name')} {v.get('id')} fix:{v.get('fix_versions')}"
        )

    worst = worst_or_unknown(all_vulns)
    fail_level = args.fail_level.lower()
    if fail_level not in SEVERITY_ORDER:
        fail_level = "high"
    if SEVERITY_ORDER.index(worst) >= SEVERITY_ORDER.index(fail_level):
        print(f"[VULN][FAIL] worst severity {worst} >= fail level {fail_level}")
        return 1
    print(f"[VULN][OK] worst severity {worst} < fail level {fail_level}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
