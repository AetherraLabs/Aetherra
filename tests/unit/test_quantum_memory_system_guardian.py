import asyncio
import json

import pytest

from Aetherra.consciousness.quantum.quantum_memory_system import (
    MemoryType,
    QuantumMemorySystem,
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
        "memory_traces": dict(system.memory_traces),
        "entanglements": dict(system.entanglements),
        "temporal_clusters": dict(system.temporal_clusters),
        "memories_stored": system.memories_stored,
        "entanglements_formed": system.entanglements_formed,
        "memory_retrievals": system.memory_retrievals,
        "evolution_events": system.evolution_events,
        "avg_retrieval_time": system.avg_retrieval_time,
    }


def test_quantum_memory_store_is_guardian_audited_without_content(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    system = QuantumMemorySystem()
    content = {"secret": "private-memory-value", "topic": "identity"}

    memory_id = asyncio.run(
        system.store_quantum_memory(
            MemoryType.EPISODIC,
            content,
            consciousness_level=0.75,
        )
    )

    assert memory_id in system.memory_traces
    ledger_text = _audit_text(tmp_path)
    assert "private-memory-value" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_memory_store"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "store"
    assert metadata["memory_type"] == "episodic"
    assert metadata["content_hash"]
    assert metadata["content_field_names"] == ["secret", "topic"]


def test_quantum_memory_store_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-memory-client",
        strict=True,
    )
    system = QuantumMemorySystem()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            system.store_quantum_memory(
                MemoryType.SEMANTIC,
                {"secret": "blocked-memory-value"},
                consciousness_level=0.5,
            )
        )

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert "blocked-memory-value" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_memory_store"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_quantum_memory_retrieve_denial_preserves_access_state(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    system = QuantumMemorySystem()
    memory_id = asyncio.run(
        system.store_quantum_memory(MemoryType.SEMANTIC, {"topic": "alpha"})
    )
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-memory-client",
        strict=True,
    )
    before = _snapshot(system)
    memory_before = system.memory_traces[memory_id]

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(system.retrieve_quantum_memory(memory_id, consciousness_context=0.8))

    assert _snapshot(system) == before
    assert system.memory_traces[memory_id] is memory_before
    assert system.memory_traces[memory_id].access_count == 0
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_memory_retrieve"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_quantum_memory_entangle_denial_preserves_links_and_sanitizes_ids(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    system = QuantumMemorySystem()
    memory_a = asyncio.run(
        system.store_quantum_memory(MemoryType.EPISODIC, {"topic": "alpha"})
    )
    memory_b = asyncio.run(
        system.store_quantum_memory(MemoryType.EMOTIONAL, {"topic": "beta"})
    )
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-memory-client",
        strict=True,
    )
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(system.create_memory_entanglement(memory_a, memory_b, "private-link"))

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert memory_a not in ledger_text
    assert memory_b not in ledger_text
    assert "private-link" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_memory_entangle"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
    assert entry["details"]["intent"]["metadata"]["memory_a_hash"]


def test_quantum_memory_search_denial_preserves_memory_objects_and_query(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    system = QuantumMemorySystem()
    memory_id = asyncio.run(
        system.store_quantum_memory(MemoryType.PROCEDURAL, {"skill": "navigation"})
    )
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-memory-client",
        strict=True,
    )
    query = {"skill": "private-search-value"}

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(system.quantum_memory_search(query, consciousness_level=0.4))

    assert not hasattr(system.memory_traces[memory_id], "search_score")
    ledger_text = _audit_text(tmp_path)
    assert "private-search-value" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_memory_search"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
    assert entry["details"]["intent"]["metadata"]["query_hash"]
