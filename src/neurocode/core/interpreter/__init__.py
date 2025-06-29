"""
NeuroCode Interpreter Subsystem
==============================

Core interpretation and execution engine for NeuroCode.
Handles code execution, debugging, and runtime management.
"""

from .base import NeuroCodeInterpreter
from .block_executor import BlockExecutor
from .debug_system import DebugSystem
from .enhanced import EnhancedInterpreter

__all__ = ["NeuroCodeInterpreter", "EnhancedInterpreter", "BlockExecutor", "DebugSystem"]


def create_interpreter(enhanced=True):
    """Create a NeuroCode interpreter instance."""
    if enhanced:
        return EnhancedInterpreter()
    return NeuroCodeInterpreter()


def execute_code(code: str, enhanced=True):
    """Execute NeuroCode source code."""
    interpreter = create_interpreter(enhanced)
    return interpreter.execute(code)
