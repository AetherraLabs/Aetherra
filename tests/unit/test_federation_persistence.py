# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import json

import pytest

fed_mod = pytest.importorskip("Aetherra.hub.federation")


def test_federation_persists_peers(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERRA_FEDERATION_STATE", "1")
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path))

    mgr = fed_mod.FederationManager(self_url="http://localhost:3999")
    mgr.add_peer("http://peer1:3001")
    mgr.add_peer("http://peer2:3001")

    state_file = tmp_path / "hub_state.json"
    assert state_file.exists()
    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert sorted(data.get("peers", [])) == ["http://peer1:3001", "http://peer2:3001"]

    # Recreate manager and ensure peers are loaded back
    mgr2 = fed_mod.FederationManager(self_url="http://localhost:3999")
    monkeypatch.setenv("AETHERRA_FEDERATION_STATE", "1")
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path))

    peers = {p["url"] for p in mgr2.list_peers()}
    assert "http://peer1:3001" in peers and "http://peer2:3001" in peers
