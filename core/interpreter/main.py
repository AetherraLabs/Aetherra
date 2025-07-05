# core/interpreter/main.py
"""
Main AetherraCode Interpreter Implementation
========================================

The main modular interpreter that combines all components.
"""

import os
from typing import Any, Dict, Union

from .base import ExecutionResult, AetherraCodeInterpreterBase
from .command_parser import CommandParser
from .enhanced_features import EnhancedFeatureParser
from .execution_engine import ExecutionEngine
from .fallback_systems import FallbackSystemManager
from .line_processor import LineProcessor


class AetherraInterpreter(AetherraCodeInterpreterBase):
    """
    Main AetherraCode Interpreter

    Combines all modular components into a cohesive interpreter system.
    """

    def __init__(self):
        super().__init__()

        # Initialize components
        self.fallback_manager = FallbackSystemManager()
        self.parser = CommandParser()
        self.line_processor = LineProcessor()
        self.enhanced_features = EnhancedFeatureParser()

        # Initialize core systems
        self.components = self._initialize_components()
        self.execution_engine = ExecutionEngine(self.components)

        # Configuration
        self.enhanced_parsing = True
        self.use_enhanced_parser = True
        self.auto_tag_enabled = False
        self.self_edit_mode = False
        self.debug_mode = False

        # Create backup directory
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def _initialize_components(self) -> Dict[str, Any]:
        """Initialize all interpreter components"""
        components = {}

        # Try to import real components, fall back to demo versions
        try:
            # Use robust import strategy
            components.update(self._import_real_components())
        except ImportError as e:
            print(f"Warning: Using fallback components due to import error: {e}")
            components.update(self.fallback_manager.enable_demo_mode())

        # Instantiate components in proper dependency order
        instantiated = {}

        # First pass: Create basic components with no dependencies
        for name, component_class in components.items():
            try:
                if name in ["AetherraMemory", "AetherraFunctions"]:
                    key = name.lower().replace("neuro", "").replace("system", "")
                    instantiated[key] = component_class()
            except Exception as e:
                print(f"Warning: Could not instantiate {name}: {e}")

        # Second pass: Create components that depend on basic ones
        for name, component_class in components.items():
            try:
                if name == "GoalSystem":
                    # Goal system needs memory (but can work without interpreter)
                    memory = instantiated.get("memory")
                    if memory:
                        instantiated["goal_system"] = component_class(memory, self)
                    else:
                        print(f"Warning: Skipping {name} - memory system not available")

                elif name == "AetherraDebugSystem":
                    # Debug system needs memory
                    memory = instantiated.get("memory")
                    if memory:
                        instantiated["debug"] = component_class(memory)
                    else:
                        print(f"Warning: Skipping {name} - memory system not available")

                elif name == "BlockExecutor":
                    # Block executor needs memory and functions
                    memory = instantiated.get("memory")
                    functions = instantiated.get("functions")
                    if memory and functions:
                        instantiated["executor"] = component_class(memory, functions)
                    else:
                        print(f"Warning: Skipping {name} - required systems not available")

            except Exception as e:
                print(f"Warning: Could not instantiate {name}: {e}")

        # Third pass: Create components that depend on multiple others
        for name, component_class in components.items():
            try:
                if name == "AetherraAgent":
                    # Agent needs memory, functions, and other components
                    memory = instantiated.get("memory")
                    functions = instantiated.get("functions")
                    if memory and functions:
                        instantiated["agent"] = component_class(memory, functions, [])
                    else:
                        print(f"Warning: Skipping {name} - required systems not available")

                elif name == "MetaPluginSystem":
                    # Meta plugins need memory, interpreter, and goal system
                    memory = instantiated.get("memory")
                    goal_system = instantiated.get("goal_system")
                    if memory:
                        instantiated["meta_plugins"] = component_class(memory, self, goal_system)
                    else:
                        print(f"Warning: Skipping {name} - required systems not available")

            except Exception as e:
                print(f"Warning: Could not instantiate {name}: {e}")

        return instantiated

    def _import_real_components(self) -> Dict[str, Any]:
        """Try to import real component classes"""
        components = {}

        try:
            # Memory system
            from ..memory import AetherraMemory

            components["AetherraMemory"] = AetherraMemory
        except ImportError:
            pass

        try:
            # Functions system
            from ..functions import AetherraFunctions

            components["AetherraFunctions"] = AetherraFunctions
        except ImportError:
            pass

        try:
            # Agent system
            from ..agent import AetherraAgent

            components["AetherraAgent"] = AetherraAgent
        except ImportError:
            pass

        try:
            # Goal system
            from ..goal_system import GoalSystem

            components["GoalSystem"] = GoalSystem
        except ImportError:
            pass

        try:
            # Debug system
            from ..debug_system import AetherraDebugSystem

            components["AetherraDebugSystem"] = AetherraDebugSystem
        except ImportError:
            pass

        try:
            # Block executor
            from ..block_executor import BlockExecutor

            components["BlockExecutor"] = BlockExecutor
        except ImportError:
            pass

        try:
            # Meta plugins
            from ..meta_plugins import MetaPluginSystem

            components["MetaPluginSystem"] = MetaPluginSystem
        except ImportError:
            pass

        # If we couldn't import any real components, raise ImportError
        if not components:
            raise ImportError("No real components available")

        return components

    def execute(self, line: str) -> Union[str, ExecutionResult]:
        """Main execution entry point"""
        line = line.strip()

        if not line:
            return ""

        # Track command
        self.track_command(line)

        # Check for enhanced features first
        if self.enhanced_features.can_handle(line):
            context = {
                "memory": self.components.get("memory"),
                "goal_system": self.components.get("goal_system"),
                "agent": self.components.get("agent"),
                "debug_system": self.components.get("debug_system"),
                "use_enhanced_parser": self.use_enhanced_parser,
                "enhanced_parsing": self.enhanced_parsing,
                "auto_tag_enabled": self.auto_tag_enabled,
                "self_edit_mode": self.self_edit_mode,
                "debug_mode": self.debug_mode,
            }

            result = self.enhanced_features.parse_enhanced_features(line, context)
            if result:
                # Update interpreter state from context
                self.use_enhanced_parser = context.get(
                    "use_enhanced_parser", self.use_enhanced_parser
                )
                self.enhanced_parsing = context.get("enhanced_parsing", self.enhanced_parsing)
                self.auto_tag_enabled = context.get("auto_tag_enabled", self.auto_tag_enabled)
                self.self_edit_mode = context.get("self_edit_mode", self.self_edit_mode)
                self.debug_mode = context.get("debug_mode", self.debug_mode)
                return result

        # Use line processor for block handling
        result = self.line_processor.process_line(line, self.parser, self.execution_engine)

        if result is not None:
            return result

        # If we're in a block, don't process as individual command
        if self.line_processor.is_in_block():
            return ""

        # Parse and execute single command
        parse_result = self.parser.parse(line)
        execution_result = self.execution_engine.execute(parse_result)

        return (
            execution_result.output
            if hasattr(execution_result, "output")
            else str(execution_result)
        )

    def parse_command(self, line: str):
        """Parse a command line into structured components"""
        return self.parser.parse(line)

    def get_command_history(self):
        """Get command execution history"""
        return self.command_history

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "interpreter": {
                "enhanced_parsing": self.enhanced_parsing,
                "use_enhanced_parser": self.use_enhanced_parser,
                "auto_tag_enabled": self.auto_tag_enabled,
                "self_edit_mode": self.self_edit_mode,
                "debug_mode": self.debug_mode,
                "demo_mode": self.fallback_manager.is_demo_mode(),
            },
            "components": dict.fromkeys(self.components.keys(), "available"),
            "line_processor": self.line_processor.get_block_info(),
            "execution_stats": self.get_execution_stats(),
            "engine_stats": self.execution_engine.get_execution_stats(),
        }

    def force_end_block(self) -> str:
        """Force end current block (for error recovery)"""
        return self.line_processor.force_end_block(self.parser, self.execution_engine)

    def reset_interpreter(self) -> str:
        """Reset interpreter to initial state"""
        self.command_history.clear()
        self.execution_stats.clear()
        self.line_processor = LineProcessor()

        # Reinitialize components if needed
        try:
            self.components = self._initialize_components()
            self.execution_engine = ExecutionEngine(self.components)
            return "🔄 Interpreter reset successfully"
        except Exception as e:
            return f"❌ Error resetting interpreter: {e}"

    def get_help(self) -> str:
        """Get comprehensive help text"""
        help_text = "🎯 AetherraCode Interpreter Help\n\n"
        help_text += "📋 Basic Commands:\n"
        help_text += '• remember("content") - Store memory\n'
        help_text += '• recall "query" - Search memories\n'
        help_text += '• goal: "objective" - Set goal\n'
        help_text += "• agent: activate - Activate agent\n"
        help_text += '• think about "topic" - Think about topic\n'
        help_text += "• analyze system - Analyze system state\n\n"

        help_text += "⚡ Enhanced Commands:\n"
        help_text += '• remember("content") as "tag1,tag2" - Tagged memory\n'
        help_text += '• goal: "objective" priority: high - Prioritized goal\n'
        help_text += '• agent: on specialization: "expertise" - Specialized agent\n\n'

        help_text += self.enhanced_features.get_feature_help()

        help_text += "\n🔧 System Commands:\n"
        help_text += "• status - Get system status\n"
        help_text += "• reset - Reset interpreter\n"
        help_text += "• help - Show this help\n"

        return help_text
