"""Standalone tests for tools/phase5_report_rollup.py.

Run with:
    python test_phase5_report_rollup_standalone.py
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

from tools.phase5_report_rollup import rollup_reports


class TestPhase5ReportRollup(unittest.TestCase):
    def _write(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_rollup_aggregates_rates(self):
        with tempfile.TemporaryDirectory() as td:
            p1 = Path(td) / "r1.json"
            p2 = Path(td) / "r2.json"
            self._write(
                p1,
                {
                    "status": "pass",
                    "runs": 10,
                    "full_pass_runs": 10,
                    "run_pass_rate": 1.0,
                    "failed": 0,
                    "total": 30,
                },
            )
            self._write(
                p2,
                {
                    "status": "fail",
                    "runs": 10,
                    "full_pass_runs": 8,
                    "run_pass_rate": 0.8,
                    "failed": 2,
                    "total": 30,
                },
            )

            out = rollup_reports([str(p1), str(p2)])
            self.assertEqual(out["summary"]["reports"], 2)
            self.assertEqual(out["summary"]["passing_reports"], 1)
            self.assertAlmostEqual(out["summary"]["aggregate_run_pass_rate"], 0.9, places=3)

    def test_rollup_handles_bad_json(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text("{ invalid json", encoding="utf-8")
            out = rollup_reports([str(bad)])
            self.assertEqual(out["summary"]["reports"], 1)
            self.assertEqual(out["summary"]["passing_reports"], 0)
            self.assertEqual(out["reports"][0]["status"], "error")

    def test_cli_writes_rollup(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "report.json"
            o = Path(td) / "rollup.json"
            self._write(
                r,
                {
                    "status": "pass",
                    "runs": 2,
                    "full_pass_runs": 2,
                    "run_pass_rate": 1.0,
                    "failed": 0,
                    "total": 6,
                },
            )

            cmd = [
                sys.executable,
                "tools/phase5_report_rollup.py",
                "--inputs",
                str(r),
                "--output",
                str(o),
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
            self.assertTrue(o.exists())
            payload = json.loads(o.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["reports"], 1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase5ReportRollup)
    total = suite.countTestCases()
    print(f"Running {total} phase-5 report-rollup tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
