# Standard library imports
import asyncio
import os
import sys
import types
from typing import Any

# Aetherra imports
import tools.run_hub_ai_api as script


class _DummyApp:
    def run(self, **_: Any) -> None:
        return None


def _close_coro(coro: Any) -> None:
    coro.close()


def test_main_sets_env_and_starts(monkeypatch):
    dummy_mod = types.SimpleNamespace(create_app=lambda: _DummyApp())
    monkeypatch.setitem(sys.modules, "aetherra_hub.app", dummy_mod)
    monkeypatch.setattr(asyncio, "run", _close_coro)

    rc = script.main(["--port", "3111", "--require-token", "--token", "SECRET"])
    assert isinstance(rc, int)
    assert os.environ.get("AETHERRA_AI_API_ENABLED") == "1"
    assert os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN") == "1"
    assert os.environ.get("AETHERRA_AI_API_TOKEN") == "SECRET"
