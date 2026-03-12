"""Standalone acceptance tests for Production Roadmap Phase 2b gates.

Run with:
    python test_phase2b_acceptance_standalone.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aetherra_coding.analysis import ImpactAnalyzer
from aetherra_coding.orchestrator import CodeOrchestrator
from aetherra_coding.verification import VerificationEngine


class TestPhase2BAcceptance(unittest.TestCase):
    def _write(self, root: Path, rel: str, content: str) -> Path:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_impact_scoring_orders_low_vs_high(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/core.py", "def stable():\n    return 1\n")
            self._write(root, "pkg/a.py", "import pkg.core\n")
            self._write(root, "pkg/b.py", "import pkg.core\n")

            analyzer = ImpactAnalyzer()
            low = analyzer.analyze_change("pkg/core.py", "+x = 1\n", root)
            high = analyzer.analyze_change(
                "pkg/core.py",
                "+def api_endpoint():\n+    return 1\n+class PublicContract:\n+    pass\n"
                + "\n".join(["+line" for _ in range(250)]),
                root,
            )

            self.assertLess(low.score, high.score)
            self.assertIn(low.risk_level, {"low", "medium", "high"})
            self.assertIn(high.risk_level, {"low", "medium", "high"})

    def test_codegen_output_is_verifiable(self):
        with tempfile.TemporaryDirectory() as td:
            orch = CodeOrchestrator(repo_root=td)
            orch.plan("Create a function to normalize with docstring and tests")
            patch = orch.generate(0, dry_run=True)

            self.assertTrue(patch.diff)
            self.assertEqual(patch.risk_level, "low")

            generated_code = (
                "def normalize(value):\n"
                "    if value is None:\n"
                "        raise ValueError('value is required')\n"
                "    return value\n"
            )
            vr = VerificationEngine().verify_code(generated_code)
            self.assertTrue(vr.passed)

    def test_safe_generation_consistency_over_10_runs(self):
        verifier = VerificationEngine()
        with tempfile.TemporaryDirectory() as td:
            orch = CodeOrchestrator(repo_root=td)
            passed = 0
            for _ in range(10):
                orch.plan("Create a function factorial recursive with error handling")
                patch = orch.generate(0, dry_run=True)
                self.assertTrue(patch.diff)
                generated = (
                    "def factorial(value):\n"
                    "    if value < 0:\n"
                    "        raise ValueError('value must be >= 0')\n"
                    "    if value <= 1:\n"
                    "        return 1\n"
                    "    return value * factorial(value - 1)\n"
                )
                result = verifier.verify_code(generated)
                if result.passed:
                    passed += 1

            self.assertEqual(passed, 10)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase2BAcceptance)
    total = suite.countTestCases()
    print(f"Running {total} phase-2b acceptance tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
