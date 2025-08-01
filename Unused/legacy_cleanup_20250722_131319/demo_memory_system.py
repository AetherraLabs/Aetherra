#!/usr/bin/env python3
"""
🧠 Lyrixa Memory System Demo
============================

Demonstrates the next-generation memory architecture with:
- FractalMesh episodic memory
- Narrative generation
- Health monitoring
- Reflective analysis

This script shows how the new memory system moves beyond simple vector RAG
to provide episodic continuity, self-reflection, and story-like recall.
"""

import asyncio
from datetime import datetime, timedelta

from Aetherra.lyrixa.memory import LyrixaMemoryEngine, MemorySystemConfig
from Aetherra.lyrixa.memory.fractal_mesh.base import MemoryFragmentType


async def demo_memory_system():
    """Comprehensive demonstration of the new memory system"""

    print("🧠 Initializing Lyrixa Next-Gen Memory System...")

    # Configure the memory system
    config = MemorySystemConfig(
        auto_narrative_generation=True,
        auto_pulse_monitoring=True,
        reflection_frequency=timedelta(minutes=30),
        core_db_path="demo_memory.db",
        fractal_db_path="demo_fractal.db",
    )

    # Initialize the integrated memory engine
    memory = LyrixaMemoryEngine(config)

    print("✅ Memory system initialized with all components active")
    print(f"📊 System status: {memory.get_system_status()['components']}")

    # === DEMONSTRATION 1: EPISODIC MEMORY STORAGE ===
    print("\n🔹 DEMO 1: Storing Episodic Memories")

    # Simulate a coding session with multiple related memories
    coding_memories = [
        {
            "content": "Started working on the FractalMesh memory architecture. Initial design looks promising.",
            "tags": ["memory_system", "fractal_mesh", "architecture"],
            "fragment_type": MemoryFragmentType.EPISODIC,
            "confidence": 0.8,
            "narrative_role": "project_initiation",
        },
        {
            "content": "Implemented the concept clustering algorithm. Memory fragments now organize into thematic groups.",
            "tags": ["memory_system", "concept_clustering", "implementation"],
            "fragment_type": MemoryFragmentType.EPISODIC,
            "confidence": 0.9,
            "narrative_role": "implementation_success",
        },
        {
            "content": "Encountered issues with temporal indexing - fragments not linking properly across time periods.",
            "tags": ["memory_system", "temporal_indexing", "debugging"],
            "fragment_type": MemoryFragmentType.EPISODIC,
            "confidence": 0.4,
            "narrative_role": "encountered_problem",
        },
        {
            "content": "Solved the temporal indexing by adding bidirectional time links. System now tracks narrative continuity.",
            "tags": ["memory_system", "temporal_indexing", "solution"],
            "fragment_type": MemoryFragmentType.EPISODIC,
            "confidence": 0.95,
            "narrative_role": "problem_resolution",
        },
    ]

    print("💾 Storing coding session memories...")
    stored_fragments = []

    for i, memory_data in enumerate(coding_memories):
        # Add small time delays to simulate real development timeline
        await asyncio.sleep(0.1)  # Simulate time passage

        result = await memory.remember(**memory_data)
        if result.success:
            stored_fragments.append(result.fragment_id)
            print(f"   ✓ Stored: {memory_data['content'][:50]}...")
        else:
            print(f"   ✗ Failed: {result.message}")

    print(f"📈 Successfully stored {len(stored_fragments)} episodic memories")

    # === DEMONSTRATION 2: INTELLIGENT RECALL ===
    print("\n🔹 DEMO 2: Multi-Strategy Memory Recall")

    # Test different recall strategies
    recall_strategies = [
        ("vector", "What issues did I encounter with temporal indexing?"),
        ("conceptual", "Show me memories about the memory system"),
        ("episodic", "Tell me the story of the coding session"),
        ("hybrid", "How did I solve the indexing problem?"),
    ]

    for strategy, query in recall_strategies:
        print(f"\n🔍 {strategy.upper()} RECALL: '{query}'")

        results = await memory.recall(query=query, recall_strategy=strategy, limit=3)

        for i, result in enumerate(results):
            print(
                f"   {i + 1}. [{result['type']}] {result['source']}: {result.get('content', {})}"
            )
            print(f"       Relevance: {result['relevance_score']:.2f}")

    # === DEMONSTRATION 3: NARRATIVE GENERATION ===
    print("\n🔹 DEMO 3: Memory Narrative Generation")

    # Generate different types of narratives
    narrative_types = ["daily", "weekly", "thematic"]

    for narrative_type in narrative_types:
        print(f"\n📖 Generating {narrative_type} narrative...")

        if narrative_type == "thematic":
            narrative = await memory.generate_narrative(
                narrative_type="thematic", theme="memory_system"
            )
        else:
            # Use current time range for demo
            end_time = datetime.now()
            start_time = end_time - timedelta(
                hours=24 if narrative_type == "daily" else 168
            )

            narrative = await memory.generate_narrative(
                narrative_type=narrative_type, time_range=(start_time, end_time)
            )

        print(f"   📝 {narrative.title}")
        print(f"   🎭 Tone: {narrative.emotional_tone}")
        print(f"   📊 Confidence: {narrative.confidence:.2f}")
        print(f"   📖 Story: {narrative.story}")

        if narrative.key_insights:
            print(f"   💡 Key Insights:")
            for insight in narrative.key_insights:
                print(f"      • {insight}")

    # === DEMONSTRATION 4: MEMORY HEALTH MONITORING ===
    print("\n🔹 DEMO 4: Memory Health & Drift Detection")

    print("🩺 Running comprehensive health check...")
    health = await memory.check_memory_health()

    print(f"   📊 Total Fragments: {health.total_fragments}")
    print(f"   🎯 Active Concepts: {health.active_concepts}")
    print(f"   ✨ Average Confidence: {health.average_confidence:.2f}")
    print(f"   ⚠️  Contradictions: {health.contradiction_count}")
    print(f"   🔗 Coherence Score: {health.coherence_score:.2f}")
    print(f"   📈 Health Trend: {health.health_trend}")

    # Check for alerts
    alerts = memory.pulse_monitor.get_active_alerts()
    if alerts:
        print(f"   🚨 Active Alerts: {len(alerts)}")
        for alert in alerts[:3]:
            print(f"      • [{alert.severity}] {alert.drift_type}: {alert.description}")
            print(f"        Recommended: {alert.recommended_action}")
    else:
        print("   ✅ No active health alerts")

    # === DEMONSTRATION 5: REFLECTIVE ANALYSIS ===
    print("\n🔹 DEMO 5: Reflective Memory Analysis")

    reflection_types = [
        ("past_week", "Analyzing recent patterns and growth"),
        ("blind_spots", "Detecting knowledge gaps"),
        ("contradictions", "Finding memory conflicts"),
    ]

    for reflection_type, description in reflection_types:
        print(f"\n🔮 {description}...")

        insights = await memory.run_reflection(reflection_type=reflection_type)

        if insights:
            print(f"   💡 Discovered {len(insights)} insights:")
            for insight in insights[:2]:  # Show top 2
                print(f"      • [{insight.insight_type}] {insight.description}")
                print(f"        Significance: {insight.significance}")
                if insight.actionable_recommendation:
                    print(f"        Action: {insight.actionable_recommendation}")
        else:
            print("   📝 No significant insights found for this analysis")

    # === DEMONSTRATION 6: INTEGRATED INSIGHTS ===
    print("\n🔹 DEMO 6: Comprehensive Memory Insights")

    print("🎯 Generating integrated insights and recommendations...")
    insights_report = await memory.get_memory_insights(days=7)

    print("📋 MEMORY INSIGHTS REPORT")
    print(
        f"   🏥 Overall Health: {insights_report['health_summary']['overall_status']}"
    )
    print(f"   📊 System Performance: {insights_report['system_stats']}")

    if insights_report["recent_insights"]:
        print("   🔍 Recent Insights:")
        for insight in insights_report["recent_insights"]:
            print(f"      • [{insight['type']}] {insight['description']}")

    if insights_report["recommendations"]:
        print("   💡 Actionable Recommendations:")
        for rec in insights_report["recommendations"]:
            print(f"      • {rec}")

    # === DEMONSTRATION 7: MAINTENANCE CYCLE ===
    print("\n🔹 DEMO 7: Automated Maintenance Cycle")

    print("🔧 Running automated maintenance cycle...")
    maintenance_results = await memory.maintenance_cycle()

    print("   ✅ Maintenance completed:")
    print(
        f"      📊 Health Score: {maintenance_results['health_check'].coherence_score:.2f}"
    )
    print(f"      💡 New Insights: {len(maintenance_results['insights'])}")
    print(
        f"      📖 Generated Narratives: {'Yes' if maintenance_results['narrative'] else 'No'}"
    )
    print(f"      🚨 Alerts Resolved: {maintenance_results['alerts_resolved']}")
    print(f"      🧹 Fragments Cleaned: {maintenance_results['fragments_cleaned']}")

    # === FINAL STATUS ===
    print("\n🎯 FINAL SYSTEM STATUS")
    final_status = memory.get_system_status()

    print("📈 Performance Metrics:")
    for metric, value in final_status["performance"].items():
        print(f"   {metric}: {value}")

    print("\n✨ Components Status:")
    for component, status in final_status["components"].items():
        print(f"   {component}: {status}")

    print("\n🎉 Demo completed! The next-generation memory system demonstrates:")
    print("   🧠 Episodic continuity beyond simple vector search")
    print("   📖 Narrative generation for story-like memory recall")
    print("   🩺 Health monitoring with drift detection")
    print("   🔮 Reflective analysis for self-improvement")
    print("   🔗 Integrated multi-dimensional memory architecture")

    print(f"\n💾 Demo databases created:")
    print(f"   • {config.core_db_path}")
    print(f"   • {config.fractal_db_path}")
    print(f"   • {config.concepts_db_path}")
    print(f"   • {config.timeline_db_path}")
    print(f"   • {config.pulse_db_path}")


if __name__ == "__main__":
    print("🚀 Starting Lyrixa Memory System Demonstration")
    print("=" * 60)

    try:
        asyncio.run(demo_memory_system())
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()

    print("\n🏁 Demo session ended")
