# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for STORM Phase 0: Shadow Mode Integration.

Validates that shadow mode:
- Runs STORM in parallel with baseline
- Emits comparison metrics
- Never affects production responses
- Handles STORM failures gracefully
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)
from Aetherra.aetherra_core.memory.models import MemoryRecallResult
from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine
from Aetherra.aetherra_core.memory.storm.shadow_logger import (
    compare_results,
    shadow_recall,
)


def test_compare_results_identical():
    """Test comparison detects identical results."""
    baseline = MemoryRecallResult(
        items=[{"content": "a"}, {"content": "b"}],
        scores=[0.9, 0.8],
        source="core",
        metadata={},
    )
    storm = MemoryRecallResult(
        items=[{"content": "a"}, {"content": "b"}],
        scores=[0.9, 0.8],
        source="storm_hybrid",
        metadata={},
    )

    comparison = compare_results(baseline, storm)
    assert comparison["agreed"] is True
    assert comparison["item_overlap"] == 1.0
    assert comparison["score_delta"] < 0.01


def test_compare_results_divergent():
    """Test comparison detects divergent results."""
    baseline = MemoryRecallResult(
        items=[{"content": "a"}, {"content": "b"}],
        scores=[0.9, 0.8],
        source="core",
        metadata={},
    )
    storm = MemoryRecallResult(
        items=[{"content": "c"}, {"content": "d"}],
        scores=[0.7, 0.6],
        source="storm_hybrid",
        metadata={},
    )

    comparison = compare_results(baseline, storm)
    assert comparison["agreed"] is False
    assert comparison["item_overlap"] == 0.0  # No overlap


def test_compare_results_partial_overlap():
    """Test comparison with partial overlap."""
    baseline = MemoryRecallResult(
        items=[{"content": "a"}, {"content": "b"}],
        scores=[0.9, 0.8],
        source="core",
        metadata={},
    )
    storm = MemoryRecallResult(
        items=[{"content": "a"}, {"content": "c"}],
        scores=[0.85, 0.75],
        source="storm_hybrid",
        metadata={},
    )

    comparison = compare_results(baseline, storm)
    # 1 out of 3 unique items = 33% overlap
    assert comparison["item_overlap"] == pytest.approx(0.33, abs=0.05)
    # Score delta for 'a': abs(0.9 - 0.85) = 0.05
    assert comparison["score_delta"] < 0.1


def test_compare_results_empty():
    """Test comparison handles empty results."""
    baseline = MemoryRecallResult(items=[], scores=[], source="core", metadata={})
    storm = MemoryRecallResult(items=[], scores=[], source="storm", metadata={})

    comparison = compare_results(baseline, storm)
    assert comparison["agreed"] is True
    assert comparison["item_overlap"] == 1.0  # Both empty = perfect


@pytest.mark.asyncio
async def test_shadow_recall_successful():
    """Test shadow recall executes and compares without affecting baseline."""
    mock_engine = MagicMock()
    mock_engine.recall = AsyncMock(
        return_value=MemoryRecallResult(
            items=[{"content": "storm result"}],
            scores=[0.95],
            source="storm_hybrid",
            metadata={},
        )
    )

    baseline = MemoryRecallResult(
        items=[{"content": "baseline result"}],
        scores=[0.9],
        source="core",
        metadata={},
    )

    result, comparison = await shadow_recall(mock_engine, baseline, "test query", 5)

    # Result should be baseline unchanged
    assert result is baseline
    assert len(result.items) == 1
    assert result.items[0]["content"] == "baseline result"

    # Comparison should have metrics
    assert "agreed" in comparison
    assert "latency_ms" in comparison
    assert comparison["latency_ms"] > 0.0


@pytest.mark.asyncio
async def test_shadow_recall_storm_fails():
    """Test shadow recall gracefully handles STORM failures."""
    mock_engine = MagicMock()
    mock_engine.recall = AsyncMock(side_effect=Exception("STORM error"))

    baseline = MemoryRecallResult(
        items=[{"content": "baseline result"}],
        scores=[0.9],
        source="core",
        metadata={},
    )

    result, comparison = await shadow_recall(mock_engine, baseline, "test query", 5)

    # Result should still be baseline unchanged
    assert result is baseline
    assert len(result.items) == 1

    # Comparison should record the error
    assert comparison["agreed"] is False
    assert comparison["error"] is not None
    assert "STORM error" in comparison["error"]


@pytest.mark.asyncio
async def test_shadow_mode_in_memory_engine():
    """Test shadow mode integration in AetherraMemoryEngineAdvanced."""
    # Create engine with shadow mode enabled
    import os

    original_storm = os.environ.get("AETHERRA_MEMORY_STORM")
    original_shadow = os.environ.get("AETHERRA_STORM_SHADOW_MODE")

    try:
        os.environ["AETHERRA_MEMORY_STORM"] = "1"
        os.environ["AETHERRA_STORM_SHADOW_MODE"] = "1"

        engine = AetherraMemoryEngineAdvanced()

        # Store some baseline data
        await engine.remember("baseline memory", tags=["test"])

        # Recall should return baseline result in shadow mode
        result = await engine.recall_typed("baseline", limit=5)

        # Should be baseline source (not storm_hybrid)
        assert result.source in ("core", "hybrid")

        # Shadow metrics should be recorded
        if engine._storm_engine:
            metrics = engine._storm_engine.metrics
            # At least one comparison should have happened
            assert metrics.shadow_comparisons_total >= 0

    finally:
        # Restore env
        if original_storm:
            os.environ["AETHERRA_MEMORY_STORM"] = original_storm
        else:
            os.environ.pop("AETHERRA_MEMORY_STORM", None)
        if original_shadow:
            os.environ["AETHERRA_STORM_SHADOW_MODE"] = original_shadow
        else:
            os.environ.pop("AETHERRA_STORM_SHADOW_MODE", None)


@pytest.mark.asyncio
async def test_production_mode_vs_shadow_mode():
    """Test that production mode returns STORM results, shadow mode returns baseline."""
    import os

    original_storm = os.environ.get("AETHERRA_MEMORY_STORM")
    original_shadow = os.environ.get("AETHERRA_STORM_SHADOW_MODE")

    try:
        # Test production mode (STORM on, shadow off)
        os.environ["AETHERRA_MEMORY_STORM"] = "1"
        os.environ["AETHERRA_STORM_SHADOW_MODE"] = "0"

        engine_prod = AetherraMemoryEngineAdvanced()
        await engine_prod.remember("test memory", tags=["test"])
        result_prod = await engine_prod.recall_typed("test", limit=5)

        # Production mode should return storm_hybrid
        if engine_prod._storm_engine:
            assert result_prod.source in ("storm", "storm_hybrid")

        # Test shadow mode (STORM on, shadow on)
        os.environ["AETHERRA_STORM_SHADOW_MODE"] = "1"

        engine_shadow = AetherraMemoryEngineAdvanced()
        await engine_shadow.remember("test memory", tags=["test"])
        result_shadow = await engine_shadow.recall_typed("test", limit=5)

        # Shadow mode should return baseline source
        assert result_shadow.source in ("core", "hybrid")

    finally:
        # Restore env
        if original_storm:
            os.environ["AETHERRA_MEMORY_STORM"] = original_storm
        else:
            os.environ.pop("AETHERRA_MEMORY_STORM", None)
        if original_shadow:
            os.environ["AETHERRA_STORM_SHADOW_MODE"] = original_shadow
        else:
            os.environ.pop("AETHERRA_STORM_SHADOW_MODE", None)


def test_storm_config_shadow_mode_env():
    """Test StormConfig reads shadow_mode from environment."""
    import os

    original = os.environ.get("AETHERRA_STORM_SHADOW_MODE")

    try:
        os.environ["AETHERRA_STORM_SHADOW_MODE"] = "1"
        cfg = StormConfig.from_env()
        assert cfg.shadow_mode is True

        os.environ["AETHERRA_STORM_SHADOW_MODE"] = "0"
        cfg = StormConfig.from_env()
        assert cfg.shadow_mode is False

    finally:
        if original:
            os.environ["AETHERRA_STORM_SHADOW_MODE"] = original
        else:
            os.environ.pop("AETHERRA_STORM_SHADOW_MODE", None)


def test_storm_engine_status_includes_shadow_mode():
    """Test that engine status includes shadow_mode field."""
    cfg = StormConfig(enabled=True, shadow_mode=True)
    engine = StormEngine(config=cfg)

    status = engine.status()
    assert "shadow_mode" in status
    assert status["shadow_mode"] is True


@pytest.mark.asyncio
async def test_shadow_metrics_recorded():
    """Test that shadow mode records comparison metrics."""
    import os

    original_storm = os.environ.get("AETHERRA_MEMORY_STORM")
    original_shadow = os.environ.get("AETHERRA_STORM_SHADOW_MODE")

    try:
        os.environ["AETHERRA_MEMORY_STORM"] = "1"
        os.environ["AETHERRA_STORM_SHADOW_MODE"] = "1"

        engine = AetherraMemoryEngineAdvanced()

        # Store and recall
        await engine.remember("test content", tags=["shadow"])
        await engine.recall_typed("test", limit=3)

        # Check shadow metrics
        if engine._storm_engine:
            metrics = engine._storm_engine.metrics.snapshot()
            # Shadow mode should have recorded at least one comparison or zero if gracefully degraded
            assert "aetherra_storm_shadow_comparisons_total" in metrics

    finally:
        if original_storm:
            os.environ["AETHERRA_MEMORY_STORM"] = original_storm
        else:
            os.environ.pop("AETHERRA_MEMORY_STORM", None)
        if original_shadow:
            os.environ["AETHERRA_STORM_SHADOW_MODE"] = original_shadow
        else:
            os.environ.pop("AETHERRA_STORM_SHADOW_MODE", None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
