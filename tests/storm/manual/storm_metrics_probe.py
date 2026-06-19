#!/usr/bin/env python3
"""Quick test to trigger STORM metrics collection."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Aetherra imports
from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)


async def main():
    print("🧪 Testing STORM shadow mode metrics...")

    # Initialize engine
    engine = AetherraMemoryEngineAdvanced()

    # Store a test memory
    await engine.remember(
        content="Testing STORM shadow mode metrics collection",
        tags=["test", "storm", "metrics"],
        category="validation",
    )
    print("✅ Stored test memory")

    # Recall with storm_hybrid strategy (should trigger STORM metrics)
    result = await engine.recall_typed(
        query="storm metrics test",
        recall_strategy="storm_hybrid",
        limit=5,
    )

    # Check result
    print(f"📊 Recall result source: {result.source}")
    print(f"📊 Items retrieved: {len(result.items)}")
    print(f"✅ Shadow mode verified: {result.source in ('base', 'hybrid')}")

    # Now check metrics endpoint
    import requests

    try:
        r = requests.get("http://localhost:3001/metrics", timeout=5)
        if r.status_code == 200:
            has_storm = "storm_" in r.text
            print(f"\n📈 Metrics endpoint: {r.status_code}")
            print(f"🎯 STORM metrics present: {has_storm}")

            if has_storm:
                # Show some STORM metrics
                lines = [
                    line
                    for line in r.text.split("\n")
                    if "storm_" in line and not line.startswith("#")
                ]
                print(f"\n🔍 Found {len(lines)} STORM metric lines")
                if lines:
                    print("Sample STORM metrics:")
                    for line in lines[:5]:
                        print(f"  {line}")
        else:
            print(f"❌ Metrics endpoint returned: {r.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to metrics endpoint: {e}")


if __name__ == "__main__":
    asyncio.run(main())
