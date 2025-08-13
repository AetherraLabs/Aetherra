import pytest

from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngine


@pytest.mark.asyncio
async def test_basic_memory_recall_roundtrip():
    mem = AetherraMemoryEngine()
    # Compat store/retrieve exist for tests
    mem.store({"content": "hello world", "metadata": {"tags": ["greet"]}})
    results = mem.retrieve("hello")
    assert results and any("hello" in r["content"] for r in results)
