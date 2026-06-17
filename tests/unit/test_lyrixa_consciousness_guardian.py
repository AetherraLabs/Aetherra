import asyncio
import json

import pytest

from Aetherra.consciousness.core.consciousness_bridge import ConsciousnessMessage
from Aetherra.consciousness.core.lyrixa_consciousness import LyrixaConsciousnessEngine
from Aetherra.consciousness.core.meta_layer_core import (
    AgentProfile,
    CollectiveIntelligenceMetrics,
)


class FakeBridge:
    def __init__(self):
        self.messages = []
        self.handlers = {}

    def register_message_handler(self, message_type, handler):
        self.handlers[message_type] = handler

    def send_message(self, message):
        self.messages.append(message)


class FakeMetaLayer:
    def __init__(self, agents=None, metrics=None):
        self.agents = agents or {}
        self.metrics = metrics or CollectiveIntelligenceMetrics(
            total_agents=len(self.agents),
            active_agents=len(self.agents),
            collective_consciousness=0.75,
            problem_solving_efficiency=0.85,
        )
        self.event_handlers = {}

    def register_event_handler(self, event_type, handler):
        self.event_handlers[event_type] = handler

    def get_all_agents(self):
        return dict(self.agents)

    def get_collective_metrics(self):
        return self.metrics


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


def _engine(agents=None, metrics=None):
    return LyrixaConsciousnessEngine(
        consciousness_bridge=FakeBridge(),
        meta_layer_core=FakeMetaLayer(agents=agents, metrics=metrics),
    )


def test_lyrixa_ethical_decision_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = _engine()

    decision = asyncio.run(
        engine._make_ethical_decision(
            "private decision context",
            ["help private-user", "harm private-system"],
            ["private-stakeholder"],
        )
    )

    assert engine.ethical_decisions == [decision]
    ledger_text = _audit_text(tmp_path)
    assert "private decision context" not in ledger_text
    assert "private-user" not in ledger_text
    assert "private-system" not in ledger_text
    assert "private-stakeholder" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.lyrixa_ethical_decision_record"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["option_count"] == 2
    assert metadata["stakeholder_count"] == 1


def test_lyrixa_ethical_decision_denial_preserves_decision_history(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-lyrixa-client",
        strict=True,
    )
    engine = _engine()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            engine._make_ethical_decision(
                "private decision context",
                ["help private-user", "harm private-system"],
                ["private-stakeholder"],
            )
        )

    assert engine.ethical_decisions == []


def test_lyrixa_agent_behavior_denial_preserves_relationship_and_messages(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-lyrixa-client",
        strict=True,
    )
    engine = _engine()
    engine.agent_relationships["private-agent"] = {
        "trust_level": 0.5,
        "collaboration_history": [],
        "performance_trend": "stable",
    }
    message = ConsciousnessMessage(
        source="private-reporter",
        destination="lyrixa_consciousness",
        message_type="agent_behavior_report",
        payload={
            "agent_id": "private-agent",
            "behavior_type": "concerning",
            "description": "private behavior details",
        },
        timestamp=engine.last_reflection,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine._handle_agent_behavior_report(message))

    assert engine.agent_relationships["private-agent"]["trust_level"] == 0.5
    assert engine.agent_relationships["private-agent"]["collaboration_history"] == []
    assert engine.consciousness_bridge.messages == []


def test_lyrixa_agent_promotion_is_guardian_audited_without_agent_identity(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    agent = AgentProfile(
        agent_id="private-agent",
        name="private agent name",
        agent_type="worker",
        capabilities=["private-capability"],
        system_origin="private-system",
        success_rate=0.95,
    )
    engine = _engine(agents={"private-agent": agent})
    engine.agent_relationships["private-agent"] = {
        "trust_level": 0.95,
        "collaboration_history": [],
        "performance_trend": "stable",
    }

    asyncio.run(engine._consider_agent_promotion(agent))

    assert len(engine.orchestration_decisions) == 1
    assert len(engine.consciousness_bridge.messages) == 1
    ledger_text = _audit_text(tmp_path)
    assert "private-agent" not in ledger_text
    assert "private-system" not in ledger_text
    entry = next(
        item
        for item in _audit_entries(tmp_path)
        if item["details"]["intent"]["action"] == "consciousness.lyrixa_agent_promotion"
    )
    assert entry["details"]["intent"]["action"] == "consciousness.lyrixa_agent_promotion"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["decision_count_before"] == 0
    assert metadata["relationship_trust"] == 0.95
