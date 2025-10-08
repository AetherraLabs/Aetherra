#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 AetherraCode Multi-LLM Backend Manager
=====================================

Unified LLM interface supporting multiple backends:
- OpenAI GPT models (gpt-4o, GPT-3.5)
- Local models via Ollama (Mistral, LLaMA, Mixtral)
- GGUF models via llama-cpp-python
- Anthropic Claude
- Google Gemini
- Azure OpenAI

This enables AetherraCode to work with any LLM backend,
making it truly independent and privacy-focused.
"""

# Standard library imports
import asyncio
import importlib
import importlib.util
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, cast

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
    """Manages multiple LLM backends for AetherraCode"""

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
        try:
            if importlib.util.find_spec("google.generativeai") is not None:
                self.providers[LLMProvider.GEMINI] = GeminiProvider()
                logger.info("✅ Gemini provider initialized")
            else:
                logger.warning("⚠️ Gemini not available (pip install google-generativeai)")
        except (ImportError, ModuleNotFoundError):
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
                    "gpt-4o": LLMConfig(
                        provider=LLMProvider.OPENAI,
                        model_name="gpt-4o",
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
            # Check what models are actually available locally
            try:
                # Third party imports
                import ollama

                client = ollama.Client()
                available_models_response = client.list()
                installed_models = [
                    model.model for model in available_models_response.models if model.model
                ]
                logger.info(f"🦙 Found Ollama models: {installed_models}")

                # Add configurations for actually installed models
                ollama_configs = {}

                # Configure mistral models
                mistral_models = [m for m in installed_models if m and "mistral" in m]
                if mistral_models:
                    ollama_configs["mistral"] = LLMConfig(
                        provider=LLMProvider.OLLAMA,
                        model_name=mistral_models[0],
                        base_url="http://localhost:11434",
                        context_window=4096,
                    )

                # Configure llama3 models
                llama3_models = [m for m in installed_models if m and "llama3" in m]
                if llama3_models:
                    # Prefer llama3:latest if available, otherwise use first llama3 model
                    llama3_latest = [m for m in llama3_models if m == "llama3:latest"]
                    llama3_model = llama3_latest[0] if llama3_latest else llama3_models[0]

                    ollama_configs["llama3"] = LLMConfig(
                        provider=LLMProvider.OLLAMA,
                        model_name=llama3_model,
                        base_url="http://localhost:11434",
                        context_window=8192,
                    )

                    # Also add llama3.2 if the 3b model is available
                    llama32_models = [m for m in installed_models if m and "llama3.2" in m]
                    if llama32_models:
                        ollama_configs["llama3.2"] = LLMConfig(
                            provider=LLMProvider.OLLAMA,
                            model_name=llama32_models[0],
                            base_url="http://localhost:11434",
                            context_window=8192,
                        )

                # Add other common models if found
                for model_full_name in installed_models:
                    if model_full_name:  # Ensure model name is not None/empty
                        model_base = model_full_name.split(":")[0]
                        if (
                            model_base not in ["mistral", "llama3"]
                            and model_base not in ollama_configs
                        ):
                            ollama_configs[model_base] = LLMConfig(
                                provider=LLMProvider.OLLAMA,
                                model_name=model_full_name,
                                base_url="http://localhost:11434",
                                context_window=4096,
                            )

                self.model_configs.update(ollama_configs)
                logger.info(f"✅ Configured {len(ollama_configs)} Ollama models")

            except Exception as e:
                logger.warning(f"⚠️ Could not detect Ollama models dynamically: {e}")
                # Fallback to default configurations
                self.model_configs.update(
                    {
                        "mistral": LLMConfig(
                            provider=LLMProvider.OLLAMA,
                            model_name="mistral:latest",
                            base_url="http://localhost:11434",
                            context_window=4096,
                        ),
                        "llama3": LLMConfig(
                            provider=LLMProvider.OLLAMA,
                            model_name="llama3:latest",
                            base_url="http://localhost:11434",
                            context_window=8192,
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
        models: Dict[str, Dict[str, Any]] = {}

        # Always expose a meta "auto" option so UIs can offer it in dropdowns
        models["auto"] = {
            "provider": "auto",
            "description": "Automatically choose the best available model",
            "is_auto": True,
            "supports_streaming": True,
        }

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
        """Set the current model for AetherraCode"""
        # Support a meta-option for automatic selection
        if model_name is None or model_name.strip().lower() in {"", "auto", "default"}:
            auto_model = self._select_auto_model()
            if not auto_model:
                logger.error("❌ No suitable model available for auto selection")
                return False
            logger.info(f"🔄 Auto-selected model: {auto_model}")
            model_name = auto_model

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

    def _select_auto_model(self) -> Optional[str]:
        """Choose the best available model based on provider availability and API keys.

        Selection priorities:
        1) OpenAI gpt-4o (if OpenAI provider loaded and OPENAI_API_KEY present)
        2) OpenAI gpt-3.5-turbo (same conditions)
        3) Anthropic claude-3-sonnet (ANTHROPIC_API_KEY present)
        4) Gemini gemini-pro (GOOGLE_API_KEY present)
        5) Local Ollama models (llama3 first, then mistral)
        6) Any other available configured model
        """
        try:
            import os
        except Exception:
            os = None  # type: ignore

        def has_env(key: str) -> bool:
            return bool(os and os.getenv(key))

        # Helper to check configuration and provider availability
        def is_available(name: str) -> bool:
            cfg = self.model_configs.get(name)
            if not cfg:
                return False
            provider = self.providers.get(cfg.provider)
            if not provider:
                return False
            # Ensure a strict bool for type checkers
            return bool(provider.is_model_available(cfg))

        # 1–2) OpenAI
        if has_env("OPENAI_API_KEY"):
            if "gpt-4o" in self.model_configs and is_available("gpt-4o"):
                return "gpt-4o"
            if "gpt-3.5-turbo" in self.model_configs and is_available("gpt-3.5-turbo"):
                return "gpt-3.5-turbo"

        # 3) Anthropic
        if (
            has_env("ANTHROPIC_API_KEY")
            and "claude-3-sonnet" in self.model_configs
            and is_available("claude-3-sonnet")
        ):
            return "claude-3-sonnet"

        # 4) Gemini
        if (
            has_env("GOOGLE_API_KEY")
            and "gemini-pro" in self.model_configs
            and is_available("gemini-pro")
        ):
            return "gemini-pro"

        # 5) Local Ollama (llama3 preferred, then mistral) if provider present and model available
        for local_name in ("llama3", "mistral"):
            if local_name in self.model_configs and is_available(local_name):
                return local_name

        # 6) Fallback to first available configured model
        for name, cfg in self.model_configs.items():
            provider = self.providers.get(cfg.provider)
            if provider and provider.is_model_available(cfg):
                # Keys are strings by definition; cast for static analyzers
                return cast(str, name)

        return None

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using current model"""
        if not self.current_model:
            raise ValueError("No model selected. Use set_model() first.")

        provider = self.providers[self.current_model.provider]

        try:
            response = await provider.generate(self.current_model, prompt, **kwargs)
            return str(response)
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
            # Third party imports
            import openai

            self.client = openai.OpenAI()
        except ImportError as e:
            raise ImportError("OpenAI package not installed") from e

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if model is available"""
        try:
            # Simple availability check
            return config.model_name in ["gpt-4o", "gpt-3.5-turbo", "gpt-4o-turbo"]
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
            # Third party imports
            import ollama

            self.client = ollama.Client()
        except ImportError as e:
            raise ImportError("Ollama package not installed") from e

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if model is available in Ollama"""
        try:
            models_response = self.client.list()
            available_models = [model.model for model in models_response.models if model.model]

            # Check exact match first
            if config.model_name in available_models:
                return True

            # Check base name match (e.g., "mistral" matches "mistral:latest")
            base_name = config.model_name.split(":")[0]
            return any(model.split(":")[0] == base_name for model in available_models)
        except Exception as e:
            logger.warning(f"⚠️ Error checking Ollama model availability: {e}")
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
            return cast(str, response["message"]["content"])
        except Exception as e:
            raise Exception(f"Ollama error: {e}") from e


class LlamaCppProvider:
    """llama-cpp-python provider for GGUF models"""

    def __init__(self):
        try:
            # Import lazily via importlib to avoid hard import errors in environments
            # without llama-cpp installed.
            module_name = "llama_cpp"
            if importlib.util.find_spec(module_name) is None:
                raise ImportError("llama-cpp-python package not installed")
            module = importlib.import_module(module_name)
            if not hasattr(module, "Llama"):
                raise ImportError("llama-cpp module missing Llama attribute")
            self.Llama = module.Llama
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
                return cast(str, response["choices"][0]["text"])
            else:
                # Handle streaming response
                return "Response received (streaming mode)"
        except Exception as e:
            raise Exception(f"LlamaCpp error: {e}") from e


class AnthropicProvider:
    """Anthropic Claude provider"""

    def __init__(self):
        try:
            # Third party imports
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
            # Third party imports
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


# Global instance for AetherraCode integration
# Instantiate on import so other modules can use it directly
llm_manager: MultiLLMManager = MultiLLMManager()

# Plugin registration for AetherraCode
PLUGIN_CLASS = None  # This is a core component, not a plugin
