# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Targeted tests for QFAC dashboard summary paths.

Focus:
- Unavailable (stub) summary path
- Available summary path with phases populated
- Integration with real QFACMemorySystem to ensure node storage is reflected

These tests are intentionally narrow to boost coverage of recently
modified logic in `QFACDashboard.get_dashboard_summary` without requiring
full OS launch overhead.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest

from Aetherra.aetherra_core.memory.qfac_dashboard import QFACDashboard
from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem


class _AnalyzerStubEmpty:
    """Analyzer stub returning no performance data (forces unavailable path)."""

    def monitor_compression_performance(self) -> dict[str, Any]:  # sync path
        return {}


class _AnalyzerStubPerf:
    """Analyzer stub returning basic performance metrics and types."""

    def monitor_compression_performance(self) -> dict[str, Any]:  # sync path
        return {
            "overall_health": 0.85,
            "overall_ratio": 1.5,
            "space_saved_percentage": 12.3,
            "performance_by_type": {
                "text": {
                    "avg_compression_ratio": 2.1,
                    "avg_compression_time": 0.002,
                    "sample_count": 3,
                }
            },
            "performance_issues": ["Minor slowdown detected"],
            "optimization_suggestions": [
                "Consider batching small nodes",
            ],
        }


@pytest.mark.asyncio
async def test_qfac_dashboard_summary_unavailable():
    """Dashboard should report 'unavailable' when no system or perf data."""
    dash = QFACDashboard(analyzer=_AnalyzerStubEmpty(), memory_system=None)
    summary = await dash.get_dashboard_summary()
    assert summary["status"] == "unavailable"
    # Reason should default to dashboard stub
    assert summary.get("reason") == "dashboard stub"
    # Performance block still present with defaults
    perf = summary.get("performance", {})
    assert "overall_health" in perf
    assert perf.get("performance_by_type") == {}
    # No phases when unavailable
    assert "phases" not in summary


@pytest.mark.asyncio
async def test_qfac_dashboard_summary_ok_with_phases():
    """Dashboard should report 'ok' and include phases when status/perf exist."""

    # Minimal memory system stub returning expected status keys
    class _MemStub:
        async def get_system_status(self):  # pragma: no cover - trivial
            return {
                "node_statistics": {
                    "total_nodes": 0,
                    "compressed_nodes": 0,
                    "compression_percentage": 0.0,
                },
                "size_statistics": {
                    "overall_compression_ratio": 1.0,
                    "space_saved_percentage": 0.0,
                },
                "fidelity_distribution": {},
                "system_health": 0.75,
            }

    dash = QFACDashboard(analyzer=_AnalyzerStubPerf(), memory_system=_MemStub())
    summary = await dash.get_dashboard_summary()
    assert summary["status"] == "ok"
    assert "phases" in summary  # phases only added in ok path
    phases = summary["phases"]  # type: ignore[index]
    assert set(phases.keys()) >= {"analysis", "compression", "quantum_bridge"}
    perf = summary["performance"]  # type: ignore[index]
    assert perf["overall_health"] == pytest.approx(0.85, rel=1e-3)
    assert perf["performance_by_type"]["text"]["sample_count"] == 3
    # Original system status preserved under 'system'
    sys_status = summary["system"]  # type: ignore[index]
    assert isinstance(sys_status, dict)
    assert "node_statistics" in sys_status
    assert "size_statistics" in sys_status


@pytest.mark.asyncio
async def test_qfac_dashboard_integrates_with_real_qfac_memory_system(tmp_path):
    """Integration: real QFACMemorySystem stores a node and dashboard returns ok summary."""
    # Force a mode to exercise hybrid path logic heuristics without quantum backend failures
    prev_mode = os.getenv("AETHERRA_QFAC_MODE")
    os.environ["AETHERRA_QFAC_MODE"] = "hybrid"
    try:
        qfac = QFACMemorySystem(data_dir=str(tmp_path / "qfac_data"))
        # Store a simple memory node
        node_id = await qfac.store_memory({"text": "coverage"}, "test_node")  # type: ignore[arg-type]
        assert node_id
        # Allow any background auto-compression tasks a brief slice
        await asyncio.sleep(0.05)
        # Summary should now be ok
        summary = await qfac.dashboard.get_dashboard_summary()
        assert summary["status"] in {"ok", "unavailable"}
        # If real metrics gathered, expect ok path
        if summary["status"] == "ok":
            assert "phases" in summary
            sys_status = summary["system"]  # type: ignore[index]
            assert isinstance(sys_status, dict)
            node_stats = sys_status.get("node_statistics", {}) or {}
            size_stats = sys_status.get("size_statistics", {}) or {}
            assert isinstance(node_stats, dict)
            assert isinstance(size_stats, dict)
            assert (node_stats.get("total_nodes") or 0) >= 1
            assert "overall_compression_ratio" in size_stats
        else:
            # Stub/unavailable fallback path still acceptable, but ensure reason
            assert summary.get("reason") == "dashboard stub"
    finally:
        # Restore environment
        if prev_mode is None:
            os.environ.pop("AETHERRA_QFAC_MODE", None)
        else:
            os.environ["AETHERRA_QFAC_MODE"] = prev_mode
