import os
import sys
import types

import tools.run_hub_ai_api as script

class _DummyServer:
    def __init__(self, port):
        self.port = port
        self.started = False
    def start_server(self):
        self.started = True
        return True

class _DummyCompat(types.SimpleNamespace):
    pass


def test_main_sets_env_and_starts(monkeypatch):
    # Replace AetherraHubServer with dummy to avoid real network bind
    dummy_mod = _DummyCompat(AetherraHubServer=_DummyServer)
    monkeypatch.setitem(sys.modules, "aetherra_hub.compat", dummy_mod)
    argv_backup = list(sys.argv)
    sys.argv = ["run_hub_ai_api.py", "--port", "3111", "--require-token", "--token", "SECRET"]
    # Cause main loop to exit after first sleep attempt
    def _raise_keyboard_interrupt(_):  # noqa: D401
        raise KeyboardInterrupt

    monkeypatch.setattr(script.time, "sleep", _raise_keyboard_interrupt)
    try:
        rc = script.main()
        assert isinstance(rc, int)
        assert os.environ.get("AETHERRA_AI_API_ENABLED") == "1"
        assert os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN") == "1"
        assert os.environ.get("AETHERRA_AI_API_TOKEN") == "SECRET"
    finally:
        sys.argv = argv_backup
