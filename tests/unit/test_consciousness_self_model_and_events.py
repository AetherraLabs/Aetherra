#!/usr/bin/env python3
"""Phase 1 Consciousness basic tests

Validates self model bootstrap/update and episodic event append + retention trimming logic (basic).
"""

from __future__ import annotations

from datetime import datetime, timedelta

from Aetherra.consciousness.episodic_store import get_episodic_store
from Aetherra.consciousness.self_model_manager import get_self_model_manager


def test_self_model_bootstrap_and_update(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERRA_SELF_MODEL_PATH", str(tmp_path / "self_model.json"))
    mgr = get_self_model_manager()
    m = mgr.get()
    assert m.identity.system_id.startswith("aetherra")
    assert m.coherence_score == 1.0

    mgr.set_resource_profile(cpu=12.5, mem_mb=256.0)
    m2 = mgr.get()
    assert m2.resources.cpu_load == 12.5
    assert m2.resources.memory_used_mb == 256.0


def test_episodic_store_append_and_retention(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERRA_EPISODIC_PATH", str(tmp_path / "events.jsonl"))
    monkeypatch.setenv("AETHERRA_EPISODIC_MAX_EVENTS", "10")
    monkeypatch.setenv(
        "AETHERRA_EPISODIC_RETENTION_HOURS", "0"
    )  # immediate retention check

    store = get_episodic_store()
    # Create older events
    for i in range(5):
        store.new_event(
            type="thought",
            content=f"old-{i}",
            source="test",
            importance=0.1,
            ts=datetime.utcnow() - timedelta(hours=1),
        )
    # Important event should bypass retention horizon
    store.new_event(
        type="thought",
        content="important",
        source="test",
        importance=0.9,
        ts=datetime.utcnow() - timedelta(hours=1),
    )
    # Recent events
    for i in range(6):
        store.new_event(
            type="thought", content=f"new-{i}", source="test", importance=0.2
        )

    recent = store.list_recent(50)
    # Ensure max events enforced (10) and important retained
    assert len(recent) <= 10
    contents = [e.content for e in recent]
    assert "important" in contents
