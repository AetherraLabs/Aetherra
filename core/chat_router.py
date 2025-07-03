#!/usr/bin/env python3
"""
🧬 Aetherra Chat Router
Intelligent routing system for natural language interaction with Aetherra

This system provides the conversational bridge between humans and Aetherra,
enabling natural language communication, command execution, and AI reasoning.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Import with dynamic loading to avoid relative import issues
import importlib.util
import os


def _safe_import_core_module(module_name):
    """Safely import core modules with fallback"""
    try:
        # First try direct import (when modules are in path)
        return importlib.import_module(module_name)
    except ImportError:
        try:
            # Try relative import
            return importlib.import_module(f".{module_name}", package="core")
        except ImportError:
            try:
                # Try loading from file path
                current_dir = os.path.dirname(__file__)
                module_path = os.path.join(current_dir, f"{module_name}.py")
                if os.path.exists(module_path):
                    spec = importlib.util.spec_from_file_location(
                        module_name, module_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        return module
            except Exception:
                pass
    return None


# Try to import the core modules
interpreter_module = _safe_import_core_module("aetherra_interpreter")
memory_module = _safe_import_core_module("memory")
compiler_module = _safe_import_core_module("natural_compiler")
ai_runtime_module = _safe_import_core_module("ai_runtime")
multi_agent_module = _safe_import_core_module("multi_agent_manager")

if interpreter_module:
    AetherraInterpreter = interpreter_module.AetherraInterpreter
else:

    class AetherraInterpreter:
        def execute(self, code):
            return "Demo mode - no execution"


if memory_module:
    AetherraMemory = memory_module.AetherraMemory
else:

    class AetherraMemory:
        def remember(self, *args):
            pass

        def recall(self, *args, **kwargs):
            return []


if compiler_module:
    NaturalLanguageCompiler = compiler_module.NaturalLanguageCompiler
else:

    class NaturalLanguageCompiler:
        def compile_natural_language(self, text):
            return "# Demo mode"

        def generate_aether_workflow(self, description, complexity="standard"):
            return f'# Basic workflow for: {description}\nremember "{description}"\nset_goal "Complete task"'


if ai_runtime_module:
    ask_ai = ai_runtime_module.ask_ai
else:

    def ask_ai(prompt, temperature=0.2):
        return "[AI Disabled] OPENAI_API_KEY not configured"


if multi_agent_module:
    MultiAgentManager = multi_agent_module.MultiAgentManager
else:

    class MultiAgentManager:
        def assign_task(self, description, priority=5):
            return "demo_task_id"

        def execute_task(self, task_id):
            return {"success": True, "result": "Demo execution"}

        def coordinate_multi_agent_task(self, description):
            return {"success": True, "agents_involved": ["Demo"]}

        def get_agent_status(self):
            return {"agents": {}, "pending_tasks": 0}


class AetherraChatRouter:
    """
    Intelligent router for chat-based Aetherra interaction
    """

    def __init__(self, demo_mode=False, debug_mode=False):
        self.interpreter = AetherraInterpreter()
        self.memory = AetherraMemory()
        self.compiler = NaturalLanguageCompiler()
        self.debug_mode = debug_mode
        self.command_history = []
        self.user_variables = {}
        self.multi_agent_manager = MultiAgentManager()

        # Load function definitions
        self.aether_functions = self._load_aether_functions()

    def _load_aether_functions(self):
        """Load Aetherra function definitions from JSON file."""
        try:
            functions_path = (
                Path(__file__).parent.parent / "data" / "aetherra_functions.json"
            )
            with open(functions_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return a default structure if file is missing or corrupt
            return {"functions": []}

    def route_message(
        self, user_id: str, message: str, chat_session: Optional[Dict] = None
    ) -> Dict:
        self.command_history.append(message)
        self.memory.remember(f"User '{user_id}' said: {message}")

        # 1. Intent Parsing
        intent, entities = self._parse_intent(message)

        # 2. Command Execution or AI response
        if intent == "execute_aether":
            code_to_run = entities.get("code", "")
            # Sanitize and execute the code
            result = self.execute_aether_code(code_to_run)
            return {"response": result, "type": "execution_result"}

        elif intent == "run_command":
            command_name = entities.get("command_name", "")
            params = entities.get("params", {})
            result = self.run_aether_command(command_name, params)
            return {"response": result, "type": "command_result"}

        elif intent == "generate_code":
            description = entities.get("description", message)
            code = self.compiler.generate_aether_workflow(description)
            return {"response": f"```aether\n{code}\n```", "type": "code_generation"}

        elif intent == "ask_question":
            # Use AI to answer general questions
            prompt = f"Answer the following question: {message}"
            answer = ask_ai(prompt)
            return {"response": answer, "type": "ai_response"}

        elif intent == "manage_memory":
            # Basic memory management
            return {
                "response": "Memory management features are under development.",
                "type": "info",
            }

        elif intent == "multi_agent_task":
            description = entities.get("description", message)
            result = self.multi_agent_manager.coordinate_multi_agent_task(description)
            return {
                "response": f"Multi-agent task initiated. Result: {result}",
                "type": "multi_agent_status",
            }

        else:  # Default to conversational AI
            # Fallback to a general conversational prompt
            prompt = self._create_conversational_prompt(user_id, message, chat_session)
            response = ask_ai(prompt, temperature=0.5)
            self.memory.remember(f"Aetherra responded: {response}")
            return {"response": response, "type": "ai_response"}

    def _parse_intent(self, message: str) -> Tuple[str, Dict]:
        """
        Parse user intent and extract entities from the message.
        This is a simplified rule-based parser. A real implementation might use an NLU model.
        """
        message_lower = message.lower()

        # Rule for executing Aetherra code
        # Looks for code blocks or direct commands
        aether_code_match = re.search(r"```aether\s*\n(.*?)\n```", message, re.DOTALL)
        if aether_code_match:
            return "execute_aether", {"code": aether_code_match.group(1)}
        if message_lower.startswith(("run:", "execute:")):
            return "execute_aether", {"code": message.split(":", 1)[1].strip()}

        # Rule for running a specific command
        command_match = re.match(r"\/(\w+)(?:\s+(.*))?", message)
        if command_match:
            command_name = command_match.group(1)
            params_str = command_match.group(2) or ""
            params = self._parse_params(params_str)
            return "run_command", {"command_name": command_name, "params": params}

        # Rule for code generation
        if "generate" in message_lower and (
            "code" in message_lower
            or "script" in message_lower
            or "workflow" in message_lower
        ):
            return "generate_code", {"description": message}

        # Rule for multi-agent tasks
        if "coordinate" in message_lower and "task" in message_lower:
            return "multi_agent_task", {"description": message}

        # Default to question asking
        return "ask_question", {}

    def _parse_params(self, params_str: str) -> Dict:
        params = {}
        # A simple key=value parser
        for part in params_str.split():
            if "=" in part:
                key, value = part.split("=", 1)
                params[key] = value.strip('"')
        return params

    def execute_aether_code(self, code: str) -> str:
        """
        Execute a block of Aetherra code.
        """
        if self.debug_mode:
            print(f"Executing Aetherra code:\n---\n{code}\n---")
        try:
            # Pre-process code: replace variables
            processed_code = self._replace_variables(code)
            # Execute with the interpreter
            result = self.interpreter.execute(processed_code)
            # Remember the execution
            self.memory.remember(f"Executed Aetherra code: {code}, result: {result}")
            return str(result)
        except Exception as e:
            if self.debug_mode:
                print(f"Error executing Aetherra code: {e}")
            return f"Error: {e}"

    def run_aether_command(self, command_name: str, params: Dict) -> str:
        """
        Run a registered Aetherra command.
        """
        if self.debug_mode:
            print(f"Running command: {command_name} with params: {params}")

        # Find the function definition
        command_def = next(
            (
                f
                for f in self.aether_functions.get("functions", [])
                if f["name"] == command_name
            ),
            None,
        )

        if not command_def:
            return f"Unknown command: '{command_name}'"

        # Check for required parameters
        required_params = command_def.get("parameters", {}).get("required", [])
        if not all(p in params for p in required_params):
            return f"Missing required parameters for '{command_name}'. Required: {', '.join(required_params)}"

        # Construct the Aetherra code to execute the command
        param_str = ", ".join([f'"{k}": "{v}"' for k, v in params.items()])
        code = f"{command_name}({param_str})"

        return self.execute_aether_code(code)

    def _create_conversational_prompt(
        self, user_id: str, message: str, chat_session: Optional[Dict]
    ) -> str:
        """
        Create a rich prompt for the conversational AI.
        """
        # Basic prompt
        prompt = "You are Lyrixa Assistant, a helpful AI assistant for the Aetherra platform."
        prompt += f" You are chatting with user '{user_id}'.\n\n"

        # Add conversation history (simplified)
        if chat_session and "history" in chat_session:
            for entry in chat_session["history"][-5:]:  # last 5 entries
                prompt += f"{entry['sender']}: {entry['message']}\n"

        # Add recent memories
        recent_memories = self.memory.recall(
            f"memory related to user {user_id}", limit=3
        )
        if recent_memories:
            prompt += "\nRecent context:\n"
            for mem in recent_memories:
                prompt += f"- {mem}\n"

        # Add current user message
        prompt += f"\nUser '{user_id}': {message}\n"
        prompt += "Aetherra: "
        return prompt

    def _replace_variables(self, code: str) -> str:
        # Simple variable replacement (e.g., $variable)
        for var_name, value in self.user_variables.items():
            code = code.replace(f"${var_name}", str(value))
        return code


# Example Usage
if __name__ == "__main__":
    print("Starting Aetherra Chat Router...")
    # Initialize with debug mode on for detailed output
    router = AetherraChatRouter(debug_mode=True)

    # --- Example Interactions ---

    # 1. Simple greeting - should be handled by conversational AI
    print("\n--- 1. Conversational AI ---")
    response = router.route_message("user123", "Hello, who are you?")
    print(f"Response: {response['response']} (Type: {response['type']})")

    # 2. Aetherra code execution
    print("\n--- 2. Aetherra Code Execution ---")
    aether_code = 'print("Hello from Aetherra!")'
    response = router.route_message("user123", f"run: {aether_code}")
    print(f"Response: {response['response']} (Type: {response['type']})")

    # 3. Code generation
    print("\n--- 3. Code Generation ---")
    response = router.route_message(
        "user123", "generate a script to read a file and print its content"
    )
    print(f"Response: {response['response']} (Type: {response['type']})")

    # 4. Running a command (assuming 'file_read' is defined in aetherra_functions.json)
    print("\n--- 4. Running a Command ---")
    response = router.route_message("user123", '/file_read path="/path/to/file.txt"')
    print(f"Response: {response['response']} (Type: {response['type']})")

    # 5. Multi-agent task
    print("\n--- 5. Multi-Agent Task ---")
    response = router.route_message(
        "user123", "coordinate a task to analyze user sentiment from last week's logs"
    )
    print(f"Response: {response['response']} (Type: {response['type']})")

    # 6. Storing and using a variable
    print("\n--- 6. Using Variables ---")
    router.user_variables["username"] = "Alice"
    response = router.route_message("user123", 'run: print("User: $username")')
    print(f"Response: {response['response']} (Type: {response['type']})")

    print("\n--- Aetherra Chat Router Demo Complete ---")
