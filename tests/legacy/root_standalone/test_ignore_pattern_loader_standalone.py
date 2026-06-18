#!/usr/bin/env python
"""
Standalone test runner for IgnorePatternLoader.

Avoids Aetherra engine initialization.

Run: python tests/legacy/root_standalone/test_ignore_pattern_loader_standalone.py
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add workspace root to path
ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from Aetherra.aetherra_core.system.ignore_pattern_loader import (
    IgnorePattern,
    IgnorePatternLoader,
)


class TestIgnorePatternLoaderStandalone(unittest.TestCase):
    """Standalone tests for IgnorePatternLoader without engine dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_loader(self):
        """Test creating pattern loader."""
        loader = IgnorePatternLoader(str(self.workspace))
        assert loader is not None
        assert loader.root_dir == self.workspace

    def test_02_load_default_patterns(self):
        """Test loading default patterns."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=True)
        success, patterns = loader.load()
        assert success, "Load should succeed"
        assert len(patterns) > 0, "Should have default patterns"

    def test_03_load_from_ignore_file(self):
        """Test loading patterns from .aetherraignore file."""
        # Create .aetherraignore file
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("# Comment\nbuild/\ndist/\n*.pyc\n")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        success, patterns = loader.load()
        assert success
        assert "build/" in patterns
        assert "dist/" in patterns
        assert "*.pyc" in patterns

    def test_04_ignore_file_comments(self):
        """Test that comments are ignored."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("# This is a comment\n*.pyc\n\nbuild/\n")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        success, patterns = loader.load()
        assert success
        assert len(patterns) == 2

    def test_05_negation_patterns(self):
        """Test negation patterns."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("*.log\n!important.log\n")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        success, patterns = loader.load()
        assert success

        # test.log should be ignored
        assert loader.should_ignore("test.log")

        # important.log should NOT be ignored (negation)
        assert not loader.should_ignore("important.log")

    def test_06_should_ignore_simple(self):
        """Test should_ignore for simple patterns."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="*.pyc"),
            IgnorePattern(pattern="__pycache__/", is_directory=True),
        ]

        assert loader.should_ignore("test.pyc")
        assert not loader.should_ignore("test.py")
        assert loader.should_ignore("__pycache__/modules")

    def test_07_should_ignore_directory(self):
        """Test should_ignore_directory."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="build/", is_directory=True),
            IgnorePattern(pattern="dist/", is_directory=True),
        ]

        assert loader.should_ignore_directory("build")
        assert loader.should_ignore_directory("dist")
        assert not loader.should_ignore_directory("src")

    def test_08_normalize_pattern(self):
        """Test pattern normalization."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)

        # Test backslash normalization
        normalized = loader._normalize_pattern("src\\main\\*.py")
        assert "/" in normalized
        assert "\\" not in normalized

        # Test leading slash removal
        normalized = loader._normalize_pattern("/build/")
        assert not normalized.startswith("/")

    def test_09_find_ignore_file(self):
        """Test finding .aetherraignore file."""
        # Create .aetherraignore in workspace
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("*.pyc\n")

        loader = IgnorePatternLoader(str(self.workspace))
        found_file = loader._find_ignore_file()
        assert found_file is not None
        assert found_file.name == ".aetherraignore"

    def test_10_list_patterns(self):
        """Test listing patterns."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("*.pyc\nbuild/\n")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.load()
        patterns = loader.list_patterns(include_negations=False)
        assert len(patterns) > 0
        assert "*.pyc" in patterns
        assert "build/" in patterns

    def test_11_get_pattern_info(self):
        """Test getting pattern information."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("*.pyc\nbuild/\n!important.pyc\n")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.load()
        info = loader.get_pattern_info()

        assert "total_patterns" in info
        assert "ignore_patterns" in info
        assert "negation_patterns" in info
        assert info["total_patterns"] > 0

    def test_12_empty_ignore_file(self):
        """Test handling empty .aetherraignore file."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=True)
        success, patterns = loader.load()
        assert success
        # Should have default patterns only
        assert len(patterns) > 0

    def test_13_pattern_matching_wildcards(self):
        """Test pattern matching with wildcards."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        pattern = IgnorePattern(pattern="*.*.pyc")

        assert pattern.matches("test.backup.pyc")
        assert not pattern.matches("test.pyc")
        assert not pattern.matches("test.py")

    def test_14_negation_priority(self):
        """Test that negation patterns have priority."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="*.log"),
            IgnorePattern(pattern="error.log", is_negation=True),
        ]
        loader._process_patterns()

        # error.log should NOT be ignored
        assert not loader.should_ignore("error.log"), "Negation pattern should override"

        # other.log SHOULD be ignored
        assert loader.should_ignore("other.log"), "Regular pattern should match"

    def test_15_directory_specific_patterns(self):
        """Test directory-specific patterns."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)

        dir_pattern = IgnorePattern(pattern="logs/", is_directory=True)
        file_pattern = IgnorePattern(pattern="*.log")

        assert dir_pattern.matches("logs/")
        assert file_pattern.matches("app.log")

    def test_16_pattern_case_handling(self):
        """Test pattern matching case handling."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)

        # Create patterns
        pattern1 = IgnorePattern(pattern="temp*")
        pattern2 = IgnorePattern(pattern="[a-z]*.txt")

        assert pattern1.matches("temporary")
        assert pattern1.matches("temp")
        assert pattern2.matches("abc.txt")
        assert not pattern2.matches("123.txt")

    def test_17_get_ignored_paths(self):
        """Test discovering ignored paths in workspace."""
        # Create directory structure
        (self.workspace / "src").mkdir()
        (self.workspace / "build").mkdir()
        (self.workspace / "src" / "main.py").touch()
        (self.workspace / "build" / "output.o").touch()

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="build/", is_directory=True),
        ]

        ignored = loader.get_ignored_paths()
        # Should find something in build directory
        ignored_strs = {str(p) for p in ignored}
        found_build = any("build" in path for path in ignored_strs)
        assert found_build, f"Expected 'build' in ignored paths: {ignored_strs}"

    def test_18_pattern_info_completeness(self):
        """Test that pattern info is complete."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("*.log\nbuild/\n")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.load()
        info = loader.get_pattern_info()

        required_keys = [
            "total_patterns",
            "ignore_patterns",
            "negation_patterns",
        ]
        for key in required_keys:
            assert key in info, f"Missing key in pattern info: {key}"

    def test_19_normalize_windows_paths(self):
        """Test normalization of Windows-style paths."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)

        # Windows path
        windows_path = "src\\tests\\*.py"
        normalized = loader._normalize_pattern(windows_path)

        assert "\\" not in normalized, "Should convert backslashes to forward slashes"
        assert "/" in normalized

    def test_20_default_ignore_list_completeness(self):
        """Test that default ignore list is comprehensive."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=True)
        success, patterns = loader.load()

        assert success
        # Check for important default patterns
        patterns_str = " ".join(patterns)

        # Check for Python patterns
        assert any("*.pyc" in p for p in patterns), "Should ignore .pyc files"
        assert any("__pycache__" in p for p in patterns), "Should ignore __pycache__"

        # Check for build artifact patterns
        assert any("build" in p for p in patterns), "Should ignore build directory"
        assert any("dist" in p for p in patterns), "Should ignore dist directory"

        # Check for version control
        assert any(".git" in p for p in patterns), "Should ignore .git"


def run_tests():
    """Run all tests with formatted output."""
    print("=" * 70)
    print("TASK 1.4: IGNORE PATTERN LOADER - UNIT TESTS")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIgnorePatternLoaderStandalone)

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    print()

    if result.wasSuccessful():
        print("PASS ALL TESTS PASSED")
        return 0
    print("FAIL SOME TESTS FAILED")
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
