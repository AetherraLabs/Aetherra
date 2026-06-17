import asyncio
import json
from datetime import datetime
from types import SimpleNamespace

import pytest

from Aetherra.consciousness.consciousness_orchestrator import ConsciousnessOrchestrator


class FakeBridge:
    is_running = True

    def __init__(self):
        self.messages = []
        self.shutdown_called = False

    def is_consciousness_bridge_healthy(self):
        return True

    def get_all_system_states(self):
        return {}

    def send_message(self, message):
        self.messages.append(message)

    async def shutdown(self):
        self.shutdown_called = True


class FakeAgentRegistry:
    is_running = True

    def __init__(self):
        self.shutdown_called = False

    def get_registry_statistics(self):
        return {
            "active_agents": 0,
            "total_agents": 0,
            "total_services": 0,
            "unique_capabilities": 0,
        }

    async def shutdown(self):
        self.shutdown_called = True


class FakeMetaLayer:
    is_running = True

    def __init__(self):
        self.shutdown_called = False

    def get_collective_metrics(self):
        return SimpleNamespace(
            collective_consciousness=0.7,
            emergent_behaviors_detected=0,
            problem_solving_efficiency=0.8,
        )

    async def shutdown(self):
        self.shutdown_called = True


class FakeNarrativeLayer:
    enabled = False

    def __init__(self):
        self.started = False
        self.stopped = False

    def start(self, background=False):
        self.started = True

    def stop(self):
        self.stopped = True

    def on_chapter(self, _handler):
        pass


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
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


def _orchestrator():
    bridge = FakeBridge()
    registry = FakeAgentRegistry()
    meta = FakeMetaLayer()
    narrative = FakeNarrativeLayer()
    orchestrator = ConsciousnessOrchestrator(
        component_initializers={
            "consciousness_bridge": lambda: bridge,
            "agent_registry": lambda: registry,
            "meta_layer_core": lambda: meta,
            "lyrixa_consciousness": lambda: None,
        },
        narrative_factory=lambda: narrative,
    )
    return orchestrator, bridge, registry, meta, narrative


def test_orchestrator_initialize_is_guardian_audited_without_message_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    orchestrator, bridge, _registry, _meta, _narrative = _orchestrator()

    asyncio.run(orchestrator.initialize())

    assert orchestrator.is_initialized is True
    assert orchestrator.is_running is True
    assert len(bridge.messages) == 2
    ledger_text = _audit_text(tmp_path)
    assert "Aetherra Consciousness System is now fully operational" not in ledger_text
    assert "Welcome to full consciousness" not in ledger_text
    actions = [entry["details"]["intent"]["action"] for entry in _audit_entries(tmp_path)]
    assert "consciousness.orchestrator_initialize" in actions
    assert "consciousness.orchestrator_component_initialize" in actions
    assert "consciousness.orchestrator_message_dispatch" in actions
    assert "consciousness.orchestrator_mark_online" in actions


def test_orchestrator_initialize_denial_preserves_offline_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-orchestrator-client",
        strict=True,
    )
    orchestrator, bridge, _registry, _meta, _narrative = _orchestrator()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(orchestrator.initialize())

    assert orchestrator.is_initialized is False
    assert orchestrator.is_running is False
    assert orchestrator.consciousness_bridge is None
    assert bridge.messages == []


def test_orchestrator_shutdown_is_guardian_audited_and_clears_references(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    orchestrator, bridge, registry, meta, narrative = _orchestrator()
    asyncio.run(orchestrator.initialize())

    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr(asyncio, "sleep", _no_sleep)

    asyncio.run(orchestrator.shutdown())

    assert bridge.shutdown_called is True
    assert registry.shutdown_called is True
    assert meta.shutdown_called is True
    assert orchestrator.consciousness_bridge is None
    assert orchestrator.agent_registry is None
    assert orchestrator.meta_layer_core is None
    assert orchestrator.is_initialized is False
    assert orchestrator.is_running is False
    assert narrative.stopped is True
    actions = [entry["details"]["intent"]["action"] for entry in _audit_entries(tmp_path)]
    assert "consciousness.orchestrator_shutdown" in actions
    assert "consciousness.orchestrator_component_shutdown" in actions
    assert "consciousness.orchestrator_clear_components" in actions


def test_orchestrator_metrics_write_is_guardian_audited_without_raw_path_or_id(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    metrics_path = tmp_path / "private_metrics.txt"
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_METRICS_PATH", str(metrics_path))
    orchestrator, _bridge, _registry, _meta, _narrative = _orchestrator()
    chapter = SimpleNamespace(
        id="private-chapter-id",
        coherence_index=0.91,
        end_ts=datetime.now(),
    )

    orchestrator._on_new_chapter(chapter)

    assert orchestrator.last_narrative_coherence == 0.91
    assert metrics_path.exists()
    ledger_text = _audit_text(tmp_path)
    assert "private-chapter-id" not in ledger_text
    assert str(metrics_path) not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.orchestrator_narrative_metrics_write"
    )
