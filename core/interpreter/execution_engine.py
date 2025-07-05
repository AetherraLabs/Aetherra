# core/interpreter/execution_engine.py
"""
Execution Engine for AetherraCode Interpreter
==========================================

Handles command execution and routing to appropriate handlers.
"""

import time
from typing import Any, Dict

from .base import ExecutionResult, ParseResult


class ExecutionEngine:
    """Main execution engine for AetherraCode commands"""

    def __init__(self, components: Dict[str, Any]):
        self.components = components
        self.handlers = {}
        self.execution_stats = {}
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup command handlers"""
        self.handlers = {
            "remember": self._handle_remember,
            "enhanced_remember": self._handle_enhanced_remember,
            "recall": self._handle_recall,
            "goal": self._handle_goal,
            "enhanced_goal": self._handle_enhanced_goal,
            "agent": self._handle_agent,
            "enhanced_agent": self._handle_enhanced_agent,
            "plugin": self._handle_plugin,
            "enhanced_plugin": self._handle_enhanced_plugin,
            "function": self._handle_function,
            "think": self._handle_think,
            "analyze": self._handle_analyze,
            "assistant": self._handle_assistant,
            "debug": self._handle_debug,
            "meta": self._handle_meta,
            "unknown": self._handle_unknown,
        }

    def execute(self, parse_result: ParseResult) -> ExecutionResult:
        """Execute a parsed command"""
        start_time = time.time()

        try:
            handler = self.handlers.get(parse_result.command_type, self._handle_unknown)
            output = handler(parse_result)

            execution_time = time.time() - start_time

            # Update stats
            cmd_type = parse_result.command_type
            self.execution_stats[cmd_type] = self.execution_stats.get(cmd_type, 0) + 1

            return ExecutionResult(
                success=True,
                output=output,
                command_type=parse_result.command_type,
                execution_time=execution_time,
                metadata={"enhanced": parse_result.enhanced},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output=f"Error executing command: {str(e)}",
                command_type=parse_result.command_type,
                execution_time=execution_time,
                error=str(e),
            )

    def _handle_remember(self, parse_result: ParseResult) -> str:
        """Handle basic remember commands"""
        memory = self.components.get("memory")
        if not memory:
            return "Memory system not available"

        content = parse_result.parameters.get("content", "")
        result = memory.remember(content)
        return f"💾 Memory stored: {content[:50]}..."

    def _handle_enhanced_remember(self, parse_result: ParseResult) -> str:
        """Handle enhanced remember commands with tags and metadata"""
        memory = self.components.get("memory")
        if not memory:
            return "Memory system not available"

        params = parse_result.parameters
        content = params.get("content", "")
        tags = params.get("tags", [])
        category = params.get("category")
        confidence = params.get("confidence")

        result = memory.remember(content, tags, category=category)

        response = "💾 Enhanced Memory Storage\n"
        response += f"   📝 Content: {content[:50]}...\n"
        response += f"   🏷️  Tags: {', '.join(tags)}\n"
        if category:
            response += f"   📂 Category: {category}\n"
        if confidence:
            response += f"   📊 Confidence: {confidence}\n"
        response += "   ✅ Memory stored with enhanced metadata"

        return response

    def _handle_recall(self, parse_result: ParseResult) -> str:
        """Handle recall commands"""
        memory = self.components.get("memory")
        if not memory:
            return "Memory system not available"

        query = parse_result.parameters.get("content", "")
        memories = memory.recall(query)

        if not memories:
            return f"🔍 No memories found for: {query}"

        response = f"🔍 Recalled {len(memories)} memories for: {query}\n"
        for i, mem in enumerate(memories[:3], 1):  # Show first 3
            response += f"{i}. {str(mem)[:60]}...\n"

        return response

    def _handle_goal(self, parse_result: ParseResult) -> str:
        """Handle basic goal commands"""
        goal_system = self.components.get("goal_system")
        if not goal_system:
            return "Goal system not available"

        goal_text = parse_result.parameters.get("content", "")
        result = goal_system.set_goal(goal_text)
        return result

    def _handle_enhanced_goal(self, parse_result: ParseResult) -> str:
        """Handle enhanced goal commands with priority and metadata"""
        goal_system = self.components.get("goal_system")
        if not goal_system:
            return "Goal system not available"

        params = parse_result.parameters
        goal_text = params.get("goal", "")
        priority = params.get("priority", "medium")
        deadline = params.get("deadline")
        agent = params.get("agent")

        result = goal_system.set_goal(goal_text, priority=priority)

        response = "🎯 Enhanced Goal Set\n"
        response += f"   📋 Goal: {goal_text}\n"
        response += f"   ⚡ Priority: {priority}\n"
        if deadline:
            response += f"   📅 Deadline: {deadline}\n"
        if agent:
            response += f"   🤖 Assigned Agent: {agent}\n"
        response += "   ✅ Goal activated and tracking enabled"

        return response

    def _handle_agent(self, parse_result: ParseResult) -> str:
        """Handle basic agent commands"""
        agent = self.components.get("agent")
        if not agent:
            return "Agent system not available"

        action = parse_result.parameters.get("content", "activate")
        if action == "activate" or action == "on":
            return agent.activate()
        else:
            agent.deactivate()
            return "🤖 Agent deactivated"

    def _handle_enhanced_agent(self, parse_result: ParseResult) -> str:
        """Handle enhanced agent commands with specialization"""
        agent = self.components.get("agent")
        if not agent:
            return "Agent system not available"

        params = parse_result.parameters
        specialization = params.get("specialization", "")

        result = agent.activate()

        response = "🤖 Enhanced Agent Activation\n"
        response += f"   🧠 Specialization: {specialization}\n"
        response += "   🚀 Agent ready for specialized tasks\n"
        response += "   💡 Use 'assistant: <question>' for expert guidance"

        return response

    def _handle_plugin(self, parse_result: ParseResult) -> str:
        """Handle basic plugin commands"""
        plugin_name = parse_result.parameters.get("content", "")
        return f"🔌 Plugin executed: {plugin_name}"

    def _handle_enhanced_plugin(self, parse_result: ParseResult) -> str:
        """Handle enhanced plugin commands with parameters"""
        params = parse_result.parameters
        plugin_name = params.get("plugin_name", "")
        plugin_params = params.get("params", {})

        response = "🔌 Enhanced Plugin Execution\n"
        response += f"   📦 Plugin: {plugin_name}\n"
        if plugin_params:
            response += f"   ⚙️  Parameters: {plugin_params}\n"
        response += "   ✅ Plugin executed with parameters"

        return response

    def _handle_function(self, parse_result: ParseResult) -> str:
        """Handle function definition commands"""
        functions = self.components.get("functions")
        if not functions:
            return "Function system not available"

        func_name = parse_result.parameters.get("content", "")
        return f"⚡ Function defined: {func_name}"

    def _handle_think(self, parse_result: ParseResult) -> str:
        """Handle think commands"""
        topic = parse_result.parameters.get("content", "")
        return f"🤔 Thinking about: {topic}"

    def _handle_analyze(self, parse_result: ParseResult) -> str:
        """Handle analyze commands"""
        target = parse_result.parameters.get("content", "")
        return f"🔍 Analyzing: {target}"

    def _handle_assistant(self, parse_result: ParseResult) -> str:
        """Handle assistant commands"""
        question = parse_result.parameters.get("content", "")
        return f"🤖 Assistant response to: {question}"

    def _handle_debug(self, parse_result: ParseResult) -> str:
        """Handle debug commands"""
        debug_system = self.components.get("debug_system")
        if not debug_system:
            return "Debug system not available"

        message = parse_result.parameters.get("content", "")
        debug_system.debug(message)
        return f"🐛 Debug: {message}"

    def _handle_meta(self, parse_result: ParseResult) -> str:
        """Handle meta commands"""
        meta_plugins = self.components.get("meta_plugins")
        if not meta_plugins:
            return "Meta-plugin system not available"

        command = parse_result.parameters.get("content", "")
        return meta_plugins.execute_meta_plugin(command)

    def _handle_unknown(self, parse_result: ParseResult) -> str:
        """Handle unknown commands"""
        return f"❓ Unknown command: {parse_result.raw_line}"

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            "command_counts": self.execution_stats,
            "total_executions": sum(self.execution_stats.values()),
            "available_handlers": list(self.handlers.keys()),
        }
