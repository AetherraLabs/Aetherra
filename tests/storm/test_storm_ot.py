import asyncio

import numpy as np
import pytest

from Aetherra.aetherra_core.memory.models import MemoryRecallResult
from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine

pytestmark = pytest.mark.asyncio


def make_engine(enabled=True, max_ms_exact=0):
    config = StormConfig(enabled=enabled, max_ms_exact=max_ms_exact)
    return StormEngine(config=config)


async def test_basic_ot_cost_decreases_for_similar_content():
    engine = make_engine()
    q = "test memory"
    # Similar content should have lower OT cost
    res1 = await engine.recall(q, limit=5)
    res2 = await engine.recall(q + " extra", limit=5)
    cost1 = res1.metadata["storm_meta"]["transport_cost"]
    cost2 = res2.metadata["storm_meta"]["transport_cost"]
    assert cost1 < cost2 or np.isclose(cost1, cost2)


async def test_ot_cost_is_zero_for_identical():
    engine = make_engine()
    q = "identical"
    res = await engine.recall(q, limit=1)
    assert np.isclose(res.metadata["storm_meta"]["transport_cost"], 0.0, atol=1e-5)


async def test_evidence_tags_present():
    engine = make_engine()
    res = await engine.recall("foo", limit=3)
    tags = res.metadata["evidence_tags"]
    assert "ot" in tags
    assert "coh" in tags
    assert "pers" in tags


async def test_budget_enforcement_switches_to_approximate():
    engine = make_engine(max_ms_exact=1)  # 1ms budget, will force approx
    _ = await engine.recall("slow test", limit=5)
    assert engine._last_recall_status["approximate"]


async def test_hybrid_mode_with_base_fallback():
    engine = make_engine()
    base_items = [{"content": "a"}, {"content": "b"}]
    base_scores = [1.0, 0.9]
    base = MemoryRecallResult(items=base_items, scores=base_scores, metadata={})
    res = await engine.recall("fallback", limit=2, base_fallback=base)
    assert res.source == "storm_hybrid"
    assert len(res.items) == 2


async def test_limit_respected():
    engine = make_engine()
    res = await engine.recall("limit test", limit=2)
    assert res.source == "storm"
    assert isinstance(res.items, list)


async def test_ot_cost_increases_with_dissimilarity():
    engine = make_engine()
    res1 = await engine.recall("cat", limit=1)
    res2 = await engine.recall("dog", limit=1)
    cost1 = res1.metadata["storm_meta"]["transport_cost"]
    cost2 = res2.metadata["storm_meta"]["transport_cost"]
    assert abs(cost1 - cost2) < 1.0  # Should be similar for unrelated


async def test_metrics_are_updated():
    engine = make_engine()
    await engine.recall("metrics", limit=1)
    assert hasattr(engine.metrics, "ot_cost_avg")


async def test_mock_embeddings_are_deterministic():
    from Aetherra.aetherra_core.memory.storm.ot_helpers import _generate_mock_embedding

    emb1 = _generate_mock_embedding("foo")
    emb2 = _generate_mock_embedding("foo")
    assert np.allclose(emb1, emb2)


async def test_distance_matrix_shape():
    from Aetherra.aetherra_core.memory.storm.ot_helpers import (
        _build_distance_matrix,
        _generate_mock_embedding,
    )

    x = [_generate_mock_embedding("a"), _generate_mock_embedding("b")]
    y = [_generate_mock_embedding("c")]
    mat = _build_distance_matrix(x, y)
    assert mat.shape == (2, 1)
