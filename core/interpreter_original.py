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
            auto_tag_content,
            reflect_on_memories,
            suggest_next_actions,
        )
        from block_executor import BlockExecutor  # type: ignore
        from debug_system import NeuroDebugSystem  # type: ignore
        from functions import NeuroFunctions  # type: ignore
        from goal_system import GoalSystem  # type: ignore
        from memory import AetherraMemory  # type: ignore
        from meta_plugins import MetaPluginSystem  # type: ignore
        from plugin_manager import PLUGIN_REGISTRY  # type: ignore
    except ImportError as e:
        print(f"Warning: Some interpreter dependencies not available: {e}")

        # Create comprehensive fallback classes for graceful degradation
        class AetherraMemory:
            def __init__(self):
                self.memory = []
                self.store_file = "memory_store.json"

            def remember(self, content, tags=None, category=None):
                return {"status": "demo mode", "id": "demo"}

            def recall(self, query=None, tags=None, category=None):
                return []

            def get_tags(self):
                return []

            def get_categories(self):
                return []

            def get_memory_summary(self):
                return {"total_memories": 0, "tags": [], "categories": []}

            def get_memory_stats(self):
                return {"total": 0}

            def pattern_analysis(self, pattern, frequency):
                return {"meets_threshold": False, "matches": 0, "analysis": "Demo mode"}

            def detect_recurring_patterns(self, min_freq, timeframe):
                return {"phrases": {}}

            def get_pattern_frequency(self, pattern, timeframe):
                return 0

            def save_to_file(self):
                pass

            def load_from_file(self):
                pass

            def clear(self):
                pass

        class NeuroFunctions:
            def __init__(self):
                self.functions = {}

            def call_function(self, name, args, executor=None):
                return f"Demo function call: {name}({args})"

            def define_function(self, name, params, commands):
                return f"Demo function defined: {name}"

            def list_functions(self):
                return []

            def show_function(self, name):
                return f"Demo function: {name}"

            def delete_function(self, name):
                return f"Demo function deleted: {name}"

        class NeuroAgent:
            def __init__(self, memory=None, functions=None, command_history=None):
                self.active = False
                self.memory = memory
                self.functions = functions
                self.command_history = command_history or []

            def activate(self):
                self.active = True
                return "Agent activated (demo mode)"

            def deactivate(self):
                self.active = False

            def get_command_type(self, command):
                return "demo"

            def detect_memory_patterns(self):
                return "Demo patterns"

            def analyze_behavior(self):
                return "Demo behavior analysis"

            def suggest_evolution(self, context):
                return "Demo evolution suggestion"

            def adaptive_suggest(self, context):
                return "Demo adaptive suggestion"

            def suggest_self_editing_opportunities(self):
                return "Demo self-editing opportunities"

            def justify_self_editing(self, filename, target):
                return "Demo justification"

        class GoalSystem:
            def __init__(self, memory=None, interpreter=None):
                self.goals = []
                self.memory = memory
                self.interpreter = interpreter
                self.agent_mode = False

            def set_goal(self, goal, priority="medium", metrics=None):
                return f"Goal set: {goal} (demo mode)"

            def set_agent_mode(self, enabled):
                self.agent_mode = enabled
                return f"Agent mode: {'enabled' if enabled else 'disabled'} (demo mode)"

            def get_goal_status(self):
                return "Demo goal status"

            def check_goal_progress(self, goal_ref):
                return "Demo goal progress"

            def autonomous_goal_monitoring(self):
                return "Demo goal monitoring"

            def reflective_loop(self):
                return "Demo reflective loop"

        class MetaPluginSystem:
            def __init__(self, *args):
                self.plugins = {}

            def execute_meta_plugin(self, name, *args):
                return f"Demo meta plugin: {name}"

            def list_meta_plugins(self):
                return []

        class BlockExecutor:
            def __init__(self, *args):
                pass

            def execute_block(self, block, executor):
                return "Demo block executed"

        class NeuroDebugSystem:
            def __init__(self, *args):
                self.error_history = []
                self.auto_apply_enabled = False

            def debug(self, msg):
                print(f"Debug: {msg}")

            def detect_and_store_error(self, error, context, filename=None):
                pass

            def suggest_fix(self, error_info):
                return {"fix": "Demo fix", "confidence": 0, "risk": "unknown"}

            def apply_fix(self, fix_suggestion, force=False):
                return False

            def set_auto_apply(self, enabled, confidence=80):
                self.auto_apply_enabled = enabled

            def show_debug_status(self):
                print("Debug system: demo mode")

        # Fallback functions with exact signatures to match imports
        def ask_ai(prompt: str, temperature: float = 0.2) -> str:
            return f"AI response to: {prompt}"

        def reflect_on_memories(memories: Any, filter_description: str) -> str:
            return "Reflection on memories"

        def auto_tag_content(summary: str) -> List[str]:
            return ["demo"]

        def suggest_next_actions(summary: str) -> str:
            return "Continue exploring"

        PLUGIN_REGISTRY = {}

# Import stdlib manager for standard plugins
import sys
from pathlib import Path

# Add paths for relative imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "neurocode"))

try:
    from stdlib import stdlib_manager
except ImportError:
    # Fallback if stdlib not available
    stdlib_manager = None

# Import the enhanced syntax tree parser
try:
    from .syntax_tree import NodeType, SyntaxNode, SyntaxTreeVisitor, parse_neurocode
except ImportError:
    try:
        from syntax_tree import NodeType, SyntaxNode, SyntaxTreeVisitor, parse_neurocode
    except ImportError:
        # Fallback if syntax tree not available
        parse_neurocode = None
        SyntaxTreeVisitor = object  # Use object as base class if SyntaxTreeVisitor not available
        SyntaxNode = None
        NodeType = None


class AetherraInterpreter:
    """
    Core NeuroCode interpreter - handles line-by-line parsing and execution flow
    Delegates specific functionality to specialized modules
    """

    def __init__(self):
        self.memory = AetherraMemory()
        self.functions = NeuroFunctions()
        self.command_history = []  # Track command usage patterns
        self.agent = NeuroAgent(self.memory, self.functions, self.command_history)
        self.goal_system = GoalSystem(self.memory, self)  # New goal system
        self.meta_plugins = MetaPluginSystem(
            self.memory, self, self.goal_system
        )  # Meta-plugin system
        self.block_executor = BlockExecutor(self.memory, self.functions)  # Block execution engine

        # Self-editing capabilities
        self.loaded_files = {}  # Store loaded file contents
        self.pending_fixes = {}  # Store suggested fixes awaiting approval
        self.backup_dir = "backups"  # Directory for file backups
        self.self_edit_mode = False  # Safety flag for self-editing

        # Block parsing state
        self.block_buffer = []  # For multi-line block parsing
        self.in_block = False
        self.block_type = None

        # Debug system
        self.debug_system = NeuroDebugSystem(self.memory)

        # Standard library manager
        self.stdlib = stdlib_manager

        # Enhanced parsing with SyntaxTree
        self.use_enhanced_parser = parse_neurocode is not None
        if self.use_enhanced_parser:
            self.syntax_visitor = NeuroExecutionVisitor(self)

        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def execute(self, line):
        """Main execution entry point - parses and executes a single line"""
        line = line.strip()

        # Enhanced preprocessing for better parsing
        enhanced_result = self._try_enhanced_parsing(line)
        if enhanced_result:
            return enhanced_result

        # Handle block parsing for multi-line constructs
        if self._is_block_start(line):
            return self._start_block(line)
        elif self.in_block:
            return self._add_to_block(line)

        # Track command usage for pattern analysis
        self._track_command(line)

        # Route command to appropriate handler
        result = self._route_command(line)
        return result

    def _try_enhanced_parsing(self, line):
        """Try enhanced parsing patterns for better NeuroCode support"""

        # Enhanced remember() parsing with multiple tags and metadata
        if "remember(" in line and " as " in line:
            enhanced_result = self._parse_enhanced_remember(line)
            if enhanced_result:
                return enhanced_result

        # Enhanced goal parsing with priority and metadata
        if line.startswith("goal:") and (
            "priority:" in line or "deadline:" in line or "agent:" in line
        ):
            enhanced_result = self._parse_enhanced_goal(line)
            if enhanced_result:
                return enhanced_result

        # Enhanced agent commands with specialization
        if line.startswith("agent:") and "specialization:" in line:
            enhanced_result = self._parse_enhanced_agent(line)
            if enhanced_result:
                return enhanced_result

        # Enhanced plugin commands with parameters
        if line.startswith("plugin:") and "(" in line:
            enhanced_result = self._parse_enhanced_plugin(line)
            if enhanced_result:
                return enhanced_result

        return None

    def _parse_enhanced_remember(self, line):
        """
        Enhanced remember parsing with metadata support

        Supports:
        - remember("content") as "tag1,tag2"
        - remember("content") as "tag" category: "learning"
        - remember("content") with confidence: 0.9 as "tag"
        """
        import re

        # Pattern: remember("content") as "tags" [optional extras]
        pattern = r'remember\s*\(\s*["\']([^"\']*)["\'\s*\)\s+as\s+["\']([^"\']*)["\']'
        match = re.search(pattern, line)

        if match:
            content = match.group(1)
            tags = [tag.strip() for tag in match.group(2).split(",")]

            # Check for additional parameters
            category = None
            confidence = None

            category_match = re.search(r'category:\s*["\']([^"\']*)["\']', line)
            if category_match:
                category = category_match.group(1)

            confidence_match = re.search(r"confidence:\s*([0-9.]+)", line)
            if confidence_match:
                confidence = float(confidence_match.group(1))

            # Execute with enhanced parameters
            result = self.memory.remember(content, tags, category=category)

            # Enhanced response
            response = "💾 Enhanced Memory Storage\n"
            response += f"   📝 Content: {content}\n"
            response += f"   🏷️ Tags: {', '.join(tags)}\n"
            if category:
                response += f"   📂 Category: {category}\n"
            if confidence:
                response += f"   📊 Confidence: {confidence}\n"
            response += f"   🆔 Memory ID: {result.get('id', 'generated') if isinstance(result, dict) else 'stored'}"

            return response

        return None

    def _parse_enhanced_goal(self, line):
        """
        Enhanced goal parsing with metadata

        Supports:
        - goal: "objective" priority: high
        - goal: "objective" priority: medium deadline: "next week"
        - goal: "objective" with agent: "specialist" priority: high
        """
        import re

        # Extract goal content
        goal_match = re.search(r'goal:\s*["\']([^"\']*)["\']', line)
        if not goal_match:
            return None

        goal_content = goal_match.group(1)

        # Extract parameters
        priority_match = re.search(r"priority:\s*(\w+)", line)
        deadline_match = re.search(r'deadline:\s*["\']([^"\']*)["\']', line)
        agent_match = re.search(r'agent:\s*["\']([^"\']*)["\']', line)

        priority = priority_match.group(1) if priority_match else "medium"
        deadline = deadline_match.group(1) if deadline_match else None
        agent = agent_match.group(1) if agent_match else None

        # Execute enhanced goal setting
        result = self.goal_system.set_goal(goal_content, priority)

        # Enhanced response
        response = "🎯 Enhanced Goal Setting\n"
        response += f"   📋 Objective: {goal_content}\n"
        response += f"   ⚡ Priority: {priority}\n"
        if deadline:
            response += f"   📅 Deadline: {deadline}\n"
        if agent:
            response += f"   🤖 Assigned Agent: {agent}\n"
        response += "   ✅ Goal activated and tracking enabled"

        return response

    def _parse_enhanced_agent(self, line):
        """Enhanced agent command parsing with specialization"""
        import re

        # Pattern: agent: on specialization: "data analysis"
        spec_match = re.search(r'specialization:\s*["\']([^"\']*)["\']', line)

        if spec_match:
            specialization = spec_match.group(1)

            # Activate agent with specialization
            self.agent.activate()

            response = "🤖 Enhanced Agent Activation\n"
            response += f"   🧠 Specialization: {specialization}\n"
            response += "   🚀 Agent ready for specialized tasks\n"
            response += "   💡 Use 'assistant: <question>' for expert guidance"

            return response

        return None

    def _parse_enhanced_plugin(self, line):
        """Enhanced plugin command with parameter parsing"""
        import re

        # Pattern: plugin: name(param1="value1", param2="value2")
        plugin_match = re.search(r"plugin:\s*(\w+)\s*\(([^)]*)\)", line)

        if plugin_match:
            plugin_name = plugin_match.group(1)
            params_str = plugin_match.group(2)

            # Parse parameters
            params = {}
            if params_str.strip():
                for param in params_str.split(","):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params[key.strip()] = value.strip().strip("\"'")

            # Execute plugin with parameters
            try:
                if plugin_name in PLUGIN_REGISTRY:
                    plugin_result = PLUGIN_REGISTRY[plugin_name](**params)
                else:
                    plugin_result = f"Plugin '{plugin_name}' not found"

                response = "🔌 Enhanced Plugin Execution\n"
                response += f"   📦 Plugin: {plugin_name}\n"
                if params:
                    response += f"   ⚙️ Parameters: {params}\n"
                response += f"   📤 Result: {plugin_result}"

                return response
            except Exception as e:
                return f"❌ Plugin execution failed: {e}"

        return None

    def _track_command(self, line):
        """Track command usage for behavioral analysis"""
        self.command_history.append(
            {
                "command": line,
                "timestamp": str(datetime.now()),
                "command_type": self.agent.get_command_type(line),
            }
        )

        # Keep only last 100 commands to avoid memory bloat
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]

    def _route_command(self, line):
        """Route commands to appropriate handlers"""

        # Memory commands
        if line.startswith("remember(") or line.startswith("remember "):
            return self._handle_remember(line)
        elif line.startswith("recall(") or line.startswith("recall tag:"):
            return self._handle_recall(line)
        elif line.startswith("memory "):
            return self._handle_memory_management(line)

        # Function commands
        elif line.startswith("define "):
            return self._handle_function_define(line)
        elif line.startswith("call "):
            return self._handle_function_call(line)
        elif line.startswith("list functions"):
            return self.functions.list_functions()
        elif line.startswith("show function "):
            func_name = line.split("show function")[-1].strip()
            return self.functions.show_function(func_name)
        elif line.startswith("delete function "):
            func_name = line.split("delete function")[-1].strip()
            return self.functions.delete_function(func_name)

        # AI and analysis commands
        elif line.startswith("reflect on"):
            return self._handle_reflect(line)
        elif line.startswith("detect patterns"):
            return self.agent.detect_memory_patterns()
        elif line.startswith("analyze behavior"):
            return self.agent.analyze_behavior()
        elif line.startswith("suggest evolution"):
            context = line.split("suggest evolution")[-1].strip().strip("\"'")
            return self.agent.suggest_evolution(context)
        elif line.startswith("adaptive suggest"):
            context = line.split("adaptive suggest")[-1].strip().strip("\"'")
            return self.agent.adaptive_suggest(context)
        elif line.startswith("self edit opportunities"):
            return self.agent.suggest_self_editing_opportunities()

        # Goal system and agent commands
        elif line.startswith("goal:"):
            return self._handle_goal_setting(line)
        elif line.startswith("agent:"):
            return self._handle_agent_control(line)
        elif line.startswith("check goal"):
            return self._handle_goal_check(line)
        elif line.startswith("goal status"):
            return self.goal_system.get_goal_status()
        elif line.startswith("reflective loop"):
            return self.goal_system.reflective_loop()
        elif line.startswith("autonomous monitoring"):
            return self.goal_system.autonomous_goal_monitoring()

        # Pattern recognition and memory analysis
        elif line.startswith("if memory.pattern"):
            return self._handle_memory_pattern_condition(line)
        elif line.startswith("detect recurring patterns"):
            return self._handle_detect_recurring_patterns(line)
        elif line.startswith("pattern frequency"):
            return self._handle_pattern_frequency(line)

        # Learning and optimization commands
        elif line.startswith("learn from"):
            return self._handle_learn_from(line)
        elif line.startswith("optimize for"):
            return self._handle_optimize(line)
        elif line.startswith("suggest fix"):
            return self._handle_suggest_fix(line)

        # Self-editing commands
        elif line.startswith("load "):
            return self._handle_load_file(line)
        elif line.startswith("analyze "):
            return self._handle_analyze_code(line)
        elif line.startswith("refactor "):
            return self._handle_refactor(line)
        elif line.startswith("apply fix"):
            return self._handle_apply_fix(line)
        elif line.startswith("backup "):
            return self._handle_backup(line)
        elif line.startswith("diff "):
            return self._handle_diff(line)
        elif line.startswith("set self_edit_mode"):
            mode = line.split("set self_edit_mode")[-1].strip()
            if mode in ["on", "true", "enabled"]:
                return self.set_self_edit_mode(True)
            elif mode in ["off", "false", "disabled"]:
                return self.set_self_edit_mode(False)
            else:
                return "[Safety] Usage: set self_edit_mode on/off"

        # Assistant and plugin commands
        elif line.startswith("assistant:"):
            return self._handle_assistant(line)
        elif line.startswith("plugin:"):
            return self._handle_plugin(line)
        elif line.startswith("meta:"):
            return self._handle_meta_plugin(line)
        elif line.startswith("list meta plugins"):
            return self.meta_plugins.list_meta_plugins()
        elif line.startswith("list plugins"):
            return self._handle_list_plugins()
        elif line.startswith("plugin info"):
            return self._handle_plugin_info(line)

        # Debug commands
        elif line.startswith("debug status"):
            self.debug_system.show_debug_status()

        elif line.startswith("set auto_debug"):
            parts = line.split()
            if len(parts) >= 3:
                enabled = parts[2].lower() in ["on", "true", "yes", "enabled"]
                confidence = int(parts[3]) if len(parts) > 3 else 80
                self.debug_system.set_auto_apply(enabled, confidence)
            else:
                print("Usage: set auto_debug on/off [confidence_threshold]")

        elif line.startswith("suggest fix"):
            # Handle manual fix suggestion
            if "for" in line:
                error_description = line.split("for", 1)[1].strip().strip('"')
                # Find matching error in history
                matching_errors = [
                    e
                    for e in self.debug_system.error_history
                    if error_description.lower() in str(e).lower()
                ]
                if matching_errors:
                    fix_suggestion = self.debug_system.suggest_fix(matching_errors[-1])
                    print(f"🤖 [Fix Suggestion] {fix_suggestion.get('fix', 'No fix available')}")
                    print(f"📊 Confidence: {fix_suggestion.get('confidence', 0)}%")
                    print(f"⚠️ Risk: {fix_suggestion.get('risk', 'unknown')}")
                    self._last_fix_suggestion = fix_suggestion
                else:
                    print("❌ No matching error found in history")
            else:
                print('Usage: suggest fix for "error description"')

        elif line.startswith("apply fix"):
            if hasattr(self, "_last_fix_suggestion"):
                force = "force" in line
                success = self.debug_system.apply_fix(self._last_fix_suggestion, force)
                if success:
                    print("✅ Fix applied successfully!")
                else:
                    print("❌ Fix application failed")
            else:
                print("❌ No fix suggestion available. Use 'suggest fix' first.")

        elif line.startswith("load "):
            # Enhanced load with error detection
            filename = line.split("load ")[1].strip().strip('"')
            self._load_and_analyze_file(filename)

        else:
            return f"[Unknown] Could not interpret: {line}"

    def _handle_remember(self, line):
        """Handle remember() command with support for both syntaxes"""
        # First try the new tagged syntax: remember("content") as "tag"
        tagged_match = re.search(r'remember\s*\(["\'](.*?)["\']\)\s+as\s+["\'](.*?)["\']', line)
        if tagged_match:
            content = tagged_match.group(1)
            tag = tagged_match.group(2).strip()
            tags = [tag] if tag else ["general"]

            self.memory.remember(content, tags=tags)
            return f"[Memory] Stored: {content} | Tag: {tag}"

        # Try the original function syntax: remember("content", tags="tag1,tag2")
        function_match = re.search(
            r'remember\(["\'](.*?)["\']\s*(?:,\s*tags=["\'](.*?)["\']\s*)?\)', line
        )
        if function_match:
            content = function_match.group(1)
            tags = function_match.group(2).split(",") if function_match.group(2) else ["general"]
            tags = [tag.strip() for tag in tags]

            self.memory.remember(content, tags=tags)
            return f"[Memory] Stored: {content} | Tags: {', '.join(tags)}"

        # If neither syntax matches
        return '[Memory] Invalid syntax. Use: remember("content") as "tag" OR remember("content", tags="tag1,tag2")'

    def _handle_recall(self, line):
        """Handle recall() command with support for both syntaxes"""
        # First try the simple tag syntax: recall tag: "tag_name"
        simple_tag_match = re.search(r'recall\s+tag:\s*["\'](.*?)["\']', line)
        if simple_tag_match:
            tag = simple_tag_match.group(1).strip()
            memories = self.memory.recall(tags=[tag])
            if memories:
                return (
                    f"[Memory] Recalled {len(memories)} memories with tag '{tag}':\n"
                    + "\n".join([f"- {m}" for m in memories])
                )
            else:
                return f"[Memory] No memories found with tag '{tag}'"

        # Try the original function syntax: recall(tags="tag1,tag2", category="cat")
        tag_match = re.search(r'tags=["\'](.*?)["\']\s*', line)
        category_match = re.search(r'category=["\'](.*?)["\']\s*', line)

        tags = tag_match.group(1).split(",") if tag_match else None
        tags = [tag.strip() for tag in tags] if tags else None
        category = category_match.group(1) if category_match else None

        memories = self.memory.recall(tags=tags, category=category)
        if memories:
            filter_desc = []
            if tags:
                filter_desc.append(f"tags: {', '.join(tags)}")
            if category:
                filter_desc.append(f"category: {category}")
            filter_text = f" (filtered by {', '.join(filter_desc)})" if filter_desc else ""

            result = f"[Recall{filter_text}] Found {len(memories)} memories:\n"
            for i, memory in enumerate(memories, 1):
                result += f"  {i}. {memory}\n"
            return result.strip()
        else:
            return "[Recall] No memories found matching criteria"

    def _handle_memory_management(self, line):
        """Handle memory management commands"""
        if line.startswith("memory tags"):
            tags = self.memory.get_tags()
            return f"[Memory Tags] Available tags: {', '.join(tags)}"
        elif line.startswith("memory categories"):
            categories = self.memory.get_categories()
            return f"[Memory Categories] Available categories: {', '.join(categories)}"
        elif line.startswith("memory summary"):
            summary = self.memory.get_memory_summary()
            result = "[Memory Summary]\n"
            result += f"  Total memories: {summary['total_memories']}\n"
            result += f"  Tags: {', '.join(summary['tags'])}\n"
            result += f"  Categories: {', '.join(summary['categories'])}"
            return result
        elif line.startswith("memory stats"):
            return self.memory.get_memory_stats()
        else:
            return "[Memory] Unknown memory command"

    def _handle_function_define(self, line):
        """Handle function definition"""
        match = re.search(r"define\s+(\w+)\s*\((.*?)\)\s*\{\s*(.*?)\s*\}", line, re.DOTALL)
        if match:
            func_name = match.group(1)
            params = [p.strip() for p in match.group(2).split(",") if p.strip()]
            commands = match.group(3).strip()

            return self.functions.define_function(func_name, params, commands)
        else:
            return (
                "[Function] Invalid syntax. Use: define function_name(param1, param2) { commands }"
            )

    def _handle_function_call(self, line):
        """Handle function call"""
        match = re.search(r"call\s+(\w+)\s*\((.*?)\)", line)
        if match:
            func_name = match.group(1)
            args = [arg.strip().strip("\"'") for arg in match.group(2).split(",") if arg.strip()]

            # Use lambda to pass execute method as callback
            result = self.functions.call_function(func_name, args, lambda cmd: self.execute(cmd))
            return result
        else:
            return "[Function] Invalid syntax. Use: call function_name(arg1, arg2)"

    def _handle_reflect(self, line):
        """Handle AI reflection on memories"""
        match = re.search(
            r'reflect on\s+(?:tags=["\'](.*?)["\']\s*|category=["\'](.*?)["\']\s*)+', line
        )
        if match:
            tags = match.group(1).split(",") if match.group(1) else None
            tags = [tag.strip() for tag in tags] if tags else None
            category = match.group(2) if match.group(2) else None

            memories = self.memory.recall(tags=tags, category=category)
            if memories:
                filter_desc = f"tags: {', '.join(tags)}" if tags else f"category: {category}"
                reflection = reflect_on_memories(memories, filter_desc)
                return f"[AI Reflection] {reflection}"
            else:
                return "[Reflect] No memories found matching criteria"
        else:
            return '[Reflect] Invalid syntax. Use: reflect on tags="tag" or reflect on category="category"'

    def _handle_learn_from(self, line):
        """Handle learning from files"""
        file = line.split("learn from")[-1].strip().strip('"')
        if os.path.exists(file):
            with open(file) as f:
                data = f.read()
            summary = ask_ai(f"Summarize and learn from this content:\n{data}")

            # Enhanced learning with auto-tagging
            tags = auto_tag_content(summary)

            self.memory.remember(f"Learned from {file}: {summary}", tags=tags, category="learning")
            result = f"[Learned] Summary stored to memory with tags: {', '.join(tags)}\n"

            # Auto-suggest NeuroCode based on learning
            suggestion = suggest_next_actions(summary)
            result += f"[Auto-Suggested NeuroCode]\n{suggestion}"
            return result
        else:
            return f"[Learn] File not found: {file}"

    def _handle_optimize(self, line):
        """Handle optimization requests"""
        goal = line.split("optimize for")[-1].strip().strip('"')
        context = "\n".join(self.memory.recall())
        result = ask_ai(f"Optimize this system for {goal} using what it knows:\n{context}")
        return f"[Optimization] {result}"

    def _handle_suggest_fix(self, line):
        """Handle fix suggestions"""
        context = "\n".join(self.memory.recall())
        issue = line.split("suggest fix for")[-1].strip().strip('"')
        suggestion = ask_ai(f"Suggest a fix for this issue: {issue}\nContext: {context}")
        return f"[Fix Suggestion] {suggestion}"

    def _handle_assistant(self, line):
        """Handle assistant queries"""
        query = line.split("assistant:", 1)[-1].strip()
        context = "\n".join(self.memory.recall())
        prompt = f"You are NeuroAssistant, a helpful AI embedded in the NeuroCode runtime. Here is your memory:\n{context}\n\nAnswer this: {query}"
        response = ask_ai(prompt)
        return f"[NeuroAssistant] {response}"

    def _handle_plugin(self, line):
        """Handle plugin execution - supports both legacy and stdlib plugins"""
        parts = line.split("plugin:")[-1].strip().split()
        if not parts:
            return "[Plugin] No plugin name provided."

        plugin_name = parts[0]
        plugin_args = parts[1:]

        # First check stdlib plugins (standard library)
        if plugin_name in self.stdlib.plugins:
            try:
                # Convert args to a single action string if needed
                action = " ".join(plugin_args) if plugin_args else "default"
                result = self.stdlib.execute_plugin_action(
                    plugin_name, action, memory_system=self.memory
                )
                return f"[StdLib:{plugin_name}] {result}"
            except Exception as e:
                return f"[StdLib:{plugin_name}] Error: {e}"

        # Fallback to legacy plugin registry
        elif plugin_name in PLUGIN_REGISTRY:
            result = PLUGIN_REGISTRY[plugin_name](*plugin_args)
            return f"[Plugin:{plugin_name}] {result}"
        else:
            # Suggest available plugins
            available_stdlib = list(self.stdlib.plugins.keys())
            available_legacy = list(PLUGIN_REGISTRY.keys())
            all_available = available_stdlib + available_legacy
            return f"[Plugin] '{plugin_name}' not found. Available: {all_available}"

    def _handle_list_plugins(self):
        """List all available plugins (stdlib and legacy)"""
        result = "[Plugins] Available plugins:\n"

        # Standard library plugins
        if self.stdlib.plugins:
            result += "\n📚 Standard Library Plugins:\n"
            for name, plugin in self.stdlib.plugins.items():
                result += f"  • {name}: {plugin.description}\n"

        # Legacy plugins
        if PLUGIN_REGISTRY:
            result += "\n🔌 Legacy Plugins:\n"
            for name in PLUGIN_REGISTRY.keys():
                result += f"  • {name}\n"

        if not self.stdlib.plugins and not PLUGIN_REGISTRY:
            result += "  No plugins available\n"

        return result.rstrip()

    def _handle_plugin_info(self, line):
        """Get detailed information about a specific plugin"""
        plugin_name = line.split("plugin info")[-1].strip()
        if not plugin_name:
            return "[Plugin Info] Please specify a plugin name. Usage: plugin info <plugin_name>"

        # Check stdlib first
        plugin_info = self.stdlib.get_plugin_info(plugin_name)
        if plugin_info:
            result = f"[Plugin Info] {plugin_name}\n"
            result += f"  Description: {plugin_info['description']}\n"
            result += f"  Actions: {', '.join(plugin_info['available_actions'])}\n"
            result += "  Source: Standard Library\n"
            return result

        # Check legacy plugins
        if plugin_name in PLUGIN_REGISTRY:
            return f"[Plugin Info] {plugin_name}\n  Source: Legacy Plugin Registry\n  Actions: execute with arguments"

        return f"[Plugin Info] Plugin '{plugin_name}' not found. Use 'list plugins' to see available plugins."

    def _handle_meta_plugin(self, line):
        """Handle meta-plugin execution"""
        parts = line.split("meta:")[-1].strip().split()
        if not parts:
            return "[Meta-Plugin] No plugin name provided."

        plugin_name = parts[0]
        plugin_args = parts[1:]

        return self.meta_plugins.execute_meta_plugin(plugin_name, *plugin_args)

    # ==================== SELF-EDITING CAPABILITIES =============
    def _handle_load_file(self, line):
        """Load and analyze a source code file for potential modifications"""
        filename = line.split("load")[-1].strip().strip('"')

        if not os.path.exists(filename):
            return f"[Load] File not found: {filename}"

        try:
            with open(filename, encoding="utf-8") as f:
                content = f.read()

            # Store file for future analysis/editing
            self.loaded_files[filename] = content

            # Use AI to analyze the file and provide insights
            from core.ai_runtime import analyze_code_structure, generate_code_summary

            analysis = analyze_code_structure(content, filename)
            summary = generate_code_summary(content, filename)

            # Remember this analysis for future reference
            self.memory.remember(
                f"Loaded and analyzed {filename}: {summary}",
                tags=["code_analysis", "file_load", "self_editing"],
                category="code_management",
            )

            result = f"[Load] Successfully loaded {filename}\n"
            result += f"[Analysis] {analysis}\n"
            result += f"[Summary] {summary}"

            return result

        except Exception as e:
            return f"[Load] Error reading file {filename}: {str(e)}"

    def _handle_analyze_code(self, line):
        """Analyze loaded code for potential improvements, bugs, or patterns"""
        filename = line.split("analyze")[-1].strip().strip('"')

        if filename not in self.loaded_files:
            return f"[Analyze] File not loaded: {filename}. Use 'load {filename}' first."

        content = self.loaded_files[filename]

        # Get relevant memories for context
        memories = self.memory.recall(tags=["code_analysis", "patterns", "bugs"])
        memory_context = "\n".join([m["text"] for m in memories[-5:]])  # Recent relevant memories

        # Use AI to perform deep code analysis
        from core.ai_runtime import deep_code_analysis, suggest_code_improvements

        analysis = deep_code_analysis(content, filename, memory_context)
        improvements = suggest_code_improvements(content, filename, memory_context)

        # Store analysis results
        analysis_summary = f"Deep analysis of {filename}: {analysis[:200]}..."
        self.memory.remember(
            analysis_summary,
            tags=["deep_analysis", "code_review", "improvements"],
            category="code_management",
        )

        result = f"[Deep Analysis] {filename}\n"
        result += f"{analysis}\n\n"
        result += f"[Suggested Improvements]\n{improvements}"

        return result

    def _handle_refactor(self, line):
        """Suggest or perform refactoring on loaded code"""
        # Extract filename and refactor target
        parts = line.split("refactor")[-1].strip().split()
        if not parts:
            return "[Refactor] Please specify: refactor <filename> [target]"

        filename = parts[0].strip('"')
        target = " ".join(parts[1:]) if len(parts) > 1 else "general improvements"

        if filename not in self.loaded_files:
            return f"[Refactor] File not loaded: {filename}. Use 'load {filename}' first."

        content = self.loaded_files[filename]

        # Get memory context for informed refactoring
        memories = self.memory.recall(tags=["refactor", "patterns", "best_practices"])
        memory_context = "\n".join([m["text"] for m in memories[-3:]])

        # Use AI to suggest refactoring
        from core.ai_runtime import justify_refactoring, suggest_refactoring

        refactor_suggestion = suggest_refactoring(content, filename, target, memory_context)
        justification = justify_refactoring(content, target, memory_context)

        # Get memory-driven justification from agent
        agent_justification = self.agent.justify_self_editing(filename, f"Refactoring for {target}")

        # Store as pending fix for review
        fix_id = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.pending_fixes[fix_id] = {
            "filename": filename,
            "original_content": content,
            "suggested_content": refactor_suggestion,
            "target": target,
            "justification": justification,
            "agent_justification": agent_justification,
            "timestamp": datetime.now().isoformat(),
        }

        # Remember this refactoring session
        self.memory.remember(
            f"Suggested refactoring for {filename} targeting '{target}': {justification[:100]}...",
            tags=["refactor_suggestion", "pending_fix", target.replace(" ", "_")],
            category="code_management",
        )

        result = f"[Refactor] Suggested improvements for {filename}\n"
        result += f"[Target] {target}\n"
        result += f"[Justification] {justification}\n\n"
        result += f"[Suggested Changes]\n{refactor_suggestion}\n\n"
        result += f"[Fix ID] {fix_id} (use 'apply fix {fix_id}' to apply)\n"
        result += f"[Safety] Use 'diff {fix_id}' to review changes before applying"

        return result

    def _handle_apply_fix(self, line):
        """Apply a pending fix after review and approval"""
        fix_id = line.split("apply fix")[-1].strip().strip('"')

        if not fix_id:
            # List all pending fixes
            if not self.pending_fixes:
                return "[Apply Fix] No pending fixes available"

            result = "[Apply Fix] Pending fixes:\n"
            for fid, fix in self.pending_fixes.items():
                result += f"  {fid}: {fix['filename']} - {fix['target']}\n"
            return result

        if fix_id not in self.pending_fixes:
            return f"[Apply Fix] Fix ID not found: {fix_id}"

        fix = self.pending_fixes[fix_id]
        filename = fix["filename"]

        # Safety check: require explicit approval for self-editing
        if not self.self_edit_mode:
            return f"[Apply Fix] Self-editing mode disabled. Enable with 'set self_edit_mode on' first.\n[Safety] This will modify {filename}. Review with 'diff {fix_id}' first."

        try:
            # Create backup before applying fix
            backup_path = self._create_backup(filename)

            # Apply the fix
            with open(filename, "w", encoding="utf-8") as f:
                f.write(fix["suggested_content"])

            # Update loaded files cache
            self.loaded_files[filename] = fix["suggested_content"]

            # Remember this action
            self.memory.remember(
                f"Applied fix {fix_id} to {filename}: {fix['justification']}",
                tags=["fix_applied", "code_modification", "self_editing"],
                category="code_management",
            )

            # Remove from pending fixes
            del self.pending_fixes[fix_id]

            result = f"[Apply Fix] Successfully applied fix {fix_id} to {filename}\n"
            result += f"[Backup] Created backup at {backup_path}\n"
            result += f"[Target] {fix['target']}\n"
            result += f"[Justification] {fix['justification']}"

            return result

        except Exception as e:
            return f"[Apply Fix] Error applying fix: {str(e)}"

    def _handle_backup(self, line):
        """Create backup of specified file"""
        filename = line.split("backup")[-1].strip().strip('"')

        if not filename:
            return "[Backup] Please specify filename: backup <filename>"

        if not os.path.exists(filename):
            return f"[Backup] File not found: {filename}"

        try:
            backup_path = self._create_backup(filename)
            self.memory.remember(
                f"Created backup of {filename} at {backup_path}",
                tags=["backup", "file_safety"],
                category="code_management",
            )
            return f"[Backup] Created backup: {backup_path}"
        except Exception as e:
            return f"[Backup] Error creating backup: {str(e)}"

    def _handle_diff(self, line):
        """Show differences between original and suggested code"""
        fix_id = line.split("diff")[-1].strip().strip('"')

        if not fix_id:
            return "[Diff] Please specify fix ID: diff <fix_id>"

        if fix_id not in self.pending_fixes:
            return f"[Diff] Fix ID not found: {fix_id}"

        fix = self.pending_fixes[fix_id]
        original = fix["original_content"].splitlines()
        suggested = fix["suggested_content"].splitlines()

        # Generate unified diff
        diff_lines = list(
            difflib.unified_diff(
                original,
                suggested,
                fromfile=f"{fix['filename']} (original)",
                tofile=f"{fix['filename']} (suggested)",
                lineterm="",
            )
        )

        if not diff_lines:
            return f"[Diff] No differences found for fix {fix_id}"

        # Format diff output
        diff_output = "\n".join(diff_lines)

        result = f"[Diff] Changes for fix {fix_id}\n"
        result += f"[File] {fix['filename']}\n"
        result += f"[Target] {fix['target']}\n"
        result += f"[Justification] {fix['justification']}\n"
        if "agent_justification" in fix:
            result += f"[Memory-Driven Justification] {fix['agent_justification']}\n"
        result += "\n[Changes]\n"
        result += diff_output

        return result

    def _create_backup(self, filename):
        """Create a timestamped backup of a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{os.path.basename(filename)}.backup.{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        shutil.copy2(filename, backup_path)
        return backup_path

    def set_self_edit_mode(self, enabled):
        """Enable/disable self-editing mode for safety"""
        self.self_edit_mode = enabled
        mode_str = "enabled" if enabled else "disabled"
        self.memory.remember(
            f"Self-editing mode {mode_str}",
            tags=["safety", "self_edit_mode"],
            category="system_settings",
        )
        return f"[Safety] Self-editing mode {mode_str}"

    # ==================== GOAL SYSTEM & AGENT HANDLERS =============
    def _handle_goal_setting(self, line):
        """Handle goal: commands"""
        goal_text = line.split("goal:")[-1].strip()

        # Parse priority if specified
        priority = "medium"
        if " priority:" in goal_text:
            parts = goal_text.split(" priority:")
            goal_text = parts[0].strip()
            priority = parts[1].strip()

        # Parse metrics if specified
        metrics = {}
        if " metrics:" in goal_text:
            parts = goal_text.split(" metrics:")
            goal_text = parts[0].strip()
            try:
                # Simple metric parsing: "key=value,key2=value2"
                metric_str = parts[1].strip()
                for metric in metric_str.split(","):
                    if "=" in metric:
                        key, value = metric.split("=", 1)
                        metrics[key.strip()] = value.strip()
            except Exception:
                pass  # Ignore metric parsing errors

        return self.goal_system.set_goal(goal_text, priority, metrics)

    def _handle_agent_control(self, line):
        """Handle agent: commands"""
        command = line.split("agent:")[-1].strip().lower()

        if command in ["on", "enabled", "true"]:
            return self.goal_system.set_agent_mode(True)
        elif command in ["off", "disabled", "false"]:
            return self.goal_system.set_agent_mode(False)
        else:
            return "[Agent] Usage: agent: on/off"

    def _handle_goal_check(self, line):
        """Handle goal checking commands"""
        goal_ref = line.split("check goal")[-1].strip()

        if not goal_ref:
            # Check all active goals
            return self.goal_system.autonomous_goal_monitoring()
        else:
            # Check specific goal
            return self.goal_system.check_goal_progress(goal_ref)

    def _handle_memory_pattern_condition(self, line):
        r"""Handle if memory\.pattern() conditional statements"""
        # Parse: if memory\.pattern("pattern", frequency="threshold"):
        pattern_match = re.search(
            r'memory\.pattern\(["\']([^"\']+)["\']\s*(?:,\s*frequency=["\']([^"\']+)["\']\s*)?\)',
            line,
        )

        if not pattern_match:
            return '[Pattern] Invalid syntax. Use: if memory.pattern("pattern", frequency="threshold"):'

        pattern = pattern_match.group(1)
        frequency = pattern_match.group(2) or "weekly"

        # Analyze the pattern
        analysis = self.memory.pattern_analysis(pattern, frequency)

        # Extract the action part after the colon
        if ":" in line:
            action_part = line.split(":", 1)[1].strip()

            if analysis["meets_threshold"]:
                # Pattern condition is met, execute the action
                result = f"[Pattern Condition] Pattern '{pattern}' meets {frequency} threshold ({analysis['matches']} matches)\n"
                result += f"[Executing] {action_part}\n"

                try:
                    action_result = self.execute(action_part)
                    result += action_result
                except Exception as e:
                    result += f"[Error] {str(e)}"

                return result
            else:
                return f"[Pattern Condition] Pattern '{pattern}' does not meet {frequency} threshold ({analysis['matches']} matches) - no action taken"
        else:
            # Just return the analysis
            return f"[Pattern Analysis] {analysis['analysis']} - Meets {frequency} threshold: {analysis['meets_threshold']}"

    def _handle_detect_recurring_patterns(self, line):
        """Handle automatic pattern detection"""
        # Parse optional parameters
        min_frequency = 3
        timeframe = 30

        if "min_frequency=" in line:
            try:
                freq_match = re.search(r"min_frequency=(\d+)", line)
                if freq_match:
                    min_frequency = int(freq_match.group(1))
            except Exception:
                pass

        if "timeframe=" in line:
            try:
                time_match = re.search(r"timeframe=(\d+)", line)
                if time_match:
                    timeframe = int(time_match.group(1))
            except Exception:
                pass

        patterns = self.memory.detect_recurring_patterns(min_frequency, timeframe)

        if not patterns["phrases"]:
            return f"[Pattern Detection] No recurring patterns found (min frequency: {min_frequency}, timeframe: {timeframe} days)"

        result = f"[Pattern Detection] Found {len(patterns['phrases'])} recurring patterns:\n"

        # Sort by frequency
        sorted_patterns = sorted(patterns["phrases"].items(), key=lambda x: x[1], reverse=True)

        for phrase, count in sorted_patterns[:10]:  # Show top 10
            result += f"  • '{phrase}' ({count} times)\n"

        # Remember this analysis
        self.memory.remember(
            f"Detected {len(patterns['phrases'])} recurring patterns in {timeframe} days",
            tags=["pattern_detection", "analysis", "recurring"],
            category="system_analysis",
        )

        return result

    def _handle_pattern_frequency(self, line):
        """Handle pattern frequency queries"""
        # Parse: pattern frequency "pattern" [timeframe=30]
        pattern_match = re.search(r'pattern frequency ["\']([^"\']+)["\']', line)

        if not pattern_match:
            return '[Pattern] Invalid syntax. Use: pattern frequency "pattern"'

        pattern = pattern_match.group(1)

        # Parse optional timeframe
        timeframe = 30
        if "timeframe=" in line:
            try:
                time_match = re.search(r"timeframe=(\d+)", line)
                if time_match:
                    timeframe = int(time_match.group(1))
            except Exception:
                pass

        frequency = self.memory.get_pattern_frequency(pattern, timeframe)

        return f"[Pattern Frequency] Pattern '{pattern}' found {frequency} times in the last {timeframe} days"

    def _is_block_start(self, line):
        """Check if line starts a multi-line block - Enhanced for NeuroCode"""
        # Standard block starters
        block_starters = ["define ", "if ", "for ", "while ", "simulate "]

        # NeuroCode-specific block starters
        neuro_block_starters = [
            "agent:",
            "with agent:",
            "function ",
            "memory {",
            "goal {",
            "reflect {",
            "analyze {",
            "think {",
            "learn {",
        ]

        stripped_line = line.strip()

        # Check standard blocks
        if any(stripped_line.startswith(starter) for starter in block_starters):
            return True

        # Check NeuroCode blocks
        if any(stripped_line.startswith(starter) for starter in neuro_block_starters):
            return True

        # Check for function definition with colon
        if stripped_line.startswith("define ") and (
            stripped_line.endswith(":") or "(" in stripped_line
        ):
            return True

        return False

    def _start_block(self, line):
        """Start a new block - Enhanced for NeuroCode constructs"""
        self.in_block = True
        self.block_buffer = [line]
        stripped_line = line.strip()

        # Determine block type
        if stripped_line.startswith("define "):
            self.block_type = "function"
            func_name = self._extract_function_name(line)
            return f"🔧 Started function definition: {func_name}\n   📝 Enter function body, use 'end' to complete"

        elif stripped_line.startswith("agent:"):
            self.block_type = "agent"
            return "🤖 Started agent configuration block\n   🎯 Define agent behavior and capabilities, use 'end' to complete"

        elif stripped_line.startswith("if "):
            self.block_type = "conditional"
            return (
                "🔀 Started conditional block\n   ⚡ Enter conditional logic, use 'end' to complete"
            )

        elif stripped_line.startswith("for "):
            self.block_type = "for_loop"
            return "🔄 Started for loop block\n   🔃 Enter loop body, use 'end' to complete"

        elif stripped_line.startswith("while "):
            self.block_type = "while_loop"
            return "🔄 Started while loop block\n   ⏳ Enter loop body, use 'end' to complete"

        elif any(
            stripped_line.startswith(starter)
            for starter in ["memory {", "reflect {", "analyze {", "think {", "learn {"]
        ):
            self.block_type = "neuro_block"
            block_name = stripped_line.split("{")[0].strip()
            return f"🧬 Started NeuroCode {block_name} block\n   💭 Enter AI-native operations, use '{{}}' to complete"

        elif stripped_line.startswith("simulate "):
            self.block_type = "simulation"
            return (
                "🎮 Started simulation block\n   🔬 Enter simulation steps, use 'end' to complete"
            )

        else:
            self.block_type = "generic"
            return "📦 Started generic block\n   📋 Enter statements, use 'end' to complete"

    def _extract_function_name(self, line):
        """Extract function name from definition line"""
        import re

        match = re.search(r"define\s+(\w+)", line)
        return match.group(1) if match else "unnamed"

    def _add_to_block(self, line):
        """Add line to current block or execute if terminator found"""
        stripped_line = line.strip()

        # Check for block terminators
        if self._is_block_terminator(stripped_line):
            return self._execute_block()
        else:
            self.block_buffer.append(line)

            # Provide helpful feedback
            if self.block_type == "function":
                return f"  ➕ Added to function (line {len(self.block_buffer)}): {line}"
            elif self.block_type == "agent":
                return f"  🤖 Added agent directive: {line}"
            elif self.block_type == "neuro_block":
                return f"  🧬 Added NeuroCode operation: {line}"
            else:
                return f"  📝 Added to {self.block_type} block: {line}"

    def _is_block_terminator(self, line):
        """Check if line terminates the current block"""
        if self.block_type == "neuro_block":
            return line == "}" or line.endswith("}")
        else:
            return line == "end" or line.endswith("end")

    def _execute_block(self):
        """Execute the current block - Enhanced for NeuroCode"""
        if not self.in_block or not self.block_buffer:
            return "❌ No block to execute"

        try:
            if self.block_type == "function":
                return self._execute_function_block()
            elif self.block_type == "agent":
                return self._execute_agent_block()
            elif self.block_type == "neuro_block":
                return self._execute_neuro_block()
            else:
                # Use the block executor for standard blocks
                result = self.block_executor.execute_block(self.block_buffer, self.execute)
                self._reset_block_state()
                return result

        except Exception as e:
            self._reset_block_state()
            return f"❌ Block execution failed: {str(e)}"

    def _execute_function_block(self):
        """Execute function definition block"""
        if len(self.block_buffer) < 1:
            self._reset_block_state()
            return "❌ Empty function definition"

        # Parse function signature
        signature = self.block_buffer[0].strip()
        import re

        # Enhanced function parsing: define func_name(param1, param2) or define func_name:
        func_match = re.search(r"define\s+(\w+)(?:\s*\(([^)]*)\))?\s*:?", signature)
        if not func_match:
            self._reset_block_state()
            return "❌ Invalid function signature. Use: define function_name(params) or define function_name:"

        func_name = func_match.group(1)
        params_str = func_match.group(2) or ""
        params = [p.strip() for p in params_str.split(",") if p.strip()]

        # Function body (excluding the signature and 'end')
        body = self.block_buffer[1:]

        # Store function using existing function system
        result = self.functions.define_function(func_name, params, body)

        self._reset_block_state()

        response = "🔧 Function Definition Complete\n"
        response += f"   📝 Function: {func_name}\n"
        response += f"   🔧 Parameters: {params if params else 'none'}\n"
        response += f"   📄 Body: {len(body)} statements\n"
        response += (
            f"   ✅ Ready to call with: call {func_name}({', '.join(['arg'] * len(params))})"
        )

        return response

    def _execute_agent_block(self):
        """Execute agent configuration block"""
        if len(self.block_buffer) < 2:
            self._reset_block_state()
            return "❌ Empty agent configuration"

        # Parse agent configuration
        config_lines = self.block_buffer[1:]  # Skip the 'agent:' line

        agent_config = {}
        for line in config_lines:
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                agent_config[key.strip()] = value.strip().strip("\"'")

        # Apply agent configuration
        specialization = agent_config.get("specialization", "general")
        memory_access = agent_config.get("memory_access", "standard")
        goal_alignment = agent_config.get("goal_alignment", "manual")

        # Activate agent with configuration
        self.agent.activate()

        self._reset_block_state()

        response = "🤖 Agent Configuration Complete\n"
        response += f"   🧠 Specialization: {specialization}\n"
        response += f"   💾 Memory Access: {memory_access}\n"
        response += f"   🎯 Goal Alignment: {goal_alignment}\n"
        response += "   🚀 Agent active and ready for tasks"

        return response

    def _execute_neuro_block(self):
        """Execute NeuroCode AI-native block"""
        if len(self.block_buffer) < 2:
            self._reset_block_state()
            return "❌ Empty NeuroCode block"

        # Determine block type and execute accordingly
        header = self.block_buffer[0].strip()
        operations = self.block_buffer[1:]

        results = []

        if header.startswith("think"):
            results.append("🧠 AI Thinking Process:")
            for op in operations:
                if op.strip():
                    results.append(f"   💭 {op.strip()}")
            results.append("   ✅ Thinking complete")

        elif header.startswith("analyze"):
            results.append("🔍 AI Analysis Process:")
            for op in operations:
                if op.strip():
                    results.append(f"   📊 {op.strip()}")
            results.append("   ✅ Analysis complete")

        elif header.startswith("memory"):
            results.append("💾 Memory Operations:")
            for op in operations:
                if op.strip():
                    # Execute memory operations
                    result = self.execute(op.strip())
                    results.append(f"   {result}")

        else:
            results.append("🧬 NeuroCode Block Execution:")
            for op in operations:
                if op.strip():
                    result = self.execute(op.strip())
                    results.append(f"   {result}")

        self._reset_block_state()
        return "\n".join(results)

    def _reset_block_state(self):
        """Reset block parsing state"""
        self.in_block = False
        self.block_buffer = []
        self.block_type = None

    def _load_and_analyze_file(self, filename):
        """Load file with automatic error detection and analysis"""
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File not found: {filename}")

            with open(filename, encoding="utf-8") as f:
                content = f.read()

            print(f"📁 [Loaded] {filename} ({len(content)} characters)")

            # Try to validate Python files
            if filename.endswith(".py"):
                try:
                    ast.parse(content)
                    print("✅ [Validation] No syntax errors detected")
                except SyntaxError as e:
                    print(f"🐛 [Syntax Error] {e}")
                    self.debug_system.detect_and_store_error(
                        e, f"Loading file: {filename}", filename
                    )

                    # Auto-suggest fix if enabled
                    if self.debug_system.auto_apply_enabled:
                        print("🔄 [Auto-Debug] Analyzing syntax error...")
                        error_info = {
                            "type": "SyntaxError",
                            "message": str(e),
                            "file_path": filename,
                            "line_number": e.lineno,
                            "context": f"Loading file: {filename}",
                            "traceback": traceback.format_exc(),
                            "timestamp": str(datetime.now()),
                        }
                        fix_suggestion = self.debug_system.suggest_fix(error_info)
                        self._last_fix_suggestion = fix_suggestion
                        print(
                            f"💡 [Suggestion] {fix_suggestion.get('fix', 'Manual review needed')}"
                        )

            # Store successful load in memory
            self.memory.remember(
                f"Loaded file: {filename}", tags=["file", "load"], category="operations"
            )

        except Exception as e:
            print(f"❌ [Load Error] {e}")
            self.debug_system.detect_and_store_error(e, f"Loading file: {filename}", filename)

    def execute_enhanced(self, code):
        """Enhanced execution using SyntaxTree parser - separates parsing from execution"""
        if not self.use_enhanced_parser or parse_neurocode is None:
            return "Enhanced parser not available, falling back to standard execution"

        try:
            # Parse the code into a syntax tree
            syntax_tree = parse_neurocode(code)

            # Execute using the visitor pattern
            result = self.syntax_visitor.visit(syntax_tree)

            return result
        except Exception as e:
            return f"Enhanced execution failed: {e}. Falling back to standard parsing."

    def execute_syntax_tree(self, syntax_tree):
        """Execute a pre-parsed syntax tree"""
        if not self.use_enhanced_parser:
            return "Enhanced parser not available"

        try:
            result = self.syntax_visitor.visit(syntax_tree)
            return result
        except Exception as e:
            return f"Syntax tree execution failed: {e}"


class NeuroExecutionVisitor:
    """Execution visitor that runs NeuroCode syntax tree nodes"""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        # Initialize base visitor if available
        if SyntaxTreeVisitor and SyntaxTreeVisitor is not object:
            super().__init__()

    def visit(self, node):
        """Visit a node using the visitor pattern"""
        method_name = f"visit_{node.type.value}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Default visitor for unhandled node types"""
        children = getattr(node, "children", []) or []
        results = []
        for child in children:
            result = self.visit(child)
            if result:
                results.append(result)
        return results

    def visit_program(self, node):
        """Execute a program node"""
        results = []
        for child in node.children:
            result = self.visit(child)
            if result:
                results.append(result)
        return "\n".join(str(r) for r in results if r)

    def visit_goal(self, node):
        """Execute a goal node"""
        goal_text = node.value
        priority = node.metadata.get("priority", "medium")

        # Use the goal system to set the goal
        self.interpreter.goal_system.set_goal(goal_text, priority)

        return f"🎯 Goal set: {goal_text} (Priority: {priority})"

    def visit_memory(self, node):
        """Execute a memory operation node"""
        action = node.value["action"]

        if action == "remember":
            content = node.value["content"]
            tag = node.value.get("tag", "general")
            tags = [tag] if tag else ["general"]

            self.interpreter.memory.remember(content, tags)
            return f"💾 Remembered: '{content}' as '{tag}'"

        elif action == "recall":
            tag = node.value.get("tag")
            since = node.value.get("since")
            category = node.value.get("category")

            # Build query parameters
            time_filter = since if since else None

            # Recall memories
            memories = self.interpreter.memory.recall(
                tags=[tag] if tag else None, category=category, time_filter=time_filter
            )

            if memories:
                return f"🧠 Recalled {len(memories)} memories:\n" + "\n".join(
                    f"  • {m}" for m in memories[:5]
                )
            else:
                return f"🔍 No memories found for tag '{tag}'"

        elif action == "search":
            keyword = node.value["keyword"]
            results = self.interpreter.memory.search(keyword)

            if results:
                return f"🔍 Found {len(results)} memories containing '{keyword}':\n" + "\n".join(
                    f"  • {r}" for r in results[:5]
                )
            else:
                return f"🔍 No memories found containing '{keyword}'"

        elif action == "pattern":
            pattern = node.value["pattern"]
            frequency = node.value.get("frequency", "weekly")

            analysis = self.interpreter.memory.pattern_analysis(pattern, frequency)
            return f"📊 Pattern analysis for '{pattern}': {analysis['matches']} matches, threshold: {analysis['meets_threshold']}"

        return f"Memory operation: {action}"

    def visit_assistant(self, node):
        """Execute an assistant call node"""
        prompt = node.value

        try:
            # Use the AI runtime if available
            response = ask_ai(prompt, temperature=0.2)
            return f"🤖 Assistant: {response}"
        except Exception as e:
            return f"🤖 Assistant: {prompt} (AI not available: {e})"

    def visit_plugin(self, node):
        """Execute a plugin call node"""
        plugin_name = node.value["name"]
        plugin_args = node.value["args"]

        try:
            if plugin_name in PLUGIN_REGISTRY:
                # Parse arguments if needed
                result = PLUGIN_REGISTRY[plugin_name](plugin_args)
                return f"🔌 Plugin '{plugin_name}': {result}"
            else:
                return f"🔌 Plugin '{plugin_name}' not found. Available: {list(PLUGIN_REGISTRY.keys())}"
        except Exception as e:
            return f"🔌 Plugin '{plugin_name}' error: {e}"

    def visit_function_def(self, node):
        """Execute a function definition node"""
        func_name = node.value["name"]
        params = node.value["params"]

        # Store function definition for later execution
        self.interpreter.functions.define_function(func_name, params, node.children)

        return f"📝 Function defined: {func_name}({', '.join(params)})"

    def visit_function_call(self, node):
        """Execute a function call node"""
        func_name = node.value["name"]
        args = node.value["args"]

        try:
            result = self.interpreter.functions.call_function(func_name, args)
            return f"🔧 Function '{func_name}' result: {result}"
        except Exception as e:
            return f"🔧 Function '{func_name}' error: {e}"

    def visit_variable_assign(self, node):
        """Execute a variable assignment node"""
        var_name = node.value["name"]
        var_value = node.value["value"]

        # Store in interpreter's variable context
        if not hasattr(self.interpreter, "variables"):
            self.interpreter.variables = {}

        self.interpreter.variables[var_name] = var_value
        return f"📋 Variable assigned: {var_name} = {var_value}"

    def visit_conditional(self, node):
        """Execute a conditional node"""
        if node.value["type"] == "if":
            condition = node.value["condition"]
            return f"🔀 If condition: {condition}"
        else:
            return "🔀 Else block"

    def visit_loop(self, node):
        """Execute a loop node"""
        if node.value["type"] == "for":
            var_name = node.value["var"]
            iterable = node.value["iterable"]
            return f"🔄 For loop: {var_name} in {iterable}"
        elif node.value["type"] == "while":
            condition = node.value["condition"]
            return f"🔄 While loop: {condition}"

    def visit_expression(self, node):
        """Execute an expression node"""
        expression = node.value

        # Try to evaluate simple expressions
        try:
            # For now, just return the expression
            return f"📐 Expression: {expression}"
        except Exception as e:
            return f"📐 Expression error: {e}"

    def visit_comment(self, node):
        """Execute a comment node (no-op)"""
        return None  # Comments don't produce output
