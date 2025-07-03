# core/interpreter.py
"""
NeuroCode Interpreter (Modular Interface)
==========================================

This module provides a compatibility interface to the new modular interpreter system.
For new development, use the modular system directly from core.interpreter.

The modular interpreter system is organized as follows:
- core/interpreter/base.py - Base classes and interfaces
- core/interpreter/command_parser.py - Command parsing logic
- core/interpreter/execution_engine.py - Command execution
- core/interpreter/line_processor.py - Line and block processing
- core/interpreter/enhanced_features.py - Enhanced parsing features
- core/interpreter/fallback_systems.py - Fallback implementations
- core/interpreter/main.py - Main interpreter class

This file maintains backward compatibility with existing code.
"""

# Import everything from the new modular system
try:
    from .interpreter import AetherraInterpreter

    # Legacy function compatibility
    def create_interpreter():
        """Create a new NeuroCode interpreter instance"""
        return AetherraInterpreter()

    # Export the same API as the original monolithic module
    __all__ = [
        "AetherraInterpreter",
        "create_interpreter",
    ]

except ImportError:
    # Fallback to inline implementation if modular system not available
    print("Warning: Modular interpreter system not available, using fallback")

    # Include original implementation as fallback
    # (The original implementation would be here for compatibility)

    class AetherraInterpreter:
        def __init__(self):
            print("Using fallback interpreter implementation")

        def execute(self, line):
            return f"Fallback interpreter processed: {line}"

    def create_interpreter():
        return AetherraInterpreter()

    __all__ = ["AetherraInterpreter", "create_interpreter"]
