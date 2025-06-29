"""
NeuroCode Core Package
====================

The core engine of the NeuroCode programming language.
Contains all fundamental components for parsing, interpretation, and execution.
"""

from .ai import create_ai_runtime
from .interpreter import create_interpreter, execute_code
from .memory import create_memory_system
from .parser import create_parser, parse_code, parse_intent

__version__ = "2.0.0"
__all__ = [
    "create_parser",
    "parse_code",
    "parse_intent",
    "create_interpreter",
    "execute_code",
    "create_memory_system",
    "create_ai_runtime",
]
