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


ROOT_DIR = Path(__file__).resolve().parents[1]
LEGACY_STANDALONE_TEST_DIR = ROOT_DIR / "tests" / "legacy" / "root_standalone"


@dataclass
class Scenario:
    name: str
    command: list[str]
    category: str


def _legacy_standalone_test(filename: str) -> str:
    """Return an absolute path for a legacy standalone validation script."""
    return str(LEGACY_STANDALONE_TEST_DIR / filename)


def build_plan(profile: str = "quick") -> list[Scenario]:
    """Build a validation plan from a named profile."""
    quick = [
        Scenario(
            name="decision-governor-learning-chain",
            command=[
                sys.executable,
                _legacy_standalone_test(
                    "test_phase4_autonomy_learning_chain_standalone.py"
                ),
            ],
            category="governance",
        ),
        Scenario(
            name="learning-quality-and-latency",
            command=[
                sys.executable,
                _legacy_standalone_test(
                    "test_phase4_learning_quality_and_latency_standalone.py"
                ),
            ],
            category="performance",
        ),
        Scenario(
            name="memory-recall-and-consolidation",
            command=[
                sys.executable,
                _legacy_standalone_test(
                    "test_phase4_memory_engine_enhancement_standalone.py"
                ),
            ],
            category="performance",
        ),
    ]

    # Full profile extends quick with broader scenario coverage aligned to
    # roadmap Week 10 integration intent.
    full = (
        [
            Scenario(
                name="reflector-codegen-apply-chain",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_orchestrator_task5_standalone.py"),
                ],
                category="integration",
            ),
            Scenario(
                name="codegen-impact-approval-chain",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_analysis_engine_standalone.py"),
                ],
                category="integration",
            ),
            Scenario(
                name="code-verification-gates",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_verification_engine_standalone.py"),
                ],
                category="security",
            ),
        ]
        + quick
        + [
            Scenario(
                name="phase3-core-modules",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_phase3_modules_standalone.py"),
                ],
                category="integration",
            ),
            Scenario(
                name="plugin-reflector",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_plugins_reflector_standalone.py"),
                ],
                category="integration",
            ),
            Scenario(
                name="plugin-system-safety",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_plugin_system_standalone.py"),
                ],
                category="security",
            ),
            Scenario(
                name="hub-blueprints-integration",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_hub_blueprints_standalone.py"),
                ],
                category="integration",
            ),
            Scenario(
                name="policy-governance-guardrails",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_policy_manager_standalone.py"),
                ],
                category="governance",
            ),
            Scenario(
                name="signature-verifier-security",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_signature_verifier_standalone.py"),
                ],
                category="security",
            ),
            Scenario(
                name="optimization-executor-safety",
                command=[
                    sys.executable,
                    _legacy_standalone_test(
                        "test_optimization_executor_standalone.py"
                    ),
                ],
                category="performance",
            ),
            Scenario(
                name="phase5-harness-self-check",
                command=[
                    sys.executable,
                    _legacy_standalone_test(
                        "test_phase5_validation_harness_standalone.py"
                    ),
                ],
                category="integration",
            ),
            Scenario(
                name="phase5-rollup-self-check",
                command=[
                    sys.executable,
                    _legacy_standalone_test("test_phase5_report_rollup_standalone.py"),
                ],
                category="integration",
            ),
        ]
    )

    if profile == "full":
        return full
    return quick


def _run_subprocess(command: list[str], timeout: int) -> dict[str, Any]:
    started = time.perf_counter()
    child_env = dict(os.environ)
    child_env.setdefault("PYTHONIOENCODING", "utf-8")
    child_env.setdefault("PYTHONUTF8", "1")
    existing_python_path = child_env.get("PYTHONPATH")
    root_python_path = str(ROOT_DIR)
    if existing_python_path:
        child_env["PYTHONPATH"] = os.pathsep.join(
            [root_python_path, existing_python_path]
        )
    else:
        child_env["PYTHONPATH"] = root_python_path
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


def _build_category_summaries(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for row in results:
        category = str(row.get("category") or "uncategorized")
        summary = summaries.setdefault(
            category,
            {
                "category": category,
                "passed": 0,
                "failed": 0,
                "total": 0,
                "scenarios": set(),
            },
        )
        summary["total"] = int(summary["total"]) + 1
        summary["scenarios"].add(str(row.get("name") or ""))
        if bool(row.get("ok", False)):
            summary["passed"] = int(summary["passed"]) + 1
        else:
            summary["failed"] = int(summary["failed"]) + 1

    payload: list[dict[str, Any]] = []
    for category in sorted(summaries):
        summary = summaries[category]
        total = int(summary["total"])
        passed = int(summary["passed"])
        payload.append(
            {
                "category": category,
                "passed": passed,
                "failed": int(summary["failed"]),
                "total": total,
                "pass_rate": round((passed / total) if total else 0.0, 4),
                "status": "pass" if passed == total else "fail",
                "scenarios": sorted(s for s in summary["scenarios"] if s),
            }
        )
    return payload


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
                "category": scenario.category,
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
    category_summaries = _build_category_summaries(results)

    return {
        "status": "pass" if full_pass_runs == runs else "fail",
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "runs": runs,
        "full_pass_runs": full_pass_runs,
        "run_pass_rate": round(run_pass_rate, 4),
        "run_summaries": run_summaries,
        "category_summaries": category_summaries,
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
            "category_summaries": _build_category_summaries(
                [{"name": s.name, "category": s.category, "ok": True} for s in plan]
            ),
            "scenarios": [
                {"name": s.name, "category": s.category, "command": s.command}
                for s in plan
            ],
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
