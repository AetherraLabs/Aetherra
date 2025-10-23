# SPDX-License-Identifier: GPL-3.0-or-later
"""Test STORM metrics stubs"""

import pytest

from Aetherra.aetherra_core.memory.storm.metrics import StormMetrics, get_metrics


def test_metrics_init():
    """Metrics initialize with zero values"""
    m = StormMetrics()
    assert m.approximate_recalls_total == 0
    assert m.ot_cost_avg == 0.0
    assert m.sheaf_inconsistency == 0.0
    assert m.tt_rank == 0
    assert m.branch_barycenters_total == 0
    assert m.maintenance_total == 0


def test_record_approximate_recall():
    """approximate_recalls_total increments"""
    m = StormMetrics()
    m.record_approximate_recall()
    assert m.approximate_recalls_total == 1
    m.record_approximate_recall()
    assert m.approximate_recalls_total == 2


def test_record_ot_cost():
    """OT cost gauge updates"""
    m = StormMetrics()
    m.record_ot_cost(1.5)
    assert m.ot_cost_avg == 1.5


def test_record_sheaf_inconsistency():
    """Sheaf inconsistency gauge updates"""
    m = StormMetrics()
    m.record_sheaf_inconsistency(0.05)
    assert m.sheaf_inconsistency == 0.05


def test_record_tt_rank():
    """TT rank gauge updates"""
    m = StormMetrics()
    m.record_tt_rank(16)
    assert m.tt_rank == 16


def test_record_recall_latency_p95():
    """p95 latency gauge updates"""
    m = StormMetrics()
    m.record_recall_latency_p95(123.45)
    assert m.recall_latency_ms_p95 == 123.45


def test_record_maintenance():
    """Maintenance counter and last timestamp update"""
    m = StormMetrics()
    m.record_maintenance("rank_trim", 1000.0)
    assert m.maintenance_total == 1
    assert m.maintenance_last["rank_trim"] == 1000.0


def test_record_branch_barycenter():
    """Branch barycenters counter increments"""
    m = StormMetrics()
    m.record_branch_barycenter()
    assert m.branch_barycenters_total == 1


def test_snapshot():
    """Snapshot returns all metrics"""
    m = StormMetrics()
    m.record_approximate_recall()
    m.record_ot_cost(2.0)
    m.record_tt_rank(32)

    snap = m.snapshot()
    assert snap["aetherra_storm_approximate_recalls_total"] == 1
    assert snap["aetherra_storm_ot_cost_avg"] == 2.0
    assert snap["aetherra_storm_tt_rank"] == 32
    assert "aetherra_storm_maintenance_last" in snap


def test_get_metrics_singleton():
    """get_metrics returns global instance"""
    m1 = get_metrics()
    m2 = get_metrics()
    assert m1 is m2
