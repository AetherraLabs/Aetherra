# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for STORM PR-5: TT/MPS-style compression via SVD shim."""

from __future__ import annotations

import numpy as np
import pytest

from Aetherra.aetherra_core.memory.models import MemoryRecallResult
from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine
from Aetherra.aetherra_core.memory.storm.tt_compression import approximate_cost_matrix


def test_approximate_cost_matrix_basic_shape_and_rank():
    rng = np.random.default_rng(0)
    cost = rng.random((8, 6))
    approx, meta = approximate_cost_matrix(cost, rank_cap=3)
    assert approx.shape == cost.shape
    assert meta.applied
    assert meta.rank_used == 3
    # Error should be finite and non-negative
    assert meta.err_fro is not None and meta.err_fro >= 0.0


def test_approximate_cost_matrix_noop_when_rank_zero():
    rng = np.random.default_rng(1)
    cost = rng.random((5, 5))
    approx, meta = approximate_cost_matrix(cost, rank_cap=0)
    assert not meta.applied
    assert np.allclose(approx, cost)


@pytest.mark.asyncio
async def test_engine_reports_tt_applied_with_base_fallback():
    # Feed the engine via base_fallback so it has items without a core memory
    base = MemoryRecallResult(
        items=[{"content": "alpha"}, {"content": "beta"}, {"content": "gamma"}],
        scores=[0.9, 0.5, 0.1],
        metadata={},
    )

    cfg = StormConfig(enabled=True, tt_max_rank=2)
    engine = StormEngine(config=cfg)
    res = await engine.recall("query text", limit=3, base_fallback=base)

    storm_meta = res.metadata["storm_meta"]
    assert storm_meta.get("tt_applied") is True
    assert 0 < int(storm_meta.get("tt_rank_used", 0)) <= 2


@pytest.mark.asyncio
async def test_engine_skips_tt_for_tiny_matrix():
    # Only one item -> matrix 1x1, compression should skip
    base = MemoryRecallResult(items=[{"content": "only"}], scores=[1.0], metadata={})
    cfg = StormConfig(enabled=True, tt_max_rank=8)
    engine = StormEngine(config=cfg)
    res = await engine.recall("q", limit=1, base_fallback=base)
    assert res.metadata["storm_meta"].get("tt_applied") is False
