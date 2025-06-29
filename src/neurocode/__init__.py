"""
NeuroCode Programming Language
=============================

A revolutionary AI-native programming language with natural language integration,
advanced memory systems, and modular architecture.

Version: 2.0.0
License: MIT
"""

from .cli import main as cli_main
from .core import create_interpreter, create_memory_system, create_parser
from .ui import launch_gui

__version__ = "2.0.0"
__author__ = "NeuroCode Development Team"
__license__ = "MIT"

__all__ = ["create_parser", "create_interpreter", "create_memory_system", "launch_gui", "cli_main"]
