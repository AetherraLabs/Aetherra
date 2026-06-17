import asyncio
import json

import pytest

from Aetherra.consciousness.quantum import quantum_tunneling_logic as qtl
from Aetherra.consciousness.quantum.quantum_tunneling_logic import (
    BarrierType,
    LogicalBarrier,
    QuantumTunnelingEngine,
    TunnelingPath,
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


def _barrier():
    return LogicalBarrier(
        barrier_id="secret_barrier_id",
        barrier_type=BarrierType.PARADIGM_BARRIER,
        height=0.8,
        width=1.1,
        description="private barrier description",
        conventional_solution_prob=0.1,
        breakthrough_potential=0.9,
        energy_required=800.0,
    )


def _path():
    return TunnelingPath(
        path_id="private_path_id",
        source_state="private_source_state",
        target_state="private_target_state",
        barriers=[_barrier()],
        tunneling_probability=1.0,
        energy_cost=10.0,
        breakthrough_value=0.95,
        path_complexity=1.0,
    )


def _snapshot(engine):
    return {
        "history": list(engine.breakthrough_history),
        "attempts": engine.tunneling_attempts,
        "successful": engine.successful_tunnelings,
        "rate": engine.breakthrough_rate,
        "innovation": engine.innovation_score,
    }


def test_quantum_tunneling_attempt_is_guardian_audited_without_path_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(qtl.np.random, "random", lambda: 0.0)
    engine = QuantumTunnelingEngine()
    path = _path()

    solution = asyncio.run(engine.attempt_quantum_tunneling(path, 20.0))

    assert solution is not None
    assert engine.tunneling_attempts == 1
    assert engine.successful_tunnelings == 1
    ledger_text = _audit_text(tmp_path)
    assert "private_path_id" not in ledger_text
    assert "private_source_state" not in ledger_text
    assert "private_target_state" not in ledger_text
    assert "secret_barrier_id" not in ledger_text
    assert "private barrier description" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_tunneling_attempt"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["barrier_count"] == 1
    assert metadata["barrier_types"] == ["paradigm_barrier"]
    assert metadata["path_hash"]


def test_quantum_tunneling_attempt_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-tunneling-logic-client",
        strict=True,
    )
    engine = QuantumTunnelingEngine()
    path = _path()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.attempt_quantum_tunneling(path, 20.0))

    assert _snapshot(engine) == before
    ledger_text = _audit_text(tmp_path)
    assert "private_path_id" not in ledger_text
    assert "secret_barrier_id" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_tunneling_attempt"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
