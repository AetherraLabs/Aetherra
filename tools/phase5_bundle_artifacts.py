#!/usr/bin/env python3
"""Phase 5 artifact bundler.

Runs the validation harness and rollup utility in one command and stores
outputs in a target artifact directory.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def bundle_artifacts(
    repo_root: Path,
    profile: str,
    runs: int,
    timeout: int,
    output_dir: Path,
    stamp: str,
    min_run_pass_rate: float | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"phase5_validation_{stamp}.json"
    rollup_path = output_dir / f"phase5_rollup_{stamp}.json"
    summary_path = output_dir / f"phase5_bundle_{stamp}.json"

    harness_cmd = [
        sys.executable,
        "tools/phase5_validation_harness.py",
        "--profile",
        profile,
        "--runs",
        str(runs),
        "--timeout",
        str(timeout),
        "--output",
        str(report_path),
    ]
    harness = _run(harness_cmd, repo_root)

    rollup_cmd = [
        sys.executable,
        "tools/phase5_report_rollup.py",
        "--inputs",
        str(report_path),
        "--output",
        str(rollup_path),
    ]
    rollup = _run(rollup_cmd, repo_root)

    report_data: dict[str, Any] = {}
    rollup_data: dict[str, Any] = {}
    try:
        report_data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        report_data = {}
    try:
        rollup_data = json.loads(rollup_path.read_text(encoding="utf-8"))
    except Exception:
        rollup_data = {}

    observed_rate = float(
        (rollup_data.get("summary") or {}).get(
            "aggregate_run_pass_rate",
            report_data.get("run_pass_rate", 0.0),
        )
        or 0.0
    )
    gate_enabled = min_run_pass_rate is not None
    gate_passed = (observed_rate >= float(min_run_pass_rate)) if gate_enabled else True

    payload = {
        "created_at": datetime.utcnow().isoformat(),
        "profile": profile,
        "runs": runs,
        "timeout": timeout,
        "artifacts": {
            "report": str(report_path),
            "rollup": str(rollup_path),
            "summary": str(summary_path),
        },
        "steps": {
            "harness": harness,
            "rollup": rollup,
        },
        "gates": {
            "min_run_pass_rate": min_run_pass_rate,
            "observed_run_pass_rate": observed_rate,
            "passed": gate_passed,
        },
    }

    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bundle phase5 validation artifacts")
    p.add_argument("--profile", choices=["quick", "full"], default="quick")
    p.add_argument("--runs", type=int, default=10)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--output-dir", default=".aetherra/reports/phase5")
    p.add_argument("--min-run-pass-rate", type=float, default=None)
    p.add_argument("--stamp", default=datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = repo_root / out_dir

    if args.dry_run:
        preview = {
            "profile": args.profile,
            "runs": int(args.runs),
            "timeout": int(args.timeout),
            "output_dir": str(out_dir),
            "min_run_pass_rate": args.min_run_pass_rate,
            "stamp": args.stamp,
        }
        print(json.dumps(preview, indent=2))
        return 0

    payload = bundle_artifacts(
        repo_root=repo_root,
        profile=args.profile,
        runs=max(1, int(args.runs)),
        timeout=max(1, int(args.timeout)),
        output_dir=out_dir,
        stamp=args.stamp,
        min_run_pass_rate=args.min_run_pass_rate,
    )

    harness_ok = bool(payload["steps"]["harness"]["ok"])
    rollup_ok = bool(payload["steps"]["rollup"]["ok"])
    gates_ok = bool(payload["gates"]["passed"])
    print(
        f"Bundle complete: harness_ok={harness_ok}, rollup_ok={rollup_ok}, gates_ok={gates_ok}, "
        f"summary={payload['artifacts']['summary']}"
    )
    return 0 if harness_ok and rollup_ok and gates_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
