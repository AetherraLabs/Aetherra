#!/usr/bin/env python3
"""
🧬 NeuroCode Enhanced Engine with Multi-LLM Support
==================================================

Complete NeuroCode execution engine that integrates the formal grammar
parser with multi-LLM support, enabling true syntax-native execution
of model and assistant statements.

Example NeuroCode with LLM integration:
    model: mistral
    assistant: generate strategy for memory cleanup

    model: gpt-4
    assistant: analyze performance bottlenecks

    model: llama2
    assistant: suggest code optimizations
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Import core components
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.aethercode_grammar import NeuroCodeAST, create_neurocode_parser
from core.llm_integration import aetherra_llm_integration
from core.multi_llm_manager import llm_manager


class NeuroCodeEngine:
    """Enhanced NeuroCode execution engine with multi-LLM support"""

    def __init__(self):
        self.parser = create_neurocode_parser()
        self.llm_integration = neurocode_llm_integration
        self.llm_manager = llm_manager
        self.variables = {}
        self.functions = {}
        self.execution_context = {
            "current_model": None,
            "conversation_history": [],
            "memory": {},
            "goals": [],
            "agents": {},
        }

        # Initialize available models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize and discover available LLM models"""
        try:
            available_models = self.llm_manager.list_available_models()
            print(
                f"🧠 Initialized NeuroCode Engine with {len(available_models)} LLM models"
            )

            # Set default model if available
            if "gpt-3.5-turbo" in available_models:
                self.llm_manager.set_model("gpt-3.5-turbo")
                self.execution_context["current_model"] = "gpt-3.5-turbo"
                print("✅ Default model set to gpt-3.5-turbo")
            elif available_models:
                # Use first available model as default
                first_model = list(available_models.keys())[0]
                self.llm_manager.set_model(first_model)
                self.execution_context["current_model"] = first_model
                print(f"✅ Default model set to {first_model}")
            else:
                print(
                    "⚠️ No LLM models available - model/assistant statements will not work"
                )

        except Exception as e:
            print(f"⚠️ Error initializing models: {e}")

    def execute_neurocode_file(self, file_path: str) -> Dict[str, Any]:
        """Execute a .aether file and return results"""
        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()

            return self.execute_neurocode(code)

        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"File not found: {file_path}",
                "file": file_path,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error reading file: {str(e)}",
                "file": file_path,
            }

    def execute_neurocode(self, code: str) -> Dict[str, Any]:
        """Parse and execute NeuroCode source code"""
        try:
            # Parse the code into AST
            result = self.parser.validate_syntax(code)

            if not result["valid"]:
                return {
                    "status": "parse_error",
                    "message": "Failed to parse NeuroCode",
                    "errors": result.get("errors", []),
                    "code": code,
                }

            ast = result["ast"]
            execution_results = []

            # Execute each statement in the AST
            for statement in ast.children:
                if statement:  # Skip None statements
                    stmt_result = self._execute_statement(statement)
                    execution_results.append(stmt_result)

            return {
                "status": "success",
                "results": execution_results,
                "context": self.execution_context.copy(),
            }

        except Exception as e:
            return {
                "status": "execution_error",
                "message": f"Error executing NeuroCode: {str(e)}",
                "code": code,
            }

    def _execute_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute a single NeuroCode statement"""
        try:
            if statement.type == "model":
                return self._execute_model_statement(statement)
            elif statement.type == "assistant":
                return self._execute_assistant_statement(statement)
            elif statement.type == "goal":
                return self._execute_goal_statement(statement)
            elif statement.type == "agent":
                return self._execute_agent_statement(statement)
            elif statement.type == "remember":
                return self._execute_remember_statement(statement)
            elif statement.type == "recall":
                return self._execute_recall_statement(statement)
            elif statement.type == "assignment":
                return self._execute_assignment(statement)
            elif statement.type == "if":
                return self._execute_if_statement(statement)
            elif statement.type == "for":
                return self._execute_for_statement(statement)
            elif statement.type == "function":
                return self._execute_function_definition(statement)
            elif statement.type == "comment":
                return {"type": "comment", "message": f"Comment: {statement.value}"}
            else:
                return {
                    "type": statement.type,
                    "status": "info",
                    "message": f"Executed {statement.type}: {statement.value}",
                }

        except Exception as e:
            return {
                "type": statement.type,
                "status": "error",
                "message": f"Error executing {statement.type}: {str(e)}",
            }

    def _execute_model_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute model: statement to switch LLM models"""
        model_name = statement.value
        config = statement.metadata.get("config", {}) if statement.metadata else {}

        # Use LLM integration to switch models
        result = self.llm_integration.execute_model_statement(model_name, config)

        if result["status"] == "success":
            self.execution_context["current_model"] = model_name
            return {
                "type": "model",
                "status": "success",
                "message": f"✅ Switched to model: {model_name}",
                "model": model_name,
                "provider": result.get("provider", "unknown"),
                "is_local": result.get("is_local", False),
            }
        else:
            return {
                "type": "model",
                "status": "error",
                "message": result["message"],
                "available_models": result.get("available_models", []),
            }

    def _execute_assistant_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute assistant: statement to interact with AI"""
        task = statement.value

        # Build context from current execution environment
        context = {
            "variables": self.variables,
            "current_model": self.execution_context.get("current_model"),
            "memory_entries": len(self.execution_context.get("memory", {})),
            "goals": len(self.execution_context.get("goals", [])),
        }

        # Use LLM integration to execute assistant task
        result = self.llm_integration.execute_assistant_statement(task, context)

        if result["status"] == "success":
            # Store in conversation history
            self.execution_context["conversation_history"].append(
                {
                    "task": task,
                    "response": result["response"],
                    "model": result["model_used"],
                    "timestamp": self._get_timestamp(),
                }
            )

            return {
                "type": "assistant",
                "status": "success",
                "message": f"🤖 Assistant ({result['model_used']}): {result['response']}",
                "task": task,
                "response": result["response"],
                "model": result["model_used"],
            }
        else:
            return {
                "type": "assistant",
                "status": "error",
                "message": result["message"],
                "task": task,
            }

    def _execute_goal_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute goal: statement"""
        goal = statement.value
        priority = (
            statement.metadata.get("priority", "medium")
            if statement.metadata
            else "medium"
        )

        self.execution_context["goals"].append(
            {"goal": goal, "priority": priority, "timestamp": self._get_timestamp()}
        )

        return {
            "type": "goal",
            "status": "success",
            "message": f"🎯 Goal set: {goal} (priority: {priority})",
            "goal": goal,
            "priority": priority,
        }

    def _execute_agent_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute agent: statement"""
        agent_command = statement.value

        if agent_command in ["on", "off"]:
            self.execution_context["agents"]["default"] = agent_command
            return {
                "type": "agent",
                "status": "success",
                "message": f"🤖 Agent {agent_command}",
                "agent_status": agent_command,
            }
        else:
            # Store agent command/task
            self.execution_context["agents"]["default"] = {
                "status": "on",
                "command": agent_command,
            }
            return {
                "type": "agent",
                "status": "success",
                "message": f"🤖 Agent task: {agent_command}",
                "command": agent_command,
            }

    def _execute_remember_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute remember statement"""
        content = statement.value
        tag = (
            statement.metadata.get("tag", "default")
            if statement.metadata
            else "default"
        )

        self.execution_context["memory"][tag] = {
            "content": content,
            "timestamp": self._get_timestamp(),
        }

        return {
            "type": "remember",
            "status": "success",
            "message": f"💾 Remembered: {content} (tag: {tag})",
            "content": content,
            "tag": tag,
        }

    def _execute_recall_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute recall statement"""
        tag = statement.value

        if tag in self.execution_context["memory"]:
            memory = self.execution_context["memory"][tag]
            return {
                "type": "recall",
                "status": "success",
                "message": f"🔍 Recalled: {memory['content']}",
                "content": memory["content"],
                "tag": tag,
            }
        else:
            return {
                "type": "recall",
                "status": "error",
                "message": f"❌ Memory not found for tag: {tag}",
                "tag": tag,
            }

    def _execute_assignment(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute variable assignment"""
        var_name = statement.value
        value = statement.children[0].value if statement.children else None

        self.variables[var_name] = value

        return {
            "type": "assignment",
            "status": "success",
            "message": f"📝 {var_name} = {value}",
            "variable": var_name,
            "value": value,
        }

    def _execute_if_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute if statement (basic implementation)"""
        condition = statement.value
        # This is a simplified implementation - real condition evaluation would be more complex
        return {
            "type": "if",
            "status": "info",
            "message": f"🔀 If condition: {condition}",
            "condition": condition,
        }

    def _execute_for_statement(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute for statement (basic implementation)"""
        return {
            "type": "for",
            "status": "info",
            "message": f"🔄 For loop: {statement.value}",
            "loop": statement.value,
        }

    def _execute_function_definition(self, statement: NeuroCodeAST) -> Dict[str, Any]:
        """Execute function definition"""
        func_name = statement.value
        params = statement.metadata.get("parameters", []) if statement.metadata else []

        self.functions[func_name] = {
            "parameters": params,
            "body": statement.children,
            "timestamp": self._get_timestamp(),
        }

        return {
            "type": "function",
            "status": "success",
            "message": f"⚙️ Function defined: {func_name}({', '.join(params)})",
            "function": func_name,
            "parameters": params,
        }

    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available LLM models"""
        return self.llm_manager.list_available_models()

    def get_current_model(self) -> Optional[str]:
        """Get current model name"""
        return self.execution_context.get("current_model")

    def get_execution_context(self) -> Dict[str, Any]:
        """Get current execution context"""
        return self.execution_context.copy()

    def clear_context(self):
        """Clear execution context"""
        self.variables.clear()
        self.functions.clear()
        self.execution_context = {
            "current_model": self.execution_context.get("current_model"),
            "conversation_history": [],
            "memory": {},
            "goals": [],
            "agents": {},
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()


# Global instance for NeuroCode integration
neurocode_engine = NeuroCodeEngine()


# Example usage and testing
def demo_multi_llm_neurocode():
    """Demonstrate multi-LLM NeuroCode execution"""
    print("🧬 NeuroCode Multi-LLM Demo")
    print("=" * 50)

    engine = NeuroCodeEngine()

    # Example NeuroCode with multiple models
    demo_code = """
# Set a goal for optimization
goal: improve system performance priority: high

# Switch to Mistral for local processing
model: mistral
assistant: analyze current system bottlenecks

# Switch to GPT-4 for complex reasoning
model: gpt-4
assistant: generate optimization strategy

# Remember the results
remember("optimization analysis complete") as "performance"

# Set agent to monitor
agent: on
"""

    print("NeuroCode:")
    print(demo_code)
    print("=" * 50)

    result = engine.execute_neurocode(demo_code)

    if result["status"] == "success":
        print("✅ Execution Results:")
        for i, stmt_result in enumerate(result["results"], 1):
            print(f"{i}. {stmt_result.get('message', stmt_result)}")

        print(
            f"\n📊 Context: {len(engine.variables)} vars, "
            f"{len(engine.functions)} functions, "
            f"Current model: {engine.get_current_model()}"
        )
    else:
        print(f"❌ Execution failed: {result['message']}")


if __name__ == "__main__":
    demo_multi_llm_neurocode()
