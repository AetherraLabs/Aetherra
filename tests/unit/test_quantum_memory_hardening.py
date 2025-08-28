from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine.quantum_memory_engine import (
    QuantumEnhancedMemoryEngine,
)


def test_store_enforces_engine_coherence_and_branch_creation():
    eng = QuantumEnhancedMemoryEngine()
    eng.set_coherence_id("coh-123")
    # Store with unknown branch should create it under current
    ok = eng.store(
        {"text": "alpha"}, context={"branch_id": "exp-1", "observer_ids": ["obsA"]}
    )
    assert ok is True
    frag = eng.memory_fragments[-1]
    assert frag["coherence_id"] == "coh-123"
    assert frag["branch_id"] == "exp-1"
    assert "exp-1" in eng.branch_parents
    # Observer drift lineage should include write event
    writes = [e for e in frag["lineage"]["observer_drift"] if e["event"] == "write"]
    assert any(e["observer_id"] == "obsA" for e in writes)


def test_branch_aware_retrieval_and_observer_drift_updates_on_read():
    eng = QuantumEnhancedMemoryEngine()
    eng.set_coherence_id("coh-123")
    eng.store(
        {"text": "beta data"}, context={"branch_id": "b1", "observer_ids": ["seed"]}
    )
    # Retrieval with different branch should not match
    miss = eng.retrieve("beta", context={"branch_id": "other"})
    assert miss.get("found") is False
    # Retrieval within branch should match and add read drift for new observer
    hit = eng.retrieve("beta", context={"branch_id": "b1", "observer_ids": ["reader"]})
    assert hit.get("data", {}).get("text") == "beta data"
    reads = [e for e in hit["lineage"]["observer_drift"] if e["event"] == "read"]
    assert any(e["observer_id"] == "reader" for e in reads)


def test_audits_coherence_score_and_branch_dag():
    eng = QuantumEnhancedMemoryEngine()
    # With no fragments coherence score is neutral 1.0
    assert eng.get_coherence_score() == 1.0
    eng.store({"text": "x"}, context={"observer_ids": ["o1"]})
    eng.store({"text": "y"}, context={"observer_ids": ["o2"]})
    # Link entanglement between the two ids (0 and 1)
    eng.link_entanglement(0, 1)
    score = eng.get_coherence_score()
    assert 0.0 <= score <= 1.0
    dag = eng.audit_branch_dag()
    assert "main" in dag["branches"]
    assert dag["root"] == "main"
