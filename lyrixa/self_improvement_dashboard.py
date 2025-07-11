#!/usr/bin/env python3
"""
Lyrixa Self-Improvement Dashboard (CLI)
Summarizes recent self-insight, evaluation cycles, and auto-improvements.
"""

import asyncio
from datetime import datetime

from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem


async def print_dashboard(memory_db_path="lyrixa_enhanced_memory.db"):
    memory = LyrixaEnhancedMemorySystem(memory_db_path=memory_db_path)
    print("\n=== Lyrixa Self-Improvement Dashboard ===\n")
    # Show recent self-insights
    insights = await memory.get_memories_by_tags(["self_insight"], limit=10)
    print(f"Recent Self-Insights ({len(insights)}):")
    for i, insight in enumerate(insights, 1):
        content = insight.get("content", {})
        print(f"  {i}. {content.get('insights', content)}")
    # Show recent evaluation cycles
    evals = await memory.get_memories_by_tags(["self_evaluation"], limit=5)
    print(f"\nRecent Evaluation Cycles ({len(evals)}):")
    for i, ev in enumerate(evals, 1):
        ts = ev.get("created_at", "?")
        recs = len(ev.get("content", {}).get("recommendations", []))
        autos = len(ev.get("content", {}).get("auto_improvements", []))
        print(f"  {i}. {ts} | {recs} recs | {autos} auto-improvements")
    # Show recent auto-improvements
    autos = await memory.get_memories_by_tags(["auto_improvement"], limit=5)
    print(f"\nRecent Auto-Improvements ({len(autos)}):")
    for i, auto in enumerate(autos, 1):
        content = auto.get("content", {})
        print(
            f"  {i}. {content.get('improvement_action', 'N/A')} | {content.get('timestamp', '?')}"
        )
    print("\n========================================\n")


if __name__ == "__main__":
    asyncio.run(print_dashboard())
