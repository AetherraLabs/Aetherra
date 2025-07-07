#!/usr/bin/env python3
"""
Comprehensive test suite for the AI Plugin Rewriter
Tests all functionality with safety measures and edge cases
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from lyrixa.ai.plugin_rewriter import PluginRewriter, PluginRewriterError


class TestPluginRewriter(unittest.TestCase):
    """Test suite for PluginRewriter with safety validation"""

    def setUp(self):
        """Set up test environment with temporary directories"""
        self.test_dir = tempfile.mkdtemp()
        self.plugin_dir = os.path.join(self.test_dir, "plugins")
        self.history_dir = os.path.join(self.test_dir, "history")

        os.makedirs(self.plugin_dir)
        os.makedirs(self.history_dir)

        # Create test plugin
        self.test_plugin_code = '''"""
Test plugin for AI rewriter testing
"""

def hello_world(name="World"):
    """Simple greeting function"""
    return f"Hello, {name}!"

class TestClass:
    """Test class with basic functionality"""

    def __init__(self, value=0):
        self.value = value

    def increment(self):
        """Increment the value"""
        self.value += 1
        return self.value

def calculate_sum(numbers):
    """Calculate sum of numbers"""
    total = 0
    for num in numbers:
        total += num
    return total
'''

        self.test_plugin_path = os.path.join(self.plugin_dir, "test_plugin.py")
        with open(self.test_plugin_path, "w") as f:
            f.write(self.test_plugin_code)

        # Initialize rewriter
        self.rewriter = PluginRewriter(
            plugin_dir=self.plugin_dir, history_dir=self.history_dir
        )

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plugin_path_validation(self):
        """Test plugin path validation and error handling"""
        # Test non-existent plugin
        with self.assertRaises(PluginRewriterError):
            self.rewriter._get_plugin_path("nonexistent_plugin")

        # Test valid plugin
        path = self.rewriter._get_plugin_path("test_plugin")
        self.assertEqual(path, self.test_plugin_path)

    def test_code_reading_and_validation(self):
        """Test safe code reading with size validation"""
        # Test normal code reading
        code = self.rewriter._read_plugin_code(self.test_plugin_path)
        self.assertEqual(code.strip(), self.test_plugin_code.strip())

        # Test size limit validation
        self.rewriter.max_code_size = 100  # Set very low limit
        with self.assertRaises(PluginRewriterError):
            self.rewriter._read_plugin_code(self.test_plugin_path)

    def test_metadata_extraction(self):
        """Test plugin metadata extraction using AST"""
        metadata = self.rewriter._extract_plugin_metadata(self.test_plugin_code)

        # Check extracted functions
        self.assertIn("hello_world", metadata["functions"])
        self.assertIn("calculate_sum", metadata["functions"])
        self.assertIn("increment", metadata["functions"])  # From class

        # Check extracted classes
        self.assertIn("TestClass", metadata["classes"])

        # Check docstring
        self.assertIsNotNone(metadata["docstring"])

    def test_syntax_validation(self):
        """Test Python syntax validation"""
        # Valid code
        self.assertTrue(self.rewriter._validate_python_syntax("x = 1\nprint(x)"))

        # Invalid code
        self.assertFalse(
            self.rewriter._validate_python_syntax("def broken_func(\n    pass")
        )

    def test_code_response_cleaning(self):
        """Test cleaning of AI responses to extract code"""
        # Test markdown removal
        markdown_response = "```python\nprint('hello')\n```"
        cleaned = self.rewriter._clean_code_response(markdown_response)
        self.assertEqual(cleaned, "print('hello')")

        # Test already clean code
        clean_code = "print('hello')"
        cleaned = self.rewriter._clean_code_response(clean_code)
        self.assertEqual(cleaned, "print('hello')")

    def test_version_backup_creation(self):
        """Test version backup functionality"""
        backup_path = self.rewriter._create_version_backup(
            "test_plugin", self.test_plugin_code
        )

        # Check backup file exists
        self.assertTrue(os.path.exists(backup_path))

        # Check backup content
        with open(backup_path, "r") as f:
            backup_content = f.read()
        self.assertEqual(backup_content, self.test_plugin_code)

        # Check backup is in history directory
        self.assertTrue(backup_path.startswith(self.history_dir))

    def test_version_listing(self):
        """Test listing of plugin versions"""
        # Create a few backups
        self.rewriter._create_version_backup("test_plugin", self.test_plugin_code)
        self.rewriter._create_version_backup(
            "test_plugin", self.test_plugin_code + "\n# Modified"
        )

        versions = self.rewriter.list_plugin_versions("test_plugin")
        self.assertGreaterEqual(len(versions), 2)

        # Versions should be sorted newest first
        self.assertTrue(versions[0] >= versions[1])

    def test_backup_cleanup(self):
        """Test cleanup of old backup files"""
        # Set low limit for testing
        self.rewriter.max_backup_files = 3

        # Create multiple backups
        for i in range(5):
            self.rewriter._create_version_backup("test_plugin", f"version {i}")

        # Check that only max_backup_files remain
        versions = self.rewriter.list_plugin_versions("test_plugin")
        self.assertLessEqual(len(versions), self.rewriter.max_backup_files)

    @patch("openai.OpenAI")
    def test_explain_plugin_success(self, mock_openai_client):
        """Test successful plugin explanation"""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[
            0
        ].message.content = "This plugin provides greeting functionality."
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client

        explanation = self.rewriter.explain_plugin("test_plugin")

        # Check that explanation was returned
        self.assertEqual(explanation, "This plugin provides greeting functionality.")

        # Check that OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

    @patch("openai.OpenAI")
    def test_explain_plugin_failure(self, mock_openai_client):
        """Test plugin explanation with API failure"""
        # Mock OpenAI failure
        mock_openai_client.side_effect = Exception("API Error")

        explanation = self.rewriter.explain_plugin("test_plugin")

        # Check that error message is returned
        self.assertIn("Failed to explain plugin", explanation)
        self.assertIn("API Error", explanation)

    @patch("openai.OpenAI")
    def test_refactor_plugin_success(self, mock_openai_client):
        """Test successful plugin refactoring"""
        # Mock OpenAI response with valid code
        refactored_code = '''"""
Refactored test plugin
"""

def hello_world(name: str = "World") -> str:
    """Simple greeting function with type hints"""
    return f"Hello, {name}!"
'''
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = refactored_code
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client

        result = self.rewriter.refactor_plugin("test_plugin", "add type hints")

        # Check success message
        self.assertIn("✅ Refactor successful", result)

        # Check that backup was created
        versions = self.rewriter.list_plugin_versions("test_plugin")
        self.assertGreater(len(versions), 0)

    @patch("openai.OpenAI")
    def test_refactor_plugin_syntax_error(self, mock_openai_client):
        """Test refactoring with syntax error in response"""
        # Mock OpenAI response with invalid code
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[
            0
        ].message.content = "def broken_function(\n    pass"  # Invalid syntax
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client

        result = self.rewriter.refactor_plugin("test_plugin", "break the code")

        # Check error message
        self.assertIn("❌ Refactored code contains syntax errors", result)

        # Check that original file is unchanged
        with open(self.test_plugin_path, "r") as f:
            current_code = f.read()
        self.assertEqual(current_code.strip(), self.test_plugin_code.strip())

    @patch("openai.OpenAI")
    def test_add_logging_success(self, mock_openai_client):
        """Test successful logging addition"""
        # Mock OpenAI response with logging added
        logged_code = '''"""
Test plugin with logging
"""
import logging

logger = logging.getLogger(__name__)

def hello_world(name="World"):
    """Simple greeting function"""
    logger.info(f"Greeting {name}")
    return f"Hello, {name}!"
'''
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = logged_code
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client

        result = self.rewriter.add_logging_to_plugin("test_plugin")

        # Check success message
        self.assertIn("✅ Logging added successfully", result)

    def test_rollback_plugin(self):
        """Test plugin rollback functionality"""
        # Create a backup first
        backup_path = self.rewriter._create_version_backup(
            "test_plugin", self.test_plugin_code
        )
        version = (
            os.path.basename(backup_path)
            .replace("test_plugin_", "")
            .replace(".bak", "")
        )

        # Modify the plugin
        modified_code = self.test_plugin_code + "\n# Modified"
        with open(self.test_plugin_path, "w") as f:
            f.write(modified_code)

        # Rollback to backup
        result = self.rewriter.rollback_plugin("test_plugin", version)

        # Check success
        self.assertIn("✅ Successfully rolled back", result)

        # Check that file was restored
        with open(self.test_plugin_path, "r") as f:
            restored_code = f.read()
        self.assertEqual(restored_code, self.test_plugin_code)

    def test_diff_plugin_versions(self):
        """Test plugin version diffing"""
        # Create two versions
        version1_path = self.rewriter._create_version_backup(
            "test_plugin", self.test_plugin_code
        )
        version2_path = self.rewriter._create_version_backup(
            "test_plugin", self.test_plugin_code + "\n# Comment"
        )

        version1 = (
            os.path.basename(version1_path)
            .replace("test_plugin_", "")
            .replace(".bak", "")
        )
        version2 = (
            os.path.basename(version2_path)
            .replace("test_plugin_", "")
            .replace(".bak", "")
        )

        # Get diff
        diff = self.rewriter.diff_plugin_versions("test_plugin", version1, version2)

        # Check that diff contains the change
        self.assertIn("# Comment", diff)
        self.assertIn("@@", diff)  # Unified diff format marker


def run_comprehensive_tests():
    """Run all tests with detailed output"""
    print("🧪 Running AI Plugin Rewriter Comprehensive Tests")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPluginRewriter)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed! Plugin Rewriter is ready for production.")
        return True
    else:
        print(
            f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)"
        )
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
