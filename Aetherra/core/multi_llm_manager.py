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
import math
import os
import threading
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Any, Dict, Optional, cast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_OPENAI_CLEANUP_TIMEOUT_SECONDS = 5.0


def _cleanup_timeout(timeout: float) -> float:
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, int | float)
        or not math.isfinite(timeout)
        or timeout < 0
    ):
        raise ValueError("llm_cleanup_timeout_invalid")
    return float(timeout)


@dataclass
class _OpenAIRequest:
    client: Any
    loop: asyncio.AbstractEventLoop
    cleanup: asyncio.Task[None] | None = None
    unresolved: bool = False
    error_code: str = ""


class LLMProvider(Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    AZURE = "azure"
    LOCAL_GGUF = "local_gguf"


class LLMProvidersUnavailableError(RuntimeError):
    """No supported backend could be initialized."""


class LLMProviderDisabledError(RuntimeError):
    """The requested provider is outside this manager's configured boundary."""


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
    """Manage explicitly enabled backends, defaulting to OpenAI-only Alpha."""

    def __init__(self, *, enabled_providers: tuple[LLMProvider, ...] = (LLMProvider.OPENAI,)):
        supported = frozenset(
            {
                LLMProvider.OPENAI,
                LLMProvider.OLLAMA,
                LLMProvider.LLAMACPP,
                LLMProvider.ANTHROPIC,
                LLMProvider.GEMINI,
            }
        )
        if (
            not isinstance(enabled_providers, tuple)
            or not enabled_providers
            or not all(
                isinstance(provider, LLMProvider) and provider in supported
                for provider in enabled_providers
            )
            or len(set(enabled_providers)) != len(enabled_providers)
        ):
            raise ValueError("llm_enabled_providers_invalid")
        self._enabled_providers = frozenset(enabled_providers)
        self._primary_provider = enabled_providers[0]
        self.providers = {}
        self.current_model = None
        self.model_configs = {}
        self.available_models = {}
        self.provider_diagnostics: dict[str, dict[str, str]] = {}

        # Initialize supported providers
        self._initialize_providers()
        self._load_model_configs()

    @property
    def enabled_providers(self) -> frozenset[LLMProvider]:
        return self._enabled_providers

    @property
    def primary_provider(self) -> LLMProvider:
        return self._primary_provider

    def _provider_enabled(self, provider: Any) -> bool:
        return isinstance(provider, LLMProvider) and provider in self.enabled_providers

    def _initialize_providers(self):
        """Initialize backends independently and retain sanitized startup outcomes."""
        backends = (
            (LLMProvider.OPENAI, "openai", OpenAIProvider),
            (LLMProvider.OLLAMA, "ollama", OllamaProvider),
            (LLMProvider.LLAMACPP, "llama_cpp", LlamaCppProvider),
            (LLMProvider.ANTHROPIC, "anthropic", AnthropicProvider),
            (LLMProvider.GEMINI, "google.generativeai", GeminiProvider),
        )
        for provider, module_name, factory in backends:
            if not self._provider_enabled(provider):
                self.provider_diagnostics[provider.value] = {
                    "status": "disabled",
                    "code": "provider_disabled",
                }
                continue
            try:
                try:
                    present = importlib.util.find_spec(module_name) is not None
                except (ImportError, ModuleNotFoundError):
                    present = False
                if not present:
                    self.provider_diagnostics[provider.value] = {
                        "status": "unavailable",
                        "code": "dependency_unavailable",
                    }
                    logger.info("LLM provider dependency unavailable: %s", provider.value)
                    continue
                instance = factory()
            except Exception:
                self.provider_diagnostics[provider.value] = {
                    "status": "failed",
                    "code": "provider_initialization_failed",
                }
                logger.warning("LLM provider initialization failed: %s", provider.value)
                continue
            self.providers[provider] = instance
            self.provider_diagnostics[provider.value] = {
                "status": "available",
                "code": "initialized",
            }
            logger.info("LLM provider initialized: %s", provider.value)
        if not self.providers:
            raise LLMProvidersUnavailableError("llm_providers_unavailable")

    def _load_model_configs(self):
        """Load model configurations from file or defaults"""
        config_file = "llm_configs.json"

        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    configs = json.load(f)
                    if not isinstance(configs, list):
                        raise ValueError("llm_model_configuration_invalid")
                    for config_data in configs:
                        entry = dict(config_data)
                        entry["provider"] = LLMProvider(entry["provider"])
                        if not self._provider_enabled(entry["provider"]):
                            continue
                        config = LLMConfig(**entry)
                        if not isinstance(config.model_name, str) or not config.model_name.strip():
                            raise ValueError("llm_model_configuration_invalid")
                        self.model_configs[config.model_name] = config
                logger.info(f"✅ Loaded {len(configs)} model configurations")
            except Exception:
                logger.error("LLM model configuration invalid")

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
            if self._provider_enabled(config.provider) and config.provider in self.providers:
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

        if not self._provider_enabled(config.provider):
            return False
        if "provider" in kwargs and kwargs["provider"] != config.provider:
            return False

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
        """Select within the configured primary provider, never across providers."""
        provider = self.providers.get(self.primary_provider)
        if provider is None:
            return None
        preferred = (
            ("gpt-4o", "gpt-3.5-turbo") if self.primary_provider is LLMProvider.OPENAI else ()
        )
        names = dict.fromkeys((*preferred, *self.model_configs))
        for name in names:
            config = self.model_configs.get(name)
            if (
                config is not None
                and config.provider is self.primary_provider
                and provider.is_model_available(config)
            ):
                return name
        return None

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using current model"""
        if not self.current_model:
            raise ValueError("No model selected. Use set_model() first.")

        if not self._provider_enabled(self.current_model.provider):
            raise LLMProviderDisabledError("llm_provider_disabled")

        provider = self.providers[self.current_model.provider]

        try:
            response = await provider.generate(self.current_model, prompt, **kwargs)
            return str(response)
        except Exception:
            logger.error("LLM generation failed")
            raise

    def generate_response_sync(self, prompt: str, **kwargs) -> str:
        """Synchronous wrapper for generate_response"""
        return asyncio.run(self.generate_response(prompt, **kwargs))

    def get_lifecycle_status(self) -> dict[str, Any]:
        active = unresolved = 0
        degraded = False
        for name, provider in self.providers.items():
            getter = getattr(provider, "get_lifecycle_status", None)
            if not self._provider_enabled(name) or not callable(getter):
                continue
            status = getter()
            active += status["active_request_count"]
            unresolved += status["unresolved_cleanup_count"]
            degraded = degraded or status["status"] == "degraded"
        result = {
            "status": "degraded" if degraded else "available",
            "active_request_count": active,
            "unresolved_cleanup_count": unresolved,
        }
        if degraded:
            result["error"] = {"code": "llm_cleanup_unconfirmed"}
        return result

    async def drain_pending_cleanup(self, timeout: float = 5.0) -> bool:
        deadline = asyncio.get_running_loop().time() + _cleanup_timeout(timeout)
        confirmed = True
        for name, provider in self.providers.items():
            drain = getattr(provider, "drain_pending_cleanup", None)
            if self._provider_enabled(name) and callable(drain):
                receipt = await drain(
                    timeout=max(0.0, deadline - asyncio.get_running_loop().time())
                )
                confirmed = (receipt is True) and confirmed
        return confirmed

    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current model"""
        if not self.current_model:
            return None
        if not self._provider_enabled(self.current_model.provider):
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
            importlib.import_module("openai")
            from Aetherra.security.sdk_egress import SdkOwner, create_guarded_async_openai

            self._client_factory = partial(create_guarded_async_openai, SdkOwner.CORE_LLM)
        except ImportError:
            raise ImportError("OpenAI package not installed") from None
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None or not api_key.strip():
            raise RuntimeError("openai_credentials_unavailable")
        base_url = os.environ.get("OPENAI_BASE_URL")
        if base_url is None:
            base_url = "https://api.openai.com/v1"
        elif not base_url.strip():
            raise RuntimeError("openai_endpoint_invalid")
        self._client_options = {
            "api_key": api_key,
            "base_url": base_url,
        }
        for option, variable in (
            ("organization", "OPENAI_ORG_ID"),
            ("project", "OPENAI_PROJECT_ID"),
        ):
            value = os.environ.get(variable)
            if value is not None:
                self._client_options[option] = value
        self._requests: dict[int, _OpenAIRequest] = {}
        self._request_lock = threading.Lock()

    def _finish_cleanup(self, record: _OpenAIRequest, task: asyncio.Task[None]) -> None:
        confirmed = not task.cancelled() and task.exception() is None
        with self._request_lock:
            if confirmed:
                self._requests.pop(id(record), None)
            else:
                record.unresolved = True
                record.error_code = "openai_cleanup_failed"

    def _records(self) -> list[_OpenAIRequest]:
        with self._request_lock:
            records = list(self._requests.values())
        for record in records:
            if record.cleanup is not None and record.cleanup.done():
                self._finish_cleanup(record, record.cleanup)
        with self._request_lock:
            return list(self._requests.values())

    def get_lifecycle_status(self) -> dict[str, Any]:
        records = self._records()
        from Aetherra.security.sdk_egress import SdkOwner, get_sdk_egress_status

        egress = get_sdk_egress_status(SdkOwner.CORE_LLM)
        with self._request_lock:
            unresolved = sum(record.unresolved for record in records)
            active = sum(record.cleanup is None for record in records)
        result = {
            "status": "degraded" if unresolved or egress["status"] == "degraded" else "available",
            "active_request_count": active,
            "unresolved_cleanup_count": unresolved,
            "egress": egress,
        }
        if result["status"] == "degraded":
            result["error"] = {"code": "openai_cleanup_unconfirmed"}
        return result

    async def drain_pending_cleanup(self, timeout: float = 5.0) -> bool:
        budget = _cleanup_timeout(timeout)
        loop = asyncio.get_running_loop()
        records = self._records()
        tasks = {
            record.cleanup
            for record in records
            if record.loop is loop and record.cleanup is not None and not record.cleanup.done()
        }
        if tasks and budget:
            await asyncio.wait(tasks, timeout=budget)
        return (not self._records()
                and self.get_lifecycle_status()["status"] == "available")

    async def _close_client(self, client: Any) -> None:
        await client.close()
        if client.is_closed() is not True:
            raise RuntimeError("openai_cleanup_unconfirmed")

    async def _close_request(self, record: _OpenAIRequest, cancelled: bool) -> None:
        task = asyncio.create_task(self._close_client(record.client))
        with self._request_lock:
            record.cleanup = task
        task.add_done_callback(lambda done: self._finish_cleanup(record, done))
        deadline = record.loop.time() + _OPENAI_CLEANUP_TIMEOUT_SECONDS
        # Cancelling asyncio.wait does not cancel the retained close task.
        while not task.done() and record.loop.time() < deadline:
            try:
                await asyncio.wait({task}, timeout=max(0.0, deadline - record.loop.time()))
            except asyncio.CancelledError:
                cancelled = True
        if task.done():
            self._finish_cleanup(record, task)
        else:
            with self._request_lock:
                record.unresolved = True
                record.error_code = "openai_cleanup_unconfirmed"
        if cancelled:
            raise asyncio.CancelledError
        if record.unresolved:
            raise RuntimeError(record.error_code)

    def is_model_available(self, config: LLMConfig) -> bool:
        """Check if model is available"""
        try:
            # Simple availability check
            return config.model_name in ["gpt-4o", "gpt-3.5-turbo", "gpt-4o-turbo"]
        except Exception:
            return False

    async def generate(self, config: LLMConfig, prompt: str, **kwargs) -> str:
        """Generate with a client owned by this invocation's event loop."""
        if self.get_lifecycle_status()["status"] == "degraded":
            raise RuntimeError("openai_cleanup_unconfirmed")
        try:
            client = await self._client_factory(**self._client_options)
        except Exception:
            raise RuntimeError("openai_client_unavailable") from None
        record = _OpenAIRequest(client, asyncio.get_running_loop())
        with self._request_lock:
            self._requests[id(record)] = record
        cancelled = False
        try:
            try:
                response = await client.chat.completions.create(
                    model=config.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get("temperature", config.temperature),
                    max_tokens=kwargs.get("max_tokens", config.max_tokens),
                    timeout=config.timeout,
                )
            except Exception:
                raise RuntimeError("openai_generation_failed") from None
            try:
                text = response.choices[0].message.content
            except Exception:
                raise RuntimeError("openai_response_invalid") from None
            if not isinstance(text, str) or not text.strip():
                raise RuntimeError("openai_response_invalid")
            return text
        except asyncio.CancelledError:
            cancelled = True
            raise
        finally:
            await self._close_request(record, cancelled)


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


# Singleton instance (lazy initialization to prevent eager import-time initialization)
_llm_manager_instance: MultiLLMManager | None = None


def get_llm_manager() -> MultiLLMManager:
    """Get or create the singleton MultiLLMManager instance."""
    global _llm_manager_instance
    if _llm_manager_instance is None:
        _llm_manager_instance = MultiLLMManager()
    return _llm_manager_instance


# Backwards compatibility: lazy property that calls get_llm_manager()
# This allows existing code using `llm_manager` to continue working
class _LLMManagerProxy:
    """Lazy proxy for backwards compatibility with code expecting llm_manager global."""

    _cached: MultiLLMManager | None = None

    def __getattr__(self, name: str) -> Any:
        if self._cached is None:
            self._cached = get_llm_manager()
        return getattr(self._cached, name)


llm_manager = _LLMManagerProxy()  # type: ignore[assignment]

# Plugin registration for AetherraCode
PLUGIN_CLASS = None  # This is a core component, not a plugin
