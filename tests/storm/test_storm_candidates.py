# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for STORM PR-2 Phase 2: Candidate enrichment and weighting strategies.

Validates:
- Real memory fetching from core memory system
- Coarse-to-fine candidate selection using k_coarse
- Probability mass weighting strategies (nearest, uniform, importance, recency)
- Integration with LyrixaMemorySystem
"""

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from Aetherra.aetherra_core.memory.models import MemoryRecallResult
from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine


@pytest.fixture
def mock_core_memory():
    """Mock LyrixaMemorySystem for candidate fetching tests."""
    memory = MagicMock()
    memory.recall_memories = AsyncMock(
        return_value=[
            {"content": "Python is great", "relevance_score": 0.9},
            {"content": "Testing is important", "relevance_score": 0.8},
            {"content": "Documentation helps", "relevance_score": 0.7},
        ]
    )
    return memory


@pytest.fixture
def storm_with_memory(mock_core_memory):
    """STORM engine with mock core memory."""
    cfg = StormConfig(enabled=True, k_coarse=64, max_ms_exact=0)
    return StormEngine(config=cfg, core_memory=mock_core_memory)


@pytest.fixture
def storm_no_memory():
    """STORM engine without core memory (pure mode)."""
    cfg = StormConfig(enabled=True, k_coarse=64, max_ms_exact=0)
    return StormEngine(config=cfg, core_memory=None)


@pytest.mark.asyncio
async def test_fetch_candidates_from_core_memory(storm_with_memory, mock_core_memory):
    """Test that STORM fetches real candidates from core memory."""
    items, scores = await storm_with_memory._fetch_candidates("test query", limit=10)

    # Should have called core memory with k_coarse limit
    mock_core_memory.recall_memories.assert_called_once()
    call_kwargs = mock_core_memory.recall_memories.call_args.kwargs
    assert call_kwargs["query"] == "test query"
    assert call_kwargs["limit"] >= 10  # Should use k_coarse if > limit

    # Should return items and scores
    assert len(items) == 3
    assert len(scores) == 3
    assert scores == [0.9, 0.8, 0.7]


@pytest.mark.asyncio
async def test_fetch_candidates_respects_k_coarse(storm_with_memory, mock_core_memory):
    """Test that k_coarse parameter controls candidate pool size."""
    cfg = StormConfig(enabled=True, k_coarse=128, max_ms_exact=0)
    engine = StormEngine(config=cfg, core_memory=mock_core_memory)

    await engine._fetch_candidates("test query", limit=10)

    # Should fetch k_coarse candidates initially
    call_kwargs = mock_core_memory.recall_memories.call_args.kwargs
    assert call_kwargs["limit"] == 128


@pytest.mark.asyncio
async def test_fetch_candidates_fallback_to_base(storm_with_memory):
    """Test fallback to base_fallback when core memory fails."""
    # Make core memory fail
    storm_with_memory.core_memory.recall_memories.side_effect = Exception("DB error")

    base_fallback = MemoryRecallResult(
        items=[{"content": "fallback item"}],
        scores=[0.5],
        metadata={},
    )

    items, scores = await storm_with_memory._fetch_candidates(
        "test query",
        limit=10,
        base_fallback=base_fallback,
    )

    # Should fall back to base items
    assert len(items) == 1
    assert items[0]["content"] == "fallback item"
    assert scores == [0.5]


@pytest.mark.asyncio
async def test_fetch_candidates_pure_mode_no_fallback(storm_no_memory):
    """Test pure STORM mode returns empty when no core memory."""
    items, scores = await storm_no_memory._fetch_candidates("test query", limit=10)

    # Pure mode without candidates returns empty
    assert items == []
    assert scores == []


def test_mass_distribution_nearest_strategy(storm_with_memory):
    """Test nearest neighbor mass distribution (Phase 1 behavior)."""
    cost_matrix = np.array([[0.5, 0.2, 0.8]])  # 3 candidates
    scores = [0.9, 0.8, 0.7]

    b = storm_with_memory._compute_mass_distribution(
        cost_matrix,
        scores,
        strategy="nearest",
    )

    # All mass on nearest (index 1, cost 0.2)
    assert b.shape == (3,)
    assert b[1] == 1.0
    assert b[0] == 0.0
    assert b[2] == 0.0


def test_mass_distribution_uniform_strategy(storm_with_memory):
    """Test uniform mass distribution across candidates."""
    cost_matrix = np.array([[0.5, 0.2, 0.8]])
    scores = [0.9, 0.8, 0.7]

    b = storm_with_memory._compute_mass_distribution(
        cost_matrix,
        scores,
        strategy="uniform",
    )

    # Equal mass on all candidates
    assert b.shape == (3,)
    assert np.allclose(b, [1 / 3, 1 / 3, 1 / 3])
    assert np.isclose(b.sum(), 1.0)


def test_mass_distribution_importance_strategy(storm_with_memory):
    """Test importance-weighted mass distribution."""
    cost_matrix = np.array([[0.5, 0.2, 0.8]])
    scores = [0.6, 0.3, 0.1]  # Higher scores = more mass

    b = storm_with_memory._compute_mass_distribution(
        cost_matrix,
        scores,
        strategy="importance",
    )

    # Mass proportional to scores
    assert b.shape == (3,)
    assert b[0] > b[1] > b[2]  # Order reflects score order
    assert np.isclose(b.sum(), 1.0)
    # Exact check: [0.6, 0.3, 0.1] normalized
    expected = np.array([0.6, 0.3, 0.1]) / 1.0
    assert np.allclose(b, expected)


def test_mass_distribution_zero_scores_importance(storm_with_memory):
    """Test importance weighting handles zero scores gracefully."""
    cost_matrix = np.array([[0.5, 0.2, 0.8]])
    scores = [0.0, 0.0, 0.0]  # All zero

    b = storm_with_memory._compute_mass_distribution(
        cost_matrix,
        scores,
        strategy="importance",
    )

    # Should add epsilon to avoid zeros
    assert b.shape == (3,)
    assert np.all(b > 0)
    assert np.isclose(b.sum(), 1.0)


def test_mass_distribution_recency_fallback(storm_with_memory):
    """Test recency strategy falls back to importance (not implemented yet)."""
    cost_matrix = np.array([[0.5, 0.2, 0.8]])
    scores = [0.6, 0.3, 0.1]

    b = storm_with_memory._compute_mass_distribution(
        cost_matrix,
        scores,
        strategy="recency",
    )

    # Should behave like importance for now
    expected = np.array([0.6, 0.3, 0.1]) / 1.0
    assert np.allclose(b, expected)


def test_mass_distribution_unknown_strategy_fallback(storm_with_memory):
    """Test unknown strategy falls back to nearest."""
    cost_matrix = np.array([[0.5, 0.2, 0.8]])
    scores = [0.9, 0.8, 0.7]

    b = storm_with_memory._compute_mass_distribution(
        cost_matrix,
        scores,
        strategy="invalid_strategy",
    )

    # Should fall back to nearest
    assert b[1] == 1.0
    assert b[0] == 0.0
    assert b[2] == 0.0


@pytest.mark.asyncio
async def test_recall_with_core_memory_candidates(storm_with_memory):
    """Test full recall pipeline with real memory candidates."""
    result = await storm_with_memory.recall("test query", limit=10)

    # Should return STORM result with fetched items
    assert result.source == "storm"
    assert len(result.items) == 3  # Mock returns 3 items
    assert len(result.scores) == 3

    # Evidence tags should be present
    assert "evidence_tags" in result.metadata
    assert "ot" in result.metadata["evidence_tags"]
    assert "coh" in result.metadata["evidence_tags"]
    assert "pers" in result.metadata["evidence_tags"]


@pytest.mark.asyncio
async def test_recall_importance_weighting_affects_cost(storm_with_memory):
    """Test that importance weighting affects OT cost computation."""
    # Mock returns items with varying scores
    storm_with_memory.core_memory.recall_memories.return_value = [
        {"content": "high score", "relevance_score": 0.9},
        {"content": "low score", "relevance_score": 0.1},
    ]

    result = await storm_with_memory.recall("test query", limit=10)

    # OT cost should reflect importance-weighted transport
    ot_cost = result.metadata["evidence_tags"]["ot"]
    assert isinstance(ot_cost, float)
    assert ot_cost >= 0.0


@pytest.mark.asyncio
async def test_recall_hybrid_mode_uses_base_fallback(storm_no_memory):
    """Test hybrid mode with base_fallback even without core memory."""
    base_fallback = MemoryRecallResult(
        items=[{"content": "base item"}],
        scores=[0.5],
        metadata={},
    )

    result = await storm_no_memory.recall(
        "test query",
        limit=10,
        base_fallback=base_fallback,
    )

    # Should use hybrid source
    assert result.source == "storm_hybrid"
    assert len(result.items) == 1


@pytest.mark.asyncio
async def test_recall_pure_mode_empty_without_memory(storm_no_memory):
    """Test pure STORM mode returns empty without core memory."""
    result = await storm_no_memory.recall("test query", limit=10)

    # Pure mode without candidates returns empty
    assert result.source == "storm"
    assert len(result.items) == 0
    assert len(result.scores) == 0


@pytest.mark.asyncio
async def test_coarse_filtering_respects_limit(storm_with_memory, mock_core_memory):
    """Test that coarse filtering fetches more than limit, then refines."""
    # Mock returns many candidates
    mock_core_memory.recall_memories.return_value = [
        {"content": f"item {i}", "relevance_score": 0.9 - i * 0.01} for i in range(100)
    ]

    items, scores = await storm_with_memory._fetch_candidates("test query", limit=10)

    # Should fetch k_coarse candidates but return only limit
    call_kwargs = mock_core_memory.recall_memories.call_args.kwargs
    assert call_kwargs["limit"] == 64  # k_coarse default
    assert len(items) == 10  # Refined to limit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
