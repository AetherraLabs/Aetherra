#!/usr/bin/env python3
"""Phase 5 report rollup utility.

Aggregates one or more JSON reports produced by tools/phase5_validation_harness.py
and emits a compact summary JSON for release/gate evidence.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any, cast


def _load_report(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return cast(dict[str, Any], payload)


def rollup_reports(paths: list[str]) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    for path in paths:
        try:
            payload = _load_report(path)
            payload["_path"] = path
            reports.append(payload)
        except Exception as exc:
            reports.append(
                {
                    "_path": path,
                    "status": "error",
                    "runs": 0,
                    "full_pass_runs": 0,
                    "run_pass_rate": 0.0,
                    "error": f"failed_to_read: {type(exc).__name__}: {exc}",
                }
            )

    total_reports = len(reports)
    passing_reports = sum(1 for r in reports if r.get("status") == "pass")
    total_runs = sum(int(r.get("runs", 0) or 0) for r in reports)
    total_full_pass_runs = sum(int(r.get("full_pass_runs", 0) or 0) for r in reports)
    aggregate_pass_rate = (total_full_pass_runs / total_runs) if total_runs else 0.0

    by_report = []
    for r in reports:
        by_report.append(
            {
                "path": r.get("_path", ""),
                "status": r.get("status", "unknown"),
                "runs": int(r.get("runs", 0) or 0),
                "full_pass_runs": int(r.get("full_pass_runs", 0) or 0),
                "run_pass_rate": float(r.get("run_pass_rate", 0.0) or 0.0),
                "failed_scenarios": int(r.get("failed", 0) or 0),
                "total_scenarios": int(r.get("total", 0) or 0),
                "error": r.get("error"),
            }
        )

    return {
        "summary": {
            "reports": total_reports,
            "passing_reports": passing_reports,
            "failing_reports": total_reports - passing_reports,
            "total_runs": total_runs,
            "full_pass_runs": total_full_pass_runs,
            "aggregate_run_pass_rate": round(aggregate_pass_rate, 4),
        },
        "reports": by_report,
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Roll up phase5 validation reports")
    p.add_argument(
        "--inputs",
        nargs="+",
        default=["phase5_validation_report*.json"],
        help="Input files or glob patterns",
    )
    p.add_argument("--output", default="phase5_validation_rollup.json")
    return p.parse_args()


def _expand_patterns(patterns: list[str]) -> list[str]:
    out: list[str] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            out.extend(matches)
        elif Path(pattern).exists():
            out.append(pattern)
    # Deduplicate preserving order
    seen = set()
    deduped: list[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def main() -> int:
    args = _parse_args()
    inputs = _expand_patterns(args.inputs)
    if not inputs:
        print("No input reports found")
        return 1

    payload = rollup_reports(inputs)
    Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = payload["summary"]
    print(
        f"Rollup: {summary['passing_reports']}/{summary['reports']} reports passing, "
        f"aggregate run pass-rate {summary['aggregate_run_pass_rate']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
