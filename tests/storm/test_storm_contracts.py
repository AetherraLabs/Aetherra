# SPDX-License-Identifier: GPL-3.0-or-later
"""Test STORM contract compliance"""

import os

import pytest

from Aetherra.aetherra_core.memory.models import MemoryRecallResult
from Aetherra.aetherra_core.memory.storm import StormEngine


@pytest.mark.asyncio
async def test_recall_result_contract():
    """Recall returns valid MemoryRecallResult with storm source"""
    engine = StormEngine()
    result = await engine.recall("test", limit=3)

    # Contract checks
    assert isinstance(result, MemoryRecallResult)
    assert result.source in ("storm", "storm_hybrid")
    assert isinstance(result.items, list)
    assert isinstance(result.scores, list)
    assert isinstance(result.metadata, dict)


@pytest.mark.asyncio
async def test_storm_metadata_fields():
    """Result metadata contains required STORM fields"""
    engine = StormEngine()
    result = await engine.recall("test", limit=3)

    storm_meta = result.metadata.get("storm_meta", {})
    assert "transport_cost" in storm_meta
    assert "sheaf_inconsistency" in storm_meta
    assert "persistence_bonus" in storm_meta
    assert "freshness" in storm_meta


@pytest.mark.asyncio
async def test_evidence_tags_mapping():
    """Evidence tags map correctly per contract"""
    engine = StormEngine()
    result = await engine.recall("test", limit=3)

    evidence = result.metadata.get("evidence_tags", {})
    assert "ot" in evidence
    assert "coh" in evidence
    assert "pers" in evidence

    # coh = 1/(1+sheaf_inconsistency)
    storm_meta = result.metadata["storm_meta"]
    expected_coh = 1.0 / (1.0 + storm_meta["sheaf_inconsistency"])
    assert abs(evidence["coh"] - expected_coh) < 0.001


@pytest.mark.asyncio
async def test_source_storm_when_no_base():
    """Source is 'storm' when no base fallback"""
    engine = StormEngine()
    result = await engine.recall("test", limit=3)
    assert result.source == "storm"


@pytest.mark.asyncio
async def test_source_storm_hybrid_with_base():
    """Source is 'storm_hybrid' when base fallback provided"""
    base = MemoryRecallResult(
        items=[{"id": 1}], scores=[0.8], source="core", metadata={}
    )
    engine = StormEngine()
    result = await engine.recall("test", limit=3, base_fallback=base)
    assert result.source == "storm_hybrid"
