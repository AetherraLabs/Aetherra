#!/usr/bin/env python3
"""
Standalone test runner for ScriptExecutor module.

Runs comprehensive tests without requiring Aetherra engine initialization,
avoiding Unicode/emoji issues in Windows cmd.exe.

Test Categories:
  - Step creation and validation (5 tests)
  - Execution context management (3 tests)
  - Result generation (3 tests)
  - Metrics tracking (3 tests)
  - Shell execution (3 tests)
  - Python execution (3 tests)
  - Plugin execution (3 tests)
  - Integration tests (4 tests)

Total: 27 comprehensive tests
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add project root to path for direct module import
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

# Import modules directly (no engine init)
from Aetherra.aetherra_core.script_service.script_executor import (
    ExecutionContext,
    ExecutionMetrics,
    ExecutionResult,
    ExecutionState,
    ScriptExecutor,
    StepResult,
    StepType,
    WorkflowStep,
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


def test_create_shell_step():
    """Test creating shell command step."""
    step = WorkflowStep(
        name="test_step",
        step_type=StepType.SHELL,
        command="echo hello",
        timeout=60,
    )
    assert step.name == "test_step"
    assert step.step_type == StepType.SHELL
    assert step.command == "echo hello"
    assert step.timeout == 60


def test_create_python_step():
    """Test creating Python code step."""
    step = WorkflowStep(
        name="py_step",
        step_type=StepType.PYTHON,
        command="x = 42",
    )
    assert step.name == "py_step"
    assert step.step_type == StepType.PYTHON


def test_create_plugin_step():
    """Test creating plugin call step."""
    step = WorkflowStep(
        name="plugin_step",
        step_type=StepType.PLUGIN,
        plugin_name="mylib",
        plugin_method="process",
    )
    assert step.plugin_name == "mylib"
    assert step.plugin_method == "process"


def test_step_with_dependencies():
    """Test step with dependency tracking."""
    step = WorkflowStep(
        name="dep_step",
        step_type=StepType.SHELL,
        command="ls",
        depends_on=["step1", "step2"],
    )
    assert step.depends_on == ["step1", "step2"]


def test_step_with_variables():
    """Test step with local variables."""
    variables = {"count": 5, "name": "test"}
    step = WorkflowStep(
        name="var_step",
        step_type=StepType.PYTHON,
        command="x = count",
        variables=variables,
    )
    assert step.variables == variables


def test_create_context():
    """Test creating execution context."""
    context = ExecutionContext(script_path="/path/to/script.aether")
    assert context.script_path == "/path/to/script.aether"
    assert context.state == ExecutionState.PENDING
    assert not context.timeout_occurred


def test_context_variable_management():
    """Test get/set variables in context."""
    context = ExecutionContext(script_path="/path/to/script.aether")
    context.set_variable("x", 42)
    context.set_variable("name", "test")

    assert context.get_variable("x") == 42
    assert context.get_variable("name") == "test"


def test_context_variable_default():
    """Test getting missing variable with default."""
    context = ExecutionContext(script_path="/path/to/script.aether")
    assert context.get_variable("missing") is None
    assert context.get_variable("missing", "default") == "default"


def test_create_success_result():
    """Test creating successful step result."""
    result = StepResult(
        step_name="test_step",
        success=True,
        output="Operation succeeded",
        duration=0.5,
    )
    assert result.success
    assert result.output == "Operation succeeded"
    assert result.duration == 0.5


def test_create_failed_result():
    """Test creating failed step result."""
    result = StepResult(
        step_name="bad_step",
        success=False,
        error="Connection timeout",
        return_code=1,
    )
    assert not result.success
    assert result.error == "Connection timeout"
    assert result.return_code == 1


def test_step_result_with_metrics():
    """Test step result with custom metrics."""
    metrics = {"rows_processed": 1000, "memory_mb": 256}
    result = StepResult(
        step_name="slow_step",
        success=True,
        metrics=metrics,
        duration=2.5,
    )
    assert result.metrics["rows_processed"] == 1000


def test_create_metrics():
    """Test creating execution metrics."""
    metrics = ExecutionMetrics(
        total_steps=10,
        completed_steps=8,
        failed_steps=2,
    )
    assert metrics.total_steps == 10
    assert metrics.completed_steps == 8
    assert metrics.failed_steps == 2


def test_metrics_duration_tracking():
    """Test step duration tracking in metrics."""
    metrics = ExecutionMetrics()
    metrics.step_durations["step1"] = 0.5
    metrics.step_durations["step2"] = 1.2
    metrics.total_duration = 1.7

    assert metrics.step_durations["step1"] == 0.5
    assert metrics.total_duration == 1.7


def test_custom_metrics():
    """Test custom application metrics."""
    metrics = ExecutionMetrics()
    metrics.custom_metrics["cache_hits"] = 150
    metrics.custom_metrics["cache_misses"] = 45

    assert metrics.custom_metrics["cache_hits"] == 150


def test_execution_result_success():
    """Test successful execution result."""
    result = ExecutionResult(
        script_path="/test/script.aether",
        success=True,
        state=ExecutionState.COMPLETED,
        message="Execution completed successfully",
        duration=2.5,
    )
    assert result.success
    assert result.state == ExecutionState.COMPLETED
    assert result.duration == 2.5


def test_execution_result_failure():
    """Test failed execution result."""
    result = ExecutionResult(
        script_path="/test/script.aether",
        success=False,
        state=ExecutionState.FAILED,
        message="Execution failed",
        error="Step 3 failed",
        error_traceback="Traceback...",
    )
    assert not result.success
    assert result.state == ExecutionState.FAILED
    assert result.error_traceback


def test_executor_initialization():
    """Test ScriptExecutor initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path, timeout=120)
        assert executor.timeout == 120
        assert executor.sandbox
        assert str(executor.script_path) == script_path


def test_executor_max_timeout():
    """Test executor enforces max timeout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path, timeout=9999)
        assert executor.timeout == 3600  # MAX_EXECUTION_TIME


def test_execute_missing_script():
    """Test execution fails with missing script."""
    executor = ScriptExecutor("/path/that/does/not/exist.aether")
    result = executor.execute()

    assert not result.success
    assert result.state == ExecutionState.FAILED


def test_execute_shell_success():
    """Test successful shell command execution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        success, stdout, stderr, code = executor._execute_shell(
            Mock(command="echo test"), timeout=10
        )

        assert success
        assert "test" in stdout
        assert code == 0


def test_execute_shell_timeout():
    """Test shell command timeout handling."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        # Test with a command that should timeout
        success, stdout, stderr, code = executor._execute_shell(
            Mock(command="ping -n 1000 127.0.0.1", timeout=1), timeout=1
        )

        # Should either timeout or fail due to timeout
        assert not success or "Timeout" in stderr or code != 0


def test_execute_python_success():
    """Test successful Python code execution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        executor.context = Mock(variables={})
        success, output, error = executor._execute_python(
            Mock(command="x = 42"), timeout=10
        )

        assert success
        assert error == ""


def test_execute_python_error():
    """Test Python code with syntax error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        executor.context = Mock(variables={})
        success, output, error = executor._execute_python(
            Mock(command="invalid python !!!"), timeout=10
        )

        assert not success
        assert error


def test_execute_python_no_code():
    """Test Python execution without code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        success, output, error = executor._execute_python(
            Mock(command=None), timeout=10
        )

        assert not success
        assert "No code" in error


def test_execute_plugin_success():
    """Test successful plugin call."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        success, output, error = executor._execute_plugin(
            Mock(plugin_name="mylib", plugin_method="process"), timeout=10
        )

        assert success
        assert "mylib" in output


def test_execute_plugin_missing_name():
    """Test plugin execution without name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        success, output, error = executor._execute_plugin(
            Mock(plugin_name=None, plugin_method="process"), timeout=10
        )

        assert not success


def test_full_execution_flow():
    """Test complete script execution flow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test script\necho hello")

        executor = ScriptExecutor(script_path)
        result = executor.execute()

        assert result is not None
        assert result.script_path == script_path
        assert result.state == ExecutionState.COMPLETED


def test_execution_result_has_metrics():
    """Test execution includes metrics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        result = executor.execute()

        assert result.metrics is not None
        assert result.metrics.total_duration >= 0


def test_execution_tracks_variables():
    """Test execution tracks variable state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        result = executor.execute()

        assert isinstance(result.variables, dict)


def test_execution_result_timestamp():
    """Test result includes execution timestamp."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "test.aether")
        with open(script_path, "w") as f:
            f.write("# Test")

        executor = ScriptExecutor(script_path)
        result = executor.execute()

        assert result.executed_at
        assert "T" in result.executed_at  # ISO format timestamp


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ScriptExecutor - Standalone Test Suite")
    print("=" * 60 + "\n")

    runner = TestRunner()

    # Step creation tests
    print("Step Creation Tests (5/27):")
    runner.run_test("Create shell step", test_create_shell_step)
    runner.run_test("Create Python step", test_create_python_step)
    runner.run_test("Create plugin step", test_create_plugin_step)
    runner.run_test("Step with dependencies", test_step_with_dependencies)
    runner.run_test("Step with variables", test_step_with_variables)

    # Context tests
    print("\nExecution Context Tests (3/27):")
    runner.run_test("Create execution context", test_create_context)
    runner.run_test("Context variable management", test_context_variable_management)
    runner.run_test("Context variable default", test_context_variable_default)

    # Result tests
    print("\nResult Generation Tests (3/27):")
    runner.run_test("Create success result", test_create_success_result)
    runner.run_test("Create failed result", test_create_failed_result)
    runner.run_test("Step result with metrics", test_step_result_with_metrics)

    # Metrics tests
    print("\nMetrics Tracking Tests (3/27):")
    runner.run_test("Create metrics", test_create_metrics)
    runner.run_test("Metrics duration tracking", test_metrics_duration_tracking)
    runner.run_test("Custom metrics", test_custom_metrics)

    # Execution result tests
    print("\nExecution Result Tests (2/27):")
    runner.run_test("Execution result success", test_execution_result_success)
    runner.run_test("Execution result failure", test_execution_result_failure)

    # Shell execution tests
    print("\nShell Execution Tests (3/27):")
    runner.run_test("Execute shell success", test_execute_shell_success)
    runner.run_test("Execute shell timeout", test_execute_shell_timeout)
    runner.run_test("Executor initialization", test_executor_initialization)

    # Python execution tests
    print("\nPython Execution Tests (3/27):")
    runner.run_test("Execute Python success", test_execute_python_success)
    runner.run_test("Execute Python error", test_execute_python_error)
    runner.run_test("Execute Python no code", test_execute_python_no_code)

    # Plugin execution tests
    print("\nPlugin Execution Tests (2/27):")
    runner.run_test("Execute plugin success", test_execute_plugin_success)
    runner.run_test("Execute plugin missing name", test_execute_plugin_missing_name)

    # Integration tests
    print("\nIntegration Tests (4/27):")
    runner.run_test("Executor max timeout", test_executor_max_timeout)
    runner.run_test("Execute missing script", test_execute_missing_script)
    runner.run_test("Full execution flow", test_full_execution_flow)
    runner.run_test("Execution result metrics", test_execution_result_has_metrics)

    # Final integration tests
    print("\nFinal Integration Tests (2/27):")
    runner.run_test("Execution tracks variables", test_execution_tracks_variables)
    runner.run_test("Execution result timestamp", test_execution_result_timestamp)

    # Print summary
    success = runner.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
