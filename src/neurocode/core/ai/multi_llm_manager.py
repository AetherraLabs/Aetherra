#!/usr/bin/env python3
"""
🧠 NeuroCode Multi-LLM Backend Manager
=====================================

Unified LLM interface supporting multiple backends:
- OpenAI GPT models (GPT-4, GPT-3.5)
- Local models via Ollama (Mistral, LLaMA, Mixtral)
- GGUF models via llama-cpp-python
- Anthropic Claude
- Google Gemini
- Azure OpenAI

This enables NeuroCode to work with any LLM backend,
making it truly independent and privacy-focused.
"""

import asyncio
import importlib.util
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    AZURE = "azure"
    LOCAL_GGUF = "local_gguf"


@dataclass
class LLMConfig:
    """Configuration for an LLM model"""

    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_path: Optional[str] = None  # For local models
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    context_window: int = 4096
    supports_streaming: bool = True


class MultiLLMManager:
    """Manages multiple LLM backends for NeuroCode"""

    def __init__(self):
        self.providers = {}
        self.current_model = None
        self.model_configs = {}
        self.available_models = {}

        # Initialize supported providers
        self._initialize_providers()
        self._load_model_configs()

    def _initialize_providers(self):
        """Initialize all supported LLM providers"""

        # OpenAI Provider
        if importlib.util.find_spec("openai") is not None:
            self.providers[LLMProvider.OPENAI] = OpenAIProvider()
            logger.info("✅ OpenAI provider initialized")
        else:
            logger.warning("⚠️ OpenAI not available (pip install openai)")

        # Ollama Provider (for local Mistral, LLaMA, etc.)
        if importlib.util.find_spec("ollama") is not None:
            self.providers[LLMProvider.OLLAMA] = OllamaProvider()
            logger.info("✅ Ollama provider initialized")
        else:
            logger.warning("⚠️ Ollama not available (pip install ollama)")

        # llama-cpp-python Provider (for GGUF models)
        if importlib.util.find_spec("llama_cpp") is not None:
            self.providers[LLMProvider.LLAMACPP] = LlamaCppProvider()
            logger.info("✅ LlamaCpp provider initialized")
        else:
            logger.warning("⚠️ LlamaCpp not available (pip install llama-cpp-python)")

        # Anthropic Provider
        if importlib.util.find_spec("anthropic") is not None:
            self.providers[LLMProvider.ANTHROPIC] = AnthropicProvider()
            logger.info("✅ Anthropic provider initialized")
        else:
            logger.warning("⚠️ Anthropic not available (pip install anthropic)")

        # Google Gemini Provider
        if importlib.util.find_spec("google.generativeai") is not None:
            self.providers[LLMProvider.GEMINI] = GeminiProvider()
            logger.info("✅ Gemini provider initialized")
        else:
            logger.warning("⚠️ Gemini not available (pip install google-generativeai)")

    def _load_model_configs(self):
        """Load model configurations from file or defaults"""
        config_file = "llm_configs.json"

        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    configs = json.load(f)
                    for config_data in configs:
                        config = LLMConfig(**config_data)
                        self.model_configs[config.model_name] = config
                logger.info(f"✅ Loaded {len(configs)} model configurations")
            except Exception as e:
                logger.error(f"❌ Error loading model configs: {e}")

        # Add default configurations
        self._add_default_configs()

    def _add_default_configs(self):
        """Add default model configurations"""

        # OpenAI models
        if LLMProvider.OPENAI in self.providers:
            self.model_configs.update(
                {
                    "gpt-4": LLMConfig(
                        provider=LLMProvider.OPENAI,
                        model_name="gpt-4",
                        context_window=8192,
                        max_tokens=4096,
                    ),
                    "gpt-3.5-turbo": LLMConfig(
                        provider=LLMProvider.OPENAI,
                        model_name="gpt-3.5-turbo",
                        context_window=4096,
                        max_tokens=2048,
                    ),
                }
            )

        # Ollama models (local)
        if LLMProvider.OLLAMA in self.providers:
            self.model_configs.update(
                {
                    "mistral": LLMConfig(
                        provider=LLMProvider.OLLAMA,
                        model_name="mistral",
                        base_url="http://localhost:11434",
                        context_window=4096,
                    ),
                    "llama2": LLMConfig(
                        provider=LLMProvider.OLLAMA,
                        model_name="llama2",
                        base_url="http://localhost:11434",
                        context_window=4096,
                    ),
                    "mixtral": LLMConfig(
                        provider=LLMProvider.OLLAMA,
                        model_name="mixtral",
                        base_url="http://localhost:11434",
                        context_window=32768,
                    ),
                    "codellama": LLMConfig(
                        provider=LLMProvider.OLLAMA,
                        model_name="codellama",
                        base_url="http://localhost:11434",
                        context_window=4096,
                    ),
                }
            )

        # Anthropic models
        if LLMProvider.ANTHROPIC in self.providers:
            self.model_configs.update(
                {
                    "claude-3-opus": LLMConfig(
                        provider=LLMProvider.ANTHROPIC,
                        model_name="claude-3-opus-20240229",
                        context_window=200000,
                        max_tokens=4096,
                    ),
                    "claude-3-sonnet": LLMConfig(
                        provider=LLMProvider.ANTHROPIC,
                        model_name="claude-3-sonnet-20240229",
                        context_window=200000,
                        max_tokens=4096,
                    ),
                }
            )

        # Google Gemini models
        if LLMProvider.GEMINI in self.providers:
            self.model_configs.update(
                {
                    "gemini-pro": LLMConfig(
                        provider=LLMProvider.GEMINI,
                        model_name="gemini-pro",
                        context_window=30720,
                        max_tokens=2048,
                    )
                }
            )

    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available models with their capabilities"""
        models = {}

        for model_name, config in self.model_configs.items():
            if config.provider in self.providers:
                models[model_name] = {
                    "provider": config.provider.value,
                    "context_window": config.context_window,
                    "max_tokens": config.max_tokens,
                    "supports_streaming": config.supports_streaming,
                    "is_local": config.provider in [LLMProvider.OLLAMA, LLMProvider.LLAMACPP],
                    "requires_api_key": config.provider
                    in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GEMINI],
                }

        return models

    def set_model(self, model_name: str, **kwargs) -> bool:
        """Set the current model for NeuroCode"""
        if model_name not in self.model_configs:
            logger.error(f"❌ Model '{model_name}' not found in configurations")
            return False

        config = self.model_configs[model_name]

        # Update config with any provided parameters
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        # Check if provider is available
        if config.provider not in self.providers:
            logger.error(f"❌ Provider '{config.provider.value}' not available")
            return False

        # Validate model availability
        provider = self.providers[config.provider]
        if not provider.is_model_available(config):
            logger.error(f"❌ Model '{model_name}' not available")
            return False

        self.current_model = config
        logger.info(f"✅ Set current model to '{model_name}' ({config.provider.value})")
        return True

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using current model"""
        if not self.current_model:
            raise ValueError("No model selected. Use set_model() first.")

        provider = self.providers[self.current_model.provider]

        try:
            response = await provider.generate(self.current_model, prompt, **kwargs)
            return response
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            raise

    def generate_response_sync(self, prompt: str, **kwargs) -> str:
        """Synchronous wrapper for generate_response"""
        return asyncio.run(self.generate_response(prompt, **kwargs))

    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current model"""
        if not self.current_model:
            return None

        return {
            "model_name": self.current_model.model_name,
            "provider": self.current_model.provider.value,
            "context_window": self.current_model.context_window,
            "max_tokens": self.current_model.max_tokens,
            "temperature": self.current_model.temperature,
            "is_local": self.current_model.provider in [LLMProvider.OLLAMA, LLMProvider.LLAMACPP],
        }

    def save_configs(self):
        """Save current model configurations to file"""
        configs = []
        for config in self.model_configs.values():
            config_dict = {
                "provider": config.provider.value,
                "model_name": config.model_name,
                "api_key": config.api_key,
                "base_url": config.base_url,
                "model_path": config.model_path,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "timeout": config.timeout,
                "context_window": config.context_window,
                "supports_streaming": config.supports_streaming,
            }
            configs.append(config_dict)

        with open("llm_configs.json", "w") as f:
            json.dump(configs, f, indent=2)

        logger.info("✅ Model configurations saved")


# Provider Implementations


class OpenAIProvider:
    """OpenAI API provider"""

    def __init__(self):
        try:
            import openai

            self.client = openai.OpenAI()
        except ImportError as e:
            raise ImportError("OpenAI package not installed") from e

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if model is available"""
        try:
            # Simple availability check
            return config.model_name in ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
        except Exception:
            return False

    async def generate(self, config: LLMConfig, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", config.temperature),
                max_tokens=kwargs.get("max_tokens", config.max_tokens),
                timeout=config.timeout,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}") from e


class OllamaProvider:
    """Ollama local model provider"""

    def __init__(self):
        try:
            import ollama

            self.client = ollama.Client()
        except ImportError as e:
            raise ImportError("Ollama package not installed") from e

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if model is available in Ollama"""
        try:
            models = self.client.list()
            available_models = [model["name"].split(":")[0] for model in models["models"]]
            return config.model_name in available_models
        except Exception:
            return False

    async def generate(self, config: LLMConfig, prompt: str, **kwargs) -> str:
        """Generate response using Ollama"""
        try:
            response = self.client.chat(
                model=config.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": kwargs.get("temperature", config.temperature),
                    "num_predict": kwargs.get("max_tokens", config.max_tokens),
                },
            )
            return response["message"]["content"]
        except Exception as e:
            raise Exception(f"Ollama error: {e}") from e


class LlamaCppProvider:
    """llama-cpp-python provider for GGUF models"""

    def __init__(self):
        try:
            from llama_cpp import Llama

            self.Llama = Llama
        except ImportError as e:
            raise ImportError("llama-cpp-python package not installed") from e

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if GGUF model file exists"""
        if config.model_path:
            return os.path.exists(config.model_path)
        return False

    async def generate(self, config: LLMConfig, prompt: str, **kwargs) -> str:
        """Generate response using llama-cpp-python"""
        try:
            if not config.model_path:
                raise ValueError("Model path is required for LlamaCpp provider")

            llm = self.Llama(
                model_path=config.model_path, n_ctx=config.context_window, verbose=False
            )

            response = llm(
                prompt,
                max_tokens=kwargs.get("max_tokens", config.max_tokens),
                temperature=kwargs.get("temperature", config.temperature),
                stop=["</s>", "\n\n"],
            )

            # llama-cpp-python returns a dict, not an iterator
            if isinstance(response, dict):
                return response["choices"][0]["text"]
            else:
                # Handle streaming response
                return "Response received (streaming mode)"
        except Exception as e:
            raise Exception(f"LlamaCpp error: {e}") from e


class AnthropicProvider:
    """Anthropic Claude provider"""

    def __init__(self):
        try:
            import anthropic

            self.client = anthropic.Anthropic()
        except ImportError as e:
            raise ImportError("Anthropic package not installed") from e

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if Anthropic model is available"""
        return config.model_name.startswith("claude-")

    async def generate(self, config: LLMConfig, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic"""
        try:
            message = self.client.messages.create(
                model=config.model_name,
                max_tokens=kwargs.get("max_tokens", config.max_tokens),
                temperature=kwargs.get("temperature", config.temperature),
                messages=[{"role": "user", "content": prompt}],
            )
            # Safely extract text content from Anthropic response
            if message.content and len(message.content) > 0:
                content_block = message.content[0]
                # Use getattr to safely access text attribute
                return getattr(content_block, "text", str(content_block))
            return "No content received"
        except Exception as e:
            raise Exception(f"Anthropic error: {e}") from e


class GeminiProvider:
    """Google Gemini provider"""

    def __init__(self):
        try:
            import google.generativeai as genai

            self.genai = genai
        except ImportError as e:
            raise ImportError("google-generativeai package not installed") from e

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if Gemini model is available"""
        return config.model_name.startswith("gemini-")

    async def generate(self, config: LLMConfig, prompt: str, **kwargs) -> str:
        """Generate response using Gemini"""
        try:
            # Use direct attribute access for Google Generative AI
            model = getattr(self.genai, "GenerativeModel", None)
            if not model:
                raise AttributeError("GenerativeModel not available in google.generativeai")

            genai_model = model(config.model_name)

            # Create generation config safely using getattr
            generation_config = None
            types_module = getattr(self.genai, "types", None)
            if types_module:
                GenerationConfig = getattr(types_module, "GenerationConfig", None)
                if GenerationConfig:
                    generation_config = GenerationConfig(
                        temperature=kwargs.get("temperature", config.temperature),
                        max_output_tokens=kwargs.get("max_tokens", config.max_tokens),
                    )

            response = genai_model.generate_content(prompt, generation_config=generation_config)
            return response.text or "No response generated"
        except Exception as e:
            raise Exception(f"Gemini error: {e}") from e


# Global instance for NeuroCode integration
llm_manager = MultiLLMManager()

# Plugin registration for NeuroCode
PLUGIN_CLASS = None  # This is a core component, not a plugin
