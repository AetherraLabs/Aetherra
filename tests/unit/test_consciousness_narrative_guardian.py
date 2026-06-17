import json
from datetime import datetime, timedelta

import pytest

from Aetherra.consciousness.episodic_store import get_episodic_store
from Aetherra.consciousness.narrator import NarrativeLayer
from Aetherra.consciousness.schemas.episodic_event import (
    EpisodicEvent,
    EventAttribution,
)


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_EPISODIC_PATH", str(tmp_path / "events.jsonl"))
    monkeypatch.setenv("AETHERRA_NARRATIVE_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_NARRATIVE_MIN_EVENTS", "3")
    monkeypatch.setenv("AETHERRA_NARRATIVE_WINDOW_MIN", "2")
    monkeypatch.setenv("AETHERRA_NARRATIVE_CHAPTER_DIR", str(tmp_path / "chapters"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _audit_text(root):
    return (root / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _audit_entries(root):
    return [
        json.loads(line)
        for line in _audit_text(root).splitlines()
        if line.strip()
    ]


def _seed_events(count=5):
    store = get_episodic_store()
    for i in range(count):
        event = EpisodicEvent(
            schema_version=1,
            id=f"private-event-id-{i}",
            type="thought",
            sub_type="guardian-test",
            content=f"private narrative seed content {i}",
            importance=0.8,
            attribution=EventAttribution(
                source="private-source", agent=None, confidence=0.9
            ),
            ts=datetime.utcnow() - timedelta(seconds=5),
            raw={"secret": f"value-{i}"},
            workspace_priority=None,
        )
        store.append(event)
    return store


def test_narrative_chapter_commit_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    store = _seed_events()
    layer = NarrativeLayer()

    layer._maybe_generate_chapter()

    chapter_files = list((tmp_path / "chapters").glob("chapter-*.json"))
    assert chapter_files
    narrative_events = [e for e in store.list_recent(20) if e.type == "narrative"]
    assert narrative_events
    ledger_text = _audit_text(tmp_path)
    assert "private narrative seed content" not in ledger_text
    assert "private-event-id" not in ledger_text
    assert "private-source" not in ledger_text
    assert str(chapter_files[0]) not in ledger_text
    entry = _audit_entries(tmp_path)[-2]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.narrative_chapter_commit"
    )
    assert entry["details"]["intent"]["metadata"]["referenced_event_count"] > 0
    assert entry["details"]["intent"]["metadata"]["summary_length"] > 0


def test_narrative_chapter_denial_skips_file_write_and_event_append(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    store = _seed_events()
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-consciousness-client",
        strict=True,
    )
    layer = NarrativeLayer()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        layer._maybe_generate_chapter()

    assert not (tmp_path / "chapters").exists()
    narrative_events = [e for e in store.list_recent(20) if e.type == "narrative"]
    assert not narrative_events
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.narrative_chapter_commit"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
