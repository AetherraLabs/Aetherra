"""Standalone tests for tools/phase5_validation_harness.py.

Run with:
    python tests/legacy/root_standalone/test_phase5_validation_harness_standalone.py
"""

from __future__ import annotations

# Standard library imports
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Aetherra imports
from tools.phase5_validation_harness import build_plan, run_validation

ROOT_DIR = Path(__file__).resolve().parents[3]


class TestPhase5ValidationHarness(unittest.TestCase):
    def test_build_plan_quick_and_full(self):
        quick = build_plan("quick")
        full = build_plan("full")
        full_names = {s.name for s in full}
        quick_categories = {s.category for s in quick}
        full_categories = {s.category for s in full}

        assert len(quick) >= 3
        assert len(full) > len(quick)
        assert quick[0].name == "decision-governor-learning-chain"
        assert "governance" in quick_categories
        assert "performance" in quick_categories
        assert "integration" in full_categories
        assert "security" in full_categories
        assert "plugin-system-safety" in full_names
        assert "hub-blueprints-integration" in full_names
        assert "policy-governance-guardrails" in full_names
        assert "signature-verifier-security" in full_names
        assert "optimization-executor-safety" in full_names
        assert "phase5-harness-self-check" in full_names
        assert "phase5-rollup-self-check" in full_names

    def test_run_validation_aggregates_pass_fail(self):
        plan = build_plan("quick")[:2]

        def fake_runner(command, timeout):
            if "quality" in " ".join(command):
                return {
                    "ok": False,
                    "returncode": 1,
                    "duration_sec": 0.2,
                    "stdout": "",
                    "stderr": "failed",
                }
            return {
                "ok": True,
                "returncode": 0,
                "duration_sec": 0.1,
                "stdout": "ok",
                "stderr": "",
            }

        report = run_validation(plan, timeout=10, runner=fake_runner)
        assert report["total"] == 2
        assert report["passed"] == 1
        assert report["failed"] == 1
        assert report["status"] == "fail"
        assert report["runs"] == 1
        assert report["full_pass_runs"] == 0
        assert "category_summaries" in report
        assert any(
            row["category"] == "governance" for row in report["category_summaries"]
        )

    def test_run_validation_repeat_runs_reports_pass_rate(self):
        plan = build_plan("quick")[:1]
        call_counter = {"n": 0}

        def flaky_runner(command, timeout):
            call_counter["n"] += 1
            ok = call_counter["n"] in (1, 3)
            return {
                "ok": ok,
                "returncode": 0 if ok else 1,
                "duration_sec": 0.1,
                "stdout": "ok" if ok else "",
                "stderr": "" if ok else "failed",
            }

        report = run_validation(plan, timeout=10, runs=3, runner=flaky_runner)
        assert report["runs"] == 3
        assert report["full_pass_runs"] == 2
        assert round(report["run_pass_rate"] - 2 / 3, 3) == 0
        assert len(report["run_summaries"]) == 3

    def test_run_validation_handles_runner_interrupt(self):
        plan = build_plan("quick")[:1]

        def interrupting_runner(command, timeout):
            raise KeyboardInterrupt("simulated stop")

        report = run_validation(plan, timeout=10, runs=1, runner=interrupting_runner)
        assert report["status"] == "fail"
        assert report["passed"] == 0
        assert report["failed"] == 1
        assert "runner_exception" in report["scenarios"][0]["stderr"]

    def test_cli_dry_run_writes_plan(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.json"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_validation_harness.py"),
                "--profile",
                "quick",
                "--runs",
                "5",
                "--dry-run",
                "--output",
                str(out),
            ]
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 0
            assert out.exists()
            payload = json.loads(out.read_text(encoding="utf-8"))
            assert payload["profile"] == "quick"
            assert payload["runs"] == 5
            assert payload["total"] >= 3
            assert "category_summaries" in payload
            assert all("category" in row for row in payload["scenarios"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestPhase5ValidationHarness
    )
    total = suite.countTestCases()
    print(f"Running {total} phase-5 harness tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
