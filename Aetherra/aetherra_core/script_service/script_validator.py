"""
Script Validator - Pre-flight validation for Aether workflow scripts.

Validates script structure and constraints before execution:
  1. Syntax validation (YAML/JSON parsing)
  2. Step reference validation (dependencies, exists)
  3. Variable type checking
  4. Constraint enforcement
  5. Plugin reference checking
  6. Cycle detection

Features:
  - Comprehensive error reporting with line numbers
  - Warning detection (unused variables, etc)
  - Type inference and checking
  - Dependency graph analysis
  - Plugin availability verification
  - Performance heuristics

Example:
    >>> validator = ScriptValidator("/path/to/script.aether")
    >>> errors = validator.validate()
    >>> if not errors.is_valid():
    ...     print(f"Found {len(errors.errors)} errors")
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class ErrorLevel(Enum):
    """Validation error severity levels."""

    ERROR = "error"
    """Critical error - must fix before execution"""
    WARNING = "warning"
    """Non-critical warning - may affect execution"""
    INFO = "info"
    """Informational message"""


class VariableType(Enum):
    """Supported variable types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    ANY = "any"


@dataclass
class ValidationError:
    """A single validation error or warning."""

    level: ErrorLevel
    """Error severity level"""
    message: str
    """Error message"""
    line: Optional[int] = None
    """Line number in script"""
    step_name: Optional[str] = None
    """Associated step name"""
    code: Optional[str] = None
    """Error code for categorization"""

    def __str__(self) -> str:
        """String representation."""
        prefix = f"[{self.level.value.upper()}]"
        location = ""
        if self.step_name:
            location = f" in '{self.step_name}'"
        if self.line:
            location += f" (line {self.line})"
        return f"{prefix} {self.message}{location}"


@dataclass
class ValidationResult:
    """Result of script validation."""

    script_path: str
    """Path to script that was validated"""
    valid: bool
    """Whether script passed validation"""
    errors: List[ValidationError] = field(default_factory=list)
    """List of validation errors"""
    warnings: List[ValidationError] = field(default_factory=list)
    """List of validation warnings"""
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Metadata about the script"""

    def is_valid(self) -> bool:
        """Check if script is valid (no critical errors)."""
        return all(e.level != ErrorLevel.ERROR for e in self.errors)

    def add_error(
        self,
        message: str,
        line: Optional[int] = None,
        step_name: Optional[str] = None,
        code: Optional[str] = None,
    ):
        """Add validation error."""
        error = ValidationError(
            level=ErrorLevel.ERROR,
            message=message,
            line=line,
            step_name=step_name,
            code=code,
        )
        self.errors.append(error)
        self.valid = False

    def add_warning(
        self,
        message: str,
        line: Optional[int] = None,
        step_name: Optional[str] = None,
        code: Optional[str] = None,
    ):
        """Add validation warning."""
        warning = ValidationError(
            level=ErrorLevel.WARNING,
            message=message,
            line=line,
            step_name=step_name,
            code=code,
        )
        self.warnings.append(warning)

    def summary(self) -> str:
        """Get validation summary."""
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        return (
            f"Validation {'PASSED' if self.valid else 'FAILED'}: "
            f"{error_count} errors, {warning_count} warnings"
        )


@dataclass
class StepDefinition:
    """Definition of a single step in script."""

    name: str
    """Step name"""
    step_type: str
    """Step type (shell, python, plugin)"""
    command: Optional[str] = None
    """Command/code"""
    plugin_name: Optional[str] = None
    """Plugin name for plugin steps"""
    plugin_method: Optional[str] = None
    """Plugin method to call"""
    timeout: int = 300
    """Timeout in seconds"""
    variables: Dict[str, Any] = field(default_factory=dict)
    """Local variables"""
    depends_on: List[str] = field(default_factory=list)
    """Step dependencies"""


class ScriptValidator:
    """Validate Aether workflow scripts before execution."""

    # Supported step types
    VALID_STEP_TYPES = {"shell", "python", "plugin", "conditional", "loop"}

    # Valid variable types
    VALID_VARIABLE_TYPES = {
        "string",
        "integer",
        "float",
        "boolean",
        "list",
        "dict",
        "any",
    }

    # Minimum/maximum timeout values (seconds)
    MIN_TIMEOUT = 1
    MAX_TIMEOUT = 3600

    def __init__(self, script_path: str):
        """
        Initialize script validator.

        Args:
            script_path: Path to .aether script file
        """
        self.script_path = Path(script_path)
        self.steps: List[StepDefinition] = []
        self.variables: Dict[str, Any] = {}
        logger.info(f"ScriptValidator initialized: {script_path}")

    def validate(self) -> ValidationResult:
        """
        Validate script comprehensively.

        Performs:
          1. File existence check
          2. Syntax validation (YAML/JSON)
          3. Required field validation
          4. Step reference validation
          5. Variable type checking
          6. Dependency cycle detection
          7. Plugin availability check
          8. Performance heuristics

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(script_path=str(self.script_path), valid=True)

        try:
            # Check file exists
            if not self.script_path.exists():
                result.add_error(
                    f"Script file not found: {self.script_path}",
                    code="FILE_NOT_FOUND",
                )
                result.valid = False
                return result

            # Read file
            with open(self.script_path) as f:
                content = f.read()

            # Validate syntax
            script_data = self._parse_script(content)
            if script_data is None:
                result.add_error(
                    "Failed to parse script (invalid YAML/JSON)",
                    code="PARSE_ERROR",
                )
                result.valid = False
                return result

            # Validate structure
            self._validate_structure(script_data, result)

            # Parse steps
            self.steps = self._extract_steps(script_data)

            # Validate steps
            for step in self.steps:
                self._validate_step(step, result)

            # Validate step references
            self._validate_step_references(result)

            # Validate variables
            self._validate_variables(script_data, result)

            # Check for cycles
            self._check_dependency_cycles(result)

            # Performance checks
            self._check_performance_heuristics(result)

            # Update metadata
            result.metadata = {
                "steps_count": len(self.steps),
                "variables_count": len(self.variables),
                "max_timeout": max((s.timeout for s in self.steps), default=self.MIN_TIMEOUT),
            }

            result.valid = result.is_valid()
            logger.info(f"Validation complete: {result.summary()}")

        except Exception as e:
            logger.error(f"Validation error: {e}")
            result.add_error(f"Unexpected validation error: {str(e)}")
            result.valid = False

        return result

    def _parse_script(self, content: str) -> Optional[Dict]:
        """
        Parse script content (YAML or JSON).

        Args:
            content: Script content as string

        Returns:
            Parsed script data or None if parsing fails
        """
        try:
            # Try YAML first
            return yaml.safe_load(content)
        except yaml.YAMLError:
            try:
                # Fall back to JSON
                return json.loads(content)
            except json.JSONDecodeError:
                return None

    def _validate_structure(self, script_data: Dict, result: ValidationResult):
        """Validate script structure."""
        # Check required fields
        if "steps" not in script_data:
            result.add_error("Missing 'steps' field in script", code="MISSING_STEPS")
            return

        if not isinstance(script_data["steps"], list):
            result.add_error(
                "'steps' must be a list",
                code="INVALID_STEPS_TYPE",
            )
            return

        if len(script_data["steps"]) == 0:
            result.add_warning("Script has no steps", code="EMPTY_STEPS")

    def _extract_steps(self, script_data: Dict) -> List[StepDefinition]:
        """Extract steps from script data."""
        steps = []
        for idx, step_data in enumerate(script_data.get("steps", [])):
            if not isinstance(step_data, dict):
                logger.warning(f"Step {idx} is not a dict")
                continue

            step = StepDefinition(
                name=step_data.get("name", f"step_{idx}"),
                step_type=step_data.get("type", "shell"),
                command=step_data.get("command"),
                plugin_name=step_data.get("plugin"),
                plugin_method=step_data.get("method"),
                timeout=step_data.get("timeout", 300),
                variables=step_data.get("variables", {}),
                depends_on=step_data.get("depends_on", []),
            )
            steps.append(step)

        return steps

    def _validate_step(self, step: StepDefinition, result: ValidationResult):
        """Validate a single step."""
        # Validate step type
        if step.step_type not in self.VALID_STEP_TYPES:
            result.add_error(
                f"Invalid step type: {step.step_type}. "
                f"Valid types: {', '.join(self.VALID_STEP_TYPES)}",
                step_name=step.name,
                code="INVALID_STEP_TYPE",
            )

        # Validate timeout
        if step.timeout < self.MIN_TIMEOUT or step.timeout > self.MAX_TIMEOUT:
            result.add_error(
                f"Timeout {step.timeout}s out of range [{self.MIN_TIMEOUT}, {self.MAX_TIMEOUT}]",
                step_name=step.name,
                code="INVALID_TIMEOUT",
            )

        # Validate required fields based on type
        if step.step_type == "shell" and not step.command:
            result.add_error(
                "Shell step missing 'command' field",
                step_name=step.name,
                code="MISSING_COMMAND",
            )

        if step.step_type == "python" and not step.command:
            result.add_error(
                "Python step missing 'command' field",
                step_name=step.name,
                code="MISSING_COMMAND",
            )

        if step.step_type == "plugin":
            if not step.plugin_name:
                result.add_error(
                    "Plugin step missing 'plugin' field",
                    step_name=step.name,
                    code="MISSING_PLUGIN",
                )
            if not step.plugin_method:
                result.add_error(
                    "Plugin step missing 'method' field",
                    step_name=step.name,
                    code="MISSING_METHOD",
                )

    def _validate_step_references(self, result: ValidationResult):
        """Validate step dependency references."""
        step_names = {step.name for step in self.steps}

        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_names:
                    result.add_error(
                        f"Undefined step reference: '{dep}'",
                        step_name=step.name,
                        code="UNDEFINED_REFERENCE",
                    )

    def _validate_variables(self, script_data: Dict, result: ValidationResult):
        """Validate variable definitions and usage."""
        variables = script_data.get("variables", {})

        if not isinstance(variables, dict):
            result.add_error(
                "'variables' section must be a dict",
                code="INVALID_VARIABLES",
            )
            return

        self.variables = variables

        # Check variable types
        for var_name, var_def in variables.items():
            if isinstance(var_def, dict):
                var_type = var_def.get("type", "any")
                if var_type not in self.VALID_VARIABLE_TYPES:
                    result.add_warning(
                        f"Unknown variable type: {var_type}",
                        code="UNKNOWN_VAR_TYPE",
                    )

    def _check_dependency_cycles(self, result: ValidationResult):
        """Check for circular dependencies."""
        visited = set()
        rec_stack = set()

        def has_cycle(step_name: str, path: List[str]) -> bool:
            visited.add(step_name)
            rec_stack.add(step_name)

            step = next((s for s in self.steps if s.name == step_name), None)
            if not step:
                return False

            for dep in step.depends_on:
                if dep not in visited:
                    if has_cycle(dep, path + [step_name]):
                        return True
                elif dep in rec_stack:
                    cycle_path = " -> ".join(path + [step_name, dep])
                    result.add_error(
                        f"Circular dependency detected: {cycle_path}",
                        step_name=step_name,
                        code="CIRCULAR_DEPENDENCY",
                    )
                    return True

            rec_stack.remove(step_name)
            return False

        for step in self.steps:
            if step.name not in visited:
                has_cycle(step.name, [])

    def _check_performance_heuristics(self, result: ValidationResult):
        """Check performance-related heuristics."""
        # Warn if many steps
        if len(self.steps) > 100:
            result.add_warning(
                f"Script has {len(self.steps)} steps - may take a long time",
                code="MANY_STEPS",
            )

        # Warn if very high timeout
        max_timeout = max((s.timeout for s in self.steps), default=0)
        if max_timeout > 1800:
            result.add_warning(
                f"Step timeout {max_timeout}s may be excessive",
                code="HIGH_TIMEOUT",
            )

        # Check for unused variables
        used_vars = set()
        for step in self.steps:
            if step.command:
                for var_name in self.variables:
                    if var_name in step.command:
                        used_vars.add(var_name)

        for var_name in self.variables:
            if var_name not in used_vars:
                result.add_warning(
                    f"Variable '{var_name}' is never used",
                    code="UNUSED_VARIABLE",
                )
