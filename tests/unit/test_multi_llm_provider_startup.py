import logging
from functools import partial
from types import SimpleNamespace

import pytest

from Aetherra.core import multi_llm_manager as module


@pytest.fixture
def provider_factories(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        module.MultiLLMManager, "_load_model_configs", lambda self: None
    )
    monkeypatch.setattr(module, "_llm_manager_instance", None)
    modules = {"openai", "ollama", "llama_cpp", "anthropic", "google.generativeai"}
    available = set()
    monkeypatch.setattr(
        module.importlib.util,
        "find_spec",
        lambda name: SimpleNamespace() if name in available else None,
    )
    created = {}
    for provider, name in [
        (module.LLMProvider.OPENAI, "OpenAIProvider"),
        (module.LLMProvider.OLLAMA, "OllamaProvider"),
        (module.LLMProvider.LLAMACPP, "LlamaCppProvider"),
        (module.LLMProvider.ANTHROPIC, "AnthropicProvider"),
        (module.LLMProvider.GEMINI, "GeminiProvider"),
    ]:

        def construct(provider=provider):
            created[provider] = object()
            return created[provider]

        monkeypatch.setattr(module, name, construct)
    return available, created, modules


@pytest.fixture
def startup(provider_factories, monkeypatch):
    manager_type = module.MultiLLMManager
    monkeypatch.setattr(
        module,
        "MultiLLMManager",
        partial(
            manager_type,
            enabled_providers=(
                module.LLMProvider.OPENAI,
                module.LLMProvider.OLLAMA,
                module.LLMProvider.LLAMACPP,
                module.LLMProvider.ANTHROPIC,
                module.LLMProvider.GEMINI,
            ),
        ),
    )
    return provider_factories


def test_default_starts_only_openai_without_discovering_disabled_sdks(
    provider_factories, monkeypatch
):
    available, created, modules = provider_factories
    available.update(modules)
    checked = []
    original = module.importlib.util.find_spec

    def discover(name):
        checked.append(name)
        return original(name)

    monkeypatch.setattr(module.importlib.util, "find_spec", discover)
    manager = module.MultiLLMManager()
    assert set(manager.providers) == {module.LLMProvider.OPENAI}
    assert set(created) == {module.LLMProvider.OPENAI}
    assert checked == ["openai"]
    assert manager.provider_diagnostics["anthropic"] == {
        "status": "disabled",
        "code": "provider_disabled",
    }


def test_missing_openai_does_not_activate_other_installed_providers(provider_factories):
    available, created, modules = provider_factories
    available.update(modules - {"openai"})
    with pytest.raises(module.LLMProvidersUnavailableError):
        module.get_llm_manager()
    assert not created
    assert module._llm_manager_instance is None


def test_disabled_model_configurations_are_not_loaded_or_selected(
    provider_factories, monkeypatch, tmp_path
):
    available, _, _ = provider_factories
    available.add("openai")
    manager = module.MultiLLMManager()
    (tmp_path / "llm_configs.json").write_text(
        '[{"provider":"anthropic","model_name":"disabled"},{"provider":"openai","model_name":"approved"}]',
        encoding="utf-8",
    )
    # Invoke the actual loader, which the startup-only fixture otherwise isolates.
    assert hasattr(manager, "enabled_providers"), "provider boundary missing"
    loader = _original_model_loader
    loader(manager)
    assert "disabled" not in manager.model_configs
    assert manager.model_configs["approved"].provider is module.LLMProvider.OPENAI
    assert "disabled" not in manager.list_available_models()
    assert not manager.set_model("disabled")


_original_model_loader = module.MultiLLMManager._load_model_configs


def test_auto_selection_does_not_fall_back_across_enabled_providers(
    startup, monkeypatch
):
    available, _, modules = startup
    available.update(modules)
    manager = module.MultiLLMManager()
    manager.model_configs = {
        "gpt-4o": module.LLMConfig(module.LLMProvider.OPENAI, "gpt-4o"),
        "other": module.LLMConfig(module.LLMProvider.ANTHROPIC, "claude-example"),
    }
    checked = []

    def unavailable(config):
        checked.append("openai")
        return False

    def available_other(config):
        checked.append("anthropic")
        return True

    manager.providers[module.LLMProvider.OPENAI] = SimpleNamespace(
        is_model_available=unavailable
    )
    manager.providers[module.LLMProvider.ANTHROPIC] = SimpleNamespace(
        is_model_available=available_other
    )
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-not-a-credential")
    assert manager._select_auto_model() is None
    assert "anthropic" not in checked
    assert manager.current_model is None


@pytest.mark.asyncio
async def test_generation_rejects_disabled_provider_even_if_registry_is_modified(
    provider_factories,
):
    available, _, _ = provider_factories
    available.add("openai")
    manager = module.MultiLLMManager()
    calls = []

    async def generate(*args, **kwargs):
        calls.append(True)
        return "unexpected"

    manager.providers[module.LLMProvider.ANTHROPIC] = SimpleNamespace(generate=generate)
    manager.current_model = module.LLMConfig(
        module.LLMProvider.ANTHROPIC, "claude-example"
    )
    with pytest.raises(RuntimeError, match="llm_provider_disabled"):
        await manager.generate_response("synthetic input")
    assert not calls


def test_model_keyword_cannot_switch_provider(provider_factories):
    available, _, _ = provider_factories
    available.add("openai")
    manager = module.MultiLLMManager()
    config = module.LLMConfig(module.LLMProvider.OPENAI, "gpt-4o")
    manager.model_configs = {"gpt-4o": config}
    assert not manager.set_model("gpt-4o", provider=module.LLMProvider.ANTHROPIC)
    assert config.provider is module.LLMProvider.OPENAI


def test_mutated_registry_cannot_expose_or_select_disabled_models(provider_factories):
    available, _, _ = provider_factories
    available.add("openai")
    manager = module.MultiLLMManager()
    calls = []
    manager.model_configs["other"] = module.LLMConfig(
        module.LLMProvider.ANTHROPIC, "claude-example"
    )
    manager.providers[module.LLMProvider.ANTHROPIC] = SimpleNamespace(
        is_model_available=lambda config: calls.append(True) or True,
    )
    assert "other" not in manager.list_available_models()
    assert not manager.set_model("other")
    assert not calls


def test_provider_boundary_properties_are_read_only(provider_factories):
    available, _, _ = provider_factories
    available.add("openai")
    manager = module.MultiLLMManager()
    assert manager.enabled_providers == frozenset({module.LLMProvider.OPENAI})
    assert manager.primary_provider is module.LLMProvider.OPENAI
    with pytest.raises(AttributeError):
        manager.enabled_providers = frozenset({module.LLMProvider.ANTHROPIC})
    with pytest.raises(AttributeError):
        manager.primary_provider = module.LLMProvider.ANTHROPIC


@pytest.mark.asyncio
async def test_generation_failure_does_not_change_provider(startup):
    available, _, modules = startup
    available.update(modules)
    manager = module.MultiLLMManager()
    counts = {"openai": 0, "anthropic": 0}

    async def failed(*args, **kwargs):
        counts["openai"] += 1
        raise RuntimeError("synthetic_provider_failure")

    async def unexpected(*args, **kwargs):
        counts["anthropic"] += 1
        return "unexpected"

    manager.providers[module.LLMProvider.OPENAI] = SimpleNamespace(generate=failed)
    manager.providers[module.LLMProvider.ANTHROPIC] = SimpleNamespace(
        generate=unexpected
    )
    selected = module.LLMConfig(module.LLMProvider.OPENAI, "gpt-4o")
    manager.current_model = selected
    with pytest.raises(RuntimeError, match="synthetic_provider_failure"):
        await manager.generate_response("synthetic input")
    assert counts == {"openai": 1, "anthropic": 0}
    assert manager.current_model is selected


@pytest.mark.parametrize(
    "providers",
    [
        (),
        ("openai",),
        (module.LLMProvider.AZURE,),
        (module.LLMProvider.OPENAI, module.LLMProvider.OPENAI),
    ],
    ids=["empty", "string", "unsupported", "duplicate"],
)
def test_invalid_enabled_provider_configuration_fails_closed(
    provider_factories, providers
):
    with pytest.raises(ValueError, match="llm_enabled_providers_invalid"):
        module.MultiLLMManager(enabled_providers=providers)


def test_one_provider_failure_does_not_abort_other_backends(
    startup, monkeypatch, caplog
):
    available, created, modules = startup
    available.update(modules)

    def failed():
        raise RuntimeError("private-startup-marker token=fixture-only")

    monkeypatch.setattr(module, "OpenAIProvider", failed)
    caplog.set_level(logging.DEBUG, logger=module.__name__)
    manager = module.MultiLLMManager()
    assert module.LLMProvider.OPENAI not in manager.providers
    assert len(manager.providers) == 4
    assert (
        manager.providers[module.LLMProvider.OLLAMA]
        is created[module.LLMProvider.OLLAMA]
    )
    assert manager.provider_diagnostics["openai"] == {
        "status": "failed",
        "code": "provider_initialization_failed",
    }
    assert "private-startup-marker" not in caplog.text
    assert "fixture-only" not in caplog.text


def test_missing_packages_remain_unavailable_without_hiding_working_backend(startup):
    available, created, _ = startup
    available.add("ollama")
    manager = module.MultiLLMManager()
    assert set(manager.providers) == {module.LLMProvider.OLLAMA}
    assert (
        manager.providers[module.LLMProvider.OLLAMA]
        is created[module.LLMProvider.OLLAMA]
    )
    assert manager.provider_diagnostics["ollama"] == {
        "status": "available",
        "code": "initialized",
    }
    assert manager.provider_diagnostics["openai"] == {
        "status": "unavailable",
        "code": "dependency_unavailable",
    }


def test_missing_namespace_does_not_abort_other_providers(startup, monkeypatch):
    available, _, _ = startup
    available.add("ollama")
    original = module.importlib.util.find_spec

    def find_spec(name):
        if name == "google.generativeai":
            raise ModuleNotFoundError("controlled_missing_namespace")
        return original(name)

    monkeypatch.setattr(module.importlib.util, "find_spec", find_spec)
    manager = module.MultiLLMManager()
    assert module.LLMProvider.OLLAMA in manager.providers
    assert manager.provider_diagnostics["gemini"]["status"] == "unavailable"


@pytest.mark.parametrize("installed", [False, True])
def test_no_working_backend_is_explicitly_unavailable_and_not_cached(
    startup, monkeypatch, installed
):
    available, _, modules = startup
    if installed:
        available.update(modules)

        def failed():
            raise RuntimeError("private-startup-marker")

        for name in (
            "OpenAIProvider",
            "OllamaProvider",
            "LlamaCppProvider",
            "AnthropicProvider",
            "GeminiProvider",
        ):
            monkeypatch.setattr(module, name, failed)
    with pytest.raises(RuntimeError, match="^llm_providers_unavailable$"):
        module.get_llm_manager()
    assert module._llm_manager_instance is None


def test_failed_startup_can_retry_when_backend_becomes_available(startup):
    available, _, _ = startup
    with pytest.raises(RuntimeError, match="^llm_providers_unavailable$"):
        module.get_llm_manager()
    available.add("ollama")
    manager = module.get_llm_manager()
    assert module.LLMProvider.OLLAMA in manager.providers
    assert module.get_llm_manager() is manager






def test_proxy_retries_after_failed_initialization(startup, monkeypatch):
    available, _, _ = startup
    proxy = module._LLMManagerProxy()
    monkeypatch.setattr(proxy, "_cached", None)
    with pytest.raises(RuntimeError, match="^llm_providers_unavailable$"):
        _ = proxy.providers
    assert proxy._cached is None
    available.add("ollama")
    assert set(proxy.providers) == {module.LLMProvider.OLLAMA}
    assert proxy._cached is module.get_llm_manager()


def test_unexpected_discovery_failure_is_isolated(startup, monkeypatch):
    available, _, _ = startup
    available.add("ollama")
    original = module.importlib.util.find_spec

    def find_spec(name):
        if name == "openai":
            raise ValueError("private-discovery-marker")
        return original(name)

    monkeypatch.setattr(module.importlib.util, "find_spec", find_spec)
    manager = module.MultiLLMManager()
    assert module.LLMProvider.OLLAMA in manager.providers
    assert manager.provider_diagnostics["openai"]["status"] == "failed"
