#!/usr/bin/env python3
"""
Standalone test runner for ScriptValidator module.

Runs comprehensive validation tests without requiring Aetherra engine initialization.

Test Categories:
  - ValidationError creation and formatting (1 test)
  - ValidationResult management (6 tests)
  - StepDefinition creation (2 tests)
  - ScriptValidator initialization (1 test)
  - File validation (missing, invalid syntax) (2 tests)
  - Script structure validation (missing/empty steps) (2 tests)
  - Step type validation (invalid types, missing fields) (3 tests)
  - Dependency validation (undefined refs, cycles) (2 tests)
  - Variable validation (unused variables, metadata) (2 tests)
  - Format validation (JSON/YAML) (1 test)

Total: 22 comprehensive tests
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import yaml

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

# Import modules directly (no engine init)
from Aetherra.aetherra_core.script_service.script_validator import (
    ErrorLevel,
    ScriptValidator,
    StepDefinition,
    ValidationError,
    ValidationResult,
)


class TestRunner:
    """Simple test runner with colored output."""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run_test(self, name, test_func):
        """Run a single test."""
        self.total += 1
        try:
            test_func()
            self.passed += 1
            print(f"  ✓ test_{self.total:02d}: {name}")
            return True
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"  ✗ test_{self.total:02d}: {name}")
            print(f"      AssertionError: {e}")
            return False
        except Exception as e:
            self.failed += 1
            self.errors.append((name, f"{type(e).__name__}: {e}"))
            print(f"  ✗ test_{self.total:02d}: {name}")
            print(f"      {type(e).__name__}: {e}")
            return False

    def summary(self):
        """Print test summary."""
        print(f"\n{'=' * 60}")
        print(f"Tests run: {self.total}")
        print(f"Passed:    {self.passed}")
        print(f"Failed:    {self.failed}")
        if self.failed > 0:
            print("\nFailures:")
            for name, error in self.errors:
                print(f"  - {name}: {error[:100]}")
        print(f"{'=' * 60}\n")
        return self.failed == 0


def test_create_error():
    """Test creating validation error."""
    error = ValidationError(
        level=ErrorLevel.ERROR,
        message="Test error",
        line=10,
        step_name="step1",
    )
    assert error.level == ErrorLevel.ERROR
    assert error.message == "Test error"
    assert error.line == 10


def test_error_string_representation():
    """Test error string representation."""
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


def test_create_result():
    """Test creating validation result."""
    result = ValidationResult(
        script_path="/test/script.aether",
        valid=True,
    )
    assert result.script_path == "/test/script.aether"
    assert result.valid is True


def test_add_error():
    """Test adding error to result."""
    result = ValidationResult(
        script_path="/test/script.aether",
        valid=True,
    )
    result.add_error("Test error", step_name="step1")
    assert len(result.errors) == 1
    assert result.errors[0].message == "Test error"


def test_add_warning():
    """Test adding warning to result."""
    result = ValidationResult(
        script_path="/test/script.aether",
        valid=True,
    )
    result.add_warning("Test warning", step_name="step1")
    assert len(result.warnings) == 1
    assert result.warnings[0].message == "Test warning"


def test_is_valid_with_errors():
    """Test validation status with errors."""
    result = ValidationResult(
        script_path="/test/script.aether",
        valid=True,
    )
    result.add_error("Test error")
    assert not result.is_valid()


def test_is_valid_without_errors():
    """Test validation status without errors."""
    result = ValidationResult(
        script_path="/test/script.aether",
        valid=True,
    )
    result.add_warning("Test warning")
    assert result.is_valid()


def test_result_summary():
    """Test result summary message."""
    result = ValidationResult(
        script_path="/test/script.aether",
        valid=True,
    )
    result.add_error("Error 1")
    result.add_warning("Warning 1")
    summary = result.summary()
    assert "FAILED" in summary
    assert "error" in summary.lower()
    assert "warning" in summary.lower()


def test_create_shell_step():
    """Test creating shell step definition."""
    step = StepDefinition(
        name="test_step",
        step_type="shell",
        command="echo hello",
    )
    assert step.name == "test_step"
    assert step.step_type == "shell"
    assert step.command == "echo hello"


def test_step_with_dependencies():
    """Test step with dependencies."""
    step = StepDefinition(
        name="step2",
        step_type="shell",
        command="ls",
        depends_on=["step1"],
    )
    assert step.depends_on == ["step1"]


def test_validator_initialization():
    """Test validator initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write(yaml.dump({"steps": []}))

        validator = ScriptValidator(script_path)
        assert str(validator.script_path) == script_path


def test_validate_missing_file():
    """Test validation fails for missing file."""
    validator = ScriptValidator("/path/that/does/not/exist.aether")
    result = validator.validate()
    assert not result.valid
    assert len(result.errors) > 0


def test_validate_invalid_yaml():
    """Test validation fails for invalid YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "bad.aether")
        with open(script_path, "w") as f:
            f.write("{ [ invalid yaml")

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid


def test_validate_missing_steps():
    """Test validation fails when steps missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "no_steps.aether")
        with open(script_path, "w") as f:
            f.write(yaml.dump({"name": "test"}))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid


def test_validate_empty_steps():
    """Test validation warns for empty steps."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "empty.aether")
        with open(script_path, "w") as f:
            f.write(yaml.dump({"steps": []}))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert len(result.warnings) > 0


def test_validate_simple_script():
    """Test validation of simple valid script."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "simple.aether")
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
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert result.valid
        assert len(validator.steps) == 1


def test_validate_invalid_step_type():
    """Test validation fails for invalid step type."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "bad_type.aether")
        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "invalid_type",
                    "command": "echo hello",
                }
            ],
        }
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid


def test_validate_shell_missing_command():
    """Test validation fails for shell without command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "missing_cmd.aether")
        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                }
            ],
        }
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid


def test_validate_plugin_missing_fields():
    """Test validation fails for plugin without name/method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "bad_plugin.aether")
        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "plugin",
                }
            ],
        }
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid
        assert len(result.errors) > 1


def test_validate_invalid_timeout():
    """Test validation fails for invalid timeout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "bad_timeout.aether")
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
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid


def test_validate_undefined_reference():
    """Test validation fails for undefined step reference."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "bad_ref.aether")
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
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid


def test_validate_circular_dependency():
    """Test validation fails for circular dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "circular.aether")
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
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert not result.valid


def test_validate_unused_variable():
    """Test validation warns for unused variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "unused_var.aether")
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
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert len(result.warnings) > 0


def test_validate_metadata():
    """Test validation includes metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "meta.aether")
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
        with open(script_path, "w") as f:
            f.write(yaml.dump(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert "steps_count" in result.metadata
        assert result.metadata["steps_count"] == 1


def test_validate_json_format():
    """Test validation accepts JSON format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "json.aether")
        script_data = {
            "steps": [
                {
                    "name": "step1",
                    "type": "shell",
                    "command": "echo hello",
                }
            ],
        }
        with open(script_path, "w") as f:
            f.write(json.dumps(script_data))

        validator = ScriptValidator(script_path)
        result = validator.validate()
        assert result.valid


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ScriptValidator - Standalone Test Suite")
    print("=" * 60 + "\n")

    runner = TestRunner()

    # ValidationError tests
    print("ValidationError Tests (2/22):")
    runner.run_test("Create validation error", test_create_error)
    runner.run_test("Error string representation", test_error_string_representation)

    # ValidationResult tests
    print("\nValidationResult Tests (6/22):")
    runner.run_test("Create validation result", test_create_result)
    runner.run_test("Add error to result", test_add_error)
    runner.run_test("Add warning to result", test_add_warning)
    runner.run_test("Is valid with errors", test_is_valid_with_errors)
    runner.run_test("Is valid without errors", test_is_valid_without_errors)
    runner.run_test("Result summary", test_result_summary)

    # StepDefinition tests
    print("\nStepDefinition Tests (2/22):")
    runner.run_test("Create shell step", test_create_shell_step)
    runner.run_test("Step with dependencies", test_step_with_dependencies)

    # ScriptValidator initialization
    print("\nScriptValidator Initialization (1/22):")
    runner.run_test("Validator initialization", test_validator_initialization)

    # File validation tests
    print("\nFile Validation Tests (2/22):")
    runner.run_test("Validate missing file", test_validate_missing_file)
    runner.run_test("Validate invalid YAML", test_validate_invalid_yaml)

    # Script structure validation
    print("\nScript Structure Validation (2/22):")
    runner.run_test("Validate missing steps", test_validate_missing_steps)
    runner.run_test("Validate empty steps", test_validate_empty_steps)

    # Step type validation
    print("\nStep Type Validation (3/22):")
    runner.run_test("Validate simple script", test_validate_simple_script)
    runner.run_test("Validate invalid step type", test_validate_invalid_step_type)
    runner.run_test(
        "Validate shell missing command", test_validate_shell_missing_command
    )

    # Plugin and timeout validation
    print("\nPlugin & Timeout Validation (2/22):")
    runner.run_test(
        "Validate plugin missing fields", test_validate_plugin_missing_fields
    )
    runner.run_test("Validate invalid timeout", test_validate_invalid_timeout)

    # Dependency validation
    print("\nDependency Validation (2/22):")
    runner.run_test("Validate undefined reference", test_validate_undefined_reference)
    runner.run_test("Validate circular dependency", test_validate_circular_dependency)

    # Variable and format validation
    print("\nVariable & Format Validation (2/22):")
    runner.run_test("Validate unused variable", test_validate_unused_variable)
    runner.run_test("Validate metadata", test_validate_metadata)

    # Final format test
    print("\nFormat Support Tests (1/22):")
    runner.run_test("Validate JSON format", test_validate_json_format)

    # Print summary
    success = runner.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
