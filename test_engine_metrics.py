#!/usr/bin/env python3
"""
Quick test to verify engine metrics are present in /api/metrics endpoint.
Starts Hub, processes a message, checks metrics output.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aetherra_hub.app_factory import create_app


async def test_metrics():
    """Test that engine metrics are exported."""
    print("Creating Hub app...")
    app = create_app()

    # Start test client
    client = app.test_client()

    # Check health
    print("Checking /health...")
    response = client.get("/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    print("✓ Health check passed")

    # Process a message to generate engine metrics
    print("\nProcessing test message...")
    response = client.get("/api/ai/ask?message=test")
    print(f"  Response status: {response.status_code}")

    # Get metrics
    print("\nFetching /api/metrics...")
    response = client.get("/api/metrics")
    assert response.status_code == 200, (
        f"Metrics request failed: {response.status_code}"
    )

    metrics_text = response.data.decode("utf-8")
    lines = metrics_text.split("\n")

    # Check for engine metrics
    required_metrics = [
        "aetherra_engine_message_latency_ms_sum",
        "aetherra_engine_message_latency_ms_count",
        "aetherra_engine_message_latency_ms_bucket",
        "aetherra_engine_recall_latency_ms_sum",
        "aetherra_engine_recall_latency_ms_count",
        "aetherra_engine_recall_latency_ms_bucket",
        "aetherra_engine_recall_success_total",
        "aetherra_engine_recall_failure_total",
        "aetherra_engine_storm_canary_comparisons_total",
        "aetherra_engine_storm_canary_divergences_total",
    ]

    found_metrics = set()
    for line in lines:
        if line.startswith("#"):
            continue
        for metric_name in required_metrics:
            if line.startswith(metric_name) and metric_name not in found_metrics:
                found_metrics.add(metric_name)
                print(f"  ✓ Found: {metric_name}")

    print(f"\nMetrics found: {len(found_metrics)}/{len(required_metrics)}")

    if len(found_metrics) < len(required_metrics):
        missing = set(required_metrics) - found_metrics
        print(f"❌ Missing metrics: {missing}")
        return False

    print("\n✅ All engine metrics present in /api/metrics!")

    # Show sample values
    print("\nSample metric values:")
    for line in lines:
        if not line.startswith("#") and "aetherra_engine_" in line:
            print(f"  {line[:80]}")
            if line.startswith("aetherra_engine_storm"):
                # Only show STORM canary lines
                continue
            break

    return True


if __name__ == "__main__":
    success = asyncio.run(test_metrics())
    sys.exit(0 if success else 1)
