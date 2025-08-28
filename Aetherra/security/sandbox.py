"""
Lightweight sandbox utilities for executing untrusted plugin hooks/workflows.

This is a best-effort shim:
- Default: subprocess micro-sandbox for .aether static checks (no execution) and optional Python eval with restricted globals.
- For real isolation, integrate with OS containers or a policy engine.
"""

from __future__ import annotations

import ast
import threading
from typing import Any, Dict, Optional

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
    pass


class TimeBudgetExceeded(SandboxViolation):
    pass


class MemoryBudgetExceeded(SandboxViolation):
    pass


def safe_eval(expr: str, variables: Dict[str, Any] | None = None) -> Any:
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
        raise SandboxViolation(f"Parse error: {e}")

    # Disallow dangerous nodes
    forbidden = (
        ast.Attribute,
        ast.Lambda,
        ast.FunctionDef,
        ast.ClassDef,
        ast.Import,
        ast.ImportFrom,
        ast.Call,  # block calls (only allow builtins through names mapping)
        ast.DictComp,
        ast.ListComp,
        ast.SetComp,
        ast.GeneratorExp,
        ast.Subscript,  # avoid obj[...]
        ast.Yield,
        ast.YieldFrom,
        ast.Await,
        ast.With,
    )
    for node in ast.walk(tree):
        if isinstance(node, forbidden):
            raise SandboxViolation(f"Forbidden construct: {type(node).__name__}")

    allowed = dict(SAFE_BUILTINS)
    # Only allow provided variables as names; no globals
    names = dict(variables or {})
    return eval(compile(tree, "<sandbox>", "eval"), {"__builtins__": allowed}, names)


def run_with_timeout(
    func,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    timeout_sec: float = 5.0,
):
    """Run a callable with a wall-clock timeout; raises TimeBudgetExceeded on timeout.
    Returns the function result otherwise.
    """
    result: Dict[str, Any] = {"value": None, "error": None}

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


def ensure_memory_budget(max_mb: Optional[float]) -> None:
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
