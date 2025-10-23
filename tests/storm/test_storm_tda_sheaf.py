# SPDX-License-Identifier: GPL-3.0-or-later
"""
PR-4 tests: Sheaf inconsistency and TDA persistence scoring.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine
from Aetherra.aetherra_core.memory.storm.tda_sheaf_helpers import (
    compute_persistence_bonus,
    compute_sheaf_inconsistency,
)


def test_sheaf_inconsistency_identical_embeddings():
    v = np.ones(8, dtype=float)
    inc = compute_sheaf_inconsistency([v, v, v])
    assert isinstance(inc, float)
    assert inc == pytest.approx(0.0, abs=1e-9)


def test_persistence_bonus_monotonicity_cluster_vs_scatter():
    # Tight cluster
    rng = np.random.RandomState(0)
    base = rng.randn(16)
    cluster = [base + 0.001 * rng.randn(16) for _ in range(5)]
    # Scattered
    scatter = [rng.randn(16) for _ in range(5)]
    b_cluster = compute_persistence_bonus(cluster)
    b_scatter = compute_persistence_bonus(scatter)
    assert 0.0 <= b_cluster <= 1.0
    assert 0.0 <= b_scatter <= 1.0
    # Cluster should have higher bonus (tighter -> smaller MST)
    assert b_cluster > b_scatter


@pytest.mark.asyncio
async def test_engine_coh_and_pers_tags_with_core_memory():
    mock_core = MagicMock()
    mock_core.recall_memories = AsyncMock(
        return_value=[
            {"content": "alpha", "relevance_score": 0.9},
            {"content": "alpha", "relevance_score": 0.8},
            {"content": "alpha", "relevance_score": 0.7},
        ]
    )
    cfg = StormConfig(enabled=True)
    engine = StormEngine(config=cfg, core_memory=mock_core)
    res = await engine.recall("alpha", limit=3)
    et = res.metadata.get("evidence_tags", {})
    assert "coh" in et
    assert "pers" in et
    # Identical items => high coherence (coh ~ 1.0)
    assert et["coh"] == pytest.approx(1.0, rel=1e-5)
    assert 0.0 <= et["pers"] <= 1.0


@pytest.mark.asyncio
async def test_engine_coh_lower_for_diverse_items():
    mock_core = MagicMock()
    mock_core.recall_memories = AsyncMock(
        return_value=[
            {"content": "alpha", "relevance_score": 0.9},
            {"content": "beta", "relevance_score": 0.8},
            {"content": "gamma", "relevance_score": 0.7},
        ]
    )
    cfg = StormConfig(enabled=True)
    engine = StormEngine(config=cfg, core_memory=mock_core)
    res = await engine.recall("alpha", limit=3)
    et = res.metadata.get("evidence_tags", {})
    assert "coh" in et
    # Diverse items -> lower coherence than identical case
    assert et["coh"] < 1.0
