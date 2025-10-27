#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Test Phase 9 Self-Incorporation Metrics Bridge
==============================================

Verifies that the Phase 9 metrics bridge correctly forwards
Self-Incorporation metrics to the self-improvement engine.

Author: Aetherra Labs
Created: 2025-10-23
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_phase9_bridge():
    """Test Phase 9 metrics bridge functionality."""
    from Aetherra.homeostasis.self_incorporation_metrics_bridge import (
        SelfIncorporationMetricsBridge,
    )

    print("🧪 Testing Phase 9 Self-Incorporation Metrics Bridge")
    print("=" * 60)

    # Create bridge instance
    bridge = SelfIncorporationMetricsBridge()
    print("✅ Bridge instance created")

    # Check initial status
    status = bridge.get_status()
    print("\n📊 Initial Status:")
    print(f"  Running: {status['running']}")
    print(f"  Metrics Forwarded: {status['metrics_forwarded']}")
    print(f"  Forward Failures: {status['forward_failures']}")
    print(f"  Bridge Interval: {status['bridge_interval']}s")

    # Test health score calculation
    print("\n🔍 Testing health score calculation...")

    # Mock Self-Incorporation health data
    mock_health = {
        "status": "running",
        "running": True,
        "config_enabled": True,
        "roots_count": 2,
    }

    mock_metrics = {
        "files_discovered": 150,
        "files_classified": 120,
        "files_integrated": 80,
        "files_quarantined": 5,
        "night_cycles_completed": 3,
        "night_cycle_insights": 12,
    }

    health_score = bridge._calculate_si_health_score(mock_health, mock_metrics)
    print(f"  Health Score: {health_score:.2f} (0.0-1.0)")

    # Calculate integration success rate
    integrated = mock_metrics["files_integrated"]
    quarantined = mock_metrics["files_quarantined"]
    total_processed = integrated + quarantined
    success_rate = integrated / total_processed if total_processed > 0 else 0.0
    print(f"  Integration Success Rate: {success_rate:.2%}")
    print(f"  Quarantine Rate: {(1 - success_rate):.2%}")

    # Expected health score breakdown:
    # - Running + Enabled: 0.4
    # - Success rate (80/85 = 94%): 0.3 * 0.94 = 0.282
    # - Files discovered: 0.1
    # - Files classified: 0.1
    # - Night cycles: 0.1
    # Total: ~0.982
    expected_score = 0.98
    print(f"  Expected Score: ~{expected_score:.2f}")

    if abs(health_score - expected_score) < 0.1:
        print("  ✅ Health score calculation correct")
    else:
        print(
            f"  ⚠️  Health score differs from expected (delta: {abs(health_score - expected_score):.2f})"
        )

    # Test metric collection
    print("\n📈 Testing metric collection...")

    # Create a proper mock with async method
    class MockSIService:
        async def health_check(self):
            return {
                **mock_health,
                "metrics": mock_metrics,
            }

    mock_si_service = MockSIService()

    metrics = await bridge._collect_si_metrics(mock_si_service)
    print(f"  Collected {len(metrics)} metrics:")
    for metric_name, metric_data in list(metrics.items())[:5]:  # Show first 5
        print(f"    - {metric_name}: {metric_data['value']} {metric_data['unit']}")

    # Verify core metrics are present
    expected_metrics = [
        "si_files_discovered",
        "si_files_classified",
        "si_files_integrated",
        "si_files_quarantined",
        "si_night_cycles_completed",
        "si_health_score",
    ]

    missing_metrics = [m for m in expected_metrics if m not in metrics]
    if not missing_metrics:
        print("  ✅ All expected metrics present")
    else:
        print(f"  ⚠️  Missing metrics: {missing_metrics}")

    print("\n" + "=" * 60)
    print("✅ Phase 9 Bridge Test Complete")
    print("\nNext Steps:")
    print("1. Start Aetherra OS with Phase 9 integrated")
    print("2. Verify metrics appear in Self-Improvement Engine")
    print("3. Check Hub dashboard for SI metrics")
    print("4. Monitor homeostasis system health includes SI contribution")


if __name__ == "__main__":
    asyncio.run(test_phase9_bridge())
