import importlib
import sys

import pytest


@pytest.fixture(autouse=True)
def enable_consciousness(monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    # Reset singletons between tests if modules were imported
    for mod_name in [
        "Aetherra.consciousness.workspace_core",
        "Aetherra.consciousness.affect_engine",
        "Aetherra.consciousness.self_model",
        "Aetherra.consciousness.event_bus",
    ]:
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
    yield
