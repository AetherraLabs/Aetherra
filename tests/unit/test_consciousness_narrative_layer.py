#!/usr/bin/env python3
"""Narrative layer tests (Phase 1)

Validates that a chapter is generated given enough synthetic episodic events and
that coherence_index lies within [0,1].
"""

from __future__ import annotations

# Standard library imports
from datetime import datetime, timedelta

# Aetherra imports
from Aetherra.consciousness.episodic_store import get_episodic_store
from Aetherra.consciousness.narrator import get_narrative_layer
from Aetherra.consciousness.schemas.episodic_event import (
    EpisodicEvent,
    EventAttribution,
)


def test_narrative_chapter_generation(tmp_path, monkeypatch):
    # Isolate store & narrative output
    monkeypatch.setenv("AETHERRA_EPISODIC_PATH", str(tmp_path / "events.jsonl"))
    monkeypatch.setenv("AETHERRA_NARRATIVE_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_NARRATIVE_MIN_EVENTS", "5")
    monkeypatch.setenv("AETHERRA_NARRATIVE_WINDOW_MIN", "1")
    monkeypatch.setenv("AETHERRA_NARRATIVE_MAX_EVENTS", "50")
    monkeypatch.setenv("AETHERRA_NARRATIVE_CHAPTER_DIR", str(tmp_path / "chapters"))

    store = get_episodic_store()

    # Seed events across types
    for i in range(8):
        evt = EpisodicEvent(
            schema_version=1,
            id=f"evt-{i}",
            type="thought" if i % 2 == 0 else "action",
            sub_type="plan" if i % 2 == 0 else "exec",
            content=f"event {i} synthetic content",
            importance=0.5,
            attribution=EventAttribution(source="test", agent=None, confidence=0.9),
            ts=datetime.utcnow() - timedelta(seconds=5),
            raw={"i": i},
            workspace_priority=None,
        )
        store.append(evt)

    nl = get_narrative_layer()
    nl.start(background=False)  # Run loop once inline
    # Force immediate chapter attempt
    nl._maybe_generate_chapter()  # noqa: SLF001 (intentional internal call for test)

    # Check chapter file existence
    chapter_dir = tmp_path / "chapters"
    chapter_files = list(chapter_dir.glob("chapter-*.json"))
    assert chapter_files, "No chapter generated"

    # Basic coherence check via last event appended of type narrative
    recent = store.list_recent(20)
    narrative_events = [e for e in recent if e.type == "narrative"]
    assert narrative_events, "Narrative event not recorded"
    coherence = (
        narrative_events[-1].raw.get("coherence") if narrative_events[-1].raw else None
    )
    assert coherence is not None and 0.0 <= coherence <= 1.0, "Coherence out of bounds"
