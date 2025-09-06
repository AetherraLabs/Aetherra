#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Provenance Tag Wrapper

Selects the appropriate tagging helper:
 - Prefer annotated provenance (create_annotated_tag.py) for rich manifest embedding.
 - Fallback to simple tag (create_provenance_tag.py) if annotated helper fails or missing.

Provides a unified interface so CI can call a single script.

Usage (print only):
  python tools/provenance_tag_wrapper.py --version 0.1.0-alpha.1

Usage (apply):
  python tools/provenance_tag_wrapper.py --version 0.1.0-alpha.1 --tag v0.1.0-alpha.1 --apply

Exit codes:
  0 success
  2 invalid args / both helpers missing
  3 both helpers failed
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HELPERS = [
    ("annotated", Path("tools/create_annotated_tag.py")),
    ("simple", Path("tools/create_provenance_tag.py")),
]


def run_helper(kind: str, path: Path, args: list[str]) -> int:
    if not path.is_file():
        return 127
    cmd = [sys.executable, str(path)] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    except Exception as e:  # pragma: no cover - external failure
        print(f"[WRAPPER][{kind}] invoke error: {e}", file=sys.stderr)
        return 126
    if res.returncode == 0:
        print(f"[WRAPPER][{kind}] OK")
        print(res.stdout.rstrip())
    else:
        print(
            f"[WRAPPER][{kind}] failed rc={res.returncode}: {res.stdout}\n{res.stderr}",
            file=sys.stderr,
        )
    return res.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Unified provenance tag helper")
    ap.add_argument("--version", required=True)
    ap.add_argument("--tag", help="Git tag name if applying")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--manifest", help="Optional manifest path")
    ap.add_argument("--lock", default="requirements.lock")
    ap.add_argument("--print-only", action="store_true")
    args = ap.parse_args(argv)

    shared = ["--version", args.version, "--lock", args.lock]
    if args.manifest:
        shared += ["--manifest", args.manifest]
    if args.print_only:
        shared.append("--print-only")
    if args.apply:
        if not args.tag:
            print("[WRAPPER][ERROR] --tag required with --apply", file=sys.stderr)
            return 2
        shared += ["--tag", args.tag, "--apply"]

    # Try annotated first, fallback to simple
    failures = []
    for kind, path in HELPERS:
        rc = run_helper(kind, path, shared)
        if rc == 0:
            return 0
        failures.append((kind, rc))
    print(f"[WRAPPER] all helpers failed: {failures}", file=sys.stderr)
    return 3


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
