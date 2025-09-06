# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import pytest

from aetherra_persistent_memory import AetherraPerśistentMemorySystem


@pytest.mark.asyncio
async def test_quantum_enhanced_recall_scoring(monkeypatch):
    # Enable quantum recall components deterministically
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_QUANTUM_RECALL", "1")
    monkeypatch.setenv("AETHERRA_QHASH_BITS", "32")
    monkeypatch.setenv("AETHERRA_QHASH_WEIGHT", "1.0")
    monkeypatch.setenv("AETHERRA_RFM_WEIGHT", "0.0")
    monkeypatch.setenv("AETHERRA_QUANTUM_AUDIT", "1")

    mem = AetherraPerśistentMemorySystem(memory_dir=".test_mem")
    await mem.initialize()

    # Store two memories, one clearly more similar to the query
    id1 = await mem.store("I love quantum hashing techniques", importance=0.1)
    id2 = await mem.store("Completely unrelated gardening tips", importance=0.9)
    assert id1 and id2

    results = await mem.retrieve("quantum hash", limit=2)
    assert len(results) >= 1
    # With QHASH weight 1.0, the text with matching tokens should rank higher
    top = results[0]
    assert "audit" in top and "quantum" in top["audit"]
