# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Unit tests for QFACMemorySystem compress_all_eligible, optimize_system, degraded fidelity handling, search, parity, and policy utilities."""

import asyncio
import os
import sys
import types

import pytest

from Aetherra.aetherra_core.memory.compression_metrics import (
    CompressionScore,
    FidelityLevel,
)
from Aetherra.aetherra_core.memory.qfac_integration import (
    QFACMemoryNode,
    QFACMemorySystem,
)


@pytest.mark.asyncio
async def test_qfac_search_memory_threshold_and_parity(monkeypatch):
    # Use a low threshold to ensure at least one result even if scores are low/degraded
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_THRESHOLD", "0.0")
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_PARITY", "1")
    system = QFACMemorySystem(data_dir=".test_qfac_search1")
    # Explicitly ensure threshold reflects test intent in case constructor clamped
    system.retrieval_threshold = 0.0
    await system.store_memory({"text": "alpha beta gamma"}, "s1")
    await system.store_memory({"text": "delta epsilon zeta"}, "s2")
    results = await system.search_memory("alpha", top_k=2)
    assert any(r["node_id"] == "s1" for r in results)
    parity = system.get_retrieval_parity_metrics_snapshot()
    assert parity["total"] >= 1
    results2 = await system.search_memory("theta", top_k=2)
    assert isinstance(results2, list)


@pytest.mark.asyncio
async def test_qfac_search_memory_fallback_naive(monkeypatch):
    # Insert a dummy module to simulate ImportError fallback
    sys.modules["Aetherra.aetherra_core.memory.qfac_retrieval"] = types.ModuleType(
        "dummy_qfac_retrieval"
    )
    system = QFACMemorySystem(data_dir=".test_qfac_search2")
    await system.store_memory({"text": "fallback test"}, "f1")
    results = await system.search_memory("fallback", top_k=1)
    assert isinstance(results, list)
    assert any(r["node_id"] == "f1" for r in results)
    del sys.modules["Aetherra.aetherra_core.memory.qfac_retrieval"]


@pytest.mark.asyncio
async def test_qfac_retrieval_parity_by_k_snapshot_accumulates(monkeypatch):
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_PARITY", "1")
    system = QFACMemorySystem(data_dir=".test_qfac_parityk1")
    for i in range(5):
        system.nodes[f"k{i}"] = QFACMemoryNode(
            node_id=f"k{i}",
            original_data={"text": f"node {i}"},
            compression_analyzer=system.analyzer,
            auto_compress=False,
        )
    await system.search_memory("node", top_k=3)
    snapshot = system.get_retrieval_parity_by_k_snapshot()
    assert all(k in snapshot for k in (1, 3, 5, 10))
    assert any(v > 0 for v in snapshot.values())


def test_qfac_retrieval_policy_config_snapshot(monkeypatch):
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_THRESHOLD", "0.42")
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_PARITY", "0")
    system = QFACMemorySystem(data_dir=".test_qfac_policycfg1")
    snap = system.get_retrieval_policy_config_snapshot()
    assert abs(snap["threshold"] - 0.42) < 1e-6
    assert snap["parity_enabled"] == 0


@pytest.mark.asyncio
async def test_qfac_reset_retrieval_parity_counters(monkeypatch):
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_PARITY", "1")
    system = QFACMemorySystem(data_dir=".test_qfac_resetparity1")
    for i in range(3):
        system.nodes[f"r{i}"] = QFACMemoryNode(
            node_id=f"r{i}",
            original_data={"text": f"reset {i}"},
            compression_analyzer=system.analyzer,
            auto_compress=False,
        )
    await system.search_memory("reset", top_k=2)
    before = system.get_retrieval_parity_metrics_snapshot()
    assert before["total"] > 0
    system.reset_retrieval_parity_counters()
    after = system.get_retrieval_parity_metrics_snapshot()
    assert all(v == 0 for v in after.values())


@pytest.mark.asyncio
async def test_qfac_compress_all_eligible_counts():
    # Create system with auto_compression off for control
    system = QFACMemorySystem(data_dir=".test_qfac_compress1")
    system.auto_compression = False
    # Add two nodes, one eligible, one not
    node_id1 = await system.store_memory({"text": "compress me"}, "n1")
    node_id2 = await system.store_memory({"text": "skip me"}, "n2")
    # Manually inject compression_score to control eligibility
    node1 = system.nodes[node_id1]
    node2 = system.nodes[node_id2]
    node1.compression_score = CompressionScore(
        entropy=0.5,
        structure_depth=2,
        recursive_density=0.3,
        fidelity_level=FidelityLevel.LOSSY_SAFE,
        compression_ratio=3.0,
        access_frequency=0.5,
        temporal_decay=0.1,
        fragment_id="frag1",
        original_size=100,
        compressed_size=33,
        last_access=0.0,
        compression_timestamp=0.0,
        pattern_confidence=0.9,
        reconstruction_quality=0.98,
        semantic_preservation=0.97,
    )
    node2.compression_score = CompressionScore(
        entropy=0.4,
        structure_depth=1,
        recursive_density=0.2,
        fidelity_level=FidelityLevel.LOSSY_SAFE,
        compression_ratio=1.0,
        access_frequency=5.0,
        temporal_decay=0.2,
        fragment_id="frag2",
        original_size=100,
        compressed_size=100,
        last_access=0.0,
        compression_timestamp=0.0,
        pattern_confidence=0.8,
        reconstruction_quality=0.95,
        semantic_preservation=0.95,
    )
    # Run compress_all_eligible
    result = await system.compress_all_eligible()
    assert result["compressed"] == 1
    assert result["skipped"] >= 1
    assert result["failed"] == 0
    assert any(d["node_id"] == node_id1 for d in result["compression_details"])


@pytest.mark.asyncio
async def test_qfac_optimize_system_actions():
    system = QFACMemorySystem(data_dir=".test_qfac_optimize1")
    system.auto_compression = False
    # Add eligible node
    node_id = await system.store_memory({"text": "optimize me"}, "n3")
    node = system.nodes[node_id]
    node.compression_score = CompressionScore(
        entropy=0.6,
        structure_depth=2,
        recursive_density=0.4,
        fidelity_level=FidelityLevel.LOSSY_SAFE,
        compression_ratio=3.5,
        access_frequency=0.2,
        temporal_decay=0.1,
        fragment_id="frag3",
        original_size=120,
        compressed_size=34,
        last_access=0.0,
        compression_timestamp=0.0,
        pattern_confidence=0.92,
        reconstruction_quality=0.99,
        semantic_preservation=0.98,
    )
    # Add already compressed node
    node_id2 = await system.store_memory({"text": "already compressed"}, "n4")
    node2 = system.nodes[node_id2]
    node2.compression_score = CompressionScore(
        entropy=0.7,
        structure_depth=3,
        recursive_density=0.5,
        fidelity_level=FidelityLevel.LOSSY_SAFE,
        compression_ratio=3.0,
        access_frequency=0.1,
        temporal_decay=0.1,
        fragment_id="frag4",
        original_size=110,
        compressed_size=37,
        last_access=0.0,
        compression_timestamp=0.0,
        pattern_confidence=0.93,
        reconstruction_quality=0.97,
        semantic_preservation=0.96,
    )
    await node2.compress()
    # Run optimize_system
    result = await system.optimize_system()
    actions = result["actions_taken"]
    assert any(a["action"] == "compress_eligible_nodes" for a in actions)
    # Should not decompress any nodes (no degraded)
    assert not any(a["action"] == "decompress_degraded_node" for a in actions)
    # Compression action should have compressed at least one node
    compress_action = next(
        (a for a in actions if a["action"] == "compress_eligible_nodes"), None
    )
    assert compress_action is not None
    details = compress_action["details"]
    assert details["compressed"] >= 1
    assert any(d["node_id"] == node_id for d in details["compression_details"])


@pytest.mark.asyncio
async def test_qfac_optimize_system_degraded_fidelity_handling():
    system = QFACMemorySystem(data_dir=".test_qfac_optimize2")
    system.auto_compression = False
    # Add node and force it to compressed, degraded
    node_id = await system.store_memory({"text": "degrade me"}, "n5")
    node = system.nodes[node_id]
    node.compression_score = CompressionScore(
        entropy=0.8,
        structure_depth=2,
        recursive_density=0.6,
        fidelity_level=FidelityLevel.DEGRADED,
        compression_ratio=3.0,
        access_frequency=0.1,
        temporal_decay=0.1,
        fragment_id="frag5",
        original_size=130,
        compressed_size=43,
        last_access=0.0,
        compression_timestamp=0.0,
        pattern_confidence=0.7,
        reconstruction_quality=0.7,
        semantic_preservation=0.7,
    )
    await node.compress()
    assert node.is_compressed
    # Run optimize_system, should decompress degraded node
    result = await system.optimize_system()
    actions = result["actions_taken"]
    assert any(
        a["action"] == "decompress_degraded_node" and a["node_id"] == node_id
        for a in actions
    )
    # Node should now be uncompressed
    assert not node.is_compressed
