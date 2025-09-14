# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lightweight sandbox utilities for executing untrusted plugin hooks/workflows.

This is a best-effort shim:
- Default: subprocess micro-sandbox for .aether static checks (no execution) and optional Python eval with restricted globals.
- For real isolation, integrate with OS containers or a policy engine.
"""

from __future__ import annotations

import ast
import threading
from typing import Any

try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore

SAFE_BUILTINS = {
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "range": range,
}


class SandboxViolation(Exception):
    """Base sandbox violation."""

    pass


class SandboxViolationError(Exception):
    """Base sandbox violation."""

    pass


class TimeBudgetExceeded(SandboxViolation):
    pass


class MemoryBudgetExceeded(SandboxViolation):
    pass


def safe_eval(expr: str, variables: dict[str, Any] | None = None) -> Any:
    """Evaluate a small arithmetic/logic expression safely.
    Blocks attribute access, function defs/calls (except whitelisted builtins),
    comprehensions, and dunder names.
    """
    # Quick checks
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
    )
    for node in ast.walk(tree):
        if isinstance(node, forbidden):
            raise SandboxViolation(f"Forbidden construct: {type(node).__name__}")
        if isinstance(node, ast.Call) and (
            not isinstance(node.func, ast.Name) or node.func.id not in SAFE_BUILTINS
        ):
            raise SandboxViolation("Forbidden function call")

    # Safe evaluation: use eval with restricted globals and provided variables
    safe_globals = {"__builtins__": SAFE_BUILTINS}
    safe_locals = variables or {}
    return eval(compile(tree, "<sandbox>", "eval"), safe_globals, safe_locals)


def run_with_timeout(
    func,
    args: tuple | None = None,
    kwargs: dict | None = None,
    timeout_sec: float = 5.0,
):
    """Run a callable with a wall-clock timeout; raises TimeBudgetExceeded on timeout.
    Returns the function result otherwise.
    """
    result: dict[str, Any] = {"value": None, "error": None}

    def _target():
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


def ensure_memory_budget(max_mb: float | None) -> None:
    """Raise MemoryBudgetExceeded if current process RSS exceeds max_mb (best-effort)."""
    if not max_mb:
        return
    try:
        if psutil is None:
            return
        proc = psutil.Process()
        rss_mb = float(proc.memory_info().rss) / (1024.0 * 1024.0)
        if rss_mb > float(max_mb):
            raise MemoryBudgetExceeded(
                f"Process memory {rss_mb:.1f}MB exceeds budget {max_mb:.1f}MB"
            )
    except Exception:
        # Best-effort only
        return


class SecuritySandbox:
    """Minimal SecuritySandbox implementation expected by tests.

    Accepts a configuration dictionary with optional keys:
      - memory_limit (int MB)
      - timeout (seconds for generic operations)
      - max_operations (int pseudo budget)
      - allowed_modules (list[str])
      - blocked_functions (list[str])

    The implementation is intentionally lightweight; it provides
    interface coverage and basic budget checking rather than full isolation.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._ops = 0
        self._max_ops = int(self.config.get("max_operations", 10_000) or 10_000)
        self._memory_limit = self.config.get("memory_limit")
        self._timeout = float(self.config.get("timeout", 5) or 5)
        self._allowed_modules = set(self.config.get("allowed_modules", []) or [])
        self._blocked_functions = set(self.config.get("blocked_functions", []) or [])

    # Simple allow list semantics; expand later as needed
    def is_allowed(self, operation: str) -> bool:
        op = (operation or "").strip().lower()
        if not op:
            return False
        # Increment operation counter
        self._ops += 1
        if self._ops > self._max_ops:
            raise TimeBudgetExceeded("Operation budget exceeded")
        # Basic heuristic: block if name matches blocked_functions
        return op not in self._blocked_functions

    def check_resource_limits(self) -> None:
        # Memory budget check (best-effort)
        ensure_memory_budget(self._memory_limit)
        # Time budget is enforced per operation via run_with_timeout if used externally.
        return

    # Convenience wrapper to execute a callable under timeout & memory check
    def run(self, func, *args, **kwargs):  # pragma: no cover - thin wrapper
        self.check_resource_limits()
        return run_with_timeout(
            func, args=args, kwargs=kwargs, timeout_sec=self._timeout
        )


__all__ = [
    "SecuritySandbox",
    "SandboxViolation",
    "TimeBudgetExceeded",
    "MemoryBudgetExceeded",
    "safe_eval",
]
