#!/usr/bin/env python3
"""Generate Week-10 integration matrix and regression evidence reports."""

from __future__ import annotations

import json
from pathlib import Path

from phase5_validation_harness import build_plan, run_validation


def main() -> int:
    out_dir = Path(".aetherra/reports/phase5")
    out_dir.mkdir(parents=True, exist_ok=True)

    full_report = run_validation(build_plan("full"), timeout=240, runs=1)
    quick_report = run_validation(build_plan("quick"), timeout=240, runs=10)

    full_path = out_dir / "phase5_validation_report_full_week10_matrix.json"
    quick_path = out_dir / "phase5_validation_report_quick_runs10_regression.json"

    full_path.write_text(json.dumps(full_report, indent=2), encoding="utf-8")
    quick_path.write_text(json.dumps(quick_report, indent=2), encoding="utf-8")

    print(
        f"full={full_report['status']} ({full_report['passed']}/{full_report['total']}), "
        f"quick={quick_report['status']} (full_pass_runs={quick_report['full_pass_runs']}/{quick_report['runs']})"
    )

    return 0 if full_report["status"] == "pass" and quick_report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
