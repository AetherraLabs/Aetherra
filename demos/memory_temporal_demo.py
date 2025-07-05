#!/usr/bin/env python3
"""
Memory Temporal Filtering Enhancement Demo
==========================================

This demo showcases the new temporal filtering and reflection capabilities
added to the AetherraCode memory system.

Features demonstrated:
- Time-based memory recall
- Temporal analysis
- Memory reflection summaries
- Period comparison
- Enhanced filtering options
"""

import os
import sys
from datetime import datetime, timedelta

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from memory import AetherraMemory


def colorize(text, color):
    """Add color to text for better output readability"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "end": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors.get('end', '')}"


def print_section(title, content=""):
    """Print a formatted section header"""
    print(f"\n{colorize('=' * 60, 'cyan')}")
    print(f"{colorize(title, 'bold')}")
    print(f"{colorize('=' * 60, 'cyan')}")
    if content:
        print(content)


def create_test_memories(memory):
    """Create test memories with different timestamps"""
    now = datetime.now()

    test_memories = [
        {
            "text": "Started working on the AetherraCode memory system enhancement",
            "tags": ["development", "memory", "enhancement"],
            "category": "work",
            "time_offset": timedelta(hours=2),
        },
        {
            "text": "Implemented temporal filtering for memory recall",
            "tags": ["development", "temporal", "filtering"],
            "category": "work",
            "time_offset": timedelta(hours=1),
        },
        {
            "text": "Had a great idea about AI-native architecture",
            "tags": ["ideas", "ai", "architecture"],
            "category": "insights",
            "time_offset": timedelta(minutes=30),
        },
        {
            "text": "Completed the reflection summary feature",
            "tags": ["development", "reflection", "complete"],
            "category": "work",
            "time_offset": timedelta(minutes=15),
        },
        {
            "text": "Testing the enhanced memory system works perfectly",
            "tags": ["testing", "memory", "success"],
            "category": "validation",
            "time_offset": timedelta(minutes=5),
        },
        {
            "text": "Thinking about future roadmap for AetherraCode",
            "tags": ["planning", "future", "roadmap"],
            "category": "strategy",
            "time_offset": timedelta(days=1),
        },
        {
            "text": "Initial concept for AetherraCode language",
            "tags": ["concept", "language", "initial"],
            "category": "research",
            "time_offset": timedelta(days=7),
        },
    ]

    # Add memories with simulated timestamps
    original_memories = memory.memory.copy()
    memory.memory = []  # Clear for demo

    for mem_data in test_memories:
        timestamp = now - mem_data["time_offset"]
        memory.memory.append(
            {
                "text": mem_data["text"],
                "timestamp": str(timestamp),
                "tags": mem_data["tags"],
                "category": mem_data["category"],
            }
        )

    memory.save()
    return original_memories


def demo_temporal_filtering():
    """Demonstrate temporal filtering capabilities"""
    print_section("🧠 AetherraCode Memory Temporal Enhancement Demo")

    # Initialize memory system
    memory = AetherraMemory()

    # Backup existing memories
    original_memories = create_test_memories(memory)

    try:
        # Demo 1: Basic time filtering
        print_section("📅 Time-Based Memory Recall")

        print(colorize("Recent memories (last 2 hours):", "yellow"))
        recent = memory.recall(time_filter="2_hours")
        for i, mem in enumerate(recent, 1):
            print(f"{i}. {mem}")

        today_text = "Today's memories:"
        print(f"\n{colorize(today_text, 'yellow')}")
        today = memory.recall(time_filter="today")
        for i, mem in enumerate(today, 1):
            print(f"{i}. {mem}")

        # Demo 2: Temporal analysis
        print_section("📊 Temporal Analysis")

        analysis = memory.temporal_analysis("7_days", "daily")
        print("Analysis for last 7 days (daily granularity):")
        print(f"Total periods with activity: {analysis['total_periods']}")

        for period, data in analysis["periods"].items():
            print(f"  {period}: {data['memory_count']} memories")
            if data["categories"]:
                cats = ", ".join([f"{cat}({count})" for cat, count in data["categories"].items()])
                print(f"    Categories: {cats}")

        # Demo 3: Reflection summary
        print_section("🔄 Memory Reflection Summary")

        reflection = memory.reflection_summary("24_hours")
        print(reflection)

        # Demo 4: Period comparison
        print_section("📈 Period Comparison")

        comparison = memory.compare_periods("1_days", "7_days")
        print("Comparing last day vs last week:")
        print(f"  Recent day: {comparison['period1_count']} memories")

        # Handle different return structures
        if "period2_extended_count" in comparison:
            print(
                f"  Previous week (excluding recent day): {comparison['period2_extended_count']} memories"
            )
        else:
            print(f"  Full week period: {comparison['period2_count']} memories")
        print(
            f"  Trend: {colorize(comparison['trend'], 'green' if comparison['trend'] == 'increasing' else 'yellow')}"
        )

        # Demo 5: Advanced time filters
        print_section("🔍 Advanced Time Filtering")

        # Custom date range
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        custom_filter = {"from": str(yesterday), "to": str(now)}

        custom_memories = memory.recall(time_filter=custom_filter)
        print(f"Memories from custom date range (last 24 hours): {len(custom_memories)}")

        # Category + time filtering
        work_today = memory.recall(category="work", time_filter="today")
        print(f"Work memories from today: {len(work_today)}")

        # Tags + time filtering
        dev_recent = memory.recall(tags=["development"], time_filter="2_hours")
        print(f"Development memories from last 2 hours: {len(dev_recent)}")

        # Demo 6: Memory statistics with temporal data
        print_section("📈 Enhanced Memory Statistics")

        stats = memory.get_memory_stats()
        print(stats)

        print_section("✨ Temporal Enhancement Benefits")
        benefits = [
            "🕐 Time-aware memory recall for context-sensitive responses",
            "📊 Temporal pattern analysis for behavioral insights",
            "🔄 Reflection summaries for periodic self-analysis",
            "📈 Period comparison for tracking progress and trends",
            "🎯 Combined filtering (time + tags + categories) for precise recall",
            "🧠 AI-native temporal awareness for smarter interactions",
        ]

        for benefit in benefits:
            print(f"  {benefit}")

        print(f"\n{colorize('Memory temporal enhancement successfully demonstrated!', 'green')}")

    finally:
        # Restore original memories
        memory.memory = original_memories
        memory.save()
        print(f"\n{colorize('Original memory state restored.', 'blue')}")


if __name__ == "__main__":
    demo_temporal_filtering()
