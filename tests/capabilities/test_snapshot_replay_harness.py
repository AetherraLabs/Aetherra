# Standard library imports
import json
import tempfile

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from aetherra_service_registry import AetherraServiceRegistry
from tools.snapshot_replay_harness import create_snapshot, replay_services


@pytest.mark.asyncio
async def test_snapshot_replay_harness_round_trip():
    tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    mem = LyrixaMemorySystem(memory_db_path=tmp_db.name)
    reg = AetherraServiceRegistry()
    await reg.start()
    # add some memories
    for i in range(7):
        await mem.store_memory({"text": f"snapshot-seed-{i}"}, context={"i": i})
    await reg.register_service("core.engine", object())
    await reg.register_service("agent.planner", object(), dependencies=["core.engine"])
    # mark core healthy, resolve dependencies
    # Aetherra imports
    from aetherra_service_registry import ServiceStatus

    await reg.update_service_status("core.engine", ServiceStatus.HEALTHY)
    await reg._check_dependencies()  # internal call for deterministic test

    snap = await create_snapshot(reg, mem, sample_limit=5)
    assert snap.memory.total >= 7
    assert any(s.name == "core.engine" for s in snap.services)

    # Serialize / deserialize in-memory (no disk write for speed)
    encoded = json.dumps(snap.to_dict())
    data = json.loads(encoded)
    assert data["schema_version"] == 1

    # Replay services
    replay_reg = await replay_services(snap)
    assert replay_reg.get_service("core.engine") is not None
    # Broadcast sanity
    await replay_reg.broadcast_message("ping.replay", {"ok": True})

    await replay_reg.stop()
    await reg.stop()
    mem.close()
