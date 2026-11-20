"""Standalone tests for tools/phase5_report_rollup.py.

Run with:
    python tests/legacy/root_standalone/test_phase5_report_rollup_standalone.py
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
from tools.phase5_report_rollup import rollup_reports

ROOT_DIR = Path(__file__).resolve().parents[3]


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
                    "category_summaries": [
                        {
                            "category": "performance",
                            "passed": 2,
                            "failed": 0,
                            "total": 2,
                            "status": "pass",
                            "scenarios": ["learning-quality-and-latency"],
                        }
                    ],
                    "scenarios": [
                        {
                            "name": "learning-quality-and-latency",
                            "category": "performance",
                            "ok": True,
                            "duration_sec": 0.1,
                        },
                        {
                            "name": "learning-quality-and-latency",
                            "category": "performance",
                            "ok": True,
                            "duration_sec": 0.2,
                        },
                    ],
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
                    "category_summaries": [
                        {
                            "category": "performance",
                            "passed": 1,
                            "failed": 1,
                            "total": 2,
                            "status": "fail",
                            "scenarios": ["memory-recall-and-consolidation"],
                        },
                        {
                            "category": "governance",
                            "passed": 1,
                            "failed": 0,
                            "total": 1,
                            "status": "pass",
                            "scenarios": ["decision-governor-learning-chain"],
                        },
                    ],
                    "scenarios": [
                        {
                            "name": "memory-recall-and-consolidation",
                            "category": "performance",
                            "ok": False,
                            "duration_sec": 0.4,
                        },
                        {
                            "name": "memory-recall-and-consolidation",
                            "category": "performance",
                            "ok": True,
                            "duration_sec": 0.3,
                        },
                    ],
                },
            )

            out = rollup_reports([str(p1), str(p2)])
            assert out["summary"]["reports"] == 2
            assert out["summary"]["passing_reports"] == 1
            assert round(out["summary"]["aggregate_run_pass_rate"] - 0.9, 3) == 0
            assert "categories" in out
            perf = next(
                row
                for row in out["categories"]["results"]
                if row["category"] == "performance"
            )
            assert perf["reports"] == 2
            assert perf["total"] == 4
            assert round(perf["aggregate_pass_rate"] - 0.75, 3) == 0
            assert "performance_evidence" in out
            assert out["performance_evidence"]["samples"] == 4
            assert out["performance_evidence"]["scenario_count"] == 2
            assert "performance_thresholds" in out
            assert out["performance_thresholds"]["passed"]

    def test_rollup_performance_threshold_gate_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p1 = Path(td) / "r1.json"
            self._write(
                p1,
                {
                    "status": "pass",
                    "runs": 1,
                    "full_pass_runs": 1,
                    "run_pass_rate": 1.0,
                    "failed": 0,
                    "total": 3,
                    "category_summaries": [
                        {
                            "category": "performance",
                            "passed": 1,
                            "failed": 0,
                            "total": 1,
                            "status": "pass",
                            "scenarios": ["learning-quality-and-latency"],
                        }
                    ],
                    "scenarios": [
                        {
                            "name": "learning-quality-and-latency",
                            "category": "performance",
                            "ok": True,
                            "duration_sec": 0.2,
                        }
                    ],
                },
            )

            out = rollup_reports(
                [str(p1)],
                performance_max_avg_duration_sec=0.001,
                performance_max_scenario_duration_sec=0.001,
                performance_min_pass_rate=1.0,
            )
            assert not out["performance_thresholds"]["passed"]
            assert len(out["performance_thresholds"]["checks"]) == 3

    def test_rollup_grouped_trends_against_previous_rollup(self):
        with tempfile.TemporaryDirectory() as td:
            p1 = Path(td) / "r1.json"
            self._write(
                p1,
                {
                    "status": "pass",
                    "runs": 1,
                    "full_pass_runs": 1,
                    "run_pass_rate": 1.0,
                    "failed": 0,
                    "total": 3,
                    "category_summaries": [
                        {
                            "category": "performance",
                            "passed": 1,
                            "failed": 0,
                            "total": 1,
                            "status": "pass",
                            "scenarios": ["learning-quality-and-latency"],
                        }
                    ],
                    "scenarios": [
                        {
                            "name": "learning-quality-and-latency",
                            "category": "performance",
                            "ok": True,
                            "duration_sec": 0.2,
                        }
                    ],
                },
            )

            previous = {
                "categories": {
                    "results": [{"category": "performance", "aggregate_pass_rate": 0.5}]
                },
                "performance_evidence": {
                    "avg_duration_sec": 0.5,
                    "max_duration_sec": 0.8,
                },
            }
            out = rollup_reports([str(p1)], previous_rollup=previous)
            assert out["grouped_trends"]["has_previous"]
            assert out["grouped_trends"]["category_deltas"]
            assert out["grouped_trends"]["performance_deltas"]

    def test_rollup_handles_bad_json(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text("{ invalid json", encoding="utf-8")
            out = rollup_reports([str(bad)])
            assert out["summary"]["reports"] == 1
            assert out["summary"]["passing_reports"] == 0
            assert out["reports"][0]["status"] == "error"
            assert out["categories"]["results"] == []
            assert out["performance_evidence"]["samples"] == 0

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
                    "category_summaries": [
                        {
                            "category": "performance",
                            "passed": 1,
                            "failed": 0,
                            "total": 1,
                            "status": "pass",
                            "scenarios": ["learning-quality-and-latency"],
                        }
                    ],
                    "scenarios": [
                        {
                            "name": "learning-quality-and-latency",
                            "category": "performance",
                            "ok": True,
                            "duration_sec": 0.2,
                        }
                    ],
                },
            )

            cmd = [
                sys.executable,
                str(ROOT_DIR / "tools" / "phase5_report_rollup.py"),
                "--inputs",
                str(r),
                "--output",
                str(o),
            ]
            proc = subprocess.run(
                cmd,
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.returncode == 0
            assert o.exists()
            payload = json.loads(o.read_text(encoding="utf-8"))
            assert payload["summary"]["reports"] == 1
            assert "categories" in payload
            assert "performance_evidence" in payload
            assert "performance_thresholds" in payload
            assert "grouped_trends" in payload


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase5ReportRollup)
    total = suite.countTestCases()
    print(f"Running {total} phase-5 report-rollup tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
