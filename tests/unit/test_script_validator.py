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

# Standard library imports
import json
import os
import tempfile
import unittest
from pathlib import Path

# Third party imports
import yaml


class TestValidationError(unittest.TestCase):
    """Test ValidationError dataclass."""

    def test_create_error(self):
        """Test creating validation error."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ErrorLevel,
            ValidationError,
        )

        error = ValidationError(
            level=ErrorLevel.ERROR,
            message="Test error",
            line=10,
            step_name="step1",
        )

        assert error.level == ErrorLevel.ERROR
        assert error.message == "Test error"
        assert error.line == 10

    def test_error_string_representation(self):
        """Test error string representation."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ErrorLevel,
            ValidationError,
        )

        error = ValidationError(
            level=ErrorLevel.ERROR,
            message="Test error",
            step_name="step1",
            line=5,
        )

        error_str = str(error)
        assert "ERROR" in error_str
        assert "Test error" in error_str
        assert "step1" in error_str


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult dataclass."""

    def test_create_result(self):
        """Test creating validation result."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )

        assert result.script_path == "/test/script.aether"
        assert result.valid

    def test_add_error(self):
        """Test adding error to result."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_error("Test error", step_name="step1")

        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"

    def test_add_warning(self):
        """Test adding warning to result."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_warning("Test warning", step_name="step1")

        assert len(result.warnings) == 1
        assert result.warnings[0].message == "Test warning"

    def test_is_valid_with_errors(self):
        """Test validation status with errors."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_error("Test error")

        assert not result.is_valid()

    def test_is_valid_without_errors(self):
        """Test validation status without errors."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ValidationResult,
        )

        result = ValidationResult(
            script_path="/test/script.aether",
            valid=True,
        )
        result.add_warning("Test warning")

        assert result.is_valid()

    def test_result_summary(self):
        """Test result summary message."""
        # Aetherra imports
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
        assert "FAILED" in summary
        assert "1 errors" in summary
        assert "1 warnings" in summary


class TestStepDefinition(unittest.TestCase):
    """Test StepDefinition dataclass."""

    def test_create_shell_step(self):
        """Test creating shell step definition."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            StepDefinition,
        )

        step = StepDefinition(
            name="test_step",
            step_type="shell",
            command="echo hello",
        )

        assert step.name == "test_step"
        assert step.step_type == "shell"
        assert step.command == "echo hello"

    def test_step_with_dependencies(self):
        """Test step with dependencies."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            StepDefinition,
        )

        step = StepDefinition(
            name="step2",
            step_type="shell",
            command="ls",
            depends_on=["step1"],
        )

        assert step.depends_on == ["step1"]


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
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script("test.aether", "steps: []")
        validator = ScriptValidator(script_path)

        assert str(validator.script_path) == script_path

    def test_validate_missing_file(self):
        """Test validation fails for missing file."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        validator = ScriptValidator("/path/that/does/not/exist.aether")
        result = validator.validate()

        assert not result.valid
        assert len(result.errors) > 0

    def test_validate_invalid_yaml(self):
        """Test validation fails for invalid YAML."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script("bad.aether", "{ [ invalid yaml")
        validator = ScriptValidator(script_path)
        result = validator.validate()

        assert not result.valid

    def test_validate_missing_steps(self):
        """Test validation fails when steps missing."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script(
            "no_steps.aether",
            yaml.dump({"name": "test"}),
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        assert not result.valid

    def test_validate_empty_steps(self):
        """Test validation warns for empty steps."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_validator import (
            ScriptValidator,
        )

        script_path = self._create_script(
            "empty.aether",
            yaml.dump({"steps": []}),
        )
        validator = ScriptValidator(script_path)
        result = validator.validate()

        assert len(result.warnings) > 0

    def test_validate_simple_script(self):
        """Test validation of simple valid script."""
        # Aetherra imports
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

        assert result.valid
        assert len(validator.steps) == 1

    def test_validate_invalid_step_type(self):
        """Test validation fails for invalid step type."""
        # Aetherra imports
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

        assert not result.valid
        assert len(result.errors) > 0

    def test_validate_shell_missing_command(self):
        """Test validation fails for shell without command."""
        # Aetherra imports
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
        script_path = self._create_script("missing_cmd.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        assert not result.valid

    def test_validate_plugin_missing_fields(self):
        """Test validation fails for plugin without name/method."""
        # Aetherra imports
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

        assert not result.valid
        assert len(result.errors) > 1

    def test_validate_invalid_timeout(self):
        """Test validation fails for invalid timeout."""
        # Aetherra imports
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

        assert not result.valid

    def test_validate_undefined_reference(self):
        """Test validation fails for undefined step reference."""
        # Aetherra imports
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
        script_path = self._create_script("bad_ref.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        assert not result.valid

    def test_validate_circular_dependency(self):
        """Test validation fails for circular dependencies."""
        # Aetherra imports
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

        assert not result.valid

    def test_validate_unused_variable(self):
        """Test validation warns for unused variables."""
        # Aetherra imports
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
        script_path = self._create_script("unused_var.aether", yaml.dump(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        assert len(result.warnings) > 0

    def test_validate_metadata(self):
        """Test validation includes metadata."""
        # Aetherra imports
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

        assert "steps_count" in result.metadata
        assert result.metadata["steps_count"] == 1

    def test_validate_json_format(self):
        """Test validation accepts JSON format."""
        # Aetherra imports
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
        script_path = self._create_script("json.aether", json.dumps(script_data))
        validator = ScriptValidator(script_path)
        result = validator.validate()

        assert result.valid


if __name__ == "__main__":
    unittest.main()
