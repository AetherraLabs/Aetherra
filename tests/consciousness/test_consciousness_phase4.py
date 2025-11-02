# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import json
import time
from pathlib import Path

import pytest

from Aetherra.consciousness.consolidation import Consolidator
from Aetherra.consciousness.continuity_memory import (
    ContinuityMemory,
    ContinuitySnapshot,
)
from Aetherra.consciousness.core import config as core_config
from Aetherra.consciousness.dream_cycle import DreamCycle
from Aetherra.consciousness.qualia_learning import QualiaLearner


class StubBus:
    def __init__(self, events=None):
        self._events = list(events or [])

    def drain(self, max_items: int = 256):
        # Return and clear events to simulate stream
        out = self._events[:max_items]
        self._events = self._events[max_items:]
        return out


class MemoryEngineStub:
    def __init__(self, episodic=None):
        # episodic: dict id -> entry
        self.episodic = {e["id"]: e for e in (episodic or [])}
        self.longterm = {}

    def get_episodic_memories(self):
        return list(self.episodic.values())

    def delete_memory(self, entry_id: str):
        self.episodic.pop(entry_id, None)

    def promote_to_longterm(self, entry_id: str):
        if entry_id in self.episodic:
            self.longterm[entry_id] = self.episodic.pop(entry_id)


@pytest.fixture
def temp_continuity(tmp_path: Path):
    path = tmp_path / "continuity.json"
    cm = ContinuityMemory(path=str(path), max_snaps=120)
    cm.clear()
    return cm, path


def _make_snapshot(valence: float, certainty: float, tick: int):
    return ContinuitySnapshot(
        ts=time.time(),
        qualia={
            "valence": valence,
            "arousal": 0.4,
            "certainty": certainty,
            "curiosity": 0.5,
            "care": 0.5,
            "fatigue": 0.2,
        },
        focuses=["svc.health", "disk.status"],
        intentions=["maintain_host_stability"],
        trust_scores={"services": 0.8, "disk": 0.7},
        tick=tick,
    )


def test_boot_continuity_snci_high(monkeypatch, temp_continuity):
    cm, path = temp_continuity

    # Seed continuity with stable, positive qualia
    for i in range(12):
        cm.buffer.append(_make_snapshot(valence=0.2, certainty=0.7, tick=i))
    cm.save()

    # Patch core to use our continuity path
    import Aetherra.consciousness.core.consciousness_core as core_mod

    def _cm_ctor_override(*args, **kwargs):
        return ContinuityMemory(path=str(path), max_snaps=120)

    monkeypatch.setattr(core_mod, "ContinuityMemory", _cm_ctor_override)

    # Build core with stub bus and memory
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    bus = StubBus()
    core = ConsciousnessCore(
        perception_bus=bus, safety_envelope=None, memory_engine=None
    )

    status = core.get_status()
    snci = status["continuity"]["snci"]
    assert snci >= 0.8, f"Expected SNCI >= 0.8 after boot, got {snci:.3f}"


def test_dream_reflection_adjusts_params(temp_continuity):
    cm, _ = temp_continuity

    # Negative valence history
    for i in range(30):
        cm.buffer.append(_make_snapshot(valence=-0.4, certainty=0.35, tick=i))
    cm.save()

    ql = QualiaLearner()
    before = ql.p.curiosity_gain

    dream = DreamCycle(continuity=cm, max_adjustment=0.2, analysis_window=50)
    result = dream.run(ql)

    after = ql.p.curiosity_gain
    assert after >= before, (
        "Curiosity gain should not decrease on negative-valence trend"
    )
    assert (after - before) <= 0.2 + 1e-6, "Adjustment must be capped at 0.2"
    assert result.get("narrative"), "Dream narrative should be synthesized"


def test_consolidation_prunes_and_promotes():
    now = time.time()
    episodic = [
        {
            "id": "low1",
            "valence": 0.0,
            "timestamp": now - 10 * 86400,
            "access_count": 0,
            "confidence": 0.2,
        },
        {
            "id": "mid1",
            "valence": 0.5,
            "timestamp": now - 2 * 86400,
            "access_count": 2,
            "confidence": 0.5,
        },
        {
            "id": "high1",
            "valence": 0.9,
            "timestamp": now - 3600,
            "access_count": 8,
            "confidence": 0.9,
        },
    ]
    me = MemoryEngineStub(episodic)

    cons = Consolidator(
        memory_engine=me, salience_threshold=0.2, promotion_threshold=0.7, batch_size=10
    )
    res = cons.consolidate()

    assert res["pruned"] >= 1, "Expected at least one low-salience prune"
    assert res["promoted"] >= 1, "Expected at least one high-salience promotion"
    # Verify side-effects
    assert "low1" not in me.episodic
    assert "high1" in me.longterm


def test_continuity_snapshotting_in_tick(monkeypatch, tmp_path):
    # Patch continuity to use temp file
    path = tmp_path / "cont.json"

    import Aetherra.consciousness.core.consciousness_core as core_mod

    def _cm_ctor_override(*args, **kwargs):
        return ContinuityMemory(path=str(path), max_snaps=120)

    monkeypatch.setattr(core_mod, "ContinuityMemory", _cm_ctor_override)

    # Make snapshot interval small for test
    old_interval = core_config.CONTINUITY_SNAPSHOT_INTERVAL
    core_config.CONTINUITY_SNAPSHOT_INTERVAL = 1

    try:
        from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

        bus = StubBus()
        core = ConsciousnessCore(
            perception_bus=bus, safety_envelope=None, memory_engine=None
        )

        # Run few ticks
        for _ in range(3):
            core.tick()

        # Load continuity
        cm = ContinuityMemory(path=str(path), max_snaps=120)
        assert cm.get_stats()["snapshots_total"] >= 2, (
            "Expected periodic snapshots to be recorded"
        )
    finally:
        core_config.CONTINUITY_SNAPSHOT_INTERVAL = old_interval
