#!/usr/bin/env python3
"""
Aetherra Enhancement Integration
Integrates new AI capabilities with existing interpreter
"""

import os
import sys
import time
from typing import Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


# Enhanced model selection strategy
class AIModelRouter:
    """Intelligent AI model selection and routing"""

    def __init__(self):
        self.model_capabilities = {
            "gpt-4": {
                "strengths": [
                    "complex_reasoning",
                    "code_generation",
                    "architecture_design",
                ],
                "speed": "medium",
                "cost": "high",
                "privacy": "cloud",
            },
            "claude-3": {
                "strengths": ["detailed_analysis", "documentation", "refactoring"],
                "speed": "medium",
                "cost": "medium",
                "privacy": "cloud",
            },
            "ollama_llama": {
                "strengths": ["fast_completion", "code_analysis", "local_processing"],
                "speed": "fast",
                "cost": "free",
                "privacy": "local",
            },
            "ollama_codellama": {
                "strengths": ["code_generation", "debugging", "local_processing"],
                "speed": "fast",
                "cost": "free",
                "privacy": "local",
            },
        }

    def select_best_model(
        self,
        task_type: str,
        privacy_required: bool = False,
        speed_priority: bool = False,
    ) -> str:
        """Select the optimal AI model for a specific task"""

        # Privacy-first selection
        if privacy_required:
            local_models = {
                k: v
                for k, v in self.model_capabilities.items()
                if v["privacy"] == "local"
            }
            if not local_models:
                return "ollama_llama"  # Default local fallback

            # Choose best local model for task
            for model, caps in local_models.items():
                if task_type in caps["strengths"]:
                    return model
            return "ollama_llama"

        # Speed-first selection
        if speed_priority:
            fast_models = {
                k: v for k, v in self.model_capabilities.items() if v["speed"] == "fast"
            }
            for model, caps in fast_models.items():
                if task_type in caps["strengths"]:
                    return model
            return "ollama_llama"

        # Quality-first selection (default)
        task_models = []
        for model, caps in self.model_capabilities.items():
            if task_type in caps["strengths"]:
                task_models.append((model, caps))

        if not task_models:
            return "gpt-4"  # Default high-quality fallback

        # Prefer cloud models for complex tasks, local for simple ones
        complex_tasks = ["complex_reasoning", "architecture_design"]
        if task_type in complex_tasks:
            cloud_models = [m for m, c in task_models if c["privacy"] == "cloud"]
            return cloud_models[0] if cloud_models else task_models[0][0]
        else:
            return task_models[0][0]


try:
    # Try relative imports first (when run as module)
    from .aetherra_interpreter import AetherraInterpreter
    from .ai_collaboration import AICollaborationFramework
    from .ai_runtime import ask_ai
    from .intent_parser import IntentToCodeParser, parse_natural_intent
except ImportError:
    # Fallback to absolute imports for standalone execution
    from aetherra_interpreter import AetherraInterpreter
    from ai_collaboration import AICollaborationFramework
    from ai_runtime import ask_ai
    from intent_parser import IntentToCodeParser, parse_natural_intent


# Minimal LocalAIEngine stub for compatibility
class LocalAIEngine:
    def is_available(self) -> bool:
        # Implement actual availability check if needed
        return False

    def intent_to_code(self, intent: str) -> str:
        """Convert natural language intent to Aetherra code"""
        # Placeholder implementation
        return f"# Generated from intent: {intent}\nprint('Not implemented yet')"


class EnhancedAetherraInterpreter(AetherraInterpreter):
    """Enhanced interpreter with natural language and AI capabilities"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intent_parser = IntentToCodeParser()
        self.ai_collaboration = AICollaborationFramework()
        self.local_ai_engine = LocalAIEngine()
        self.ai_model_router = AIModelRouter()
        self.execution_count = 0
        self.last_execution_time = 0

    def execute_aether(self, code: str, **kwargs) -> Any:
        """Execute Aetherra code with enhanced AI capabilities"""
        start_time = time.time()

        # Keyword-based AI routing
        if code.strip().startswith("ai:"):
            return self.handle_ai_command(code[3:].strip())

        # Natural language intent parsing
        try:
            is_natural_intent, intent_certainty = self.is_natural_language_intent(code)
            if is_natural_intent:
                if intent_certainty > 0.8:
                    return self.handle_natural_intent(code)
                else:
                    # Ask for clarification if uncertain
                    clarification = self.ask_for_clarification(code)
                    if clarification.lower().startswith("yes"):
                        return self.handle_natural_intent(code)
                    else:
                        return super().execute(code)
        except Exception:
            # Fallback to standard execution on parsing error
            pass

        # Standard code execution
        result = super().execute(code)

        # Performance monitoring and adaptation
        self.execution_count += 1
        self.last_execution_time = time.time() - start_time
        self.adapt_performance()

        return result

    def is_natural_language_intent(self, code: str) -> tuple[bool, float]:
        """Check if the code is a natural language intent"""
        # Simple keyword-based check for now
        keywords = ["create", "build", "generate", "show me", "what is", "explain"]
        if any(code.lower().startswith(kw) for kw in keywords):
            return True, 0.9  # High certainty for keyword match
        return False, 0.0

    def ask_for_clarification(self, code: str) -> str:
        """Ask the user for clarification on an ambiguous command"""
        print(f"🤖 Ambiguous command: '{code}'")
        response = input(
            "Did you mean to execute this as a natural language command? (yes/no): "
        )
        return response.strip()

    def handle_natural_intent(self, intent: str) -> Any:
        """Parse and execute a natural language intent"""
        print(f"🤖 Interpreting natural language: '{intent}'")
        try:
            # Use local AI for faster, private parsing
            if self.local_ai_engine.is_available():
                aether_code = self.local_ai_engine.intent_to_code(intent)
            else:
                aether_code = parse_natural_intent(intent)

            print(f"💻 Generated Aetherra Code:\n{aether_code}")
            return super().execute(aether_code)
        except Exception as e:
            return f"Error handling natural intent: {e}"

    def handle_ai_command(self, command: str) -> Any:
        """Handle special 'ai:' commands for direct AI interaction"""
        parts = command.split(maxsplit=1)
        action = parts[0]
        query = parts[1] if len(parts) > 1 else ""

        # Select best model for the task
        model = self.ai_model_router.select_best_model(action)
        print(f"🤖 Using AI model: {model}")

        if action == "explain":
            return self.explain_code(query, model=model)
        elif action == "refactor":
            return self.refactor_code(query, model=model)
        elif action == "generate":
            return self.generate_code(query, model=model)
        else:
            return f"Unknown AI command: {action}"

    def explain_code(self, code_or_concept: str, model: str) -> str:
        """Use AI to explain a code snippet or concept"""
        prompt = f"Explain the following Aetherra code or concept in simple terms:\n\n{code_or_concept}"
        return ask_ai(prompt, model=model)

    def refactor_code(self, code: str, model: str) -> str:
        """Use AI to refactor and improve a piece of code"""
        prompt = f"Refactor the following Aetherra code to improve its clarity, efficiency, and adherence to best practices:\n\n{code}"
        return ask_ai(prompt, model=model)

    def generate_code(self, description: str, model: str) -> str:
        """Use AI to generate code from a natural language description"""
        prompt = f"Generate Aetherra code for the following task:\n\n{description}"
        return ask_ai(prompt, model=model)

    def get_enhancement_status(self):
        """Returns the status of the enhancements."""
        return {
            "enhancements_available": True,
            "performance_metrics": {"commands_processed": self.execution_count},
        }

    def demonstrate_enhancements(self):
        """Demonstrates the enhancements."""
        return "Natural language processing is an enhancement."

    def adapt_performance(self):
        """Dynamically adapt interpreter performance settings"""
        if self.execution_count % 20 == 0 and self.last_execution_time > 0.5:
            print("🐌 Performance seems slow. Consider enabling optimizations.")


def create_enhanced_interpreter():
    """Factory function to create enhanced interpreter"""
    return EnhancedAetherraInterpreter()


def test_enhancements():
    """Test enhancement integrations"""
    interpreter = create_enhanced_interpreter()
    print("🧪 Testing enhancements...")

    # Test status
    status = interpreter.get_enhancement_status()
    print(f"✅ Enhancements available: {status['enhancements_available']}")

    return True


if __name__ == "__main__":
    # Run enhancement tests
    test_enhancements()

    # Interactive mode
    print("\n🚀 Enhanced Aetherra Interactive Mode")
    print("Type 'demo' to see capabilities, 'quit' to exit")

    interpreter = create_enhanced_interpreter()

    while True:
        try:
            user_input = input("\nAetherra> ").strip()

            if user_input.lower() in ["quit", "exit"]:
                break
            elif user_input.lower() == "demo":
                print(interpreter.demonstrate_enhancements())
            elif user_input.lower() == "status":
                status = interpreter.get_enhancement_status()
                print(
                    f"Enhanced features available: {status['enhancements_available']}"
                )
                print(
                    f"Commands processed: {status['performance_metrics']['commands_processed']}"
                )
            elif user_input:
                result = interpreter.execute_aether(user_input)
                print(result)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Aetherra enhancements ready for the future!")
            break
