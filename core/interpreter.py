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
    from .performance_integration import performance_optimized, memory_optimized, optimized_operation
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
    from .speed_enhancement_suite import optimize_interpreter_system, ultra_fast, get_speed_suite
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
    from .interpreter.main import NeuroCodeInterpreter as BaseNeuroCodeInterpreter

    class NeuroCodeInterpreter(BaseNeuroCodeInterpreter):
        """Ultra-fast performance-optimized NeuroCode interpreter"""
        
        def __init__(self, *args, **kwargs):
            if PERFORMANCE_AVAILABLE:
                with optimized_operation("interpreter_initialization"):
                    super().__init__(*args, **kwargs)
            else:
                super().__init__(*args, **kwargs)
            
            # Apply speed optimizations
            if SPEED_ENHANCEMENT_AVAILABLE:
                optimize_interpreter_system(self)
                print("⚡ Interpreter speed optimized!")
        
        @ultra_fast("neurocode_execution")
        @performance_optimized("neurocode_execution", enable_caching=True)
        def execute(self, line):
            """Execute NeuroCode with performance optimizations"""
            return super().execute(line)
        
        @memory_optimized(intern_strings=True)
        def parse_line(self, line):
            """Parse NeuroCode line with memory optimizations"""
            if hasattr(super(), 'parse_line'):
                return super().parse_line(line)
            return line.strip()
        
        @performance_optimized("neurocode_processing")
        def process_command(self, command, args):
            """Process commands with performance optimizations"""
            if hasattr(super(), 'process_command'):
                return super().process_command(command, args)
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

except ImportError:
    # Fallback to inline implementation if modular system not available
    print("Warning: Modular interpreter system not available, using fallback")

    # Include original implementation as fallback
    # (The original implementation would be here for compatibility)

    class NeuroCodeInterpreter:
        def __init__(self):
            print("Using fallback interpreter implementation")

        def execute(self, line):
            return f"Fallback interpreter processed: {line}"

    def create_interpreter():
        """Create a new NeuroCode interpreter instance"""
        return NeuroCodeInterpreter()

    __all__ = ["NeuroCodeInterpreter", "create_interpreter"]
