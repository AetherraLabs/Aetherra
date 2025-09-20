# Standard library imports
import sys
import types

# Aetherra imports
from aetherra_hub.app import create_app


class DummyRegistry:
    def __init__(self):
        self.unregistered: list[str] = []

    async def unregister_service(self, name: str):
        self.unregistered.append(name)


def _install_dummy_registry(monkeypatch, dummy: DummyRegistry):
    mod = types.ModuleType("aetherra_service_registry")

    async def get_service_registry():  # noqa: D401
        return dummy

    mod.get_service_registry = get_service_registry  # type: ignore[attr-defined]
    # Replace any pre-imported real module first
    monkeypatch.setitem(sys.modules, "aetherra_service_registry", mod)


def test_reset_engine_on_start(monkeypatch):
    monkeypatch.setenv("AETHERRA_HUB_RESET_ENGINE_ON_START", "1")
    dummy = DummyRegistry()
    _install_dummy_registry(monkeypatch, dummy)
    # Minimize unrelated init noise
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "0")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "0")
    create_app()
    assert "aetherra_engine" in dummy.unregistered


def test_test_reset_engine(monkeypatch):
    monkeypatch.setenv("AETHERRA_TEST_RESET_ENGINE", "1")
    dummy = DummyRegistry()
    _install_dummy_registry(monkeypatch, dummy)
    create_app()
    assert "aetherra_engine" in dummy.unregistered
