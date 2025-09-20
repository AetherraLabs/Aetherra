# Standard library imports
import sys
import types
from typing import Any


def test_run_hub_ai_api_main_flags(monkeypatch: Any) -> None:
    # Create a fake AetherraHubServer in import path
    class FakeServer:
        def __init__(self, port: int) -> None:
            self.port = port

        def start_server(self) -> bool:
            return True

    # Inject fake module and class into aetherra_hub.compat via sys.modules
    fake_mod = types.SimpleNamespace(AetherraHubServer=FakeServer)
    monkeypatch.setitem(sys.modules, "aetherra_hub.compat", fake_mod)

    # Standard library imports
    import importlib

    mod = importlib.import_module("tools.run_hub_ai_api")

    # Replace asyncio.run path to skip actual register_service calls
    # Standard library imports
    import asyncio

    monkeypatch.setattr(asyncio, "run", lambda coro: None)  # type: ignore

    # Prevent infinite sleep loop by making time.sleep raise KeyboardInterrupt once
    # Standard library imports
    import time as _time

    def _sleep_raises(_: float) -> None:
        raise KeyboardInterrupt()

    monkeypatch.setattr(_time, "sleep", _sleep_raises)

    # Run with explicit token requirement and token
    rc = mod.main(["--port", "3012", "--require-token", "--token", "ABC123"])
    assert rc == 0
    # Environment flags should be set accordingly
    # Standard library imports
    import os

    assert os.environ.get("AETHERRA_AI_API_ENABLED") == "1"
    assert os.environ.get("AETHERRA_AI_API_STREAM") == "1"
    assert os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN") == "1"
    assert os.environ.get("AETHERRA_AI_API_TOKEN") == "ABC123"
