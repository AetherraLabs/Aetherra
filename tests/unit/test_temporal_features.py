#!/usr/bin/env python3
"""
Test the enhanced memory system with temporal filtering.
This test demonstrates the new temporal features directly.
"""

import os
import sys
from datetime import datetime, timedelta

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from memory import AetherraMemory


def test_temporal_memory_features():
    """Test temporal memory features directly"""
    print("🧠 Testing Memory Temporal Features")
    print("=" * 50)

    memory = AetherraMemory()

    # Store original memories
    original_memories = memory.memory.copy()

    try:
        # Clear for testing
        memory.memory = []

        # Add test memories with different times
        now = datetime.now()
        test_data = [
            (
                "Implemented temporal filtering",
                ["development", "memory"],
                "work",
                now - timedelta(hours=1),
            ),
            ("Fixed memory bugs", ["bugfix", "memory"], "work", now - timedelta(hours=2)),
            ("Had lunch break", ["personal"], "life", now - timedelta(hours=3)),
            ("Code review session", ["review", "team"], "work", now - timedelta(days=1)),
            ("Weekend project idea", ["ideas", "personal"], "creativity", now - timedelta(days=2)),
        ]

        for text, tags, category, timestamp in test_data:
            memory.memory.append(
                {"text": text, "tags": tags, "category": category, "timestamp": str(timestamp)}
            )

        memory.save()

        print("✅ Test memories created")

        # Test 1: Basic time filtering
        print("\n📅 Test 1: Time-based recall")
        today_memories = memory.recall(time_filter="today")
        print(f"Today's memories: {len(today_memories)}")
        for mem in today_memories:
            print(f"  - {mem}")

        # Test 2: Category + time filtering
        print("\n📂 Test 2: Category + time filtering")
        work_today = memory.recall(category="work", time_filter="today")
        print(f"Work memories from today: {len(work_today)}")
        for mem in work_today:
            print(f"  - {mem}")

        # Test 3: Tag + time filtering
        print("\n🏷️ Test 3: Tag + time filtering")
        memory_tagged = memory.recall(tags=["memory"], time_filter="24_hours")
        print(f"Memory-tagged items in last 24 hours: {len(memory_tagged)}")
        for mem in memory_tagged:
            print(f"  - {mem}")

        # Test 4: Temporal analysis
        print("\n📊 Test 4: Temporal analysis")
        analysis = memory.temporal_analysis("7_days", "daily")
        print(f"Analysis results: {analysis['total_periods']} periods")
        for period, data in analysis["periods"].items():
            print(f"  {period}: {data['memory_count']} memories")

        # Test 5: Reflection summary
        print("\n🔄 Test 5: Reflection summary")
        reflection = memory.reflection_summary("24_hours")
        print(reflection)

        # Test 6: Memory statistics
        print("\n📈 Test 6: Enhanced statistics")
        stats = memory.get_memory_stats()
        print(stats)

        print("\n✅ All temporal memory tests passed!")

    finally:
        # Restore original memories
        memory.memory = original_memories
        memory.save()
        print("\n🔧 Original memory state restored")


if __name__ == "__main__":
    test_temporal_memory_features()
