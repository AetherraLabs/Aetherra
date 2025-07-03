#!/usr/bin/env python3
"""
🧠 NeuroCode LLM Integration Module
==================================

Extends NeuroCode interpreter with multi-LLM support.
Enables NeuroCode programs to use different AI models:

model: mistral
assistant: generate strategy for memory cleanup

model: gpt-4
assistant: analyze performance bottlenecks

model: llama2
assistant: suggest code optimizations
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _get_llm_manager():
    """Dynamically import the LLM manager to handle path setup"""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from core.multi_llm_manager import llm_manager

    return llm_manager


class NeuroCodeLLMIntegration:
    """Integrates multi-LLM support into NeuroCode interpreter"""

    def __init__(self):
        self.llm_manager = _get_llm_manager()
        self.current_model = None
        self.conversation_history = []
        self.model_preferences = {}

    def execute_model_statement(
        self, model_name: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute model: statement in NeuroCode"""
        try:
            # Apply any configuration parameters
            kwargs = config or {}

            # Set the model
            success = self.llm_manager.set_model(model_name, **kwargs)

            if success:
                self.current_model = model_name
                model_info = self.llm_manager.get_current_model_info() or {}

                return {
                    "status": "success",
                    "message": f"✅ Model set to '{model_name}'",
                    "model_info": model_info,
                    "is_local": model_info.get("is_local", False),
                    "provider": model_info.get("provider", "unknown"),
                }
            else:
                return {
                    "status": "error",
                    "message": f"❌ Failed to set model '{model_name}'",
                    "available_models": list(self.llm_manager.list_available_models().keys()),
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting model: {str(e)}",
                "available_models": list(self.llm_manager.list_available_models().keys()),
            }

    def execute_assistant_statement(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute assistant: statement in NeuroCode"""
        if not self.current_model:
            return {
                "status": "error",
                "message": "❌ No model selected. Use 'model: <model_name>' first.",
                "suggestion": "Try: model: gpt-3.5-turbo",
            }

        try:
            # Build context-aware prompt
            full_prompt = self._build_context_prompt(task, context)

            # Generate response using current model
            response = self.llm_manager.generate_response_sync(full_prompt)

            # Store in conversation history
            self.conversation_history.append(
                {
                    "model": self.current_model,
                    "task": task,
                    "response": response,
                    "timestamp": self._get_timestamp(),
                }
            )

            return {
                "status": "success",
                "response": response,
                "model_used": self.current_model,
                "task": task,
                "tokens_estimated": len(response.split()),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Assistant error: {str(e)}",
                "task": task,
                "model": self.current_model,
            }

    def _build_context_prompt(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build context-aware prompt for the LLM"""
        prompt_parts = []

        # Add system context
        prompt_parts.append(
            "You are an AI assistant integrated into NeuroCode, an AI-native programming language."
        )
        prompt_parts.append("Provide clear, actionable responses focused on the specific task.")

        # Add context if provided
        if context:
            prompt_parts.append("\nContext:")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")

        # Add conversation history (last 3 exchanges)
        if self.conversation_history:
            prompt_parts.append("\nRecent conversation:")
            for exchange in self.conversation_history[-3:]:
                prompt_parts.append(f"Task: {exchange['task']}")
                prompt_parts.append(f"Response: {exchange['response'][:100]}...")

        # Add the current task
        prompt_parts.append(f"\nCurrent task: {task}")
        prompt_parts.append("\nResponse:")

        return "\n".join(prompt_parts)

    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available models with their capabilities"""
        return self.llm_manager.list_available_models()

    def get_current_model_status(self) -> Dict[str, Any]:
        """Get status of current model"""
        if not self.current_model:
            return {
                "status": "no_model",
                "message": "No model currently selected",
                "available_models": list(self.llm_manager.list_available_models().keys()),
            }

        model_info = self.llm_manager.get_current_model_info()
        return {
            "status": "active",
            "current_model": self.current_model,
            "model_info": model_info,
            "conversation_length": len(self.conversation_history),
        }

    def switch_model_for_task(self, task_type: str) -> Optional[str]:
        """Intelligently switch models based on task type"""
        # Model preferences for different task types
        task_preferences = {
            "code": ["gpt-4", "codellama", "gpt-3.5-turbo"],
            "analysis": ["gpt-4", "claude-3-opus", "mistral"],
            "creative": ["gpt-4", "claude-3-sonnet", "mixtral"],
            "local": ["mistral", "llama2", "mixtral"],
            "fast": ["gpt-3.5-turbo", "mistral", "gemini-pro"],
            "reasoning": ["gpt-4", "claude-3-opus", "mixtral"],
        }

        available_models = self.list_available_models()
        preferred_models = task_preferences.get(task_type, ["gpt-3.5-turbo"])

        # Find first available preferred model
        for model in preferred_models:
            if model in available_models:
                result = self.execute_model_statement(model)
                if result["status"] == "success":
                    return model

        return None

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]

    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()

    def save_model_preferences(self, preferences: Dict[str, str]):
        """Save user model preferences"""
        self.model_preferences.update(preferences)

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()


# Standard library plugin for NeuroCode
class LLMPlugin:
    """NeuroCode plugin for multi-LLM support"""

    def __init__(self):
        self.name = "llm"
        self.description = "Multi-LLM integration for NeuroCode"
        self.available_actions = [
            "set_model",
            "ask_assistant",
            "list_models",
            "model_status",
            "switch_for_task",
            "conversation_history",
            "clear_history",
            "status",
        ]
        self.integration = NeuroCodeLLMIntegration()

    def execute_action(self, action: str, memory_system=None, **kwargs) -> str:
        """Execute LLM plugin action"""
        try:
            if action == "set_model":
                model_name = kwargs.get("model", "gpt-3.5-turbo")
                config = kwargs.get("config", {})
                result = self.integration.execute_model_statement(model_name, config)
                return f"Model setting: {result['message']}"

            elif action == "ask_assistant" or action == "assistant":
                task = kwargs.get("task", "Help me with NeuroCode")
                context = kwargs.get("context", {})
                result = self.integration.execute_assistant_statement(task, context)
                if result["status"] == "success":
                    return f"Assistant ({result['model_used']}): {result['response'][:200]}..."
                else:
                    return f"Assistant error: {result['message']}"

            elif action == "list_models":
                models = self.integration.list_available_models()
                model_list = [f"{name} ({info['provider']})" for name, info in models.items()]
                return f"Available models: {', '.join(model_list)}"

            elif action == "model_status":
                status = self.integration.get_current_model_status()
                if status["status"] == "active":
                    return f"Current model: {status['current_model']} ({status['model_info']['provider']})"
                else:
                    return "No model selected"

            elif action == "switch_for_task":
                task_type = kwargs.get("task_type", "general")
                model = self.integration.switch_model_for_task(task_type)
                return (
                    f"Switched to {model} for {task_type} tasks"
                    if model
                    else f"No suitable model for {task_type}"
                )

            elif action == "conversation_history":
                limit = kwargs.get("limit", 5)
                history = self.integration.get_conversation_history(limit)
                return f"Conversation history: {len(history)} recent exchanges"

            elif action == "clear_history":
                self.integration.clear_conversation_history()
                return "Conversation history cleared"

            elif action == "status":
                available_count = len(self.integration.list_available_models())
                current = self.integration.current_model or "None"
                return f"LLM Plugin: {available_count} models available, current: {current}"

            else:
                available = ", ".join(self.available_actions)
                return f"Unknown action '{action}'. Available: {available}"

        except Exception as e:
            return f"Error in llm.{action}: {str(e)}"


# Global instances for NeuroCode integration
neurocode_llm_integration = NeuroCodeLLMIntegration()
PLUGIN_CLASS = LLMPlugin
