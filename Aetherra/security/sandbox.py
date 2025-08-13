"""
Lightweight sandbox utilities for executing untrusted plugin hooks/workflows.

This is a best-effort shim:
- Default: subprocess micro-sandbox for .aether static checks (no execution) and optional Python eval with restricted globals.
- For real isolation, integrate with OS containers or a policy engine.
"""

from __future__ import annotations

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
    """Evaluate a simple expression with restricted builtins.
    Not suitable for untrusted arbitrary code; used for small expressions.
    """
    allowed = dict(SAFE_BUILTINS)
    vars = dict(variables or {})
    # Remove dunder access
    if any(seg.startswith("__") for seg in expr.split(".")):
        raise SandboxViolation("Dunder access is not allowed")
    return eval(expr, {"__builtins__": allowed}, vars)
