import asyncio

import pytest

from Aetherra.consciousness.workspace_core import get_workspace


@pytest.mark.asyncio
async def test_workspace_broadcast_basic():
    ws = get_workspace()
    received = []
    ws.subscribe(lambda msg: received.append(msg))
    added = ws.add_candidate({"foo": "bar"}, priority=5, source="test")
    assert added
    await ws.start()
    # Retry loop up to 1s total (interval defaults to 500ms)
    for _ in range(6):
        if any(m.get("foo") == "bar" for m in received):
            break
        await asyncio.sleep(0.2)
    await ws.stop()
    assert any(m.get("foo") == "bar" for m in received)
