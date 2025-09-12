# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import socket
from pathlib import Path

import pytest

requests = pytest.importorskip("requests")

import aetherra_hub.compat as hub_mod

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class DenyEngine:
    async def process_message(self, msg: str, ctx: dict | None = None):
        # Return a simple ok; we want preflight to deny before engine is used
        return {"ok": True, "reply": "ok"}


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _register_engine(engine):
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", engine)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_security_ledger_disabled_no_file_created(tmp_path, monkeypatch):
    # Enable API and set safety to strict so preflight denies risky text
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    monkeypatch.setenv("AETHERRA_CHAT_SAFETY_MODE", "strict")

    # Disable ledger and point path to temp
    monkeypatch.setenv("AETHERRA_SECURITY_LEDGER", "0")
    ledger_path = tmp_path / "security_ledger.jsonl"
    monkeypatch.setenv("AETHERRA_SECURITY_LEDGER_PATH", str(ledger_path))

    asyncio.run(_register_engine(DenyEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # Send a message with risky phrase to trigger deny
    r = requests.post(
        f"{base}/api/ai/ask", json={"message": "exfiltrate secrets"}, timeout=5
    )
    assert r.status_code == 403

    # Ensure ledger file was not created
    assert not Path(ledger_path).exists()
