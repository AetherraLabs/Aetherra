import os

import pytest


@pytest.mark.asyncio
async def test_read_only_queues_and_list_clear(tmp_path, monkeypatch):
    # Force headless/read_only with local outbox directory
    monkeypatch.setenv("AAR_MODE", "headless")
    monkeypatch.setenv("AAR_READ_ONLY", "1")
    # Ensure Outbox writes into tmp_path by chdir
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        from aetherra_agent_fabric import AgentFabric
        from aetherra_service_registry import AetherraServiceRegistry

        reg = AetherraServiceRegistry()
        await reg.start()

        fabric = AgentFabric(reg)
        await fabric.start()

        # Direct run to executor should be queued
        res = await fabric.handle_message(
            "agent.run",
            {
                "agent": "agent.executor",
                "action": "pipeline_task",
                "params": {"goal": "demo"},
            },
        )
        assert res.get("ok") is True
        assert res.get("queued") is True
        key = res.get("outbox_key")
        assert key and isinstance(key, str)

        # List via new endpoint
        listed = await fabric.handle_message("agents.outbox.list", {})
        assert listed.get("ok") is True
        assert listed.get("count") == 1
        assert listed["entries"][0]["key"] == key

        # Clear should fail under read_only
        cleared = await fabric.handle_message("agents.outbox.clear", {})
        assert cleared.get("ok") is False
        assert cleared.get("error") == "read_only"

        # Switch to full mode (new instance) and clear
        monkeypatch.setenv("AAR_MODE", "full")
        monkeypatch.setenv("AAR_READ_ONLY", "0")
        fabric2 = AgentFabric(reg)
        await fabric2.start()

        listed2 = await fabric2.handle_message("agents.outbox.list", {})
        assert listed2.get("ok") is True
        assert listed2.get("count") == 1

        cleared2 = await fabric2.handle_message("agents.outbox.clear", {})
        assert cleared2.get("ok") is True
        listed3 = await fabric2.handle_message("agents.outbox.list", {})
        assert listed3.get("ok") is True
        assert listed3.get("count") == 0
    finally:
        os.chdir(old_cwd)
