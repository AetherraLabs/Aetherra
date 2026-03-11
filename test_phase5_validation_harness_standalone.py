"""Standalone tests for tools/phase5_validation_harness.py.

Run with:
    python test_phase5_validation_harness_standalone.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.phase5_validation_harness import build_plan, run_validation


class TestPhase5ValidationHarness(unittest.TestCase):
    def test_build_plan_quick_and_full(self):
        quick = build_plan("quick")
        full = build_plan("full")
        full_names = {s.name for s in full}
        quick_categories = {s.category for s in quick}
        full_categories = {s.category for s in full}

        self.assertGreaterEqual(len(quick), 3)
        self.assertGreater(len(full), len(quick))
        self.assertEqual(quick[0].name, "decision-governor-learning-chain")
        self.assertIn("governance", quick_categories)
        self.assertIn("performance", quick_categories)
        self.assertIn("integration", full_categories)
        self.assertIn("security", full_categories)
        self.assertIn("plugin-system-safety", full_names)
        self.assertIn("hub-blueprints-integration", full_names)
        self.assertIn("policy-governance-guardrails", full_names)
        self.assertIn("signature-verifier-security", full_names)
        self.assertIn("optimization-executor-safety", full_names)
        self.assertIn("phase5-harness-self-check", full_names)
        self.assertIn("phase5-rollup-self-check", full_names)

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
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["runs"], 1)
        self.assertEqual(report["full_pass_runs"], 0)
        self.assertIn("category_summaries", report)
        self.assertTrue(any(row["category"] == "governance" for row in report["category_summaries"]))

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
        self.assertEqual(report["runs"], 3)
        self.assertEqual(report["full_pass_runs"], 2)
        self.assertAlmostEqual(report["run_pass_rate"], 2 / 3, places=3)
        self.assertEqual(len(report["run_summaries"]), 3)

    def test_run_validation_handles_runner_interrupt(self):
        plan = build_plan("quick")[:1]

        def interrupting_runner(command, timeout):
            raise KeyboardInterrupt("simulated stop")

        report = run_validation(plan, timeout=10, runs=1, runner=interrupting_runner)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["passed"], 0)
        self.assertEqual(report["failed"], 1)
        self.assertIn("runner_exception", report["scenarios"][0]["stderr"])

    def test_cli_dry_run_writes_plan(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.json"
            cmd = [
                sys.executable,
                "tools/phase5_validation_harness.py",
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
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out.exists())
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["profile"], "quick")
            self.assertEqual(payload["runs"], 5)
            self.assertGreaterEqual(payload["total"], 3)
            self.assertIn("category_summaries", payload)
            self.assertTrue(all("category" in row for row in payload["scenarios"]))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestPhase5ValidationHarness
    )
    total = suite.countTestCases()
    print(f"Running {total} phase-5 harness tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
