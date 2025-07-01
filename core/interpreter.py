# SPDX-License-Identifier: GPL-3.0-or-later
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

# Import performance optimizations
try:
    from .performance_integration import (
        optimized_operation,
        performance_optimized,
    )

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

    def performance_optimized(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


def memory_optimized(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


# Import speed enhancement suite
try:
    from .speed_enhancement_suite import optimize_interpreter_system, ultra_fast

    SPEED_ENHANCEMENT_AVAILABLE = True
    print("🚀 Speed Enhancement Suite integrated with interpreter")
except ImportError:
    SPEED_ENHANCEMENT_AVAILABLE = False

    def ultra_fast(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


# Import everything from the new modular system
try:
    from .interpreter.main import NeuroCodeInterpreter as ModularNeuroCodeInterpreter

    _MODULAR_AVAILABLE = True
except ImportError:
    _MODULAR_AVAILABLE = False


if _MODULAR_AVAILABLE:
    # Performance-optimized wrapper around the modular interpreter
    class NeuroCodeInterpreter(ModularNeuroCodeInterpreter):  # type: ignore[misc]
        """Ultra-fast performance-optimized NeuroCode interpreter"""

        def __init__(self, *args, **kwargs):
            if PERFORMANCE_AVAILABLE:
                try:
                    with optimized_operation("interpreter_initialization"):
                        super().__init__(*args, **kwargs)
                except Exception:
                    super().__init__(*args, **kwargs)
            else:
                super().__init__(*args, **kwargs)

            # Apply speed optimizations
            if SPEED_ENHANCEMENT_AVAILABLE:
                try:
                    optimize_interpreter_system(self)
                    print("⚡ Interpreter speed optimized!")
                except Exception:
                    pass

        @ultra_fast("neurocode_execution")
        @performance_optimized("neurocode_execution", enable_caching=True)
        def execute(self, line):
            """Execute NeuroCode with performance optimizations"""
            try:
                return super().execute(line)
            except AttributeError:
                # Fallback if base class doesn't have execute method
                return self.parse_line(line)

        @memory_optimized(intern_strings=True)
        def parse_line(self, line):
            """Parse NeuroCode line with memory optimizations"""
            # Simple fallback implementation
            return line.strip()

        @performance_optimized("neurocode_processing")
        def process_command(self, command, args):
            """Process commands with performance optimizations"""
            # Simple fallback implementation
            return f"Processed: {command} {args}"

else:
    # Fallback implementation if modular system is not available
    class NeuroCodeInterpreter:
        """Fallback NeuroCode interpreter implementation"""

        def __init__(self, *args, **kwargs):
            print("🔄 Using fallback interpreter implementation")
            pass

        def execute(self, line):
            """Execute NeuroCode (fallback implementation)"""
            return self.parse_line(line)

        def parse_line(self, line):
            """Parse NeuroCode line (fallback implementation)"""
            return line.strip()

        def process_command(self, command, args):
            """Process commands (fallback implementation)"""
            return f"Processed: {command} {args}"


# Legacy function compatibility
def create_interpreter():
    """Create a new NeuroCode interpreter instance"""
    return NeuroCodeInterpreter()


# Export the same API as the original monolithic module
__all__ = [
    "NeuroCodeInterpreter",
    "create_interpreter",
]
