# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for STORM maintenance operations during night cycle."""

from __future__ import annotations

import json

import pytest

from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine
from Aetherra.aetherra_core.memory.storm.metrics import get_metrics
from Aetherra.aetherra_core.memory.storm.ot_helpers import _generate_mock_embedding


@pytest.fixture(autouse=True)
def guardian_env(monkeypatch, tmp_path):
    """Keep Guardian audit state isolated for STORM maintenance tests."""
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return tmp_path


@pytest.fixture
def maintenance_engine():
    """Create a STORM engine for maintenance testing."""
    config = StormConfig(
        enabled=True,
        shadow_mode=False,
        sqlite_path=":memory:",  # In-memory DB for testing
    )
    return StormEngine(config=config)


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.mark.asyncio
async def test_run_maintenance_all_tasks(maintenance_engine):
    """Test that run_maintenance executes all tasks successfully."""
    results = await maintenance_engine.run_maintenance()

    # Verify all tasks completed
    assert "tt_rank_trim" in results
    assert "barycenter_refresh" in results
    assert "inconsistency_scan" in results
    assert "ot_cache_prune" in results

    # All tasks should succeed
    assert results["tt_rank_trim"]["status"] == "ok"
    assert results["barycenter_refresh"]["status"] == "ok"
    assert results["inconsistency_scan"]["status"] == "ok"
    assert results["ot_cache_prune"]["status"] == "ok"


@pytest.mark.asyncio
async def test_run_maintenance_writes_guardian_audit_without_storage_path(
    guardian_env, tmp_path
):
    sqlite_path = tmp_path / "secret-storm-path.sqlite"
    engine = StormEngine(
        config=StormConfig(
            enabled=True,
            shadow_mode=False,
            sqlite_path=str(sqlite_path),
        )
    )

    results = await engine.run_maintenance()
    entries = _audit_entries(guardian_env)
    audit_json = json.dumps(entries[-1])

    assert results["ot_cache_prune"]["status"] == "ok"
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.storm_run"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "secret-storm-path" not in audit_json
    assert str(sqlite_path) not in audit_json


@pytest.mark.asyncio
async def test_run_maintenance_blocks_external_requester_before_metrics(
    monkeypatch, guardian_env, maintenance_engine
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    maintenance_engine.metrics.maintenance_total = 0
    maintenance_engine.metrics.maintenance_last.clear()

    results = await maintenance_engine.run_maintenance(requester="untrusted_operator")

    assert results["tt_rank_trim"]["status"].startswith(
        "guardian_denied:missing_capability"
    )
    assert results["ot_cache_prune"]["status"].startswith(
        "guardian_denied:missing_capability"
    )
    assert maintenance_engine.metrics.maintenance_total == 0
    assert maintenance_engine.metrics.maintenance_last == {}


@pytest.mark.asyncio
async def test_maintenance_metrics_tracking(maintenance_engine):
    """Test that maintenance operations update metrics correctly."""
    metrics = maintenance_engine.metrics

    # Clear metrics
    metrics.maintenance_total = 0
    metrics.maintenance_last.clear()
    metrics.branch_barycenters_total = 0

    # Run maintenance
    await maintenance_engine.run_maintenance()

    # Verify maintenance total incremented (4 tasks)
    assert metrics.maintenance_total == 4

    # Verify all maintenance actions recorded
    assert "tt_rank_trim" in metrics.maintenance_last
    assert "barycenter_refresh" in metrics.maintenance_last
    assert "inconsistency_scan" in metrics.maintenance_last
    assert "ot_cache_prune" in metrics.maintenance_last

    # Verify timestamps are reasonable
    for _action, timestamp in metrics.maintenance_last.items():
        assert timestamp > 0

    # Verify branch barycenter counter incremented
    assert metrics.branch_barycenters_total == 1


@pytest.mark.asyncio
async def test_maintenance_inconsistency_scan_with_embeddings(maintenance_engine):
    """Test inconsistency scan with stored embeddings."""
    # Store some embeddings first
    if maintenance_engine._storage is not None:
        for i in range(5):
            content = f"test memory item {i}"
            emb = _generate_mock_embedding(content)
            maintenance_engine._storage.upsert_embedding(content, emb)

    # Run maintenance
    results = await maintenance_engine.run_maintenance()

    # Inconsistency scan should report a value
    assert "avg_inconsistency" in results["inconsistency_scan"]
    inconsistency = results["inconsistency_scan"]["avg_inconsistency"]
    assert isinstance(inconsistency, float)
    assert inconsistency >= 0.0


@pytest.mark.asyncio
async def test_maintenance_inconsistency_scan_empty_storage(maintenance_engine):
    """Test inconsistency scan with no stored embeddings."""
    results = await maintenance_engine.run_maintenance()

    # Should complete successfully even with empty storage
    assert results["inconsistency_scan"]["status"] == "ok"
    assert results["inconsistency_scan"]["avg_inconsistency"] == 0.0


@pytest.mark.asyncio
async def test_maintenance_no_storage():
    """Test maintenance when storage is None."""
    config = StormConfig(enabled=True, shadow_mode=False, sqlite_path="")
    engine = StormEngine(config=config)
    engine._storage = None  # Explicitly disable storage

    # Should still complete without errors
    results = await engine.run_maintenance()

    assert results["inconsistency_scan"]["status"] == "ok"
    assert results["inconsistency_scan"]["avg_inconsistency"] == 0.0


@pytest.mark.asyncio
async def test_maintenance_metrics_snapshot_includes_counts():
    """Test that metrics snapshot includes maintenance counts."""
    config = StormConfig(enabled=True, sqlite_path=":memory:")
    engine = StormEngine(config=config)

    # Run maintenance
    await engine.run_maintenance()

    # Get metrics snapshot
    snapshot = engine.metrics.snapshot()

    # Verify maintenance metrics present
    assert "aetherra_storm_maintenance_total" in snapshot
    maintenance_total = snapshot["aetherra_storm_maintenance_total"]
    assert isinstance(maintenance_total, int)
    assert maintenance_total >= 4

    assert "aetherra_storm_maintenance_last" in snapshot
    assert isinstance(snapshot["aetherra_storm_maintenance_last"], dict)
    assert len(snapshot["aetherra_storm_maintenance_last"]) == 4

    assert "aetherra_storm_branch_barycenters_total" in snapshot
    barycenter_total = snapshot["aetherra_storm_branch_barycenters_total"]
    assert isinstance(barycenter_total, int)
    assert barycenter_total >= 1


@pytest.mark.asyncio
async def test_maintenance_idempotent():
    """Test that maintenance can be run multiple times safely."""
    config = StormConfig(enabled=True, sqlite_path=":memory:")
    engine = StormEngine(config=config)

    # Record initial maintenance count
    initial_count = engine.metrics.maintenance_total

    # Run maintenance multiple times
    results1 = await engine.run_maintenance()
    results2 = await engine.run_maintenance()
    results3 = await engine.run_maintenance()

    # All runs should succeed
    for results in [results1, results2, results3]:
        assert results["tt_rank_trim"]["status"] == "ok"
        assert results["barycenter_refresh"]["status"] == "ok"
        assert results["inconsistency_scan"]["status"] == "ok"
        assert results["ot_cache_prune"]["status"] == "ok"

    # Maintenance total should increment by 12 (4 tasks × 3 runs)
    assert engine.metrics.maintenance_total == initial_count + 12


@pytest.mark.asyncio
async def test_maintenance_with_high_inconsistency(maintenance_engine):
    """Test that maintenance records metrics when inconsistency is high."""
    # Create embeddings with potential high inconsistency
    if maintenance_engine._storage is not None:
        # Store varied embeddings
        for i in range(10):
            content = f"diverse content {i} with unique patterns"
            emb = _generate_mock_embedding(content)
            maintenance_engine._storage.upsert_embedding(content, emb)

    # Clear sheaf inconsistency metric
    maintenance_engine.metrics.sheaf_inconsistency = 0.0

    # Run maintenance
    results = await maintenance_engine.run_maintenance()

    # Should complete successfully
    assert results["inconsistency_scan"]["status"] == "ok"

    # If inconsistency > 0.1, it should be recorded in metrics
    avg_inc = results["inconsistency_scan"]["avg_inconsistency"]
    if avg_inc > 0.1:
        assert maintenance_engine.metrics.sheaf_inconsistency > 0.0


@pytest.mark.asyncio
async def test_maintenance_graceful_error_handling():
    """Test that maintenance handles errors gracefully per task."""
    config = StormConfig(enabled=True, sqlite_path=":memory:")
    engine = StormEngine(config=config)

    # Simulate a problematic storage by breaking get_all_embeddings
    original_storage = engine._storage
    if original_storage is not None:
        # Monkey-patch to simulate failure
        def failing_get_all():
            raise RuntimeError("Simulated storage failure")

        original_storage.get_all_embeddings = failing_get_all  # type: ignore[assignment]

    # Run maintenance - should not raise exception
    results = await engine.run_maintenance()

    # Other tasks should succeed
    assert results["tt_rank_trim"]["status"] == "ok"
    assert results["barycenter_refresh"]["status"] == "ok"
    assert results["ot_cache_prune"]["status"] == "ok"

    # Inconsistency scan should report error but not crash
    assert "error" in results["inconsistency_scan"]["status"].lower()


@pytest.mark.asyncio
async def test_maintenance_returns_expected_structure():
    """Test that maintenance result has the expected structure."""
    config = StormConfig(enabled=True, sqlite_path=":memory:")
    engine = StormEngine(config=config)

    results = await engine.run_maintenance()

    # Verify result structure
    assert isinstance(results, dict)

    # Each task should have status and task-specific fields
    assert "status" in results["tt_rank_trim"]
    assert "items_cleared" in results["tt_rank_trim"]

    assert "status" in results["barycenter_refresh"]
    assert "barycenters_updated" in results["barycenter_refresh"]

    assert "status" in results["inconsistency_scan"]
    assert "avg_inconsistency" in results["inconsistency_scan"]

    assert "status" in results["ot_cache_prune"]
    assert "entries_pruned" in results["ot_cache_prune"]
