# SPDX-License-Identifier: GPL-3.0-or-later
"""Test basic STORM engine operations"""

import os

import pytest

from Aetherra.aetherra_core.memory.storm import StormConfig, StormEngine


def test_config_from_env_default_off():
    """STORM should be disabled by default"""
    os.environ.pop("AETHERRA_MEMORY_STORM", None)
    cfg = StormConfig.from_env()
    assert not cfg.enabled
    assert cfg.ot_backend == "auto"
    assert cfg.tt_max_rank == 32
    assert cfg.k_coarse == 64


def test_config_from_env_enabled():
    """STORM config respects environment flag"""
    os.environ["AETHERRA_MEMORY_STORM"] = "1"
    cfg = StormConfig.from_env()
    assert cfg.enabled
    os.environ.pop("AETHERRA_MEMORY_STORM", None)


def test_config_backend_override():
    """STORM backend can be overridden"""
    os.environ["AETHERRA_STORM_OT_BACKEND"] = "keops"
    cfg = StormConfig.from_env()
    assert cfg.ot_backend == "keops"
    os.environ.pop("AETHERRA_STORM_OT_BACKEND", None)


def test_engine_status_disabled():
    """Engine status reports disabled when flag off"""
    os.environ.pop("AETHERRA_MEMORY_STORM", None)
    engine = StormEngine()
    status = engine.status()
    assert not status["enabled"]
    assert "backends" in status
    assert "selected_backend" in status
    assert "tt_rank_cap" in status


def test_engine_status_enabled():
    """Engine status reports enabled when flag on"""
    os.environ["AETHERRA_MEMORY_STORM"] = "1"
    cfg = StormConfig.from_env()
    engine = StormEngine(config=cfg)
    status = engine.status()
    assert status["enabled"]
    assert status["selected_backend"] in ("pot", "keops")
    os.environ.pop("AETHERRA_MEMORY_STORM", None)


@pytest.mark.asyncio
async def test_recall_empty():
    """Recall with no base fallback returns empty storm result"""
    engine = StormEngine()
    result = await engine.recall("test query", limit=5)
    assert result.source == "storm"
    assert isinstance(result.items, list)
    assert len(result.items) == 0
    assert "storm_meta" in result.metadata


@pytest.mark.asyncio
async def test_recall_with_base_fallback():
    """Recall with base fallback returns storm_hybrid"""
    from Aetherra.aetherra_core.memory.models import MemoryRecallResult

    base = MemoryRecallResult(
        items=[{"content": "test"}], scores=[0.9], source="core", metadata={}
    )
    engine = StormEngine()
    result = await engine.recall("test", limit=5, base_fallback=base)
    assert result.source == "storm_hybrid"
    assert len(result.items) == 1
    assert "storm_meta" in result.metadata
