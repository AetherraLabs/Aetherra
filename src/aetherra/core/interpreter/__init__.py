"""
Aetherra Interpreter Subsystem
==============================

Core interpretation and execution engine for Aetherra.
Handles code execution, debugging, and runtime management.
"""

from .base import AetherraInterpreter
from .enhanced import EnhancedAetherraInterpreter

__all__ = [
    "AetherraInterpreter",
    "EnhancedAetherraInterpreter",
    "BlockExecutor",
    "NeuroDebugSystem",
]


def create_interpreter(enhanced=True):
    """Create a Aetherra interpreter instance."""
    if enhanced:
        return EnhancedAetherraInterpreter()
    return AetherraInterpreter()


def execute_code(code: str, enhanced=True):
    """Execute Aetherra source code."""
    interpreter = create_interpreter(enhanced)
    return interpreter.execute(code)
