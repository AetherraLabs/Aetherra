#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Verify that current environment matches requirements.lock.

Process:
 1. Read requirements.lock into set of lines (pkg==ver)
 2. Run pip freeze, filter to same pattern
 3. Compare sets; if drift found, list differences and exit non-zero

Usage:
  python tools/enforce_lock_sync.py --lock requirements.lock

Exit Codes:
  0 match
  1 drift
  2 lock missing
"""

from __future__ import annotations

# Standard library imports
import argparse
import re
import subprocess
from pathlib import Path

LINE_RE = re.compile(r"^([A-Za-z0-9_.\-]+)==([A-Za-z0-9_.\-]+)$")


def collect_freeze() -> set[str]:
    out = subprocess.check_output(
        ["python", "-m", "pip", "freeze"], text=True, encoding="utf-8", errors="replace"
    )
    items = set()
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("-") or line.startswith("#"):
            continue
        if line.startswith("@"):
            continue
        if " @ " in line:
            continue
        if LINE_RE.match(line):
            items.add(line)
    return items


def parse_lock(lock: Path) -> set[str]:
    items = set()
    for line in lock.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if LINE_RE.match(line):
            items.add(line)
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", default="requirements.lock")
    args = ap.parse_args()
    lock_path = Path(args.lock)
    if not lock_path.exists():
        print(f"[LOCK][FAIL] missing {lock_path}")
        return 2

    lock_set = parse_lock(lock_path)
    env_set = collect_freeze()

    missing = lock_set - env_set
    extra = env_set - lock_set

    if not missing and not extra:
        print("[LOCK][OK] environment matches lock file")
        return 0

    if missing:
        print("[LOCK][DRIFT] missing in environment:")
        for m in sorted(missing):
            print(f"  - {m}")
    if extra:
        print("[LOCK][DRIFT] unexpected extra packages:")
        for e in sorted(extra):
            print(f"  + {e}")

    print("[LOCK][FAIL] drift detected — regenerate lock or sync environment")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
