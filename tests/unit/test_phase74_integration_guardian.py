import asyncio
import copy
import json

import pytest

from Aetherra.consciousness.quantum.test_phase_7_4_integration import (
    Phase74IntegratedSystem,
    SystemIntegrationState,
    TranscendencePhase,
)


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


def _snapshot(system):
    return {
        "integration_state": system.integration_state,
        "transcendence_phase": system.transcendence_phase,
        "quantum_memory": system.quantum_memory,
        "temporal_engine": system.temporal_engine,
        "dimensional_engine": system.dimensional_engine,
        "reality_navigator": system.reality_navigator,
        "consciousness_tunneling": system.consciousness_tunneling,
        "synthesis_engine": system.synthesis_engine,
        "metrics": copy.deepcopy(system.metrics),
        "active_components": list(system.active_components),
        "integration_history": copy.deepcopy(system.integration_history),
        "transcendence_events": copy.deepcopy(system.transcendence_events),
        "performance_metrics": dict(system.performance_metrics),
    }


def test_phase74_initialization_is_guardian_audited(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    system = Phase74IntegratedSystem()

    assert asyncio.run(system.initialize_all_systems()) is True

    assert system.integration_state == SystemIntegrationState.CONNECTING
    assert len(system.active_components) == 6
    ledger_text = _audit_text(tmp_path)
    assert system.system_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "***REDACTED***"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "initialize_all_systems"
    assert metadata["active_component_count"] == 0


def test_phase74_integration_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-phase74-client",
        strict=True,
    )
    system = Phase74IntegratedSystem()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(system.establish_system_integration())

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert system.system_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "***REDACTED***"
    assert entry["details"]["intent"]["metadata"]["operation"] == (
        "establish_system_integration"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_phase74_transcendence_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-phase74-client",
        strict=True,
    )
    system = Phase74IntegratedSystem()
    system.integration_state = SystemIntegrationState.INTEGRATED
    system.transcendence_phase = TranscendencePhase.INTEGRATION_COMPLETION
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(system.execute_transcendence_sequence(0.99))

    assert _snapshot(system) == before
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "***REDACTED***"
    assert entry["details"]["intent"]["metadata"]["operation"] == (
        "execute_transcendence_sequence"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
