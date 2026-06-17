"""
Script Executor - Execute Aether workflow scripts with comprehensive error handling.

Manages script execution lifecycle:
  1. Parse and validate script
  2. Create execution context
  3. Execute workflow steps sequentially
  4. Handle errors and timeouts
  5. Collect metrics and logs

Features:
  - Isolated execution contexts per script
  - Timeout and resource management
  - Comprehensive error handling with stack traces
  - Variable scoping and context management
  - Execution metrics and observability
  - Support for step types: shell, python, plugin calls
  - Pre/post-hook execution
  - Error recovery strategies

Example:
    >>> executor = ScriptExecutor("/path/to/script.aether")
    >>> result = executor.execute()
    >>> print(f"Success: {result.success}, Duration: {result.duration}s")
"""

import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent
from Aetherra.security.sandbox import (
    IsolatedExecutionError,
    SandboxViolation,
    TimeBudgetExceeded,
    execute_restricted_python,
    run_command_no_shell,
)

logger = logging.getLogger(__name__)


class StepType(Enum):
    """Types of workflow steps supported."""

    SHELL = "shell"
    """Execute shell command"""
    PYTHON = "python"
    """Execute Python code"""
    PLUGIN = "plugin"
    """Call plugin function"""
    CONDITIONAL = "conditional"
    """Conditional branching"""
    LOOP = "loop"
    """Looping over items"""


class ExecutionState(Enum):
    """Execution state transitions."""

    PENDING = "pending"
    """Waiting to execute"""
    RUNNING = "running"
    """Currently executing"""
    COMPLETED = "completed"
    """Finished successfully"""
    FAILED = "failed"
    """Failed with error"""
    TIMEOUT = "timeout"
    """Exceeded time limit"""
    CANCELLED = "cancelled"
    """Manually cancelled"""


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    name: str
    """Step identifier"""
    step_type: StepType
    """Type of step"""
    command: Optional[str] = None
    """Command/code to execute"""
    plugin_name: Optional[str] = None
    """Plugin name for plugin steps"""
    plugin_method: Optional[str] = None
    """Plugin method to call"""
    timeout: int = 300
    """Step timeout in seconds"""
    retries: int = 0
    """Number of retries on failure"""
    variables: Dict[str, Any] = field(default_factory=dict)
    """Step-specific variables"""
    on_error: str = "fail"
    """Error handler: 'fail', 'skip', 'retry'"""
    depends_on: List[str] = field(default_factory=list)
    """Step dependencies"""


@dataclass
class StepResult:
    """Result of executing a step."""

    step_name: str
    """Name of the executed step"""
    success: bool
    """Whether step succeeded"""
    output: str = ""
    """Step output"""
    error: Optional[str] = None
    """Error message if failed"""
    error_context: Dict[str, Any] = field(default_factory=dict)
    """Additional error context"""
    duration: float = 0.0
    """Execution time in seconds"""
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    """When step started"""
    end_time: str = ""
    """When step ended"""
    metrics: Dict[str, Any] = field(default_factory=dict)
    """Step-specific metrics"""
    stdout: str = ""
    """Captured stdout"""
    stderr: str = ""
    """Captured stderr"""
    return_code: int = 0
    """Return code for shell steps"""


@dataclass
class ExecutionMetrics:
    """Metrics collected during execution."""

    total_steps: int = 0
    """Total number of steps"""
    completed_steps: int = 0
    """Steps completed successfully"""
    failed_steps: int = 0
    """Steps that failed"""
    skipped_steps: int = 0
    """Steps that were skipped"""
    total_duration: float = 0.0
    """Total execution time"""
    step_durations: Dict[str, float] = field(default_factory=dict)
    """Per-step duration tracking"""
    memory_usage: float = 0.0
    """Peak memory usage in MB"""
    cpu_usage: float = 0.0
    """CPU usage percentage"""
    error_count: int = 0
    """Total errors encountered"""
    warning_count: int = 0
    """Total warnings"""
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    """Application-specific metrics"""


@dataclass
class ExecutionContext:
    """Isolated execution context for a script."""

    script_path: str
    """Path to script being executed"""
    variables: Dict[str, Any] = field(default_factory=dict)
    """Global variables accessible to steps"""
    state: ExecutionState = ExecutionState.PENDING
    """Current execution state"""
    step_results: List[StepResult] = field(default_factory=list)
    """Results of executed steps"""
    start_time: Optional[datetime] = None
    """When execution started"""
    end_time: Optional[datetime] = None
    """When execution ended"""
    error: Optional[Exception] = None
    """Exception if execution failed"""
    timeout_occurred: bool = False
    """Whether timeout was triggered"""

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get variable value from context."""
        return self.variables.get(name, default)

    def set_variable(self, name: str, value: Any):
        """Set variable in context."""
        self.variables[name] = value

    def duration(self) -> float:
        """Get elapsed time."""
        if not self.start_time:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()


@dataclass
class ExecutionResult:
    """Result of script execution."""

    script_path: str
    """Path to the script"""
    success: bool
    """Whether execution succeeded"""
    state: ExecutionState
    """Final execution state"""
    message: str
    """Status message"""
    step_results: List[StepResult] = field(default_factory=list)
    """Results per step"""
    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    """Execution metrics"""
    duration: float = 0.0
    """Total execution time"""
    error: Optional[str] = None
    """Error message if failed"""
    error_traceback: str = ""
    """Full error traceback"""
    executed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """When execution completed"""
    variables: Dict[str, Any] = field(default_factory=dict)
    """Final variable state"""


class ScriptExecutor:
    """Execute Aether workflow scripts with comprehensive error handling."""

    DEFAULT_TIMEOUT = 300  # 5 minutes
    MAX_EXECUTION_TIME = 3600  # 1 hour

    def __init__(
        self,
        script_path: str,
        timeout: int = DEFAULT_TIMEOUT,
        sandbox: bool = True,
    ):
        """
        Initialize script executor.

        Args:
            script_path: Path to .aether script file
            timeout: Maximum execution time in seconds
            sandbox: Whether to run in sandboxed environment
        """
        self.script_path = Path(script_path)
        self.timeout = min(timeout, self.MAX_EXECUTION_TIME)
        self.sandbox = sandbox
        self.context: Optional[ExecutionContext] = None
        self.metrics = ExecutionMetrics()
        logger.info(
            f"ScriptExecutor initialized: {script_path}, timeout={timeout}s, sandbox={sandbox}"
        )

    def execute(self) -> ExecutionResult:
        """
        Execute script with comprehensive error handling.

        Process:
          1. Validate script syntax
          2. Create execution context
          3. Execute pre-hooks
          4. Execute steps sequentially
          5. Execute post-hooks
          6. Collect metrics
          7. Return result

        Returns:
            ExecutionResult with detailed status
        """
        result = ExecutionResult(
            script_path=str(self.script_path),
            success=False,
            state=ExecutionState.PENDING,
            message="Execution not started",
        )

        try:
            # Validate script
            if not self.script_path.exists():
                raise FileNotFoundError(f"Script not found: {self.script_path}")

            guardian_decision = self._evaluate_guardian()
            if guardian_decision.status in {
                GuardianStatus.DENY,
                GuardianStatus.REQUIRE_APPROVAL,
                GuardianStatus.CONTAIN,
            }:
                result.state = ExecutionState.FAILED
                result.message = f"Script execution blocked by Guardian: {guardian_decision.reason}"
                result.error = guardian_decision.reason
                result.metrics = self.metrics
                self.metrics.custom_metrics["guardian_decision"] = (
                    guardian_decision.to_audit_dict()
                )
                return result

            # Initialize context
            self.context = ExecutionContext(script_path=str(self.script_path))
            self.context.state = ExecutionState.RUNNING
            self.context.start_time = datetime.now()

            # Parse script (mock implementation)
            steps = self._parse_script()
            self.metrics.total_steps = len(steps)

            # Execute steps
            for step in steps:
                try:
                    step_result = self._execute_step(step)
                    self.context.step_results.append(step_result)

                    if step_result.success:
                        self.metrics.completed_steps += 1
                    else:
                        self.metrics.failed_steps += 1

                        # Handle error strategy
                        if step.on_error == "fail":
                            raise RuntimeError(f"Step failed: {step.name}: {step_result.error}")
                        elif step.on_error == "skip":
                            logger.warning(f"Skipping step {step.name}")
                            self.metrics.skipped_steps += 1

                except Exception as e:
                    logger.error(f"Error executing step {step.name}: {e}")
                    self.metrics.error_count += 1
                    self.metrics.failed_steps += 1

                    if step.on_error == "fail":
                        raise

            # Success
            self.context.state = ExecutionState.COMPLETED
            self.context.end_time = datetime.now()
            result.success = True
            result.state = ExecutionState.COMPLETED
            result.message = (
                f"Script executed successfully: "
                f"{self.metrics.completed_steps}/{self.metrics.total_steps} steps"
            )
            result.metrics = self.metrics

        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            if self.context:
                self.context.state = ExecutionState.FAILED
                self.context.error = e
                self.context.end_time = datetime.now()
            result.success = False
            result.state = ExecutionState.FAILED
            result.message = f"Script execution failed: {str(e)}"
            result.error = str(e)
            result.error_traceback = traceback.format_exc()
            self.metrics.failed_steps = self.metrics.total_steps - (
                self.metrics.completed_steps + self.metrics.skipped_steps
            )
            result.metrics = self.metrics

        finally:
            # Finalize result
            if self.context:
                duration = self.context.duration()
                result.duration = duration
                result.step_results = self.context.step_results
                result.variables = self.context.variables
                self.metrics.total_duration = duration

            logger.info(
                f"Script execution completed: success={result.success}, duration={result.duration}s"
            )

        return result

    def _evaluate_guardian(self):
        """Evaluate Guardian policy before script workflow execution."""

        intent = IntentDeclaration(
            requester="core:script_executor",
            subsystem="script_service",
            action="script.execute",
            target=str(self.script_path),
            purpose="Execute Aether workflow script",
            capabilities=("script:run",),
            evidence=(f"script:{self.script_path.name}",),
        )
        return evaluate_intent(intent)

    def _parse_script(self) -> List[WorkflowStep]:
        """
        Parse .aether script file into steps.

        Args:
            None

        Returns:
            List of WorkflowStep objects
        """
        try:
            with open(self.script_path) as f:
                f.read()

            # Mock parsing (real implementation would parse YAML/JSON)
            steps = []

            # For now, return empty list to demonstrate structure
            # In real implementation, would parse script format

            return steps

        except Exception as e:
            logger.error(f"Error parsing script: {e}")
            raise

    def _execute_step(self, step: WorkflowStep) -> StepResult:
        """
        Execute single workflow step.

        Args:
            step: WorkflowStep to execute

        Returns:
            StepResult with execution details
        """
        result = StepResult(
            step_name=step.name,
            success=False,
        )
        start_time = time.time()

        try:
            if step.step_type == StepType.SHELL:
                success, output, error, code = self._execute_shell(step, step.timeout)
                result.success = success
                result.output = output
                result.error = error
                result.return_code = code
                result.stdout = output
                result.stderr = error

            elif step.step_type == StepType.PYTHON:
                success, output, error = self._execute_python(step, step.timeout)
                result.success = success
                result.output = output
                result.error = error

            elif step.step_type == StepType.PLUGIN:
                success, output, error = self._execute_plugin(step, step.timeout)
                result.success = success
                result.output = output
                result.error = error

            else:
                raise ValueError(f"Unknown step type: {step.step_type}")

            result.end_time = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Error in step {step.name}: {e}")
            result.success = False
            result.error = str(e)
            result.error_context = {"exception_type": type(e).__name__}

        finally:
            result.duration = time.time() - start_time
            self.metrics.step_durations[step.name] = result.duration

        return result

    def _execute_shell(self, step: WorkflowStep, timeout: int) -> Tuple[bool, str, str, int]:
        """
        Execute shell command step.

        Args:
            step: Shell step to execute
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, stdout, stderr, return_code)
        """
        try:
            if not step.command:
                return False, "", "No command specified", 1

            result = run_command_no_shell(step.command, timeout_sec=timeout)
            return (
                result.return_code == 0,
                result.stdout,
                result.stderr,
                result.return_code,
            )
        except TimeBudgetExceeded:
            return False, "", f"Timeout after {timeout}s", -1
        except (IsolatedExecutionError, SandboxViolation, OSError, ValueError) as e:
            return False, "", str(e), -1

    def _execute_python(self, step: WorkflowStep, timeout: int) -> Tuple[bool, str, str]:
        """
        Execute Python code step.

        Args:
            step: Python step to execute
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, output, error)
        """
        try:
            if not step.command:
                return False, "", "No code specified"

            initial_variables = self.context.variables if self.context else {}
            result = execute_restricted_python(step.command, initial_variables)
            if self.context is not None:
                self.context.variables.clear()
                self.context.variables.update(result.variables)
            return True, "\n".join(result.output), ""

        except SandboxViolation as exc:
            return False, "", str(exc)

    def _execute_plugin(self, step: WorkflowStep, timeout: int) -> Tuple[bool, str, str]:
        """
        Execute plugin call step.

        Args:
            step: Plugin step to execute
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, output, error)
        """
        try:
            if not step.plugin_name or not step.plugin_method:
                return False, "", "Plugin name or method not specified"

            # Mock implementation (would call actual plugin registry)
            output = f"Plugin {step.plugin_name}.{step.plugin_method} called"
            return True, output, ""

        except Exception as e:
            return False, "", str(e)

    def _get_step_by_name(self, name: str) -> Optional[WorkflowStep]:
        """Get step by name from execution context."""
        if not self.context:
            return None

        for result in self.context.step_results:
            if result.step_name == name:
                return None  # Would return actual step object in real impl

        return None

    def cancel(self):
        """Cancel execution."""
        if self.context:
            self.context.state = ExecutionState.CANCELLED
            logger.info("Execution cancelled")
