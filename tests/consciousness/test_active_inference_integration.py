from Aetherra.consciousness.active_inference import get_active_inference
from Aetherra.consciousness.affect_engine import get_affect_engine
from Aetherra.consciousness.episodic_store import get_episodic_store
from Aetherra.consciousness.ethics_critic import get_ethics_critic


def test_active_inference_rationale_components(monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    store = get_episodic_store()
    # Seed events to raise uncertainty via affect (inject high-importance error events)
    for i in range(3):
        store.new_event(
            type="action",
            content=f"error event {i}",
            source="test",
            importance=0.9,
            sub_type="error",
        )
    affect = get_affect_engine().compute()
    critic = get_ethics_critic()
    decision, risk, flags, counter = critic.evaluate("delete remote http config")
    surprise, rationale = get_active_inference().estimate("network_plugin")
    # Rationale should reflect network and possibly uncertainty and ethics terms
    assert "network+0.25" in rationale
    assert ("uncertainty+0.2" in rationale) or affect.uncertainty <= 0.6
    # If ethics flagged veto or revise, rationale should include corresponding tag
    assert (
        ("ethics_veto+0.3" in rationale)
        or ("ethics_revise+0.15" in rationale)
        or risk < 0.5
    )
