"""
Lightweight sandbox utilities for executing untrusted plugin hooks/workflows.

This is a best-effort shim:
- Default: subprocess micro-sandbox for .aether static checks (no execution) and optional Python eval with restricted globals.
- For real isolation, integrate with OS containers or a policy engine.
"""

from __future__ import annotations

import ast
from typing import Any, Dict

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
