"""Extended Crash Recovery & Service Rehydration Capability Test

Validates that after a simulated crash:
1. Persistent memory rows remain intact (baseline from basic test).
2. Service registry can be restarted cleanly and accepts re-registration of services.
3. Dependencies resolve again and healthy status is achieved.
4. New memory writes succeed post-registry restart.

This extends the lightweight persistence check to incorporate the service layer
that higher-level agents depend upon.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceStatus,
)


class DummyService:
    def __init__(self, name: str):
        self.name = name
        self.messages: list[tuple[str, dict]] = []

    async def handle_message(
        self, msg_type: str, data: dict
    ):  # pragma: no cover - simple capture
        self.messages.append((msg_type, data))


@pytest.mark.asyncio
async def test_extended_crash_recovery_and_service_rehydration():
    # Phase 1: create persistent memory and write baseline entries
    temp_dir = tempfile.TemporaryDirectory()
    db_path = Path(temp_dir.name) / "extended_recovery_mem.db"

    # (Placeholder for future parallel init tasks)

    with LyrixaMemorySystem(memory_db_path=str(db_path)) as system:
        ids = []
        for i in range(15):
            mid = asyncio.create_task(
                system.store_memory({"text": f"extended-crash-{i}"})
            )
            ids.append(mid)
        # Await all store tasks
        stored_ids = [await t for t in ids]
        assert len(stored_ids) == 15

    # Simulated crash: system context manager closed (file handles released)

    # Phase 2: Recreate memory system, verify rows
    recovered = LyrixaMemorySystem(memory_db_path=str(db_path))
    cur = recovered.ensure_connection().cursor()
    cur.execute("SELECT COUNT(*) FROM memories WHERE content LIKE '%extended-crash-%'")
    (row_count,) = cur.fetchone()
    assert row_count >= 15, f"Expected >=15 rows, found {row_count}"

    # Phase 3: Service registry rehydration
    registry = AetherraServiceRegistry()
    await registry.start()

    svc_core = DummyService("core.engine")
    svc_agent = DummyService("agent.planner")
    await registry.register_service("core.engine", svc_core)
    await registry.register_service(
        "agent.planner", svc_agent, dependencies=["core.engine"]
    )

    # Promote core.engine to healthy -> dependency chain should resolve
    await registry.update_service_status("core.engine", ServiceStatus.HEALTHY)
    await asyncio.sleep(0)  # yield to dependency check
    info_agent = registry.get_service_info("agent.planner")
    # agent.planner starts as STARTING until deps satisfied; trigger dependency resolver
    await (
        registry._check_dependencies()
    )  # internal call acceptable for capability guard
    info_agent = registry.get_service_info("agent.planner")
    assert info_agent is not None and info_agent.status == ServiceStatus.HEALTHY

    # Phase 4: Post-recovery memory write
    post_id = await recovered.store_memory(
        {"text": "post-registry-recovery"}, context={"phase": "post_rehydrate"}
    )
    assert post_id

    # Sanity: broadcast message and verify receipt (ensures handlers functional)
    await registry.broadcast_message("system.ping", {"ok": True})
    assert any(m[0] == "system.ping" for m in svc_core.messages + svc_agent.messages)

    await registry.stop()
    recovered.close()
    temp_dir.cleanup()
