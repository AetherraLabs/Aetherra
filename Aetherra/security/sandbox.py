# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lightweight sandbox utilities for executing untrusted plugin hooks/workflows.

This is a best-effort shim:
- Default: subprocess micro-sandbox for .aether static checks (no execution) and optional Python eval with restricted globals.
- For real isolation, integrate with OS containers or a policy engine.
"""

from __future__ import annotations

# Standard library imports
import ast
import importlib
import importlib.util
import json
import multiprocessing
import os
import shlex
import subprocess
import threading
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    # Third party imports
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore

SAFE_BUILTINS = {
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
}

MAX_EXPRESSION_LENGTH = 4_096
MAX_AST_NODES = 256
MAX_SCRIPT_LENGTH = 16_384
MAX_SCRIPT_STATEMENTS = 128
MAX_COMMAND_LENGTH = 4_096
MAX_COMMAND_ARGUMENTS = 128
MAX_COMMAND_OUTPUT_BYTES = 1_048_576
MAX_CONTAINER_ITEMS = 1_000
MAX_STRING_LENGTH = 10_000

RISKY_OPERATIONS = {
    "subprocess",
    "subprocess.run",
    "os.system",
    "os.popen",
    "eval",
    "exec",
    "__import__",
}


def _is_production_profile() -> bool:
    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    return profile in {"prod", "production"}


class SandboxViolation(Exception):
    """Base sandbox violation."""

    def __init__(self, message: str = "Sandbox policy violation"):
        super().__init__(message)


class SandboxViolationError(Exception):
    """Base sandbox violation."""

    def __init__(self, message: str = "Sandbox execution violation"):
        super().__init__(message)


class TimeBudgetExceeded(SandboxViolation):
    """Raised when execution exceeds configured time budget."""

    def __init__(self, message: str = "Time budget exceeded"):
        super().__init__(message)


class MemoryBudgetExceeded(SandboxViolation):
    """Raised when execution exceeds configured memory budget."""

    def __init__(self, message: str = "Memory budget exceeded"):
        super().__init__(message)


class IsolatedExecutionError(SandboxViolation):
    """Raised when an isolated worker cannot execute safely."""


@dataclass(frozen=True)
class IsolatedCallSpec:
    """Serializable description of a callable reconstructed in a worker."""

    module_name: str
    callable_name: str
    module_path: str | None = None
    class_name: str | None = None


@dataclass(frozen=True)
class RestrictedExecutionResult:
    """Result of executing the restricted statement language."""

    variables: dict[str, Any]
    output: tuple[str, ...]


@dataclass(frozen=True)
class CommandResult:
    """Result of a non-shell subprocess invocation."""

    return_code: int
    stdout: str
    stderr: str


def _validate_variable_value(value: Any, *, depth: int = 0) -> None:
    if depth > 8:
        raise SandboxViolation("Variable nesting exceeds sandbox limit")
    if value is None or isinstance(value, bool | int | float):
        return
    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            raise SandboxViolation("String variable exceeds sandbox limit")
        return
    if isinstance(value, tuple | list):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise SandboxViolation("Container variable exceeds sandbox limit")
        for item in value:
            _validate_variable_value(item, depth=depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise SandboxViolation("Mapping variable exceeds sandbox limit")
        for key, item in value.items():
            _validate_variable_value(key, depth=depth + 1)
            _validate_variable_value(item, depth=depth + 1)
        return
    raise SandboxViolation(
        f"Unsupported sandbox variable type: {type(value).__name__}"
    )


def _validate_variables(variables: dict[str, Any] | None) -> dict[str, Any]:
    if not variables:
        return {}
    validated: dict[str, Any] = {}
    for name, value in variables.items():
        if not isinstance(name, str) or not name.isidentifier() or name.startswith("__"):
            raise SandboxViolation("Invalid sandbox variable name")
        if name in SAFE_BUILTINS:
            raise SandboxViolation(f"Variable shadows safe builtin: {name}")
        _validate_variable_value(value)
        validated[name] = value
    return validated


def safe_eval(expr: str, variables: dict[str, Any] | None = None) -> Any:
    """Evaluate a small arithmetic/logic expression safely.
    Blocks attribute access, function defs/calls (except whitelisted builtins),
    comprehensions, and dunder names.
    """
    if not isinstance(expr, str):
        raise SandboxViolation("Expression must be a string")
    if len(expr) > MAX_EXPRESSION_LENGTH:
        raise SandboxViolation("Expression exceeds sandbox length limit")
    if "__" in expr:
        raise SandboxViolation("Dunder access is not allowed")

    try:
        tree = ast.parse(expr, mode="eval")
    except Exception as e:
        raise SandboxViolation(f"Parse error: {e}") from None

    # Disallow dangerous nodes; allow ast.Call conditionally (handled below)
    forbidden = (
        ast.Attribute,
        ast.Lambda,
        ast.FunctionDef,
        ast.ClassDef,
        ast.Import,
        ast.ImportFrom,
        ast.DictComp,
        ast.ListComp,
        ast.SetComp,
        ast.GeneratorExp,
        ast.Subscript,
        ast.Yield,
        ast.YieldFrom,
        ast.Await,
        ast.With,
        ast.NamedExpr,
    )
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_AST_NODES:
        raise SandboxViolation("Expression exceeds sandbox complexity limit")
    for node in nodes:
        if isinstance(node, forbidden):
            raise SandboxViolation(f"Forbidden construct: {type(node).__name__}")
        if isinstance(node, ast.Call) and (
            not isinstance(node.func, ast.Name) or node.func.id not in SAFE_BUILTINS
        ):
            raise SandboxViolation("Forbidden function call")

    safe_locals = _validate_variables(variables)
    _validate_expression_resources(nodes, safe_locals)

    # Safe evaluation: use eval with restricted globals and provided variables
    safe_globals = {"__builtins__": SAFE_BUILTINS}
    # nosec B307: eval used in controlled sandbox with restricted globals/builtins
    return eval(compile(tree, "<sandbox>", "eval"), safe_globals, safe_locals)


def _simple_operand_value(node: ast.AST, variables: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return variables.get(node.id)
    return None


def _validate_expression_resources(
    nodes: list[ast.AST], variables: dict[str, Any]
) -> None:
    for node in nodes:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str) and len(node.value) > MAX_STRING_LENGTH:
                raise SandboxViolation("String literal exceeds sandbox limit")
            if isinstance(node.value, int) and abs(node.value) > 10**12:
                raise SandboxViolation("Integer literal exceeds sandbox limit")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            exponent = _simple_operand_value(node.right, variables)
            if not isinstance(exponent, int) or isinstance(exponent, bool) or abs(exponent) > 16:
                raise SandboxViolation("Exponent exceeds sandbox limit")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            left = _simple_operand_value(node.left, variables)
            right = _simple_operand_value(node.right, variables)
            sequence, multiplier = (
                (left, right)
                if isinstance(left, str | list | tuple)
                else (right, left)
            )
            if isinstance(sequence, str | list | tuple) and isinstance(multiplier, int):
                limit = MAX_STRING_LENGTH if isinstance(sequence, str) else MAX_CONTAINER_ITEMS
                if multiplier < 0 or len(sequence) * multiplier > limit:
                    raise SandboxViolation("Sequence multiplication exceeds sandbox limit")


def _expression_source(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except (AttributeError, ValueError) as exc:
        raise SandboxViolation("Unable to normalize restricted expression") from exc


def _validate_assignment_name(name: str) -> None:
    if not name.isidentifier() or name.startswith("__") or name in SAFE_BUILTINS:
        raise SandboxViolation(f"Invalid assignment target: {name}")


def execute_restricted_python(
    code: str,
    variables: dict[str, Any] | None = None,
) -> RestrictedExecutionResult:
    """Execute a deliberately small, non-Turing-complete Python subset.

    Supported statements are simple name assignments and expression statements.
    The only callable statement is ``print(...)``; expression calls remain limited
    to ``SAFE_BUILTINS`` through :func:`safe_eval`.
    """
    if not isinstance(code, str):
        raise SandboxViolation("Restricted script must be a string")
    if len(code) > MAX_SCRIPT_LENGTH:
        raise SandboxViolation("Restricted script exceeds length limit")
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise SandboxViolation(f"Parse error: {exc.msg}") from None
    if len(tree.body) > MAX_SCRIPT_STATEMENTS:
        raise SandboxViolation("Restricted script exceeds statement limit")

    state = _validate_variables(variables).copy()
    output: list[str] = []
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
                raise SandboxViolation("Only simple name assignments are allowed")
            name = statement.targets[0].id
            _validate_assignment_name(name)
            value = safe_eval(_expression_source(statement.value), state)
            _validate_variable_value(value)
            state[name] = value
            continue

        if isinstance(statement, ast.Expr):
            expression = statement.value
            if (
                isinstance(expression, ast.Call)
                and isinstance(expression.func, ast.Name)
                and expression.func.id == "print"
            ):
                if expression.keywords:
                    raise SandboxViolation("print keyword arguments are not allowed")
                values = [
                    safe_eval(_expression_source(argument), state)
                    for argument in expression.args
                ]
                output.append(" ".join(str(value) for value in values))
                continue
            safe_eval(_expression_source(expression), state)
            continue

        raise SandboxViolation(
            f"Forbidden restricted statement: {type(statement).__name__}"
        )

    return RestrictedExecutionResult(variables=state, output=tuple(output))


def parse_command_arguments(command: str) -> list[str]:
    """Parse a command string without permitting shell operators."""
    if not isinstance(command, str) or not command.strip():
        raise SandboxViolation("Command must be a non-empty string")
    if len(command) > MAX_COMMAND_LENGTH:
        raise SandboxViolation("Command exceeds length limit")
    if any(character in command for character in ("\n", "\r", "\x00")):
        raise SandboxViolation("Command contains forbidden control characters")
    try:
        arguments = shlex.split(command, posix=os.name != "nt")
    except ValueError as exc:
        raise SandboxViolation(f"Invalid command quoting: {exc}") from exc
    if os.name == "nt":
        arguments = [
            argument[1:-1]
            if len(argument) >= 2 and argument[0] == argument[-1] == '"'
            else argument
            for argument in arguments
        ]
    if not arguments or len(arguments) > MAX_COMMAND_ARGUMENTS:
        raise SandboxViolation("Command has an invalid argument count")
    shell_tokens = {"|", "||", "&", "&&", ";", ">", ">>", "<", "<<"}
    if any(argument in shell_tokens for argument in arguments):
        raise SandboxViolation("Shell operators are not allowed")
    return arguments


def run_command_no_shell(command: str, *, timeout_sec: float = 30.0) -> CommandResult:
    """Run one executable directly with bounded output and no shell expansion."""
    arguments = parse_command_arguments(command)
    try:
        completed = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            shell=False,
            text=False,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeBudgetExceeded(f"Command exceeded {timeout_sec:g}s") from exc
    except OSError as exc:
        raise IsolatedExecutionError(f"Unable to start command: {exc}") from exc

    stdout_bytes = completed.stdout or b""
    stderr_bytes = completed.stderr or b""
    if (
        len(stdout_bytes) > MAX_COMMAND_OUTPUT_BYTES
        or len(stderr_bytes) > MAX_COMMAND_OUTPUT_BYTES
    ):
        raise SandboxViolation("Command output exceeds sandbox limit")
    return CommandResult(
        return_code=completed.returncode,
        stdout=stdout_bytes.decode("utf-8", errors="replace"),
        stderr=stderr_bytes.decode("utf-8", errors="replace"),
    )


def run_with_timeout(
    func,
    args: tuple | None = None,
    kwargs: dict | None = None,
    timeout_sec: float = 5.0,
):
    """Run trusted cooperative code with a wall-clock timeout.

    The worker thread cannot be forcibly stopped. Use ``run_isolated`` for
    untrusted or potentially non-terminating code.
    """
    result: dict[str, Any] = {"value": None, "error": None}

    def _target() -> Any:
        try:
            result["value"] = func(*(args or ()), **(kwargs or {}))
        except Exception as e:
            result["error"] = e

    th = threading.Thread(target=_target, daemon=True)
    th.start()
    th.join(timeout=timeout_sec)
    if th.is_alive():
        raise TimeBudgetExceeded(f"Execution exceeded {timeout_sec}s")
    if result["error"] is not None:
        raise result["error"]  # re-raise original
    return result["value"]


def _json_round_trip(value: Any, label: str) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False))
    except (TypeError, ValueError) as exc:
        raise IsolatedExecutionError(f"{label} must be JSON-serializable") from exc


def _load_isolated_callable(spec: IsolatedCallSpec):
    if spec.module_path:
        module_path = Path(spec.module_path).resolve()
        module_spec = importlib.util.spec_from_file_location(spec.module_name, module_path)
        if module_spec is None or module_spec.loader is None:
            raise ImportError(f"unable to load module from {module_path}")
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
    else:
        module = importlib.import_module(spec.module_name)
    target: Any = module
    if spec.class_name:
        plugin_class = getattr(module, spec.class_name)
        target = plugin_class()
    callable_object = getattr(target, spec.callable_name)
    if not callable(callable_object):
        raise TypeError(f"isolated target is not callable: {spec.callable_name}")
    return callable_object


def _isolated_worker(connection, spec: IsolatedCallSpec, args_json: str, kwargs_json: str):
    try:
        callable_object = _load_isolated_callable(spec)
        result = callable_object(*json.loads(args_json), **json.loads(kwargs_json))
        payload = {"ok": True, "result": _json_round_trip(result, "isolated result")}
    except BaseException as exc:  # Worker must report plugin failures without escaping.
        payload = {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(limit=20),
        }
    try:
        connection.send_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    finally:
        connection.close()


def run_isolated(
    spec: IsolatedCallSpec,
    *,
    args: tuple[Any, ...] | list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    timeout_sec: float = 5.0,
    max_memory_mb: float | None = None,
) -> Any:
    """Execute a reconstructable callable in a terminable worker process."""
    try:
        timeout = float(timeout_sec)
    except (TypeError, ValueError) as exc:
        raise ValueError("timeout_sec must be numeric") from exc
    if timeout <= 0:
        raise ValueError("timeout_sec must be greater than zero")
    memory_limit = None
    if max_memory_mb is not None:
        try:
            memory_limit = float(max_memory_mb)
        except (TypeError, ValueError) as exc:
            raise ValueError("max_memory_mb must be numeric") from exc
        if memory_limit <= 0:
            raise ValueError("max_memory_mb must be greater than zero")

    clean_args = _json_round_trip(list(args or ()), "isolated arguments")
    clean_kwargs = _json_round_trip(dict(kwargs or {}), "isolated keyword arguments")
    context = multiprocessing.get_context("spawn")
    parent_connection, child_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=_isolated_worker,
        args=(
            child_connection,
            spec,
            json.dumps(clean_args, ensure_ascii=False),
            json.dumps(clean_kwargs, ensure_ascii=False),
        ),
        daemon=True,
    )
    process.start()
    child_connection.close()
    deadline = time.monotonic() + timeout
    try:
        while process.is_alive():
            if time.monotonic() >= deadline:
                process.terminate()
                process.join(timeout=1)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=1)
                raise TimeBudgetExceeded(f"Execution exceeded {timeout:g}s")
            if memory_limit is not None and psutil is not None:
                try:
                    rss_mb = psutil.Process(process.pid).memory_info().rss / (1024 * 1024)
                    if rss_mb > memory_limit:
                        process.terminate()
                        process.join(timeout=1)
                        raise MemoryBudgetExceeded(
                            f"Worker memory {rss_mb:.1f}MB exceeds budget {memory_limit:.1f}MB"
                        )
                except psutil.NoSuchProcess:
                    break
            if parent_connection.poll(0.01):
                break
        process.join(timeout=1)
        if not parent_connection.poll():
            raise IsolatedExecutionError(
                f"isolated worker exited without a result (exit code {process.exitcode})"
            )
        try:
            payload = json.loads(parent_connection.recv_bytes())
        except (EOFError, UnicodeError, json.JSONDecodeError) as exc:
            raise IsolatedExecutionError("isolated worker returned invalid data") from exc
        if not isinstance(payload, dict) or payload.get("ok") is not True:
            error_type = payload.get("error_type", "ExecutionError") if isinstance(payload, dict) else "ExecutionError"
            error = payload.get("error", "unknown worker failure") if isinstance(payload, dict) else "invalid worker response"
            raise IsolatedExecutionError(f"{error_type}: {error}")
        return payload.get("result")
    finally:
        parent_connection.close()
        if process.is_alive():
            process.kill()
            process.join(timeout=1)


def ensure_memory_budget(max_mb: float | None) -> None:
    """Raise MemoryBudgetExceeded if current process RSS exceeds max_mb."""
    if not max_mb:
        return
    if psutil is None:
        return
    try:
        proc = psutil.Process()
        rss_mb = float(proc.memory_info().rss) / (1024.0 * 1024.0)
        budget_mb = float(max_mb)
    except (AttributeError, OSError, TypeError, ValueError) as exc:
        raise SandboxViolation(f"Unable to evaluate memory budget: {exc}") from exc
    if budget_mb <= 0:
        raise SandboxViolation("Memory budget must be greater than zero")
    if rss_mb > budget_mb:
        raise MemoryBudgetExceeded(
            f"Process memory {rss_mb:.1f}MB exceeds budget {budget_mb:.1f}MB"
        )


class SecuritySandbox:
    """Minimal SecuritySandbox implementation expected by tests.

    Accepts a configuration dictionary with optional keys:
      - memory_limit (int MB)
      - timeout (seconds for generic operations)
      - max_operations (int pseudo budget)
      - allowed_modules (list[str])
      - blocked_functions (list[str])

    The implementation is intentionally lightweight but now applies stricter
    defaults in production-like profiles, blocking obviously risky operations
    unless explicitly allowed in configuration.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._ops = 0
        self._max_ops = int(self.config.get("max_operations", 10_000) or 10_000)
        self._memory_limit = self.config.get("memory_limit")
        self._timeout = float(self.config.get("timeout", 5) or 5)
        self._allowed_modules = set(self.config.get("allowed_modules", []) or [])
        self._blocked_functions = set(self.config.get("blocked_functions", []) or [])
        if _is_production_profile():
            self._blocked_functions.update(RISKY_OPERATIONS)

    # Simple allow list semantics; expand later as needed
    def is_allowed(self, operation: str) -> bool:
        op = (operation or "").strip().lower()
        if not op:
            return False
        if op in self._blocked_functions:
            return False
        # Increment operation counter
        self._ops += 1
        if self._ops > self._max_ops:
            raise TimeBudgetExceeded("Operation budget exceeded")
        return True

    def check_resource_limits(self) -> None:
        # Memory budget check (best-effort)
        ensure_memory_budget(self._memory_limit)
        # Time budget is enforced per operation via run_with_timeout if used externally.
        return

    # Convenience wrapper to execute a callable under timeout & memory check
    def run(self, func, *args, **kwargs) -> Any:  # pragma: no cover - thin wrapper
        self.check_resource_limits()
        timeout = kwargs.pop("timeout", self._timeout)
        return run_with_timeout(func, args=args, kwargs=kwargs, timeout_sec=timeout)


__all__ = [
    "IsolatedCallSpec",
    "IsolatedExecutionError",
    "CommandResult",
    "RestrictedExecutionResult",
    "SecuritySandbox",
    "SandboxViolation",
    "TimeBudgetExceeded",
    "MemoryBudgetExceeded",
    "safe_eval",
    "execute_restricted_python",
    "parse_command_arguments",
    "run_command_no_shell",
    "run_isolated",
    "run_with_timeout",
    "ensure_memory_budget",
]
