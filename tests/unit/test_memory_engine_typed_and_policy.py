import pytest

from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
    MemorySystemConfig,
)
from Aetherra.aetherra_core.memory.models import MemoryRecallResult, PolicyViolation


@pytest.mark.asyncio
async def test_recall_typed_returns_memory_recall_result():
    engine = AetherraMemoryEngineAdvanced()
    # seed some memories via compat path on simple adapter on Advanced engine
    await engine.remember("alpha test memory", tags=["alpha"], category="test")
    await engine.remember("beta test memory", tags=["beta"], category="test")

    result = await engine.recall_typed("test")
    assert isinstance(result, MemoryRecallResult)
    assert isinstance(result.items, list)
    assert len(result.items) > 0
    assert isinstance(result.scores, list)
    assert len(result.scores) == len(result.items)


@pytest.mark.asyncio
async def test_policy_violation_blocks_unsigned_sensitive_plugin_output():
    cfg = MemorySystemConfig(persist_sensitive_only_if_signed=True)
    engine = AetherraMemoryEngineAdvanced(config=cfg)

    # Attempt to persist content flagged as sensitive and plugin-originated without signature
    with pytest.raises(PolicyViolation):
        await engine.remember(
            content={"text": "secret from plugin"},
            tags=["sensitive"],
            category="project",
            narrative_role=None,
        )
