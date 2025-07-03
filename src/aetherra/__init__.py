# -*- coding: utf-8 -*-
"""
Aetherra Programming Language
=============================

A revolutionary AI-native programming language with natural language integration,
advanced memory systems, and modular architecture.

Version: 2.0.0
License: MIT
"""

# Core functionality (always available)
from .core import create_interpreter, create_memory_system, create_parser
from .ui import launch_gui

# Optional CLI functionality
try:
    from .cli.main import main as cli_main

    CLI_AVAILABLE = True
except ImportError:
    print("⚠️ CLI modules have dependency issues, core functionality available")

    def cli_main() -> None:
        print("CLI functionality not available due to missing dependencies")

    CLI_AVAILABLE = False

__version__ = "2.0.0"
__author__ = "Aetherra Development Team"
__license__ = "MIT"

__all__ = [
    "create_parser",
    "create_interpreter",
    "create_memory_system",
    "launch_gui",
    "cli_main",
    "CLI_AVAILABLE",
]
