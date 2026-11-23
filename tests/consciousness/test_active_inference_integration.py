# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness import affect_engine, ethics_critic
from Aetherra.consciousness.active_inference import get_active_inference
from Aetherra.consciousness.episodic_store import get_episodic_store


@pytest.mark.parametrize(
    ("plugin", "ethics_term", "score"),
    [
        ("network_plugin", None, 0.75),
        ("network_delete", "ethics_revise+0.15", 0.9),
        ("network_delete_secret", "ethics_veto+0.3", 1.0),
    ],
)
def test_active_inference_rationale_components(
    monkeypatch, tmp_path, plugin, ethics_term, score
):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_EPISODIC_PATH", str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(affect_engine, "AFFECT_ENGINE_SINGLETON", None)
    monkeypatch.setattr(ethics_critic, "ETHICS_CRITIC_SINGLETON", None)
    store = get_episodic_store()
    # Four actual errors exceed the uncertainty threshold without shared history.
    for i in range(4):
        store.new_event(
            type="action",
            content=f"error event {i}",
            source="test",
            importance=0.9,
            sub_type="error",
        )
    affect = affect_engine.get_affect_engine().compute()
    assert affect.uncertainty == pytest.approx(0.68)
    surprise, rationale = get_active_inference().estimate(plugin)
    assert "network+0.25" in rationale
    assert "uncertainty+0.2" in rationale
    if ethics_term:
        assert ethics_term in rationale
    else:
        assert "ethics_" not in rationale
    assert surprise == pytest.approx(score)
