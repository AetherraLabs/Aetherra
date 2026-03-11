"""Standalone tests for aetherra_coding.verification.

Run with:
    python test_verification_engine_standalone.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aetherra_coding.verification import VerificationEngine, verify_code


class TestVerificationEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = VerificationEngine(max_line_length=80)

    def test_valid_code_passes(self):
        code = "def add(x, y):\n    return x + y\n"
        result = self.engine.verify_code(code)
        self.assertTrue(result.passed)
        self.assertTrue(result.syntax_ok)
        self.assertTrue(result.imports_ok)
        self.assertTrue(result.style_ok)
        self.assertTrue(result.logic_ok)

    def test_syntax_error_fails(self):
        code = "def bad(:\n    pass\n"
        result = self.engine.verify_code(code)
        self.assertFalse(result.passed)
        self.assertFalse(result.syntax_ok)
        self.assertGreaterEqual(result.error_count(), 1)

    def test_missing_import_fails(self):
        code = "import this_module_should_not_exist_abc123\n\nvalue = 1\n"
        result = self.engine.verify_code(code)
        self.assertFalse(result.imports_ok)
        self.assertFalse(result.passed)
        self.assertTrue(any(i.category == "import" for i in result.issues))

    def test_relative_import_warns(self):
        code = "from .local_module import thing\n\nvalue = 1\n"
        result = self.engine.verify_code(code)
        # Relative import warning should not force import failure.
        self.assertTrue(result.imports_ok)
        self.assertTrue(any(i.severity == "warning" for i in result.issues))

    def test_line_length_style_error(self):
        code = "x = '" + ("a" * 100) + "'\n"
        result = self.engine.verify_code(code)
        self.assertFalse(result.style_ok)
        self.assertTrue(any(i.category == "style" for i in result.issues))

    def test_trailing_whitespace_style_error(self):
        code = "def f():    \n    return 1\n"
        result = self.engine.verify_code(code)
        self.assertFalse(result.style_ok)

    def test_tab_indentation_style_error(self):
        code = "def f():\n\treturn 1\n"
        result = self.engine.verify_code(code)
        self.assertFalse(result.style_ok)

    def test_eval_is_logic_error(self):
        code = "def f(s):\n    return eval(s)\n"
        result = self.engine.verify_code(code)
        self.assertFalse(result.logic_ok)
        self.assertFalse(result.passed)
        self.assertTrue(any("Dangerous call" in i.message for i in result.issues))

    def test_exec_is_logic_error(self):
        code = "def f(s):\n    exec(s)\n"
        result = self.engine.verify_code(code)
        self.assertFalse(result.logic_ok)

    def test_bare_except_is_warning(self):
        code = "def f():\n    try:\n        return 1\n    except:\n        return 0\n"
        result = self.engine.verify_code(code)
        self.assertTrue(result.logic_ok)
        self.assertTrue(any("Bare except" in i.message for i in result.issues))

    def test_broad_exception_is_warning(self):
        code = "def f():\n    try:\n        return 1\n    except Exception:\n        return 0\n"
        result = self.engine.verify_code(code)
        self.assertTrue(result.logic_ok)
        self.assertTrue(any("Broad except" in i.message for i in result.issues))

    def test_verify_file_reads_content(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "tmp_mod.py"
            p.write_text("def ok():\n    return True\n", encoding="utf-8")
            result = self.engine.verify_file(p)
            self.assertTrue(result.passed)

    def test_verify_file_read_error(self):
        result = self.engine.verify_file("this/path/does/not/exist.py")
        self.assertFalse(result.passed)
        self.assertTrue(any(i.category == "file" for i in result.issues))

    def test_convenience_function(self):
        result = verify_code("x = 1\n")
        self.assertTrue(result.passed)

    def test_mypy_skipped_when_disabled(self):
        result = self.engine.verify_code("x = 1\n", run_mypy=False)
        self.assertTrue(result.types_ok)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestVerificationEngine)
    total = suite.countTestCases()
    print(f"Running {total} verification tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)
