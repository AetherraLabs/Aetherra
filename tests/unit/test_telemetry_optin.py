# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Aetherra imports
from Aetherra.telemetry.optin import Telemetry


def test_telemetry_respects_env_and_file(tmp_path, monkeypatch):
    # Use a temp config dir
    tmp_conf_dir = tmp_path / ".aetherra"
    monkeypatch.setattr("Aetherra.telemetry.optin.APP_DIR", tmp_conf_dir)
    monkeypatch.setattr(
        "Aetherra.telemetry.optin.CONF_FILE", tmp_conf_dir / "telemetry.json"
    )

    # default disabled
    t = Telemetry(endpoint="http://localhost:0")
    assert t.enabled is False

    # env overrides
    monkeypatch.setenv("AETHERRA_TELEMETRY", "1")
    t2 = Telemetry(endpoint="http://localhost:0")
    assert t2.enabled is True

    # file-based opt-in
    monkeypatch.delenv("AETHERRA_TELEMETRY", raising=False)
    t3 = Telemetry(endpoint="http://localhost:0")
    t3.set_opt_in(True)
    t4 = Telemetry(endpoint="http://localhost:0")
    assert t4.enabled is True


def test_telemetry_emit_filters_sensitive_fields(monkeypatch, tmp_path):
    # Temp conf
    tmp_conf_dir = tmp_path / ".aetherra"
    monkeypatch.setattr("Aetherra.telemetry.optin.APP_DIR", tmp_conf_dir)
    monkeypatch.setattr(
        "Aetherra.telemetry.optin.CONF_FILE", tmp_conf_dir / "telemetry.json"
    )

    # Enable
    t = Telemetry(endpoint="http://localhost:1")
    t.set_opt_in(True)

    # Mock requests
    class R:
        status_code = 200

    calls = {}

    def fake_post(url, json=None, timeout=2):
        calls["payload"] = json
        return R()

    monkeypatch.setenv("AETHERRA_TELEMETRY", "1")
    monkeypatch.setattr(
        "Aetherra.telemetry.optin.requests",
        type("Req", (), {"post": staticmethod(fake_post)}),
    )

    ok = t.emit("unit_test", {"content": "secret", "safe": 1, "prompt": "x"})
    assert ok is True
    assert "content" not in calls["payload"]["props"]
    assert "prompt" not in calls["payload"]["props"]
    assert calls["payload"]["props"]["safe"] == 1
