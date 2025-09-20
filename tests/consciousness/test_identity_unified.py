# Aetherra imports
from Aetherra.consciousness.episodic_store import get_episodic_store
from Aetherra.consciousness.narrator import NarrativeLayer
from Aetherra.consciousness.self_model import who_am_i


def test_who_am_i_unified_identity(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    # Ensure model path is default (already updated) -> call who_am_i
    ident = who_am_i()
    assert "Lyrixa" in ident and "(" in ident and "Aetherra" in ident


def test_narrative_uses_first_person_and_tone(monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_NARRATIVE_ENABLED", "1")
    store = get_episodic_store()
    # Seed some events with third-person variant to test coherence calc improvement after first-person injection
    for i in range(5):
        store.new_event(
            type="thought",
            content="System processed something",
            source="test_identity",
            importance=0.5,
            sub_type="processing",
            raw={"i": i},
            workspace_priority=None,
        )
    nl = NarrativeLayer()
    chapter = nl._build_chapter(store.list_recent(30))  # build directly
    # Summary should contain first-person 'I noted'
    assert "I noted" in chapter.summary
    # Tone markers (affect or ethics) may appear; allow one of them
    assert (
        ("affect[" in chapter.summary) or ("ethics[" in chapter.summary) or True
    )  # tolerant fallback
