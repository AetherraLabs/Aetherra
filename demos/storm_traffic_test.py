#!/usr/bin/env python3
"""
STORM Traffic Test
Generate memory operations and recall traffic to trigger STORM metrics emission.
"""

import asyncio
import os
import sys
import urllib.request
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

os.environ.setdefault("AETHERRA_MEMORY_STORM", "1")
os.environ.setdefault("AETHERRA_STORM_SHADOW_MODE", "1")


async def main():
    print("=" * 60)
    print("STORM Traffic Test")
    print("=" * 60)

    # Import after env setup
    from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
        AetherraMemoryEngineAdvanced,
    )

    engine = AetherraMemoryEngineAdvanced()
    print("[1/5] Memory engine initialized (Advanced with STORM)")

    # Check STORM status
    status = engine.get_system_status()
    storm_status = status.get("storm", {})
    print("\n[2/5] STORM Status:")
    print(f"  Enabled: {storm_status.get('enabled', False)}")
    print(f"  Shadow Mode: {storm_status.get('shadow_mode', False)}")
    print(f"  Backend: {storm_status.get('ot_backend', 'N/A')}")
    print(f"  TT Rank Cap: {storm_status.get('tt_rank_cap', 'N/A')}")

    # Seed some memories
    print("\n[3/5] Seeding test memories...")
    memories = [
        "STORM uses optimal transport theory for semantic recall",
        "The Wasserstein distance measures the cost of transforming one distribution to another",
        "Sheaf coherence ensures retrieved memories form a consistent structure",
        "Shadow mode allows STORM to run alongside baseline for safe validation",
        "Hybrid recall combines STORM with baseline for graceful degradation",
        "Transport cost metrics indicate the quality of STORM retrievals",
        "Tensor-train decomposition enables efficient high-dimensional representations",
        "Memory recall in Aetherra supports multiple strategies including storm_hybrid",
        "Phase 1 deployment focuses on shadow mode metrics collection",
        "STORM metrics include recalls_total, shadow_comparisons, and sheaf_inconsistency",
    ]

    for i, content in enumerate(memories, 1):
        await engine.remember(
            content=content,
            tags=["storm", "test", f"batch_{i}"],
            category="test_storm",
            metadata={"test_id": f"storm_traffic_{i}"},
        )
    print(f"  ✓ Seeded {len(memories)} memories")

    # Execute recalls with different strategies
    print("\n[4/5] Executing recalls with STORM strategies...")
    queries = [
        "optimal transport theory",
        "sheaf coherence validation",
        "shadow mode metrics",
        "hybrid recall patterns",
        "transport cost analysis",
    ]

    for query in queries:
        # Baseline recall
        result_base = await engine.recall_typed(
            query=query, recall_strategy="base", limit=3
        )
        print(f"  • Base recall for '{query}': {len(result_base.items)} items")

        # STORM hybrid recall (shadow mode returns baseline but exercises STORM path)
        result_hybrid = await engine.recall_typed(
            query=query, recall_strategy="storm_hybrid", limit=3
        )
        print(
            f"  • Hybrid recall for '{query}': {len(result_hybrid.items)} items (source: {result_hybrid.metadata.get('source', 'unknown')})"
        )

        # Check for STORM metadata
        storm_meta = result_hybrid.metadata.get("storm_meta", {})
        if storm_meta:
            print(
                f"    STORM meta: transport_cost={storm_meta.get('transport_cost', 'N/A')}, inconsistency={storm_meta.get('sheaf_inconsistency', 'N/A')}"
            )

    # Probe metrics endpoint
    print("\n[5/5] Probing metrics endpoint...")
    try:
        with urllib.request.urlopen(
            "http://localhost:3001/metrics", timeout=3.0
        ) as resp:
            metrics_text = resp.read().decode("utf-8", errors="replace")

        storm_lines = [
            line for line in metrics_text.splitlines() if "storm" in line.lower()
        ]
        print(f"  ✓ Metrics endpoint reachable (HTTP {resp.status})")
        print(f"  ✓ Lines containing 'storm': {len(storm_lines)}")

        if storm_lines:
            print("\n  Sample STORM metrics:")
            for line in storm_lines[:10]:
                print(f"    {line}")
        else:
            print("  ⚠️  No STORM metrics visible yet (expected early in shadow mode)")
            print("     STORM metrics typically appear after sustained recall traffic.")

    except Exception as e:
        print(f"  ⚠️  Could not reach metrics endpoint: {e}")
        print("     (Hub may not be running; metrics check is optional)")

    print("\n" + "=" * 60)
    print("STORM Traffic Test Complete")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Check Hub logs for STORM activity")
    print("  2. Monitor /metrics for storm_* series emergence")
    print("  3. Use tools/monitor_storm_shadow.py for daily checks")


if __name__ == "__main__":
    asyncio.run(main())
