# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
test_hub_storm_metrics_export.py
=================================

Unit tests for STORM metrics export via Hub /metrics endpoint.

Verifies:
- STORM metrics appear when STORM enabled
- All 13 metric series exported (6 counters, 6 gauges, 1 labeled)
- Correct Prometheus format
- Metrics absent when STORM disabled
- Error handling for unavailable STORM engine
"""

# Standard library imports
import pytest


class _MockSTORMMetrics:
    """Mock STORM metrics object."""

    def __init__(self, data):
        self.data = data

    def snapshot(self):
        """Return metrics snapshot matching StormMetrics.snapshot()."""
        return self.data


class _MockSTORMEngine:
    """Lightweight mock STORM engine for testing."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        # Metrics data with correct keys matching StormMetrics.snapshot()
        metrics_data = {
            "aetherra_storm_approximate_recalls_total": 42,
            "aetherra_storm_maintenance_total": 5,
            "aetherra_storm_branch_barycenters_total": 3,
            "aetherra_storm_shadow_comparisons_total": 100,
            "aetherra_storm_shadow_divergences_total": 2,
            "aetherra_storm_shadow_errors_total": 0,
            "aetherra_storm_ot_cost_avg": 0.234,
            "aetherra_storm_sheaf_inconsistency": 0.012,
            "aetherra_storm_tt_rank": 16,
            "aetherra_storm_recall_latency_ms_p95": 45.6,
            "aetherra_storm_shadow_agreement_rate": 0.98,
            "aetherra_storm_shadow_latency_ms_avg": 12.3,
            "aetherra_storm_maintenance_last": {
                "rebalance_clusters": 1698765432.0,
                "update_barycenters": 1698765400.0,
                "scan_inconsistencies": 1698765380.0,
                "prune_ot_cache": 1698765360.0,
            },
        }
        self.metrics = _MockSTORMMetrics(metrics_data)


class _MockMemoryEngine:
    """Mock memory engine with STORM support."""

    def __init__(self, storm_enabled=True):
        self._storm_engine = _MockSTORMEngine(enabled=storm_enabled)

    def get_status(self):
        """Mock get_status for Hub compatibility."""
        return {
            "storm": {
                "enabled": self._storm_engine.enabled,
                "shadow_mode": False,
                "backends": {"pot": True, "keops": False},
                "selected_backend": "pot",
            }
        }


class _MockMemorySystem:
    """Mock memory system wrapping engine."""

    def __init__(self, storm_enabled=True):
        self.engine = _MockMemoryEngine(storm_enabled=storm_enabled)


class _MockEngine:
    """Mock Aetherra engine with memory system."""

    def __init__(self, storm_enabled=True):
        self.memory_system = _MockMemorySystem(storm_enabled=storm_enabled)


@pytest.fixture
def mock_engine_with_storm():
    """Create a mock engine with STORM-enabled memory system."""
    return _MockEngine(storm_enabled=True)


@pytest.fixture
def mock_engine_without_storm():
    """Create a mock engine with STORM-disabled memory system."""
    return _MockEngine(storm_enabled=False)


@pytest.mark.asyncio
async def test_storm_metrics_export_when_enabled(mock_engine_with_storm):
    """Verify STORM metrics exported when engine enabled."""
    # Aetherra imports
    from aetherra_hub.services import metrics_accum
    from aetherra_hub.services.registry_client import _get_registry_async
    from aetherra_service_registry import get_service_registry

    # Register mock engine
    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", mock_engine_with_storm)

    # Get STORM metrics directly from the async path (bypass sync wrapper)
    reg = await _get_registry_async()
    info = reg.get_service_info("aetherra_engine")
    assert info is not None
    assert info.instance is not None

    eng = info.instance
    ms = getattr(eng, "memory_system", None)
    assert ms is not None

    engine = getattr(ms, "engine", None)
    assert engine is not None

    storm_engine = getattr(engine, "_storm_engine", None)
    assert storm_engine is not None
    assert hasattr(storm_engine, "metrics")
    assert hasattr(storm_engine.metrics, "snapshot")

    snapshot = storm_engine.metrics.snapshot()
    assert isinstance(snapshot, dict)
    assert "aetherra_storm_approximate_recalls_total" in snapshot

    # Build metrics output using the correct function
    lines = metrics_accum.build_all_metrics_lines()
    output = "\n".join(lines)

    # Verify all STORM counters present
    assert "aetherra_storm_approximate_recalls_total" in output
    assert "aetherra_storm_maintenance_total" in output
    assert "aetherra_storm_branch_barycenters_total" in output
    assert "aetherra_storm_shadow_comparisons_total" in output
    assert "aetherra_storm_shadow_divergences_total" in output
    assert "aetherra_storm_shadow_errors_total" in output

    # Verify all STORM gauges present
    assert "aetherra_storm_ot_cost_avg" in output
    assert "aetherra_storm_sheaf_inconsistency" in output
    assert "aetherra_storm_tt_rank" in output
    assert "aetherra_storm_recall_latency_ms_p95" in output
    assert "aetherra_storm_shadow_agreement_rate" in output
    assert "aetherra_storm_shadow_latency_ms_avg" in output

    # Verify labeled gauge present (maintenance_last)
    assert "aetherra_storm_maintenance_last" in output


@pytest.mark.asyncio
async def test_storm_metrics_absent_when_disabled(mock_engine_without_storm):
    """Verify STORM metrics not exported when engine disabled."""
    # Aetherra imports
    from aetherra_hub.services import metrics_accum, registry_client
    from aetherra_service_registry import get_service_registry

    # Register mock engine with STORM disabled
    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", mock_engine_without_storm)

    # Get STORM metrics via registry client
    storm = registry_client.get_storm_metrics()
    assert storm is not None
    assert storm.get("enabled") is False

    # Build metrics output
    lines = metrics_accum.build_all_metrics_lines()
    output = "\n".join(lines)

    # Verify STORM metrics NOT present
    assert "aetherra_storm_approximate_recalls_total" not in output
    assert "aetherra_storm_maintenance_total" not in output
    assert "aetherra_storm_ot_cost_avg" not in output
    assert "aetherra_storm_maintenance_last" not in output


@pytest.mark.asyncio
async def test_storm_metrics_format_valid_prometheus(mock_engine_with_storm):
    """Verify STORM metrics follow valid Prometheus format."""
    # Aetherra imports
    from aetherra_hub.services import metrics_accum
    from aetherra_service_registry import get_service_registry

    # Register engine
    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", mock_engine_with_storm)

    # Build metrics
    lines = metrics_accum.build_all_metrics_lines()

    # Verify format: each line should be "metric_name value" or "metric_name{labels} value"
    storm_lines = [line for line in lines if "aetherra_storm_" in line]
    assert len(storm_lines) > 0, "Expected STORM metrics in output"

    for line in storm_lines:
        # Skip comments
        if line.startswith("#"):
            continue

        # Must have metric name and value
        assert " " in line, f"Invalid metric line (no space): {line}"

        # Should not have multiple consecutive spaces
        assert "  " not in line, f"Invalid metric line (double space): {line}"

        # Value should be numeric or "NaN"
        parts = line.rsplit(" ", 1)
        value = parts[-1]
        assert value.replace(".", "", 1).replace("-", "", 1).isdigit() or value in [
            "NaN",
            "+Inf",
            "-Inf",
        ], f"Invalid metric value: {value} in line: {line}"


@pytest.mark.asyncio
async def test_storm_metrics_graceful_fallback_on_error():
    """Verify graceful fallback when STORM engine unavailable."""
    # Aetherra imports
    from aetherra_hub.services import registry_client
    from aetherra_service_registry import get_service_registry

    # Register engine WITHOUT memory_system
    class _MockEngine:
        pass

    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", _MockEngine())

    # Should return fallback dict
    storm = registry_client.get_storm_metrics()
    assert storm == {"enabled": False}


@pytest.mark.asyncio
async def test_storm_metrics_maintenance_last_labels(mock_engine_with_storm):
    """Verify maintenance_last has proper action labels."""
    # Aetherra imports
    from aetherra_hub.services import metrics_accum
    from aetherra_service_registry import get_service_registry

    # Register engine (mock already has maintenance_last populated)
    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", mock_engine_with_storm)

    # Build metrics
    lines = metrics_accum.build_all_metrics_lines()
    output = "\n".join(lines)

    # Verify labeled gauge format: aetherra_storm_maintenance_last{action="..."} value
    assert 'aetherra_storm_maintenance_last{action="' in output

    # Should have entries for the 4 maintenance actions
    assert (
        "rebalance_clusters" in output
        or "update_barycenters" in output
        or "scan_inconsistencies" in output
        or "prune_ot_cache" in output
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
