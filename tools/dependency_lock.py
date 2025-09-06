#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Generate a simple frozen dependency lock file (requirements.lock).

Strategy (alpha):
- Assumes project (and optional extras) already installed in current venv
- Runs `pip freeze` and filters out editable local project path lines (-e .)
- Writes deterministic sorted list to requirements.lock

Usage:
  python tools/dependency_lock.py            # writes requirements.lock
  python tools/dependency_lock.py --output custom.lock

Notes:
- For reproducible builds in CI, commit the produced lock file.
- In future we can adopt pip-tools or uv for resolution; this script is intentionally minimal.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="requirements.lock")
    args = ap.parse_args()

    cmd = [sys.executable, "-m", "pip", "freeze"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out, _ = proc.communicate()
    if proc.returncode != 0:
        print("[LOCK][FAIL] pip freeze failed")
        return proc.returncode

    lines = []
    for line in out.splitlines():
        if not line or line.startswith("#"):
            continue
        if line.startswith("-e ") and (
            "aetherra" in line.lower() or line.endswith(".")
        ):
            continue  # skip editable project reference
        lines.append(line)

    lines = sorted(set(lines), key=str.lower)
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[LOCK] Wrote {args.output} ({len(lines)} entries)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
