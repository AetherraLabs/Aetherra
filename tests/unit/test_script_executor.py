"""
Unit tests for ScriptExecutor module.

Tests cover:
  - Step creation and types
  - Execution context management
  - Shell command execution
  - Python code execution
  - Plugin call execution
  - Error handling and recovery
  - Timeout management
  - Metrics collection
  - Result generation
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch


class TestWorkflowStep(unittest.TestCase):
    """Test WorkflowStep dataclass."""

    def test_create_shell_step(self):
        """Test creating a shell command step."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepType,
            WorkflowStep,
        )

        step = WorkflowStep(
            name="test_step",
            step_type=StepType.SHELL,
            command="echo hello",
            timeout=60,
        )

        self.assertEqual(step.name, "test_step")
        self.assertEqual(step.step_type, StepType.SHELL)
        self.assertEqual(step.command, "echo hello")
        self.assertEqual(step.timeout, 60)

    def test_create_python_step(self):
        """Test creating a Python code step."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepType,
            WorkflowStep,
        )

        step = WorkflowStep(
            name="py_step",
            step_type=StepType.PYTHON,
            command="x = 42",
            timeout=30,
        )

        self.assertEqual(step.name, "py_step")
        self.assertEqual(step.step_type, StepType.PYTHON)
        self.assertTrue("x = 42" in step.command)

    def test_create_plugin_step(self):
        """Test creating a plugin call step."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepType,
            WorkflowStep,
        )

        step = WorkflowStep(
            name="plugin_step",
            step_type=StepType.PLUGIN,
            plugin_name="mylib",
            plugin_method="process",
            timeout=45,
        )

        self.assertEqual(step.plugin_name, "mylib")
        self.assertEqual(step.plugin_method, "process")

    def test_step_with_dependencies(self):
        """Test step with dependency tracking."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepType,
            WorkflowStep,
        )

        step = WorkflowStep(
            name="dep_step",
            step_type=StepType.SHELL,
            command="ls",
            depends_on=["step1", "step2"],
        )

        self.assertEqual(step.depends_on, ["step1", "step2"])

    def test_step_with_variables(self):
        """Test step storing local variables."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepType,
            WorkflowStep,
        )

        variables = {"count": 5, "name": "test"}
        step = WorkflowStep(
            name="var_step",
            step_type=StepType.PYTHON,
            command="x = count",
            variables=variables,
        )

        self.assertEqual(step.variables, variables)


class TestExecutionContext(unittest.TestCase):
    """Test ExecutionContext dataclass."""

    def test_create_context(self):
        """Test creating execution context."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionContext,
            ExecutionState,
        )

        context = ExecutionContext(script_path="/path/to/script.aether")

        self.assertEqual(context.script_path, "/path/to/script.aether")
        self.assertEqual(context.state, ExecutionState.PENDING)
        self.assertFalse(context.timeout_occurred)

    def test_variable_management(self):
        """Test get/set variables."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionContext,
        )

        context = ExecutionContext(script_path="/path/to/script.aether")
        context.set_variable("x", 42)
        context.set_variable("name", "test")

        self.assertEqual(context.get_variable("x"), 42)
        self.assertEqual(context.get_variable("name"), "test")

    def test_variable_default(self):
        """Test getting variable with default."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionContext,
        )

        context = ExecutionContext(script_path="/path/to/script.aether")

        self.assertIsNone(context.get_variable("missing"))
        self.assertEqual(context.get_variable("missing", "default"), "default")

    def test_context_duration(self):
        """Test context duration tracking."""
        import time

        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionContext,
        )

        context = ExecutionContext(script_path="/path/to/script.aether")
        context.start_time = datetime.now()
        time.sleep(0.1)
        context.end_time = datetime.now()

        duration = context.duration()
        self.assertGreater(duration, 0.05)
        self.assertLess(duration, 1.0)


class TestStepResult(unittest.TestCase):
    """Test StepResult dataclass."""

    def test_create_success_result(self):
        """Test creating successful step result."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepResult,
        )

        result = StepResult(
            step_name="test_step",
            success=True,
            output="Operation succeeded",
            duration=0.5,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.output, "Operation succeeded")
        self.assertEqual(result.duration, 0.5)

    def test_create_failed_result(self):
        """Test creating failed step result."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepResult,
        )

        result = StepResult(
            step_name="bad_step",
            success=False,
            error="Connection timeout",
            return_code=1,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "Connection timeout")
        self.assertEqual(result.return_code, 1)

    def test_step_result_with_metrics(self):
        """Test step result with custom metrics."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            StepResult,
        )

        metrics = {"rows_processed": 1000, "memory_mb": 256}
        result = StepResult(
            step_name="slow_step",
            success=True,
            metrics=metrics,
            duration=2.5,
        )

        self.assertEqual(result.metrics["rows_processed"], 1000)


class TestExecutionMetrics(unittest.TestCase):
    """Test ExecutionMetrics dataclass."""

    def test_create_metrics(self):
        """Test creating execution metrics."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionMetrics,
        )

        metrics = ExecutionMetrics(
            total_steps=10,
            completed_steps=8,
            failed_steps=2,
        )

        self.assertEqual(metrics.total_steps, 10)
        self.assertEqual(metrics.completed_steps, 8)
        self.assertEqual(metrics.failed_steps, 2)

    def test_metrics_duration_tracking(self):
        """Test step duration tracking."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionMetrics,
        )

        metrics = ExecutionMetrics()
        metrics.step_durations["step1"] = 0.5
        metrics.step_durations["step2"] = 1.2
        metrics.total_duration = 1.7

        self.assertEqual(metrics.step_durations["step1"], 0.5)
        self.assertEqual(metrics.total_duration, 1.7)

    def test_custom_metrics(self):
        """Test custom application metrics."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionMetrics,
        )

        metrics = ExecutionMetrics()
        metrics.custom_metrics["cache_hits"] = 150
        metrics.custom_metrics["cache_misses"] = 45

        self.assertEqual(metrics.custom_metrics["cache_hits"], 150)


class TestExecutionResult(unittest.TestCase):
    """Test ExecutionResult dataclass."""

    def test_create_success_result(self):
        """Test creating successful execution result."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionResult,
            ExecutionState,
        )

        result = ExecutionResult(
            script_path="/test/script.aether",
            success=True,
            state=ExecutionState.COMPLETED,
            message="Execution completed successfully",
            duration=2.5,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.state, ExecutionState.COMPLETED)
        self.assertEqual(result.duration, 2.5)

    def test_create_failed_result(self):
        """Test creating failed execution result."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionResult,
            ExecutionState,
        )

        result = ExecutionResult(
            script_path="/test/script.aether",
            success=False,
            state=ExecutionState.FAILED,
            message="Execution failed",
            error="Step 3 failed: Command not found",
            error_traceback="Traceback...",
        )

        self.assertFalse(result.success)
        self.assertEqual(result.state, ExecutionState.FAILED)
        self.assertTrue(result.error_traceback)


class TestScriptExecutor(unittest.TestCase):
    """Test ScriptExecutor class."""

    def setUp(self):
        """Create temporary script file."""
        self.tempdir = tempfile.TemporaryDirectory()
        self.script_path = os.path.join(self.tempdir.name, "test.aether")

        # Create minimal valid script file
        with open(self.script_path, "w") as f:
            f.write("# Test script\necho hello")

    def tearDown(self):
        """Clean up temporary directory."""
        self.tempdir.cleanup()

    def test_executor_initialization(self):
        """Test ScriptExecutor initialization."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path, timeout=120)

        self.assertEqual(executor.timeout, 120)
        self.assertTrue(executor.sandbox)
        self.assertEqual(str(executor.script_path), self.script_path)

    def test_executor_with_custom_timeout(self):
        """Test executor with custom timeout."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path, timeout=500)
        self.assertEqual(executor.timeout, 500)

    def test_executor_max_timeout_constraint(self):
        """Test executor enforces max timeout."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path, timeout=9999)
        self.assertEqual(executor.timeout, 3600)  # MAX_EXECUTION_TIME

    def test_execute_missing_script(self):
        """Test execution fails gracefully with missing script."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionState,
            ScriptExecutor,
        )

        executor = ScriptExecutor("/path/that/does/not/exist.aether")
        result = executor.execute()

        self.assertFalse(result.success)
        self.assertEqual(result.state, ExecutionState.FAILED)

    def test_parse_script_with_valid_file(self):
        """Test script parsing with valid file."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        steps = executor._parse_script()

        self.assertIsInstance(steps, list)

    def test_parse_script_with_invalid_file(self):
        """Test parsing invalid script file."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        bad_path = os.path.join(self.tempdir.name, "nonexistent.aether")
        executor = ScriptExecutor(bad_path)

        with self.assertRaises(FileNotFoundError):
            executor._parse_script()

    def test_execute_shell_step_success(self):
        """Test successful shell step execution."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        success, stdout, stderr, code = executor._execute_shell(
            Mock(command="echo test", timeout=10), timeout=10
        )

        self.assertTrue(success)
        self.assertIn("test", stdout)
        self.assertEqual(code, 0)

    def test_execute_shell_step_failure(self):
        """Test failed shell step execution."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        success, stdout, stderr, code = executor._execute_shell(
            Mock(command="exit 1", timeout=10), timeout=10
        )

        self.assertFalse(success)
        self.assertNotEqual(code, 0)

    def test_execute_shell_step_timeout(self):
        """Test shell step timeout."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        success, stdout, stderr, code = executor._execute_shell(
            Mock(command="sleep 5", timeout=1), timeout=1
        )

        self.assertFalse(success)
        self.assertIn("Timeout", stderr)

    def test_execute_python_step_success(self):
        """Test successful Python step execution."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        executor.context = Mock(variables={})
        success, output, error = executor._execute_python(
            Mock(command="x = 42"), timeout=10
        )

        self.assertTrue(success)
        self.assertEqual(error, "")

    def test_execute_python_step_error(self):
        """Test Python step with syntax error."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        executor.context = Mock(variables={})
        success, output, error = executor._execute_python(
            Mock(command="invalid python !!!"), timeout=10
        )

        self.assertFalse(success)
        self.assertTrue(error)

    def test_execute_python_step_no_code(self):
        """Test Python step without code."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        success, output, error = executor._execute_python(
            Mock(command=None), timeout=10
        )

        self.assertFalse(success)
        self.assertIn("No code", error)

    def test_execute_plugin_step_success(self):
        """Test successful plugin step execution."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        success, output, error = executor._execute_plugin(
            Mock(plugin_name="mylib", plugin_method="process"), timeout=10
        )

        self.assertTrue(success)
        self.assertIn("mylib", output)

    def test_execute_plugin_step_missing_name(self):
        """Test plugin step without plugin name."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        success, output, error = executor._execute_plugin(
            Mock(plugin_name=None, plugin_method="process"), timeout=10
        )

        self.assertFalse(success)

    def test_execute_step_metrics(self):
        """Test step execution collects metrics."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionContext,
            ScriptExecutor,
            StepType,
            WorkflowStep,
        )

        executor = ScriptExecutor(self.script_path)
        executor.context = ExecutionContext(script_path=self.script_path)

        step = WorkflowStep(name="test", step_type=StepType.PYTHON, command="x=1")
        result = executor._execute_step(step)

        self.assertGreater(result.duration, 0)
        self.assertEqual(executor.metrics.step_durations["test"], result.duration)


class TestScriptExecutorIntegration(unittest.TestCase):
    """Integration tests for ScriptExecutor."""

    def setUp(self):
        """Create temporary script file."""
        self.tempdir = tempfile.TemporaryDirectory()
        self.script_path = os.path.join(self.tempdir.name, "test.aether")

        with open(self.script_path, "w") as f:
            f.write("# Test script\necho hello")

    def tearDown(self):
        """Clean up."""
        self.tempdir.cleanup()

    def test_full_execution_flow(self):
        """Test complete execution flow."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ExecutionState,
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        result = executor.execute()

        self.assertIsNotNone(result)
        self.assertEqual(str(result.script_path), self.script_path)
        self.assertEqual(result.state, ExecutionState.COMPLETED)

    def test_execution_result_has_metrics(self):
        """Test execution result includes metrics."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        result = executor.execute()

        self.assertIsNotNone(result.metrics)
        self.assertGreaterEqual(result.metrics.total_duration, 0)

    def test_execution_tracks_variables(self):
        """Test execution tracks variables."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        result = executor.execute()

        self.assertIsInstance(result.variables, dict)

    def test_execution_result_timestamp(self):
        """Test result includes execution timestamp."""
        from Aetherra.aetherra_core.script_service.script_executor import (
            ScriptExecutor,
        )

        executor = ScriptExecutor(self.script_path)
        result = executor.execute()

        self.assertTrue(result.executed_at)


if __name__ == "__main__":
    unittest.main()
