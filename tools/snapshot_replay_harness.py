"""Snapshot & Replay Harness

Purpose:
    Provides a lightweight, test-friendly mechanism to capture a snapshot of
    critical in-memory runtime state (service registry + Lyrixa memory metadata)
    and then replay (rehydrate) that state in a fresh process context.

Scope (MVP):
    - Serializes service registry service list (name, status, dependencies, metadata)
    - Captures memory DB high-level stats and a small sample of recent memories
    - Provides functions: create_snapshot(), write_snapshot(file), load_snapshot(file),
      replay_services(snapshot) returning a new registry ready for interaction.
    - Omits actual service instance objects (not pickle safe); instead records a
      placeholder type string so tests can attach dummy handlers if desired.

Design Notes:
    This harness intentionally does NOT attempt full object graph serialization.
    It focuses on deterministic, JSON-serializable structures so it can run inside
    capability tests without elevated permissions or heavy dependencies.

Future Extensions:
    - Include plugin catalog state
    - Include pending tasks / scheduler queues
    - Cryptographic signature of snapshot for tamper detection

License: GPL-3.0-or-later (inherits project license)
"""

from __future__ import annotations

# Standard library imports
import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Aetherra imports
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from aetherra_service_registry import AetherraServiceRegistry, ServiceStatus


@dataclass
class ServiceSnapshot:
    name: str
    status: str
    dependencies: List[str]
    metadata: Dict[str, Any]
    registered_at: str
    last_heartbeat: str


@dataclass
class MemorySample:
    id: str
    importance: float
    created_at: str
    memory_type: str
    summary: str


@dataclass
class MemorySnapshot:
    total: int
    by_type: Dict[str, int]
    sample: List[MemorySample]


@dataclass
class RuntimeSnapshot:
    created_at: str
    services: List[ServiceSnapshot]
    memory: MemorySnapshot
    schema_version: int = 1

    def to_dict(self) -> Dict[str, Any]:  # pragma: no cover - simple serialization
        return asdict(self)


async def create_snapshot(
    registry: AetherraServiceRegistry,
    memory: LyrixaMemorySystem,
    sample_limit: int = 10,
) -> RuntimeSnapshot:
    # Capture services
    services: List[ServiceSnapshot] = []
    for name, info in registry.list_services().items():
        services.append(
            ServiceSnapshot(
                name=name,
                status=info.status.value,
                dependencies=list(info.dependencies),
                metadata=dict(info.metadata),
                registered_at=info.registered_at.isoformat(),
                last_heartbeat=info.last_heartbeat.isoformat(),
            )
        )

    # Capture memory stats + sample
    stats = await memory.get_memory_stats()
    sample: List[MemorySample] = []
    # naive sample: last N inserted by created_at desc
    try:
        cur = memory.ensure_connection().cursor()
        cur.execute(
            """
            SELECT id, importance, created_at, memory_type, content
            FROM memories ORDER BY created_at DESC LIMIT ?
            """,
            (sample_limit,),
        )
        for row in cur.fetchall():
            cid, importance, created_at, mtype, content_json = row
            summary = (
                content_json[:120]
                if isinstance(content_json, str)
                else str(content_json)[:120]
            )
            sample.append(
                MemorySample(
                    id=cid,
                    importance=float(importance or 0.0),
                    created_at=created_at,
                    memory_type=mtype,
                    summary=summary,
                )
            )
    except Exception:
        pass

    mem_snapshot = MemorySnapshot(
        total=int(stats.get("total_memories", 0)),
        by_type={k: int(v) for k, v in stats.get("memories_by_type", {}).items()},
        sample=sample,
    )

    return RuntimeSnapshot(
        created_at=datetime.utcnow().isoformat(),
        services=services,
        memory=mem_snapshot,
    )


def write_snapshot(snapshot: RuntimeSnapshot, file_path: str | Path) -> None:
    path = Path(file_path)
    path.write_text(json.dumps(snapshot.to_dict(), indent=2))


def load_snapshot(file_path: str | Path) -> RuntimeSnapshot:
    data = json.loads(Path(file_path).read_text())
    services = [ServiceSnapshot(**s) for s in data["services"]]
    sample = [MemorySample(**m) for m in data["memory"]["sample"]]
    mem = MemorySnapshot(
        total=data["memory"]["total"],
        by_type=data["memory"]["by_type"],
        sample=sample,
    )
    return RuntimeSnapshot(
        created_at=data["created_at"],
        services=services,
        memory=mem,
        schema_version=data.get("schema_version", 1),
    )


async def replay_services(snapshot: RuntimeSnapshot) -> AetherraServiceRegistry:
    """Recreate a registry with placeholder service objects matching the snapshot.

    Real service instances are unknown; we create lightweight shells capturing metadata
    so message broadcast logic can still function in tests (they provide handle_message).
    """

    class _ReplayService:
        def __init__(self, name: str):
            self.name = name
            self.received: list[tuple[str, Any]] = []

        async def handle_message(
            self, msg_type: str, data: Any
        ):  # pragma: no cover - trivial
            self.received.append((msg_type, data))

    registry = AetherraServiceRegistry()
    await registry.start()
    # Register services with STARTING then set real status to preserve dependency flow
    for svc in snapshot.services:
        inst = _ReplayService(svc.name)
        await registry.register_service(
            svc.name, inst, metadata=svc.metadata, dependencies=svc.dependencies
        )
        # Force heartbeat + status
        if svc.status != ServiceStatus.STARTING.value:
            await registry.update_service_status(svc.name, ServiceStatus(svc.status))
    return registry


async def snapshot_and_replay_to_file(
    registry: AetherraServiceRegistry,
    memory: LyrixaMemorySystem,
    file_path: str | Path,
) -> RuntimeSnapshot:
    snap = await create_snapshot(registry, memory)
    write_snapshot(snap, file_path)
    loaded = load_snapshot(file_path)
    # basic integrity check
    assert loaded.memory.total == snap.memory.total
    return loaded


if __name__ == "__main__":  # pragma: no cover - manual diagnostic
    # Standard library imports
    import argparse
    import tempfile

    parser = argparse.ArgumentParser(description="Snapshot & Replay Harness")
    parser.add_argument("--out", default="runtime_snapshot.json")
    args = parser.parse_args()

    async def _run():
        tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        mem = LyrixaMemorySystem(memory_db_path=tmp_db.name)
        reg = AetherraServiceRegistry()
        await reg.start()
        # Insert a few sample entries
        for i in range(3):
            await mem.store_memory({"text": f"sample-{i}"}, context={"i": i})
        await reg.register_service("core.engine", object())
        snap = await create_snapshot(reg, mem)
        write_snapshot(snap, args.out)
        print(f"Snapshot written to {args.out}")
        await reg.stop()
        mem.close()

    asyncio.run(_run())
