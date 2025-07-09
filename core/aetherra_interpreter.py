# SPDX-License-Identifier: GPL-3.0-or-later
# core/aetherra_interpreter.py
"""
Aetherra Interpreter (Modular Interface)
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

    def optimized_operation(*args, **kwargs):
        from contextlib import contextmanager

        @contextmanager
        def dummy_context():
            yield

        return dummy_context()

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

    def optimize_interpreter_system(*args, **kwargs):
        pass

    def ultra_fast(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


# Import everything from the new modular system
try:
    from .interpreter.main import AetherraInterpreter as ModularAetherraInterpreter

    _MODULAR_AVAILABLE = True
except ImportError:
    _MODULAR_AVAILABLE = False


if _MODULAR_AVAILABLE:
    # Performance-optimized wrapper around the modular interpreter
    class AetherraInterpreter(ModularAetherraInterpreter):  # type: ignore[misc]
        """Ultra-fast performance-optimized Aetherra interpreter"""

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

        @ultra_fast("aether_execution")
        @performance_optimized("aether_execution", enable_caching=True)
        def execute(self, line):
            """Execute Aetherra with performance optimizations"""
            try:
                return super().execute(line)
            except Exception as e:
                # Fallback to a safe execution
                return super().execute(line)

else:
    # Fallback implementation if modular interpreter is not available
    class AetherraInterpreter:
        def __init__(self, *args, **kwargs):
            print("⚠️  Modular interpreter not found. Using fallback.")

        def execute(self, line):
            return f"Received: {line}"
