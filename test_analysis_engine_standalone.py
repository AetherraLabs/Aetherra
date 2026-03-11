"""Standalone tests for aetherra_coding.analysis.

Run with:
    python test_analysis_engine_standalone.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aetherra_coding.analysis import (
    DependencyGraphBuilder,
    ImpactAnalyzer,
    analyze_patch,
)


class TestAnalysisEngine(unittest.TestCase):
    def _write(self, root: Path, rel: str, content: str) -> Path:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_dependency_graph_build(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/a.py", "import pkg.b\n")
            self._write(root, "pkg/b.py", "x = 1\n")
            gb = DependencyGraphBuilder()
            graph = gb.build_graph(root)
            self.assertIn(Path("pkg/a.py"), graph)

    def test_find_dependents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/a.py", "import pkg.b\n")
            self._write(root, "pkg/b.py", "x = 1\n")
            gb = DependencyGraphBuilder()
            gb.build_graph(root)
            deps = gb.find_dependents("pkg/b.py")
            self.assertIn(Path("pkg/a.py"), deps)

    def test_find_transitive_dependents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/a.py", "import pkg.b\n")
            self._write(root, "pkg/b.py", "import pkg.c\n")
            self._write(root, "pkg/c.py", "x = 1\n")
            gb = DependencyGraphBuilder()
            gb.build_graph(root)
            deps = gb.find_transitive_dependents("pkg/c.py")
            self.assertIn(Path("pkg/a.py"), deps)
            self.assertIn(Path("pkg/b.py"), deps)

    def test_detect_cycles(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/a.py", "import pkg.b\n")
            self._write(root, "pkg/b.py", "import pkg.a\n")
            gb = DependencyGraphBuilder()
            gb.build_graph(root)
            cycles = gb.detect_cycles()
            self.assertTrue(len(cycles) >= 1)

    def test_impact_analyze_low(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/a.py", "x = 1\n")
            ia = ImpactAnalyzer()
            rp = ia.analyze_change("pkg/a.py", "+x = 2\n", root)
            self.assertIn(rp.risk_level, {"low", "medium", "high"})
            self.assertGreaterEqual(rp.score, 0.0)

    def test_impact_api_change_factor(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/a.py", "def f():\n    return 1\n")
            ia = ImpactAnalyzer()
            rp = ia.analyze_change("pkg/a.py", "+def api_func():\n+    return 1\n", root)
            self.assertGreater(rp.factors["api_change_factor"], 0.0)

    def test_impact_suggests_tests(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "pkg/a.py", "x=1\n")
            ia = ImpactAnalyzer()
            rp = ia.analyze_change("pkg/a.py", "+x=2\n", root)
            self.assertTrue(any("test_a.py" in t for t in rp.suggested_tests))

    def test_impact_for_test_file_lowers_test_factor(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "tests/unit/test_mod.py", "def test_x():\n    assert True\n")
            ia = ImpactAnalyzer()
            rp = ia.analyze_change("tests/unit/test_mod.py", "+assert True\n", root)
            self.assertEqual(rp.factors["test_factor"], 0.0)

    def test_analyze_patch_backward_compat(self):
        diff = "*** Update File: a.py\n+line\n*** Add File: b.py\n+line\n"
        report = analyze_patch(diff)
        self.assertEqual(report.risk_level, "low")
        self.assertEqual(len(report.touched_files), 2)

    def test_analyze_patch_risk_levels(self):
        base = "\n".join([f"*** Update File: f{i}.py" for i in range(13)])
        report = analyze_patch(base)
        self.assertEqual(report.risk_level, "high")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAnalysisEngine)
    total = suite.countTestCases()
    print(f"Running {total} analysis tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
