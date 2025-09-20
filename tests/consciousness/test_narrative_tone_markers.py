# Aetherra imports
from Aetherra.consciousness.episodic_store import get_episodic_store
from Aetherra.consciousness.narrator import NarrativeLayer


def test_narrative_tone_contains_affect_or_ethics(monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_NARRATIVE_ENABLED", "1")
    store = get_episodic_store()
    # Seed enough events to force salient selection
    for i in range(20):
        store.new_event(
            type="thought",
            content=f"I am evaluating scenario {i}",
            source="tone_test",
            importance=0.6,
            sub_type="planning" if i % 2 == 0 else "reflection",
        )
    nl = NarrativeLayer()
    chapter = nl._build_chapter(store.list_recent(50))
    assert "I noted" in chapter.summary
    # Expect at least one tone marker
    assert ("affect[" in chapter.summary) or ("ethics[" in chapter.summary)
