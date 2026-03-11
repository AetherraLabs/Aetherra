"""Standalone tests for tools/phase5_bundle_artifacts.py.

Run with:
    python test_phase5_bundle_artifacts_standalone.py
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


class TestPhase5BundleArtifacts(unittest.TestCase):
    def test_cli_dry_run(self):
        cmd = [
            sys.executable,
            "tools/phase5_bundle_artifacts.py",
            "--profile",
            "quick",
            "--runs",
            "3",
            "--timeout",
            "120",
            "--dry-run",
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
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["profile"], "quick")
        self.assertEqual(payload["runs"], 3)
        self.assertIsNone(payload["min_run_pass_rate"])
        self.assertIsNone(payload["allowed_scenario_failures"])
        self.assertEqual(payload["scenario_min_pass_rate"], [])
        self.assertFalse(payload["emit_release_manifest"])
        self.assertIsNone(payload["release_manifest_version"])

    def test_bundle_generates_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "standalone_test"
            cmd = [
                sys.executable,
                "tools/phase5_bundle_artifacts.py",
                "--profile",
                "quick",
                "--runs",
                "1",
                "--timeout",
                "120",
                "--output-dir",
                td,
                "--stamp",
                stamp,
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

            report = Path(td) / f"phase5_validation_{stamp}.json"
            rollup = Path(td) / f"phase5_rollup_{stamp}.json"
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            self.assertTrue(report.exists())
            self.assertTrue(rollup.exists())
            self.assertTrue(summary.exists())

            bundle = json.loads(summary.read_text(encoding="utf-8"))
            self.assertTrue(bundle["steps"]["harness"]["ok"])
            self.assertTrue(bundle["steps"]["rollup"]["ok"])
            self.assertTrue(bundle["gates"]["passed"])
            self.assertIn("integrity", bundle)
            self.assertTrue(bundle["integrity"]["report_sha256"])
            self.assertTrue(bundle["integrity"]["rollup_sha256"])
            self.assertIn("trend", bundle)
            self.assertIn("categories", bundle)
            self.assertIn("results", bundle["categories"])
            self.assertTrue(bundle["categories"]["results"])
            self.assertIn("category_results", bundle["gates"])
            self.assertIn("release_manifest", bundle)
            self.assertFalse(bundle["release_manifest"]["enabled"])

    def test_bundle_emits_release_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "manifest_emit"
            cmd = [
                sys.executable,
                "tools/phase5_bundle_artifacts.py",
                "--profile",
                "quick",
                "--runs",
                "1",
                "--timeout",
                "120",
                "--output-dir",
                td,
                "--stamp",
                stamp,
                "--emit-release-manifest",
                "--release-manifest-version",
                "0.0.0-phase5-test",
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

            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            manifest = Path(td) / f"phase5_release_manifest_{stamp}.json"
            self.assertTrue(summary.exists())
            self.assertTrue(manifest.exists())

            bundle = json.loads(summary.read_text(encoding="utf-8"))
            self.assertTrue(bundle["release_manifest"]["enabled"])
            self.assertEqual(bundle["release_manifest"]["version"], "0.0.0-phase5-test")
            self.assertTrue(bundle["release_manifest"]["step"]["ok"])
            self.assertTrue(bundle["release_manifest"]["sha256"])

    def test_bundle_rejects_negative_failure_budget(self):
        cmd = [
            sys.executable,
            "tools/phase5_bundle_artifacts.py",
            "--profile",
            "quick",
            "--runs",
            "1",
            "--allowed-scenario-failures",
            "-1",
        ]
        proc = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, 2)

    def test_bundle_records_non_prod_failure_budget(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "budget_quick"
            cmd = [
                sys.executable,
                "tools/phase5_bundle_artifacts.py",
                "--profile",
                "quick",
                "--runs",
                "1",
                "--timeout",
                "120",
                "--output-dir",
                td,
                "--stamp",
                stamp,
                "--allowed-scenario-failures",
                "999",
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
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            self.assertTrue(bundle["gates"]["budget_applies"])
            self.assertEqual(bundle["gates"]["allowed_scenario_failures"], 999)
            self.assertTrue(bundle["gates"]["budget_passed"])

    def test_bundle_fails_when_scenario_threshold_not_met(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "scenario_threshold_fail"
            cmd = [
                sys.executable,
                "tools/phase5_bundle_artifacts.py",
                "--profile",
                "quick",
                "--runs",
                "1",
                "--timeout",
                "120",
                "--output-dir",
                td,
                "--stamp",
                stamp,
                "--scenario-min-pass-rate",
                "learning-quality-and-latency=1.1",
            ]
            proc = subprocess.run(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(proc.returncode, 1)
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            self.assertTrue(summary.exists())

            bundle = json.loads(summary.read_text(encoding="utf-8"))
            self.assertFalse(bundle["gates"]["passed"])

    def test_bundle_includes_trend_delta_against_previous_summary(self):
        with tempfile.TemporaryDirectory() as td:
            previous = Path(td) / "phase5_bundle_prev.json"
            previous.write_text(
                json.dumps(
                    {
                        "gates": {
                            "observed_run_pass_rate": 0.5,
                            "scenario_results": [
                                {
                                    "name": "learning-quality-and-latency",
                                    "observed_pass_rate": 0.5,
                                }
                            ],
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            stamp = "trend_check"
            cmd = [
                sys.executable,
                "tools/phase5_bundle_artifacts.py",
                "--profile",
                "quick",
                "--runs",
                "1",
                "--timeout",
                "120",
                "--output-dir",
                td,
                "--stamp",
                stamp,
                "--scenario-min-pass-rate",
                "learning-quality-and-latency=0.0",
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
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            self.assertTrue(bundle["trend"]["has_previous"])
            self.assertEqual(bundle["trend"]["previous_observed_run_pass_rate"], 0.5)
            self.assertGreaterEqual(
                bundle["trend"]["delta_observed_run_pass_rate"], 0.0
            )
            self.assertIn("category_deltas", bundle["trend"])
            self.assertEqual(len(bundle["gates"]["scenario_results"]), 1)
            self.assertTrue(bundle["gates"]["scenario_results"][0]["passed"])

    def test_bundle_fails_when_threshold_not_met(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "threshold_fail"
            cmd = [
                sys.executable,
                "tools/phase5_bundle_artifacts.py",
                "--profile",
                "quick",
                "--runs",
                "1",
                "--timeout",
                "120",
                "--output-dir",
                td,
                "--stamp",
                stamp,
                "--min-run-pass-rate",
                "1.1",
            ]
            proc = subprocess.run(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(proc.returncode, 1)

            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            self.assertTrue(summary.exists())
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            self.assertFalse(bundle["gates"]["passed"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase5BundleArtifacts)
    total = suite.countTestCases()
    print(f"Running {total} phase-5 bundle-artifacts tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
