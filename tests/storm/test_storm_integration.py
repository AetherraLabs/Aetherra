# SPDX-License-Identifier: GPL-3.0-or-later
"""Test STORM integration with memory engine"""

import os

import pytest

from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)


def test_memory_engine_storm_status_disabled():
    """Memory engine includes storm status block (disabled by default)"""
    os.environ.pop("AETHERRA_MEMORY_STORM", None)
    engine = AetherraMemoryEngineAdvanced()
    status = engine.get_system_status()

    assert "storm" in status
    storm_status = status["storm"]
    assert not storm_status["enabled"]
    assert "backends" in storm_status
    assert "selected_backend" in storm_status


def test_memory_engine_storm_status_enabled():
    """Memory engine storm status reflects enabled flag"""
    os.environ["AETHERRA_MEMORY_STORM"] = "1"
    engine = AetherraMemoryEngineAdvanced()
    status = engine.get_system_status()

    assert "storm" in status
    assert status["storm"]["enabled"]
    os.environ.pop("AETHERRA_MEMORY_STORM", None)


@pytest.mark.asyncio
async def test_recall_typed_disabled():
    """recall_typed returns normal result when STORM disabled"""
    os.environ.pop("AETHERRA_MEMORY_STORM", None)
    engine = AetherraMemoryEngineAdvanced()
    result = await engine.recall_typed("test", limit=3)

    # Should not be storm source when disabled
    assert result.source in ("core", "hybrid", "conceptual", "episodic")
    assert isinstance(result.items, list)


@pytest.mark.asyncio
async def test_recall_typed_enabled_returns_storm_hybrid():
    """recall_typed returns storm_hybrid when STORM enabled"""
    os.environ["AETHERRA_MEMORY_STORM"] = "1"
    engine = AetherraMemoryEngineAdvanced()
    result = await engine.recall_typed("test", limit=3)

    # Should return storm_hybrid wrapping base recall
    assert result.source in ("storm", "storm_hybrid")
    assert "storm_meta" in result.metadata
    os.environ.pop("AETHERRA_MEMORY_STORM", None)


@pytest.mark.asyncio
async def test_memory_engine_backward_compat():
    """Memory engine maintains backward compatibility with old recall()"""
    os.environ.pop("AETHERRA_MEMORY_STORM", None)
    engine = AetherraMemoryEngineAdvanced()

    # Old dict-based recall should still work
    results = await engine.recall("test", recall_strategy="vector", limit=5)
    assert isinstance(results, list)
    # Results should be dicts with expected keys when available
    for r in results:
        if r:
            assert isinstance(r, dict)
