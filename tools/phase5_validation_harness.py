#!/usr/bin/env python3
"""Phase 5 validation harness.

Provides a structured runner for roadmap validation scenarios with a JSON report.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Scenario:
    name: str
    command: list[str]


def build_plan(profile: str = "quick") -> list[Scenario]:
    """Build a validation plan from a named profile."""
    quick = [
        Scenario(
            name="decision-governor-learning-chain",
            command=[
                sys.executable,
                "test_phase4_autonomy_learning_chain_standalone.py",
            ],
        ),
        Scenario(
            name="learning-quality-and-latency",
            command=[
                sys.executable,
                "test_phase4_learning_quality_and_latency_standalone.py",
            ],
        ),
        Scenario(
            name="memory-recall-and-consolidation",
            command=[
                sys.executable,
                "test_phase4_memory_engine_enhancement_standalone.py",
            ],
        ),
    ]

    # Full profile extends quick with broader scenario coverage aligned to
    # roadmap Week 10 integration intent.
    full = [
        Scenario(
            name="reflector-codegen-apply-chain",
            command=[sys.executable, "test_orchestrator_task5_standalone.py"],
        ),
        Scenario(
            name="codegen-impact-approval-chain",
            command=[sys.executable, "test_analysis_engine_standalone.py"],
        ),
        Scenario(
            name="code-verification-gates",
            command=[sys.executable, "test_verification_engine_standalone.py"],
        ),
    ] + quick + [
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


def _run_subprocess(command: list[str], timeout: int) -> dict[str, Any]:
    started = time.perf_counter()
    child_env = dict(os.environ)
    child_env.setdefault("PYTHONIOENCODING", "utf-8")
    child_env.setdefault("PYTHONUTF8", "1")
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=child_env,
        )
        elapsed = time.perf_counter() - started
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "duration_sec": round(elapsed, 4),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        return {
            "ok": False,
            "returncode": 124,
            "duration_sec": round(elapsed, 4),
            "stdout": str(exc.stdout or ""),
            "stderr": f"timeout after {timeout}s",
        }
    except KeyboardInterrupt:
        elapsed = time.perf_counter() - started
        return {
            "ok": False,
            "returncode": 130,
            "duration_sec": round(elapsed, 4),
            "stdout": "",
            "stderr": "interrupted",
        }


def run_validation(
    plan: list[Scenario],
    timeout: int = 180,
    runs: int = 1,
    runner: Callable[[list[str], int], dict[str, Any]] = _run_subprocess,
) -> dict[str, Any]:
    """Execute validation scenarios and return aggregate results.

    When runs > 1, all scenarios are executed per run and pass-rate evidence
    is included in the report.
    """
    runs = max(1, int(runs))
    results: list[dict[str, Any]] = []
    run_summaries: list[dict[str, Any]] = []

    for run_index in range(1, runs + 1):
        run_rows: list[dict[str, Any]] = []
        for scenario in plan:
            try:
                outcome = runner(scenario.command, timeout)
            except BaseException as exc:
                outcome = {
                    "ok": False,
                    "returncode": 99,
                    "duration_sec": 0.0,
                    "stdout": "",
                    "stderr": f"runner_exception: {type(exc).__name__}: {exc}",
                }
            row = {
                "run": run_index,
                "name": scenario.name,
                "command": scenario.command,
                "ok": bool(outcome.get("ok", False)),
                "returncode": int(outcome.get("returncode", 1)),
                "duration_sec": float(outcome.get("duration_sec", 0.0)),
                "stdout": str(outcome.get("stdout", "")),
                "stderr": str(outcome.get("stderr", "")),
            }
            run_rows.append(row)
            results.append(row)

        run_passed = sum(1 for row in run_rows if row["ok"])
        run_total = len(run_rows)
        run_summaries.append(
            {
                "run": run_index,
                "status": "pass" if run_passed == run_total else "fail",
                "passed": run_passed,
                "failed": run_total - run_passed,
                "total": run_total,
            }
        )

    passed = sum(1 for row in results if row["ok"])
    total = len(results)
    full_pass_runs = sum(1 for rs in run_summaries if rs["status"] == "pass")
    run_pass_rate = (full_pass_runs / runs) if runs else 0.0

    return {
        "status": "pass" if full_pass_runs == runs else "fail",
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "runs": runs,
        "full_pass_runs": full_pass_runs,
        "run_pass_rate": round(run_pass_rate, 4),
        "run_summaries": run_summaries,
        "scenarios": results,
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Phase 5 validation harness")
    p.add_argument("--profile", choices=["quick", "full"], default="quick")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--runs", type=int, default=1)
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
            "runs": max(1, int(args.runs)),
            "total": len(plan),
            "scenarios": [{"name": s.name, "command": s.command} for s in plan],
        }
        Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 0

    report = run_validation(plan=plan, timeout=args.timeout, runs=args.runs)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"Validation status: {report['status']} ({report['passed']}/{report['total']} passed)"
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
