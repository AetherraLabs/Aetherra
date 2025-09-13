#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parse Baseline Regression Gate

Compares a newly generated parse_baseline.json against a reference (e.g., main branch)
and enforces thresholds for increases in specific error categories.

Exit Codes:
 0 - OK (no regression)
 1 - Regression detected (threshold exceeded)
 2 - Input / usage error

Default thresholds:
  --abs-threshold 5      (absolute allowed increase per targeted code)
  --rel-threshold 0.10   (relative allowed increase (10%))
Targeted codes: PARSE_ERROR, VALIDATION_ERROR

Usage:
  python tools/parse_baseline_regression_gate.py --new path/to/new/parse_baseline.json --ref path/to/ref/parse_baseline.json

The gate prints a JSON summary to stdout for CI consumption.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

TARGET_CODES = {"PARSE_ERROR", "VALIDATION_ERROR"}


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Failed to read {path}: {e}")


def extract_counts(data: dict) -> dict:
    by_code = data.get("by_code") or {}
    # Accept either structure: {"PARSE_ERROR": count} or nested {code:{count:int,...}}
    counts = {}
    for k, v in by_code.items():
        if isinstance(v, dict) and "count" in v:
            counts[k] = v.get("count", 0)
        elif isinstance(v, int):
            counts[k] = v
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True, help="New baseline JSON (current run)")
    ap.add_argument(
        "--ref", required=True, help="Reference baseline JSON (previous/main)"
    )
    ap.add_argument(
        "--abs-threshold",
        type=int,
        default=5,
        help="Absolute allowed increase per code",
    )
    ap.add_argument(
        "--rel-threshold",
        type=float,
        default=0.10,
        help="Relative allowed increase fraction per code",
    )
    ap.add_argument(
        "--fail-on-missing-ref",
        action="store_true",
        help="Fail if reference file missing instead of treating as zero counts",
    )
    args = ap.parse_args()

    new_path = Path(args.new)
    ref_path = Path(args.ref)
    if not new_path.exists():
        print(json.dumps({"ok": False, "error": f"new baseline missing: {new_path}"}))
        return 2

    if not ref_path.exists():
        if args.fail_on_missing_ref:
            print(
                json.dumps(
                    {"ok": False, "error": f"reference baseline missing: {ref_path}"}
                )
            )
            return 2
        ref_data = {"by_code": {}}
    else:
        ref_data = load(ref_path)
    new_data = load(new_path)

    ref_counts = extract_counts(ref_data)
    new_counts = extract_counts(new_data)

    regressions = []
    for code in TARGET_CODES:
        old = ref_counts.get(code, 0)
        new = new_counts.get(code, 0)
        if new > old:
            delta = new - old
            rel = (delta / old) if old else 1.0  # 100% relative if old=0 and new>0
            if delta > args.abs_threshold and rel > args.rel_threshold:
                regressions.append(
                    {
                        "code": code,
                        "old": old,
                        "new": new,
                        "delta": delta,
                        "relative_increase": round(rel, 4),
                    }
                )

    ok = len(regressions) == 0
    summary = {
        "ok": ok,
        "timestamp": datetime.now(UTC).isoformat(),
        "new_counts": {k: new_counts.get(k, 0) for k in TARGET_CODES},
        "ref_counts": {k: ref_counts.get(k, 0) for k in TARGET_CODES},
        "abs_threshold": args.abs_threshold,
        "rel_threshold": args.rel_threshold,
        "regressions": regressions,
    }
    print(json.dumps(summary, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
