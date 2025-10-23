# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for STORM PR-3: SQLite persistence layer for embeddings/cells.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine
from Aetherra.aetherra_core.memory.storm.persistence import StormStorage


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> str:
    return str(tmp_path / "storm_test.db")


def test_storage_init_and_schema(tmp_db_path: str):
    storage = StormStorage(tmp_db_path)
    try:
        # Verify meta schema_version exists
        assert storage._conn is not None
        conn = storage._conn
        cur = conn.cursor()
        row = cur.execute(
            "SELECT value FROM storm_meta WHERE key='schema_version'"
        ).fetchone()
        assert row is not None
        assert int(row[0]) >= 1
    finally:
        storage.close()


def test_storage_upsert_and_get(tmp_db_path: str):
    storage = StormStorage(tmp_db_path)
    try:
        content = "Hello persistence!"
        emb = np.arange(4, dtype=np.float32)
        h = storage.upsert_embedding(content, emb)
        assert h

        # Get embedding back
        loaded = storage.get_embedding(content)
        assert loaded is not None
        assert loaded.dtype == emb.dtype
        assert loaded.shape == emb.shape
        assert np.allclose(loaded, emb)
    finally:
        storage.close()


@pytest.mark.asyncio
async def test_engine_persists_embeddings(tmp_db_path: str):
    # Mock core memory to return two items
    mock_core = MagicMock()
    mock_core.recall_memories = AsyncMock(
        return_value=[
            {"content": "alpha", "relevance_score": 0.9},
            {"content": "beta", "relevance_score": 0.8},
        ]
    )

    cfg = StormConfig(enabled=True, sqlite_path=tmp_db_path)
    engine = StormEngine(config=cfg, core_memory=mock_core)

    # Run recall to trigger embedding generation/persist
    res = await engine.recall("alpha", limit=2)
    assert res.items
    assert len(res.items) == 2

    # Verify DB has persisted rows for items
    storage = StormStorage(tmp_db_path)
    try:
        for item in ["alpha", "beta"]:
            emb = storage.get_embedding(item)
            assert emb is not None
            assert isinstance(emb, np.ndarray)
            assert emb.size > 0
    finally:
        storage.close()


@pytest.mark.asyncio
async def test_engine_reads_persisted_embeddings(tmp_db_path: str):
    # Pre-populate DB with embedding for an item
    storage = StormStorage(tmp_db_path)
    try:
        pre_emb = np.random.RandomState(42).randn(128).astype(np.float32)
        storage.upsert_embedding("gamma", pre_emb)
    finally:
        storage.close()

    # Engine should read persisted embedding instead of recomputing
    mock_core = MagicMock()
    mock_core.recall_memories = AsyncMock(
        return_value=[
            {"content": "gamma", "relevance_score": 0.7},
        ]
    )

    cfg = StormConfig(enabled=True, sqlite_path=tmp_db_path)
    engine = StormEngine(config=cfg, core_memory=mock_core)

    res = await engine.recall("whatever", limit=1)
    assert res.items
    assert len(res.items) == 1

    # Load embedding and ensure it's the pre-populated one
    storage2 = StormStorage(tmp_db_path)
    try:
        loaded = storage2.get_embedding("gamma")
        assert loaded is not None
        assert np.allclose(loaded, pre_emb)
    finally:
        storage2.close()
