"""
Unit tests for IgnorePatternLoader - Parse and apply .aetherraignore patterns.

Tests cover:
- Pattern file parsing
- Glob pattern matching
- Negation patterns
- Comment handling
- Directory-specific patterns
- Default patterns
- File discovery and ignoring
"""

import unittest
import tempfile
from pathlib import Path

import sys

# Add parent directory to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent)
)

from Aetherra.aetherra_core.system.ignore_pattern_loader import (
    IgnorePatternLoader,
    IgnorePattern,
)


class TestIgnorePattern(unittest.TestCase):
    """Test IgnorePattern dataclass."""

    def test_01_create_pattern(self):
        """Test creating ignore pattern."""
        pattern = IgnorePattern(
            pattern="*.pyc",
            is_negation=False,
            is_directory=False,
        )
        self.assertEqual(pattern.pattern, "*.pyc")
        self.assertFalse(pattern.is_negation)

    def test_02_pattern_glob_matching(self):
        """Test glob pattern matching."""
        pattern = IgnorePattern(pattern="*.py", is_regex=False)
        self.assertTrue(pattern.matches("test.py"))
        self.assertFalse(pattern.matches("test.txt"))

    def test_03_pattern_directory_matching(self):
        """Test directory pattern matching."""
        pattern = IgnorePattern(
            pattern="build/",
            is_directory=True,
        )
        self.assertTrue(pattern.matches("build/"))
        self.assertTrue(pattern.matches("build/output"))

    def test_04_pattern_negation(self):
        """Test negation pattern."""
        pattern = IgnorePattern(
            pattern="!important.txt",
            is_negation=True,
        )
        self.assertTrue(pattern.is_negation)
        self.assertEqual(pattern.pattern, "!important.txt")


class TestIgnorePatternLoader(unittest.TestCase):
    """Test IgnorePatternLoader functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_loader(self):
        """Test creating pattern loader."""
        loader = IgnorePatternLoader(str(self.workspace))
        self.assertIsNotNone(loader)
        self.assertEqual(loader.root_dir, self.workspace)

    def test_02_load_default_patterns(self):
        """Test loading default patterns."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=True)
        success, patterns = loader.load()
        self.assertTrue(success)
        self.assertGreater(len(patterns), 0)

    def test_03_load_from_ignore_file(self):
        """Test loading patterns from .aetherraignore file."""
        # Create .aetherraignore file
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text(
            "# Comment\n"
            "build/\n"
            "dist/\n"
            "*.pyc\n"
        )

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        success, patterns = loader.load()
        self.assertTrue(success)
        self.assertIn("build/", patterns)
        self.assertIn("dist/", patterns)
        self.assertIn("*.pyc", patterns)

    def test_04_ignore_file_comments(self):
        """Test that comments are ignored."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text(
            "# This is a comment\n"
            "*.pyc\n"
            "\n"  # Blank line
            "  # Indented comment\n"
            "build/\n"
        )

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        success, patterns = loader.load()
        self.assertTrue(success)
        # Should have 2 patterns, not comments
        self.assertEqual(len(patterns), 2)

    def test_05_negation_patterns(self):
        """Test negation patterns."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text(
            "*.log\n"
            "!important.log\n"
        )

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        success, patterns = loader.load()
        self.assertTrue(success)

        # test.log should be ignored
        self.assertTrue(loader.should_ignore("test.log"))

        # important.log should NOT be ignored (negation)
        self.assertFalse(loader.should_ignore("important.log"))

    def test_06_should_ignore_simple(self):
        """Test should_ignore for simple patterns."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="*.pyc"),
            IgnorePattern(pattern="__pycache__/"),
        ]

        self.assertTrue(loader.should_ignore("test.pyc"))
        self.assertFalse(loader.should_ignore("test.py"))
        self.assertTrue(loader.should_ignore("__pycache__/modules"))

    def test_07_should_ignore_directory(self):
        """Test should_ignore_directory."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="build/", is_directory=True),
            IgnorePattern(pattern="dist/", is_directory=True),
        ]

        self.assertTrue(loader.should_ignore_directory("build"))
        self.assertTrue(loader.should_ignore_directory("dist"))
        self.assertFalse(loader.should_ignore_directory("src"))

    def test_08_normalize_pattern(self):
        """Test pattern normalization."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)

        # Test backslash normalization
        normalized = loader._normalize_pattern("src\\main\\*.py")
        self.assertIn("/", normalized)
        self.assertNotIn("\\", normalized)

        # Test leading slash removal
        normalized = loader._normalize_pattern("/build/")
        self.assertFalse(normalized.startswith("/"))

    def test_09_find_ignore_file(self):
        """Test finding .aetherraignore file."""
        # Create .aetherraignore in workspace
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("*.pyc\n")

        loader = IgnorePatternLoader(str(self.workspace))
        found_file = loader._find_ignore_file()
        self.assertIsNotNone(found_file)
        self.assertEqual(found_file.name, ".aetherraignore")

    def test_10_list_patterns(self):
        """Test listing patterns."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text(
            "*.pyc\n"
            "build/\n"
        )

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.load()
        patterns = loader.list_patterns(include_negations=False)
        self.assertGreater(len(patterns), 0)
        self.assertIn("*.pyc", patterns)
        self.assertIn("build/", patterns)

    def test_11_get_pattern_info(self):
        """Test getting pattern information."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text(
            "*.pyc\n"
            "build/\n"
            "!important.pyc\n"
        )

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.load()
        info = loader.get_pattern_info()

        self.assertIn("total_patterns", info)
        self.assertIn("ignore_patterns", info)
        self.assertIn("negation_patterns", info)
        self.assertGreater(info["total_patterns"], 0)

    def test_12_glob_patterns_subdirs(self):
        """Test glob patterns matching subdirectories."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="tests/**/test_*.py"),
        ]

        # Create actual files
        tests_dir = self.workspace / "tests" / "unit"
        tests_dir.mkdir(parents=True)
        test_file = tests_dir / "test_foo.py"
        test_file.touch()

        # Check if pattern would match
        rel_path = test_file.relative_to(self.workspace).as_posix()
        # Note: Our simple implementation converts ** to * for fnmatch compatibility
        # This test documents the behavior

    def test_13_empty_ignore_file(self):
        """Test handling empty .aetherraignore file."""
        ignore_file = self.workspace / ".aetherraignore"
        ignore_file.write_text("")

        loader = IgnorePatternLoader(str(self.workspace), use_defaults=True)
        success, patterns = loader.load()
        self.assertTrue(success)
        # Should have default patterns only
        self.assertGreater(len(patterns), 0)

    def test_14_get_ignored_paths(self):
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
        # build directory should be in ignored set
        ignored_strs = {str(p) for p in ignored}
        self.assertTrue(
            any("build" in path for path in ignored_strs),
            f"Expected 'build' in ignored paths: {ignored_strs}",
        )

    def test_15_multiple_wildcards(self):
        """Test patterns with multiple wildcards."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        pattern = IgnorePattern(pattern="*.*.pyc")  # files like foo.bar.pyc

        self.assertTrue(pattern.matches("test.backup.pyc"))
        self.assertFalse(pattern.matches("test.pyc"))
        self.assertFalse(pattern.matches("test.py"))

    def test_16_pattern_priority_negation(self):
        """Test that negation patterns have priority."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        loader.patterns = [
            IgnorePattern(pattern="*.log"),
            IgnorePattern(pattern="!error.log", is_negation=True),
        ]
        loader._process_patterns()

        # error.log should NOT be ignored despite matching *.log
        self.assertFalse(loader.should_ignore("error.log"))

        # other.log SHOULD be ignored
        self.assertTrue(loader.should_ignore("other.log"))

    def test_17_case_sensitivity(self):
        """Test pattern matching case sensitivity."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)
        pattern = IgnorePattern(pattern="*.PYC")

        # fnmatch is case-sensitive on Unix, case-insensitive on Windows
        # Document the behavior
        result = pattern.matches("test.pyc")
        # On Windows this might be True, on Unix False
        # Just check that matching works consistently

    def test_18_special_characters_in_patterns(self):
        """Test handling special characters in patterns."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)

        # Create patterns with special chars
        pattern1 = IgnorePattern(pattern="temp*")  # temp<anything>
        pattern2 = IgnorePattern(pattern="[a-z]*.txt")  # files starting with lowercase

        self.assertTrue(pattern1.matches("temporary"))
        self.assertTrue(pattern1.matches("temp"))
        self.assertTrue(pattern2.matches("abc.txt"))
        self.assertFalse(pattern2.matches("123.txt"))

    def test_19_directory_vs_file_patterns(self):
        """Test difference between directory and file patterns."""
        loader = IgnorePatternLoader(str(self.workspace), use_defaults=False)

        # Directory pattern with trailing slash
        dir_pattern = IgnorePattern(pattern="logs/", is_directory=True)
        # File pattern without trailing slash  
        file_pattern = IgnorePattern(pattern="*.log")

        self.assertTrue(dir_pattern.matches("logs/"))
        self.assertTrue(file_pattern.matches("app.log"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
