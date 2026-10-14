"""Standalone tests for tools/phase5_bundle_artifacts.py.

Run with:
    python tests/legacy/root_standalone/test_phase5_bundle_artifacts_standalone.py
"""

from __future__ import annotations

# Standard library imports
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))


class TestPhase5BundleArtifacts(unittest.TestCase):
    def test_cli_dry_run(self):
        cmd = [
            sys.executable,
            str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert proc.returncode == 0
        payload = json.loads(proc.stdout)
        assert payload["profile"] == "quick"
        assert payload["runs"] == 3
        assert payload["min_run_pass_rate"] is None
        assert payload["allowed_scenario_failures"] is None
        assert payload["scenario_min_pass_rate"] == []
        assert not payload["emit_release_manifest"]
        assert payload["release_manifest_version"] is None

    def test_bundle_generates_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "standalone_test"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 0

            report = Path(td) / f"phase5_validation_{stamp}.json"
            rollup = Path(td) / f"phase5_rollup_{stamp}.json"
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            assert report.exists()
            assert rollup.exists()
            assert summary.exists()

            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert bundle["steps"]["harness"]["ok"]
            assert bundle["steps"]["rollup"]["ok"]
            assert bundle["gates"]["passed"]
            assert "integrity" in bundle
            assert bundle["integrity"]["report_sha256"]
            assert bundle["integrity"]["rollup_sha256"]
            assert "trend" in bundle
            assert "categories" in bundle
            assert "results" in bundle["categories"]
            assert bundle["categories"]["results"]
            assert "rollup_analysis" in bundle
            assert "grouped_trends" in bundle["rollup_analysis"]
            assert "category_results" in bundle["gates"]
            assert "release_manifest" in bundle
            assert not bundle["release_manifest"]["enabled"]

    def test_bundle_emits_release_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "manifest_emit"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 0

            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            manifest = Path(td) / f"phase5_release_manifest_{stamp}.json"
            assert summary.exists()
            assert manifest.exists()

            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert bundle["release_manifest"]["enabled"]
            assert bundle["release_manifest"]["version"] == "0.0.0-phase5-test"
            assert bundle["release_manifest"]["step"]["ok"]
            assert bundle["release_manifest"]["sha256"]

    def test_bundle_rejects_negative_failure_budget(self):
        cmd = [
            sys.executable,
            str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
            "--profile",
            "quick",
            "--runs",
            "1",
            "--allowed-scenario-failures",
            "-1",
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert proc.returncode == 2

    def test_bundle_records_non_prod_failure_budget(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "budget_quick"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 0
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert bundle["gates"]["budget_applies"]
            assert bundle["gates"]["allowed_scenario_failures"] == 999
            assert bundle["gates"]["budget_passed"]

    def test_bundle_fails_when_scenario_threshold_not_met(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "scenario_threshold_fail"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 1
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            assert summary.exists()

            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert not bundle["gates"]["passed"]

    def test_bundle_fails_when_category_threshold_not_met(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "category_threshold_fail"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                "--category-min-pass-rate",
                "integration=1.0",
            ]
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 1
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert "category_threshold_results" in bundle["gates"]
            assert not bundle["gates"]["category_threshold_results"][0]["passed"]
            assert not bundle["gates"]["passed"]

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
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 0
            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert bundle["trend"]["has_previous"]
            assert bundle["trend"]["previous_observed_run_pass_rate"] == 0.5
            assert bundle["trend"]["delta_observed_run_pass_rate"] >= 0.0
            assert "category_deltas" in bundle["trend"]
            assert "rollup_category_deltas" in bundle["trend"]
            assert "rollup_performance_deltas" in bundle["trend"]
            assert len(bundle["gates"]["scenario_results"]) == 1
            assert bundle["gates"]["scenario_results"][0]["passed"]

    def test_bundle_fails_when_threshold_not_met(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "threshold_fail"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 1

            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            assert summary.exists()
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert not bundle["gates"]["passed"]

    def test_bundle_fails_when_performance_threshold_not_met(self):
        with tempfile.TemporaryDirectory() as td:
            stamp = "performance_threshold_fail"
            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_bundle_artifacts.py"),
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
                "--performance-max-avg-duration-sec",
                "0.0001",
                "--performance-max-scenario-duration-sec",
                "0.0001",
                "--performance-min-pass-rate",
                "1.0",
            ]
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 1

            summary = Path(td) / f"phase5_bundle_{stamp}.json"
            assert summary.exists()
            bundle = json.loads(summary.read_text(encoding="utf-8"))
            assert "performance_thresholds" in bundle["gates"]
            assert not bundle["gates"]["performance_thresholds_passed"]
            assert not bundle["gates"]["passed"]


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase5BundleArtifacts)
    total = suite.countTestCases()
    print(f"Running {total} phase-5 bundle-artifacts tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
