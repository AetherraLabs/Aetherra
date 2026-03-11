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
