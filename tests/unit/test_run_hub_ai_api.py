import sys
import types
from typing import Any


def test_run_hub_ai_api_main_flags(monkeypatch: Any) -> None:
    class FakeApp:
        def run(self, **_: Any) -> None:
            return None

    fake_app_mod = types.SimpleNamespace(create_app=lambda: FakeApp())
    monkeypatch.setitem(sys.modules, "aetherra_hub.app", fake_app_mod)

    # Standard library imports
    import importlib

    mod = importlib.import_module("tools.run_hub_ai_api")

    # Replace asyncio.run path to skip actual register_service calls
    # Standard library imports
    import asyncio

    def _close_coro(coro: Any) -> None:
        coro.close()

    monkeypatch.setattr(asyncio, "run", _close_coro)

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
