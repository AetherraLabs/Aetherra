# aetherra/runtime/aether_runtime.py

import asyncio
import re
import time
from datetime import datetime
from queue import Queue
from typing import Any, Dict, Optional


class ExecutionContext:
    """
    Holds runtime state: memory, plugin manager, agents, variables, goals.
    """

    def __init__(self):
        self.memory = None
        self.plugins = None
        self.agents = None
        self.variables = {}
        self.goals = []
        self.goal_queue = Queue()
        self.execution_history = []


class AetherRuntime:
    """
    Core runtime engine that interprets and executes .aether scripts.
    Enhanced with goal queue scheduling and Lyrixa integration.
    """

    def __init__(self):
        self.context = ExecutionContext()
        self.script_lines = []
        self.running = False

    def register_context(self, memory=None, plugins=None, agents=None):
        """Register Lyrixa's components with the runtime."""
        self.context.memory = memory
        self.context.plugins = plugins
        self.context.agents = agents
        print("🔌 Aether Runtime connected to Lyrixa ecosystem")
        print(f"   📝 Memory: {'✅' if memory else '❌'}")
        print(f"   🧩 Plugins: {'✅' if plugins else '❌'}")
        print(f"   🤖 Agents: {'✅' if agents else '❌'}")

    def load_script(self, script: str, from_file: bool = True):
        """Load .aether script from file or string."""
        if from_file:
            with open(script, "r", encoding="utf-8") as f:
                self.script_lines = [line.strip() for line in f if line.strip()]
        else:
            self.script_lines = [
                line.strip() for line in script.strip().split("\n") if line.strip()
            ]

    def load_aether_goal(self, file_path: str):
        """Load and execute a .aether goal file."""
        print(f"📁 Loading .aether goal from: {file_path}")
        self.load_script(file_path, from_file=True)
        return self.execute()

    def execute_goal(self, goal: str):
        """Execute a single .aether goal string."""
        print(f"🎯 Executing .aether goal: {goal}")
        self.load_script(goal, from_file=False)
        return self.execute()

    def queue_goal(self, goal: str, priority: int = 0):
        """Add a goal to the execution queue."""
        goal_item = {
            "goal": goal,
            "priority": priority,
            "queued_at": datetime.now(),
            "status": "queued",
        }
        self.context.goal_queue.put(goal_item)
        print(f"📋 Queued goal: {goal}")

    def process_goal_queue(self):
        """Process all queued goals."""
        print("🔄 Processing goal queue...")
        processed = 0

        while not self.context.goal_queue.empty():
            goal_item = self.context.goal_queue.get()
            goal_item["status"] = "executing"
            goal_item["started_at"] = datetime.now()

            print(f"⚡ Executing queued goal: {goal_item['goal']}")

            try:
                result = self.execute_goal(goal_item["goal"])
                goal_item["status"] = "completed"
                goal_item["completed_at"] = datetime.now()
                goal_item["result"] = result
                processed += 1
            except Exception as e:
                goal_item["status"] = "failed"
                goal_item["error"] = str(e)
                print(f"❌ Goal failed: {e}")

            self.context.execution_history.append(goal_item)

        print(f"✅ Processed {processed} goals from queue")
        return processed

    def execute(self):
        """Execute the loaded script."""
        if not self.script_lines:
            print("[WARN] No script loaded")
            return False

        self.running = True
        start_time = time.time()

        print(
            f"🚀 Starting .aether script execution ({len(self.script_lines)} commands)"
        )

        for i, line in enumerate(self.script_lines, 1):
            if not self.running:
                print("⏹️ Execution stopped")
                break

            print(f"[{i}/{len(self.script_lines)}] → {line}")

            try:
                self.interpret_command(line)
            except Exception as e:
                print(f"❌ Error executing line {i}: {e}")
                # Continue execution unless it's a critical error

        execution_time = time.time() - start_time
        print(f"✅ Script execution completed in {execution_time:.2f}s")
        self.running = False
        return True

    def stop_execution(self):
        """Stop the current execution."""
        self.running = False
        print("🛑 Execution stop requested")

    def get_execution_stats(self):
        """Get execution statistics."""
        return {
            "goals_completed": len(
                [
                    h
                    for h in self.context.execution_history
                    if h["status"] == "completed"
                ]
            ),
            "goals_failed": len(
                [h for h in self.context.execution_history if h["status"] == "failed"]
            ),
            "variables_set": len(self.context.variables),
            "goals_defined": len(self.context.goals),
            "queue_size": self.context.goal_queue.qsize(),
        }

    def interpret_command(self, line: str):
        """
        Parse and execute a single .aether instruction.
        Enhanced with better error handling and feedback.
        """
        line = line.strip()
        if not line or line.startswith("#"):
            return  # Skip empty lines and comments

        # Goal definition
        if line.startswith("goal "):
            goal_text = line.replace("goal", "", 1).strip('" ')
            self.context.goals.append(goal_text)
            print(f"🎯 New goal added: {goal_text}")

        # Plugin usage
        elif line.startswith("use plugin "):
            plugin_name = line.replace("use plugin", "", 1).strip('" ')
            if self.context.plugins:
                try:
                    result = self.context.plugins.execute_plugin(plugin_name)
                    self.context.variables["last_plugin_result"] = result
                    print(f"🧩 Plugin '{plugin_name}' executed successfully")
                except Exception as e:
                    print(f"❌ Plugin '{plugin_name}' failed: {e}")
            else:
                print("❌ No plugin manager available")

        # Memory recall with enhanced pattern matching
        elif "recall" in line and "→" in line:
            match = re.match(r"recall [\"'](.+?)[\"'] → \$(\w+)", line)
            if match and self.context.memory:
                query, var_name = match.groups()
                try:
                    result = self.context.memory.search(query)
                    self.context.variables[var_name] = result
                    print(f"🧠 Recalled '{query}' → ${var_name}")
                    print(
                        f"   📊 Found {len(result) if isinstance(result, list) else 1} results"
                    )
                except Exception as e:
                    print(f"❌ Memory recall failed: {e}")
            else:
                print("❌ No memory system available or invalid syntax")

        # Agent execution with enhanced pattern matching
        elif line.startswith("run agent"):
            match = re.match(r"run agent [\"'](.+?)[\"'] with \$(\w+)", line)
            if match and self.context.agents:
                agent_name, input_var = match.groups()
                data = self.context.variables.get(input_var)
                if data is not None:
                    try:
                        output = self.context.agents.run(agent_name, data)
                        self.context.variables["last_output"] = output
                        self.context.variables[f"{agent_name}_output"] = output
                        print(f"🤖 Agent '{agent_name}' executed with ${input_var}")
                        print(
                            f"   📤 Output stored in $last_output and ${agent_name}_output"
                        )
                    except Exception as e:
                        print(f"❌ Agent '{agent_name}' failed: {e}")
                else:
                    print(f"❌ Variable ${input_var} not found")
            else:
                print("❌ No agent system available or invalid syntax")

        # Store in memory with enhanced handling
        elif line.startswith("store"):
            match = re.match(
                r"store \$(\w+) in memory(?:\s+as\s+[\"'](.+?)[\"'])?", line
            )
            if match and self.context.memory:
                var_name = match.group(1)
                tag = match.group(2) if match.group(2) else var_name
                data = self.context.variables.get(var_name)
                if data is not None:
                    try:
                        self.context.memory.store(data, tag=tag)
                        print(f"💾 Stored ${var_name} into memory as '{tag}'")
                    except Exception as e:
                        print(f"❌ Failed to store in memory: {e}")
                else:
                    print(f"❌ Variable ${var_name} not found")
            else:
                print("❌ No memory system available or invalid syntax")

        # Variable assignment
        elif "=" in line and "$" in line:
            match = re.match(r"\$(\w+)\s*=\s*(.+)", line)
            if match:
                var_name, value = match.groups()
                # Handle string literals, numbers, and references to other variables
                if value.startswith('"') and value.endswith('"'):
                    self.context.variables[var_name] = value[1:-1]
                elif value.startswith("$"):
                    ref_var = value[1:]
                    self.context.variables[var_name] = self.context.variables.get(
                        ref_var
                    )
                else:
                    try:
                        # Try to parse as number
                        self.context.variables[var_name] = (
                            float(value) if "." in value else int(value)
                        )
                    except ValueError:
                        self.context.variables[var_name] = value
                print(f"📝 Set ${var_name} = {self.context.variables[var_name]}")

        # Show variables
        elif line == "show variables" or line == "vars":
            print("📊 Current variables:")
            for var, value in self.context.variables.items():
                print(f"   ${var} = {value}")

        # Show goals
        elif line == "show goals":
            print("🎯 Current goals:")
            for i, goal in enumerate(self.context.goals, 1):
                print(f"   {i}. {goal}")

        # Show status
        elif line == "status":
            stats = self.get_execution_stats()
            print("📊 Aether Runtime Status:")
            print(f"   🎯 Goals completed: {stats['goals_completed']}")
            print(f"   ❌ Goals failed: {stats['goals_failed']}")
            print(f"   📝 Variables set: {stats['variables_set']}")
            print(f"   🎯 Goals defined: {stats['goals_defined']}")
            print(f"   📋 Queue size: {stats['queue_size']}")

        else:
            print(f"[WARN] Unknown command: {line}")
            print(
                "   💡 Available commands: goal, use plugin, recall, run agent, store, $var=value, show variables, show goals, status"
            )

    def interpret_aether_line(self, line: str):
        """
        Interpret a single .aether line for chat integration.
        This method is called by Lyrixa's conversation engine.
        """
        if (
            line.startswith("goal")
            or "→" in line
            or line.startswith("use plugin")
            or line.startswith("run agent")
            or line.startswith("store")
        ):
            print(f"🔮 Executing .aether instruction: {line}")
            self.interpret_command(line)
            return True
        else:
            print(f"❌ Invalid .aether command: {line}")
            return False

    async def initialize(self):
        """Initialize the runtime context and ensure all components are ready."""
        print("Initializing AetherRuntime...")
        if not self.context.memory or not self.context.plugins:
            raise RuntimeError(
                "Memory or plugins are not registered in the runtime context."
            )
        await asyncio.sleep(0)  # Simulate async initialization if needed
        print("AetherRuntime initialized successfully.")

    def execute_async(
        self, command: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a command asynchronously using the executor."""
        if not hasattr(self, "executor"):
            from Aetherra.stdlib.executor import ExecutorPlugin

            self.executor = ExecutorPlugin()

        return self.executor.execute_async(command, context)
