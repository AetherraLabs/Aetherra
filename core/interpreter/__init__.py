# core/interpreter/__init__.py
"""
NeuroCode Interpreter System (Modular)
======================================

This module provides the modular NeuroCode interpreter system.
The interpreter is split into focused components for better maintainability.

Components:
- base.py - Core interpreter base class and interfaces
- command_parser.py - Command parsing and routing logic
- execution_engine.py - Main execution engine
- line_processor.py - Line-by-line processing
- enhanced_features.py - Enhanced parsing features
- fallback_systems.py - Fallback class implementations

Main API:
- NeuroCodeInterpreter - Main interpreter class
- ExecutionResult - Result wrapper
- parse_command - Command parsing utility
"""

# Import the main interpreter components
try:
    from .base import NeuroCodeInterpreterBase
    from .command_parser import CommandParser, ParseResult
    from .enhanced_features import EnhancedFeatureParser
    from .execution_engine import ExecutionEngine
    from .fallback_systems import FallbackSystemManager
    from .line_processor import LineProcessor

    # Main interpreter class
    from .main import NeuroCodeInterpreter

    # Export the main API
    __all__ = [
        "NeuroCodeInterpreter",
        "NeuroCodeInterpreterBase",
        "CommandParser",
        "ExecutionEngine",
        "LineProcessor",
        "EnhancedFeatureParser",
        "FallbackSystemManager",
        "ParseResult",
    ]

except ImportError as e:
    # Fallback implementation
    print(f"Warning: Some interpreter components not available: {e}")

    class NeuroCodeInterpreter:
        def __init__(self):
            print("Using fallback interpreter implementation")

        def execute(self, line):
            return f"Fallback interpreter processed: {line}"

    __all__ = ["NeuroCodeInterpreter"]

# Version and metadata
__version__ = "2.0.0"
__author__ = "NeuroCode Team"
__description__ = "Modular NeuroCode Interpreter System"
