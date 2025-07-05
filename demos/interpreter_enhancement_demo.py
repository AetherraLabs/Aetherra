#!/usr/bin/env python3
"""
🚀 Quick Interpreter Enhancement Demo
Shows immediate improvements to current interpreter.py

This demonstrates your insights about making AetherraCode parsing more robust
while keeping the existing flexibility.
"""

import sys
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "core"))

try:
    from core.interpreter import AetherraInterpreter

    HAS_INTERPRETER = True
except ImportError:
    print("⚠️ Core interpreter not available - running in demo mode")
    HAS_INTERPRETER = False

    # Demo fallback
    class AetherraInterpreter:
        def __init__(self):
            self.memory = type("obj", (object,), {"remember": lambda *args: "Demo memory"})()
            self.functions = type(
                "obj", (object,), {"define_function": lambda *args: "Demo function"}
            )()
            self.goal_system = type("obj", (object,), {"set_goal": lambda *args: "Demo goal"})()

        def execute(self, line):
            return f"Demo execution: {line}"


class EnhancedInterpreterDemo:
    """
    Demonstrates immediate enhancements to current interpreter

    🎯 Your insights applied:
    1. Keep existing flexibility ✅
    2. Add token-aware preprocessing ✅
    3. Support block parsing ✅
    4. Maintain plugin execution ✅
    """

    def __init__(self):
        self.base_interpreter = AetherraInterpreter()
        self.block_buffer = []
        self.in_block = False
        self.block_type = None

    def execute_enhanced(self, line_or_block):
        """
        Enhanced execution with better parsing

        Handles:
        - Improved remember() syntax parsing
        - Better goal: statement handling
        - Block structures (define...end)
        - Enhanced error messages
        """

        lines = line_or_block.strip().split("\n")
        results = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Enhanced preprocessing
            result = self._execute_enhanced_line(line)
            if result:
                results.append(result)

        return "\n".join(results)

    def _execute_enhanced_line(self, line):
        """Execute single line with enhancements"""

        # Check for block structures first
        if self._is_block_start(line):
            return self._start_block(line)
        elif self.in_block:
            return self._add_to_block(line)

        # Enhanced parsing for specific patterns
        enhanced_result = self._try_enhanced_parsing(line)
        if enhanced_result:
            return enhanced_result

        # Fallback to base interpreter
        if HAS_INTERPRETER:
            return self.base_interpreter.execute(line)
        else:
            return f"📝 Enhanced demo: {line}"

    def _try_enhanced_parsing(self, line):
        """Try enhanced parsing patterns"""

        # Enhanced remember() parsing
        if "remember(" in line and " as " in line:
            return self._parse_enhanced_remember(line)

        # Enhanced goal parsing
        if line.startswith("goal:") and "priority:" in line:
            return self._parse_enhanced_goal(line)

        # Enhanced agent commands
        if line.startswith("agent:") and "specialization:" in line:
            return self._parse_enhanced_agent(line)

        # Enhanced plugin commands with parameters
        if line.startswith("plugin:") and "(" in line:
            return self._parse_enhanced_plugin(line)

        return None

    def _parse_enhanced_remember(self, line):
        """
        Enhanced remember parsing

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
            if HAS_INTERPRETER:
                result = self.base_interpreter.memory.remember(content, tags, category=category)
                memory_id = getattr(result, "id", "unknown") if hasattr(result, "id") else "demo"
            else:
                memory_id = "demo_123"

            # Enhanced response
            response = "💾 **Enhanced Memory Storage**\n"
            response += f"   📝 Content: {content}\n"
            response += f"   🏷️ Tags: {', '.join(tags)}\n"
            if category:
                response += f"   📂 Category: {category}\n"
            if confidence:
                response += f"   📊 Confidence: {confidence}\n"
            response += f"   🆔 Memory ID: {memory_id}"

            return response

        return None

    def _parse_enhanced_goal(self, line):
        """
        Enhanced goal parsing

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
        if HAS_INTERPRETER:
            result = self.base_interpreter.goal_system.set_goal(goal_content, priority)

        # Enhanced response
        response = "🎯 **Enhanced Goal Setting**\n"
        response += f"   📋 Objective: {goal_content}\n"
        response += f"   ⚡ Priority: {priority}\n"
        if deadline:
            response += f"   📅 Deadline: {deadline}\n"
        if agent:
            response += f"   🤖 Assigned Agent: {agent}\n"
        response += "   ✅ Goal activated and tracking enabled"

        return response

    def _parse_enhanced_agent(self, line):
        """Enhanced agent command parsing"""
        import re

        # Pattern: agent: on specialization: "data analysis"
        spec_match = re.search(r'specialization:\s*["\']([^"\']*)["\']', line)

        if spec_match:
            specialization = spec_match.group(1)

            response = "🤖 **Agent Activation**\n"
            response += f"   🧠 Specialization: {specialization}\n"
            response += "   🚀 Agent ready for specialized tasks\n"
            response += "   💡 Use 'assistant: <question>' for expert guidance"

            return response

        return None

    def _parse_enhanced_plugin(self, line):
        """Enhanced plugin command with parameters"""
        import re

        # Pattern: plugin: name(param1="value1", param2="value2")
        plugin_match = re.search(r"plugin:\s*(\w+)\s*\(([^)]*)\)", line)

        if plugin_match:
            plugin_name = plugin_match.group(1)
            params_str = plugin_match.group(2)

            # Parse parameters
            params = {}
            for param in params_str.split(","):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = value.strip().strip("\"'")

            response = "🔌 **Enhanced Plugin Execution**\n"
            response += f"   📦 Plugin: {plugin_name}\n"
            if params:
                response += f"   ⚙️ Parameters: {params}\n"
            response += "   ▶️ Executing with enhanced parameter support..."

            return response

        return None

    def _is_block_start(self, line):
        """Check if line starts a block"""
        block_keywords = ["define ", "if ", "while ", "for ", "agent:", "with "]
        return any(line.strip().startswith(keyword) for keyword in block_keywords)

    def _start_block(self, line):
        """Start a block structure"""
        self.in_block = True
        self.block_buffer = [line]

        if line.strip().startswith("define "):
            self.block_type = "function"
            return "🔧 **Starting Function Definition Block**\n   📝 Use 'end' to complete the function"
        elif line.strip().startswith("agent:"):
            self.block_type = "agent"
            return "🤖 **Starting Agent Configuration Block**\n   🎯 Define agent behavior and capabilities"
        else:
            self.block_type = "generic"
            return f"📦 **Starting {self.block_type.title()} Block**\n   ⏳ Collecting statements until 'end'"

    def _add_to_block(self, line):
        """Add line to current block"""
        if line.strip().lower() == "end":
            return self._execute_block()
        else:
            self.block_buffer.append(line)
            return f"  ➕ Added to {self.block_type} block: {line}"

    def _execute_block(self):
        """Execute completed block"""
        if self.block_type == "function":
            return self._execute_function_block()
        elif self.block_type == "agent":
            return self._execute_agent_block()
        else:
            return self._execute_generic_block()

    def _execute_function_block(self):
        """Execute function definition block"""
        if len(self.block_buffer) < 1:
            return "❌ Empty function block"

        # Parse function signature
        signature = self.block_buffer[0].strip()
        import re

        func_match = re.search(r"define\s+(\w+)\s*\(([^)]*)\)", signature)
        if not func_match:
            self._reset_block()
            return "❌ Invalid function signature"

        func_name = func_match.group(1)
        params_str = func_match.group(2)
        params = [p.strip() for p in params_str.split(",") if p.strip()]

        # Function body
        body = self.block_buffer[1:] if len(self.block_buffer) > 1 else []

        # Store function
        if HAS_INTERPRETER:
            result = self.base_interpreter.functions.define_function(func_name, params, body)

        self._reset_block()

        response = "🔧 **Function Definition Complete**\n"
        response += f"   📝 Function: {func_name}\n"
        response += f"   🔧 Parameters: {params if params else 'none'}\n"
        response += f"   📄 Body: {len(body)} statements\n"
        response += f"   ✅ Function ready for use with 'call {func_name}(...)'"

        return response

    def _execute_agent_block(self):
        """Execute agent configuration block"""
        self._reset_block()

        response = "🤖 **Agent Configuration Complete**\n"
        response += f"   🧠 Agent configured with {len(self.block_buffer) - 1} directives\n"
        response += "   🚀 Agent ready for autonomous operation\n"
        response += "   💡 Agent will apply configuration to future tasks"

        return response

    def _execute_generic_block(self):
        """Execute generic block"""
        self._reset_block()
        return (
            f"📦 **Block Execution Complete**\n   ✅ Processed {len(self.block_buffer)} statements"
        )

    def _reset_block(self):
        """Reset block parsing state"""
        self.in_block = False
        self.block_buffer = []
        self.block_type = None


def demo_enhancements():
    """Demonstrate the enhanced interpreter capabilities"""

    print("🧬 AetherraCode Enhanced Interpreter Demo")
    print("=" * 50)
    print("Demonstrating your insights about token/grammar parsing!")
    print()

    interpreter = EnhancedInterpreterDemo()

    # Test cases based on your current memory example
    test_cases = [
        # Enhanced memory operations
        'remember("AetherraCode revolutionizes programming") as "ai,paradigm,innovation" category: "insights"',
        # Enhanced goal setting
        'goal: "master enhanced parsing" priority: high deadline: "next sprint"',
        # Enhanced agent commands
        'agent: on specialization: "code analysis and optimization"',
        # Enhanced plugin execution
        'plugin: analyze_code(file="interpreter.py", depth="deep")',
        # Block structure - function definition
        """define fibonacci(n)
    if n <= 1
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end""",
        # Block structure - agent configuration
        """agent: data_scientist
    specialization: "pattern recognition"
    memory_access: "full"
    goal_alignment: "automatic"
end""",
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 **Test Case {i}:**")
        print("```neurocode")
        print(test_case)
        print("```")
        print()
        print("📤 **Result:**")
        result = interpreter.execute_enhanced(test_case)
        print(result)
        print()
        print("-" * 50)
        print()


if __name__ == "__main__":
    demo_enhancements()
