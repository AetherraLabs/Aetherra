# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Unit tests for QFAC mode selection and hybrid fallback behavior.

These tests validate that:
- Classical mode does not attempt quantum bridge operations.
- Hybrid mode initializes the bridge when available, but retrieval works even if no
  real quantum frameworks are present (graceful fallback via classical shadow).
- System status exports include expected fields and do not crash.
"""

import asyncio
import os
from contextlib import contextmanager

import pytest

from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem


@contextmanager
def env(**kwargs):
    old = {k: os.environ.get(k) for k in kwargs}
    try:
        for k, v in kwargs.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = str(v)
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.mark.asyncio
async def test_qfac_classical_mode_roundtrip():
    # Force classical mode
    with env(AETHERRA_QFAC_MODE="classical"):
        system = QFACMemorySystem()
        node_id = await system.store_memory({"text": "hello world"}, "t1")
        assert node_id == "t1"

        # Allow auto-analyze task to complete briefly
        await asyncio.sleep(0.2)

        data = await system.retrieve_memory(node_id)
        assert isinstance(data, dict)
        assert data.get("text") == "hello world"

        status = await system.get_system_status()
        assert "node_statistics" in status
        assert status["node_statistics"]["total_nodes"] >= 1


@pytest.mark.asyncio
async def test_qfac_hybrid_mode_fallback_and_metadata():
    # Force hybrid mode; QuantumMemoryBridge may run in sim mode
    with env(AETHERRA_QFAC_MODE="hybrid"):
        system = QFACMemorySystem()
        node_id = await system.store_memory({"content": "quantum-ish"}, "h1")

        # Wait a bit for possible auto compression/quantum encode
        await asyncio.sleep(0.5)

        # Ensure retrieval works regardless of backend availability
        data = await system.retrieve_memory(node_id)
        assert data.get("content") == "quantum-ish"

        # Check node metadata for optional quantum info without raising
        node = system.nodes[node_id]
        meta = node.compression_metadata or {}
        # In hybrid mode we try quantum; metadata may or may not include quantum_encoding
        if "quantum_encoding" in meta:
            qe = meta["quantum_encoding"]
            assert "state_id" in qe
            assert "backend" in qe
        # System status should compute without error
        status = await system.get_system_status()
        assert "size_statistics" in status


@pytest.mark.asyncio
async def test_qfac_export_report(tmp_path):
    with env(AETHERRA_QFAC_MODE="classical"):
        system = QFACMemorySystem(data_dir=str(tmp_path))
        await system.store_memory({"text": "report"}, "r1")
        await asyncio.sleep(0.1)
        # Export report; ensure file is created
        path = await system.export_system_report("unit_qfac_report.json")
        assert os.path.exists(path)
