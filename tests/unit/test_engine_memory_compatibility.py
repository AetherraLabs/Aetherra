# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from __future__ import annotations

import asyncio
import sqlite3
import threading
from datetime import datetime

import pytest

from Aetherra.aetherra_core.cognitive.reasoning_engine import (
    ReasoningContext as CognitiveReasoningContext,
)
from Aetherra.aetherra_core.cognitive.reasoning_engine import (
    ReasoningEngine as CognitiveReasoningEngine,
)
from Aetherra.aetherra_core.engine.reasoning_engine import (
    ReasoningContext as EngineReasoningContext,
)
from Aetherra.aetherra_core.engine.reasoning_engine import (
    ReasoningEngine as EngineReasoningEngine,
)
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem


def test_reasoning_engine_shim_reexports_canonical_symbols():
    assert EngineReasoningContext is CognitiveReasoningContext
    assert EngineReasoningEngine is CognitiveReasoningEngine


def test_memory_core_connection_supports_cross_thread_usage(tmp_path):
    memory = LyrixaMemorySystem(str(tmp_path / "compat_memory.db"))
    errors: list[BaseException] = []

    async def _store_main_thread() -> None:
        memory_id = await memory.store_memory(
            content={"text": "main thread memory"},
            context={"thread": "main"},
            tags=["compat"],
            importance=0.5,
            memory_type="conversation",
        )
        assert memory_id

    asyncio.run(_store_main_thread())

    def _worker() -> None:
        async def _store_worker_thread() -> None:
            memory_id = await memory.store_memory(
                content={"text": "worker thread memory"},
                context={"thread": "worker"},
                tags=["compat"],
                importance=0.6,
                memory_type="conversation",
            )
            assert memory_id
            recalled = await memory.recall_memories("worker thread memory", limit=2)
            assert any(
                isinstance(item.content, dict)
                and item.content.get("text") == "worker thread memory"
                for item in recalled
            )

        try:
            asyncio.run(_store_worker_thread())
        except BaseException as exc:  # pragma: no cover - assertion collected below
            errors.append(exc)

    worker = threading.Thread(target=_worker)
    worker.start()
    worker.join(timeout=10)

    memory.close()

    assert not errors
    assert not worker.is_alive()


@pytest.mark.asyncio
async def test_failed_memory_transaction_returns_no_receipt_or_cache(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    memory = LyrixaMemorySystem(str(tmp_path / "failed.db"))
    try:
        receipt = await memory.store_memory(
            {"text": "synthetic"}, context={"time": datetime.now()}
        )
        assert receipt == ""
        assert memory.memory_cache == {}
        assert (
            memory.ensure_connection()
            .execute("SELECT COUNT(*) FROM memories")
            .fetchone()[0]
            == 0
        )
    finally:
        memory.close()


@pytest.mark.asyncio
async def test_readonly_memory_does_not_acknowledge_failed_insert(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "readonly.db"
    memory = LyrixaMemorySystem(str(path))
    memory.close()
    memory.conn = sqlite3.connect("file:" + path.as_posix() + "?mode=ro", uri=True)
    try:
        receipt = await memory.store_memory(
            {"text": "synthetic"}, context={"time": "now"}
        )
        assert receipt == ""
        assert memory.memory_cache == {}
        assert memory.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == 0
    finally:
        memory.close()


@pytest.mark.asyncio
async def test_failed_commit_and_rollback_cannot_commit_ghost_memory(
    monkeypatch, tmp_path
):
    class FailingTransaction(sqlite3.Connection):
        def commit(self):
            raise sqlite3.OperationalError("controlled_commit_failure")

        def rollback(self):
            raise sqlite3.OperationalError("controlled_rollback_failure")

    monkeypatch.chdir(tmp_path)
    path = tmp_path / "failed_transaction.db"
    memory = LyrixaMemorySystem(str(path))
    memory.close()
    memory.conn = sqlite3.connect(path, factory=FailingTransaction)
    try:
        receipt = await memory.store_memory({"text": "uncommitted_marker"}, context={})
        assert receipt == ""
        assert memory.memory_cache == {}
        assert memory.conn is None
        next_receipt = await memory.store_memory(
            {"text": "committed_marker"}, context={}
        )
        assert next_receipt
        assert await memory.recall_memories("uncommitted_marker") == []
        assert len(await memory.recall_memories("committed_marker")) == 1
    finally:
        memory.close()


@pytest.mark.asyncio
async def test_failed_transaction_close_retains_owner_and_blocks_reuse(
    monkeypatch, tmp_path
):
    class FailedCleanup(sqlite3.Connection):
        def commit(self):
            raise sqlite3.OperationalError("controlled_commit_failure")

        def rollback(self):
            raise sqlite3.OperationalError("controlled_rollback_failure")

        def close(self):
            raise sqlite3.OperationalError("controlled_close_failure")

    monkeypatch.chdir(tmp_path)
    path = tmp_path / "failed_cleanup.db"
    memory = LyrixaMemorySystem(str(path))
    memory.close()
    connection = sqlite3.connect(path, factory=FailedCleanup)
    memory.conn = connection
    try:
        assert (
            await memory.store_memory({"text": "uncommitted_marker"}, context={}) == ""
        )
        assert memory.conn is connection
        assert memory.memory_cache == {}
        with pytest.raises(RuntimeError, match="^memory_transaction_unavailable$"):
            memory.ensure_connection()
    finally:
        sqlite3.Connection.close(connection)
        memory.conn = None
