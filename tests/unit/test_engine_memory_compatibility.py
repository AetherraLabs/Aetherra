# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from __future__ import annotations

import asyncio
import threading

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
