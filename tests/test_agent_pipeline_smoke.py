# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import os

import pytest


@pytest.mark.asyncio
async def test_pipeline_queue_and_summarize(tmp_path, monkeypatch):
    # Headless/read_only to force execute stage to queue
    monkeypatch.setenv("AAR_MODE", "headless")
    monkeypatch.setenv("AAR_READ_ONLY", "1")
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        from aetherra_agent_fabric import AgentFabric
        from aetherra_service_registry import AetherraServiceRegistry

        reg = AetherraServiceRegistry()
        await reg.start()
        fabric = AgentFabric(reg)
        await fabric.start()

        res = await fabric.handle_message(
            "agent.pipeline", {"goal": "Summarize hello world and execute"}
        )
        assert res.get("ok") is True
        stages = res.get("stages") or {}
        assert "plan" in stages and stages["plan"].get("ok")
        assert "retrieve" in stages and stages["retrieve"].get("ok")
        assert "summarize" in stages and stages["summarize"].get("ok")
        # Execute should be queued in read_only
        exec_stage = stages.get("execute")
        assert exec_stage and exec_stage.get("queued") is True
    finally:
        os.chdir(old_cwd)
