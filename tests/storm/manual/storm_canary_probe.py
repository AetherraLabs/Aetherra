#!/usr/bin/env python3
"""
Test STORM canary sampling to verify shadow recall divergence detection.
Processes multiple messages with AETHERRA_STORM_CANARY_PCT=10 to trigger sampling.
"""

import asyncio
import os
import sys
from pathlib import Path

# Set canary percentage before imports
os.environ["AETHERRA_STORM_CANARY_PCT"] = "10"

# Add project to path
ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from aetherra_hub.app import create_app


async def test_storm_canary():
    """Test STORM canary with 10% sampling rate."""
    print("Testing STORM canary sampling (10% rate)...")
    print(f"AETHERRA_STORM_CANARY_PCT={os.environ.get('AETHERRA_STORM_CANARY_PCT')}")

    app = create_app()
    client = app.test_client()

    # Check health
    print("\n1. Health check...")
    response = client.get("/health")
    assert response.status_code == 200
    print("   ✓ Health OK")

    # Get initial metrics
    print("\n2. Getting initial metrics...")
    response = client.get("/api/metrics")
    initial_metrics = response.data.decode("utf-8")

    initial_comparisons = 0
    initial_divergences = 0
    for line in initial_metrics.split("\n"):
        if line.startswith("aetherra_engine_storm_canary_comparisons_total"):
            initial_comparisons = int(line.split()[1])
        elif line.startswith("aetherra_engine_storm_canary_divergences_total"):
            initial_divergences = int(line.split()[1])

    print(f"   Initial comparisons: {initial_comparisons}")
    print(f"   Initial divergences: {initial_divergences}")

    # Process multiple messages to trigger canary sampling
    print("\n3. Processing 50 messages to trigger ~5 canary comparisons (10% rate)...")
    for i in range(50):
        response = client.get(f"/api/ai/ask?message=test_message_{i}")
        if i % 10 == 0:
            print(f"   Processed {i} messages...")
    print("   ✓ All messages processed")

    # Get final metrics
    print("\n4. Getting final metrics...")
    response = client.get("/api/metrics")
    final_metrics = response.data.decode("utf-8")

    final_comparisons = 0
    final_divergences = 0
    final_shadow_latency_count = 0
    for line in final_metrics.split("\n"):
        if line.startswith("aetherra_engine_storm_canary_comparisons_total"):
            final_comparisons = int(line.split()[1])
        elif line.startswith("aetherra_engine_storm_canary_divergences_total"):
            final_divergences = int(line.split()[1])
        elif line.startswith("aetherra_engine_storm_canary_shadow_latency_count"):
            final_shadow_latency_count = int(line.split()[1])

    print(f"   Final comparisons: {final_comparisons}")
    print(f"   Final divergences: {final_divergences}")
    print(f"   Shadow latency count: {final_shadow_latency_count}")

    # Verify sampling occurred
    delta_comparisons = final_comparisons - initial_comparisons
    delta_divergences = final_divergences - initial_divergences

    print("\n5. Results:")
    print(f"   Comparisons delta: {delta_comparisons}")
    print(f"   Divergences delta: {delta_divergences}")
    print(
        f"   Sampling rate achieved: {delta_comparisons / 50 * 100:.1f}% (expected ~10%)"
    )

    if delta_comparisons > 0:
        print("\n✅ STORM canary sampling working!")
        print(f"   - {delta_comparisons} shadow recalls executed")
        print(f"   - {delta_divergences} divergences detected")
        print(f"   - {final_shadow_latency_count} shadow latency measurements recorded")
        return True
    print("\n⚠️  No STORM canary comparisons triggered")
    print("   This may happen with small sample sizes or if recall is deterministic")
    return False


if __name__ == "__main__":
    success = asyncio.run(test_storm_canary())
    sys.exit(0 if success else 1)
