"""Failure/compatibility checks for chat recall without model/network downloads."""

import asyncio
import sqlite3

import pytest

from Aetherra.aetherra_core.memory import chat_retrieval
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem


def test_chat_recall_read_failure_propagates(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory = LyrixaMemorySystem(str(tmp_path / "memory.db"))
    try:
        memory.ensure_connection().execute("DROP TABLE memories")
        with pytest.raises(sqlite3.OperationalError):
            asyncio.run(memory.recall_chat_memories("a personal question"))
    finally:
        memory.close()


def test_chat_recall_model_failure_is_not_an_empty_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory = LyrixaMemorySystem(str(tmp_path / "memory.db"))
    try:
        receipt = asyncio.run(
            memory.store_memory({"role": "user", "content": "Synthetic personal fact."})
        )
        assert receipt

        def unavailable():
            raise RuntimeError("embedding_model_unavailable")

        monkeypatch.setattr(chat_retrieval, "_encoder", unavailable)
        with pytest.raises(RuntimeError, match="embedding_model_unavailable"):
            asyncio.run(memory.recall_chat_memories("personal fact"))
        # Existing substring callers still work without an embedding dependency.
        legacy = asyncio.run(memory.recall_memories("Synthetic personal fact."))
        assert [m.id for m in legacy] == [receipt]
    finally:
        memory.close()


def test_questions_and_assistant_output_do_not_become_fact_evidence(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    memory = LyrixaMemorySystem(str(tmp_path / "memory.db"))
    try:
        for content in (
            {"role": "assistant", "content": "An invented personal fact."},
            {"role": "user", "content": "Is this invented personal fact true?"},
            {"event": "conversation_start"},
        ):
            assert asyncio.run(memory.store_memory(content))
        current = asyncio.run(
            memory.store_memory({"role": "user", "content": "Current statement."})
        )
        # Real selection should produce no candidates and not load a model.
        monkeypatch.setattr(
            chat_retrieval,
            "_encoder",
            lambda: pytest.fail("No candidates should be embedded"),
        )
        assert (
            asyncio.run(
                memory.recall_chat_memories("personal fact", exclude_id=current)
            )
            == []
        )
    finally:
        memory.close()


def test_unavailable_provider_fallback_does_not_claim_recall():
    from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine

    text = AetherraEngine._generate_response(
        None, "What is my secret?", {"reasoning": "invented answer"}, []
    )
    assert "can't reach my language model" in text
    assert "invented answer" not in text


def test_mixed_statement_and_question_remains_retrievable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    memory = LyrixaMemorySystem(str(tmp_path / "memory.db"))
    fact = {"role": "user", "content": "My dog's name is Luna. Can you remember that?"}
    try:
        saved_id = asyncio.run(memory.store_memory(fact))
        asyncio.run(
            memory.store_memory({"role": "user", "content": "Is my dog called Nova?"})
        )
        hits = asyncio.run(memory.recall_chat_memories("What is my dog's name?"))
        assert [hit.id for hit in hits] == [saved_id]
        assert hits[0].content == fact
    finally:
        memory.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("old_core", [False, True])
async def test_launcher_chat_recall_preserves_legacy_memory_interfaces(
    tmp_path, monkeypatch, old_core
):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    import aetherra_os_launcher as launcher_module
    from Aetherra.aetherra_core.engine import aetherra_engine as core_engine

    monkeypatch.chdir(tmp_path)
    engine = SimpleNamespace()
    monkeypatch.setattr(core_engine, "boot", AsyncMock(return_value=engine))
    monkeypatch.setattr(launcher_module, "register_service", AsyncMock())
    recall = AsyncMock(return_value=[{"id": "legacy-record"}])
    memory = (
        SimpleNamespace(core_memory=SimpleNamespace(recall_memories=recall))
        if old_core
        else SimpleNamespace(recall=recall)
    )
    launcher = launcher_module.AetherraOSLauncher()
    launcher.systems["memory"] = SimpleNamespace(impl=memory)
    await launcher._load_aetherra_engine({})
    hits = await engine.memory_system.recall_chat_memories(
        "personal fact", limit=3, exclude_id="current-record"
    )
    assert hits == [{"id": "legacy-record"}]
    if old_core:
        recall.assert_awaited_once_with(
            query_text="personal fact", limit=3, memory_type="conversation"
        )
    else:
        recall.assert_awaited_once_with(query="personal fact", limit=3)


def test_long_message_keeps_evidence_in_generation_budget():
    from Aetherra.aetherra_core.engine.aetherra_engine import (
        MAX_LLM_PROMPT_CHARS,
        MAX_MESSAGE_CHARS,
        AetherraEngine,
    )

    engine = AetherraEngine.__new__(AetherraEngine)
    prompt = engine._build_llm_prompt(
        "x" * MAX_MESSAGE_CHARS,
        [{"id": "opaque-saved-id", "content": "Synthetic remembered detail."}],
    )
    assert len(prompt) <= MAX_LLM_PROMPT_CHARS
    assert "opaque-saved-id" in prompt
    assert "Synthetic remembered detail." in prompt


@pytest.mark.asyncio
async def test_overlapping_turns_keep_their_own_retrieval_trace(tmp_path, monkeypatch):
    """A slow generation must not report another turn's retrieved record IDs."""
    from types import SimpleNamespace

    from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setenv("AETHERRA_AB_RECALL_MODE", "classical")
    monkeypatch.delenv("AETHERRA_INTELLIGENCE_PROVIDER", raising=False)
    started, release = asyncio.Event(), asyncio.Event()

    class SlowGenerator:
        primary_provider = SimpleNamespace(value="openai")

        def get_current_model_info(self):
            return {"provider": "openai", "model": "slow-context-responder"}

        async def generate_response(self, prompt):
            if "User: Who taught me to repair my bicycle tire?" in prompt:
                started.set()
                await release.wait()
            return "My answer uses the supplied memories."

        async def close(self, **kwargs):
            return {"ok": True}

    engine = AetherraEngine()
    engine.initialized = True
    engine._llm_manager = SlowGenerator()
    engine._llm_selected = True
    try:
        await engine.start_conversation()
        saved_id = await engine.memory_system.store_memory(
            {
                "role": "user",
                "content": "My aunt Leona taught me to mend a flat bike tire.",
            }
        )
        await engine.memory_system.store_memory(
            {"role": "user", "content": "My favorite breakfast is blueberry pancakes."}
        )
        first = asyncio.create_task(
            engine.process_message("Who taught me to repair my bicycle tire?")
        )
        await asyncio.wait_for(started.wait(), 60)
        second = await engine.process_message("What do I like eating for breakfast?")
        release.set()
        result = await first
        assert saved_id in result["recall"]["record_ids"]
        assert result["recall"]["record_ids"] == result["llm"]["evidence_ids"]
        assert result["recall"]["record_ids"] != second["recall"]["record_ids"]
    finally:
        release.set()
        await engine.shutdown()
