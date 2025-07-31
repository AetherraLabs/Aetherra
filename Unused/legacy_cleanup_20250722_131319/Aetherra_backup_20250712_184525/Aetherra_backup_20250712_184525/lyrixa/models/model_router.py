"""
Model Router for Lyrixa
=======================

Dynamic routing between OpenAI, local models, and other LLM providers.
"""

from typing import Any, Dict, Optional

from .local_model import LocalModel
from .openai_model import OpenAIModel


class ModelRouter:
    """Routes requests between different model providers"""

    def __init__(self):
        self.models = {}
        self.default_model = "openai"
        self.fallback_model = "local"

        # Initialize available models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize available model providers"""
        try:
            self.models["openai"] = OpenAIModel()
        except Exception:
            pass

        try:
            self.models["local"] = LocalModel()
        except Exception:
            pass

    def add_model(self, name: str, model_instance: Any):
        """Add a custom model provider"""
        self.models[name] = model_instance

    def set_default_model(self, model_name: str):
        """Set the default model to use"""
        if model_name in self.models:
            self.default_model = model_name
        else:
            raise ValueError(f"Model '{model_name}' not available")

    def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate response using specified or default model"""

        # Use specified model or default
        model_name = model or self.default_model

        # Try primary model
        if model_name in self.models:
            try:
                return self.models[model_name].generate_response(
                    prompt, context, system_prompt, **kwargs
                )
            except Exception as e:
                print(f"Error with {model_name}: {e}")

        # Try fallback model if primary fails
        if self.fallback_model in self.models and model_name != self.fallback_model:
            try:
                return self.models[self.fallback_model].generate_response(
                    prompt, context, system_prompt, **kwargs
                )
            except Exception as e:
                print(f"Error with fallback {self.fallback_model}: {e}")

        # Final fallback
        return "Error: No available models could process the request"

    def get_available_models(self) -> Dict[str, bool]:
        """Get list of available models and their status"""
        status = {}

        for name, model in self.models.items():
            try:
                if hasattr(model, "is_available"):
                    status[name] = model.is_available()
                else:
                    # Assume available if no check method
                    status[name] = True
            except Exception:
                status[name] = False

        return status

    def route_by_task(self, task_type: str) -> str:
        """Route to best model based on task type"""

        task_routing = {
            "code_generation": "openai",  # GPT-4 is good at code
            "conversation": "local",  # Local models for chat
            "analysis": "openai",  # GPT-4 for analysis
            "creative": "local",  # Local models for creativity
            "technical": "openai",  # GPT-4 for technical tasks
        }

        preferred_model = task_routing.get(task_type, self.default_model)

        # Check if preferred model is available
        available_models = self.get_available_models()
        if available_models.get(preferred_model, False):
            return preferred_model

        # Return any available model
        for model_name, is_available in available_models.items():
            if is_available:
                return model_name

        return self.default_model

    def generate_code(self, description: str, language: str = "aether") -> str:
        """Generate code using best available model for code generation"""
        best_model = self.route_by_task("code_generation")

        if best_model in self.models:
            return self.models[best_model].generate_code(description, language)

        return f"# Error: No model available for code generation\n# {description}"


# Global router instance
router = ModelRouter()
