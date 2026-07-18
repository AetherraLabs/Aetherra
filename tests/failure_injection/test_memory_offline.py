#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Failure injection: simulate memory offline and assert graceful fallback.

This test does NOT require real memory DB corruption; it monkeypatches the
memory system retrieval to raise and ensures the higher-level component
(Engine or Chat bridge) returns a safe error or fallback structure.
"""

# Standard library imports
import asyncio

# Third party imports
import pytest

pytestmark = pytest.mark.unit


class FailingRecallMemory:
    async def store_memory(self, *args, **kwargs):
        return "memory-test-id"

    async def recall_memories(self, *args, **kwargs):
        raise RuntimeError("simulated db unavailable")


class StableReasoning:
    async def reason(self, context):
        from Aetherra.aetherra_core.engine.reasoning_engine import ReasoningResult

        return ReasoningResult(
            conclusion="respond with degraded memory context",
            confidence=0.75,
            reasoning_steps=["memory recall failed safely", "fallback response allowed"],
            supporting_evidence=[],
            alternatives=["ask user to retry later"],
            metadata={"mode": "failure_injection"},
        )


@pytest.mark.asyncio
async def test_memory_recall_graceful(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_INTELLIGENCE_PROVIDER", "")
    monkeypatch.setenv("AETHERRA_LLM_TIMEOUT_SEC", "1")

    from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine

    engine = AetherraEngine(
        memory_db_path=str(tmp_path / "memory.db"),
        reasoning_db_path=str(tmp_path / "reasoning.db"),
        improvement_db_path=str(tmp_path / "improvement.db"),
        orchestrator_db_path=str(tmp_path / "orchestrator.db"),
    )
    engine.memory_system = FailingRecallMemory()
    engine.reasoning_engine = StableReasoning()
    engine._ensure_persistent_memory = _persistent_memory_unavailable

    result = await asyncio.wait_for(
        engine.process_message("hello", context=None),
        timeout=5.0,
    )

    assert isinstance(result, dict)
    assert result["response"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["evidence"] == []
    assert engine._last_recall_info["event"] == "degraded"
    assert engine._last_recall_info["error"]["code"] == "primary_recall_failed"


async def _persistent_memory_unavailable():
    return False
