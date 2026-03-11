#!/usr/bin/env python3
"""Phase 5 validation harness.

Provides a structured runner for roadmap validation scenarios with a JSON report.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List


@dataclass
class Scenario:
    name: str
    command: List[str]


def build_plan(profile: str = "quick") -> List[Scenario]:
    """Build a validation plan from a named profile."""
    quick = [
        Scenario(
            name="decision-governor-learning-chain",
            command=[sys.executable, "test_phase4_autonomy_learning_chain_standalone.py"],
        ),
        Scenario(
            name="learning-quality-and-latency",
            command=[sys.executable, "test_phase4_learning_quality_and_latency_standalone.py"],
        ),
        Scenario(
            name="memory-recall-and-consolidation",
            command=[sys.executable, "test_phase4_memory_engine_enhancement_standalone.py"],
        ),
    ]

    full = quick + [
        Scenario(
            name="phase3-core-modules",
            command=[sys.executable, "test_phase3_modules_standalone.py"],
        ),
        Scenario(
            name="plugin-reflector",
            command=[sys.executable, "test_plugins_reflector_standalone.py"],
        ),
    ]

    if profile == "full":
        return full
    return quick


def _run_subprocess(command: List[str], timeout: int) -> Dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    elapsed = time.perf_counter() - started
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "duration_sec": round(elapsed, 4),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def run_validation(
    plan: List[Scenario],
    timeout: int = 180,
    runner: Callable[[List[str], int], Dict[str, Any]] = _run_subprocess,
) -> Dict[str, Any]:
    """Execute validation scenarios and return aggregate results."""
    results: List[Dict[str, Any]] = []

    for scenario in plan:
        outcome = runner(scenario.command, timeout)
        results.append(
            {
                "name": scenario.name,
                "command": scenario.command,
                "ok": bool(outcome.get("ok", False)),
                "returncode": int(outcome.get("returncode", 1)),
                "duration_sec": float(outcome.get("duration_sec", 0.0)),
                "stdout": str(outcome.get("stdout", "")),
                "stderr": str(outcome.get("stderr", "")),
            }
        )

    passed = sum(1 for row in results if row["ok"])
    total = len(results)
    return {
        "status": "pass" if passed == total else "fail",
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "scenarios": results,
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Phase 5 validation harness")
    p.add_argument("--profile", choices=["quick", "full"], default="quick")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--output", default="phase5_validation_report.json")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Emit selected scenario plan and exit without execution",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    plan = build_plan(args.profile)

    if args.dry_run:
        payload = {
            "profile": args.profile,
            "total": len(plan),
            "scenarios": [{"name": s.name, "command": s.command} for s in plan],
        }
        Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 0

    report = run_validation(plan=plan, timeout=args.timeout)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Validation status: {report['status']} ({report['passed']}/{report['total']} passed)")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
