"""
Unit tests for ScriptValidator module.

Tests cover:
  - Script syntax validation (YAML/JSON)
  - Step validation and type checking
  - Step reference validation
  - Variable validation
  - Dependency cycle detection
  - Performance heuristics
  - Error reporting
"""

import unittest
import tempfile
import os
import json
import yaml
from pathlib import Path


class TestValidationError(unittest.TestCase):
    """Test ValidationError dataclass."""

    def test_create_error(self):
        """Test creating validation error."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationError,
            ErrorLevel,
        )

        error = ValidationError(
            level=ErrorLevel.ERROR,
            message="Test error",
            line=10,
            step_name="step1",
        )

        self.assertEqual(error.level, ErrorLevel.ERROR)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.line, 10)

    def test_error_string_representation(self):
        """Test error string representation."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationError,
            ErrorLevel,
        )

        error = ValidationError(
            level=ErrorLevel.ERROR,
            message="Test error",
            step_name="step1",
            line=5,
        )

        error_str = str(error)
        self.assertIn("ERROR", error_str)
        self.assertIn("Test error", error_str)
        self.assertIn("step1", error_str)


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult dataclass."""

    def test_create_result(self):
        """Test creating validation result."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )

        self.assertEqual(result.script_path, "/test/script.aether")
        self.assertTrue(result.valid)

    def test_add_error(self):
        """Test adding error to result."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_error("Test error", step_name="step1")

        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].message, "Test error")

    def test_add_warning(self):
        """Test adding warning to result."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_warning("Test warning", step_name="step1")

        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0].message, "Test warning")

    def test_is_valid_with_errors(self):
        """Test validation status with errors."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_error("Test error")

        self.assertFalse(result.is_valid())

    def test_is_valid_without_errors(self):
        """Test validation status without errors."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_warning("Test warning")

        self.assertTrue(result.is_valid())

    def test_result_summary(self):
        """Test result summary message."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_error("Error 1")
        result.add_warning("Warning 1")

        summary = result.summary()
        self.assertIn("FAILED", summary)
        self.assertIn("1 errors", summary)
        self.assertIn("1 warnings", summary)


class TestStepDefinition(unittest.TestCase):
    """Test StepDefinition dataclass."""

    def test_create_shell_step(self):
        """Test creating shell step definition."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            StepDefinition,
        )

        step = StepDefinition(
            name="test_step",
            step_type="shell",
            command="echo hello",
        )

        self.assertEqual(step.name, "test_step")
        self.assertEqual(step.step_type, "shell")
        self.assertEqual(step.command, "echo hello")

    def test_step_with_dependencies(self):
        """Test step with dependencies."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            StepDefinition,
        )

        step = StepDefinition(
            name="step2",
            step_type="shell",
            command="ls",
            depends_on=["step1"],
        )

        self.assertEqual(step.depends_on, ["step1"])


class TestScriptValidator(unittest.TestCase):
    """Test ScriptValidator class."""

    def setUp(self):
        """Create temporary script directory."""
        self.tempdir = tempfile.TemporaryDirectory()
        self.script_dir = self.tempdir.name

    def tearDown(self):
        """Clean up."""
        self.tempdir.cleanup()

    def _create_script(self, filename, content):
        """Helper to create script file."""
        path = os.path.join(self.script_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_validator_initialization(self):
        """Test validator initialization."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script("test.aether", "steps: []")
        validator = ScriptValidator(script_path)

        self.assertEqual(str(validator.script_path), script_path)

    def test_validate_missing_file(self):
        """Test validation fails for missing file."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        validator = ScriptValidator("/path/that/does/not/exist.aether")
        result = validator.validate()

        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_validate_invalid_yaml(self):
        """Test validation fails for invalid YAML."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script("bad.aether", "{ [ invalid yaml")
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)

    def test_validate_missing_steps(self):
        """Test validation fails when steps missing."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script(
            "no_steps.aether",
            yaml.dump({"name": "test"}),
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)

    def test_validate_empty_steps(self):
        """Test validation warns for empty steps."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script(
            "empty.aether",
            yaml.dump({"steps": []}),
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertGreater(len(result.warnings), 0)

    def test_validate_simple_script(self):
        """Test validation of simple valid script."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "name": "test",
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                    "command": "echo hello",
                }
            ],
        }
        script_path = self._create_script("simple.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertTrue(result.valid)
        self.assertEqual(len(validator.steps), 1)

    def test_validate_invalid_step_type(self):
        """Test validation fails for invalid step type."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "invalid_type",
                    "command": "echo hello",
                }
            ],
        }
        script_path = self._create_script("bad_type.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_validate_shell_missing_command(self):
        """Test validation fails for shell without command."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                }
            ],
        }
        script_path = self._create_script(
            "missing_cmd.aether", yaml.dump(script_data)
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)

    def test_validate_plugin_missing_fields(self):
        """Test validation fails for plugin without name/method."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "plugin",
                }
            ],
        }
        script_path = self._create_script("bad_plugin.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 1)

    def test_validate_invalid_timeout(self):
        """Test validation fails for invalid timeout."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                    "command": "ls",
                    "timeout": 5000,  # Too high
                }
            ],
        }
        script_path = self._create_script("bad_timeout.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)

    def test_validate_undefined_reference(self):
        """Test validation fails for undefined step reference."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "steps": [
                {
                    "name": "step2",
                    "type": "shell",
                    "command": "ls",
                    "depends_on": ["undefined_step"],
                }
            ],
        }
        script_path = self._create_script(
            "bad_ref.aether", yaml.dump(script_data)
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)

    def test_validate_circular_dependency(self):
        """Test validation fails for circular dependencies."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                    "command": "ls",
                    "depends_on": ["step2"],
                },
                {
                    "name": "step2",
                    "type": "shell",
                    "command": "ls",
                    "depends_on": ["step1"],
                },
            ],
        }
        script_path = self._create_script("circular.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertFalse(result.valid)

    def test_validate_unused_variable(self):
        """Test validation warns for unused variables."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "variables": {
                "unused": "value",
            },
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                    "command": "echo hello",
                }
            ],
        }
        script_path = self._create_script(
            "unused_var.aether", yaml.dump(script_data)
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertGreater(len(result.warnings), 0)

    def test_validate_metadata(self):
        """Test validation includes metadata."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "variables": {"var1": "value"},
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                    "command": "echo hello",
                    "timeout": 120,
                }
            ],
        }
        script_path = self._create_script("meta.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertIn("steps_count", result.metadata)
        self.assertEqual(result.metadata["steps_count"], 1)

    def test_validate_json_format(self):
        """Test validation accepts JSON format."""
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                    "command": "echo hello",
                }
            ],
        }
        script_path = self._create_script(
            "json.aether", json.dumps(script_data)
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        self.assertTrue(result.valid)


if __name__ == "__main__":
    unittest.main()
