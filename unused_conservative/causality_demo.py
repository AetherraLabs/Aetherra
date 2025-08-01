#!/usr/bin/env python3
"""
🔗 Timeline Causality & Self-Narrative Demo
============================================

Demonstrates enhanced causality tracking and self-narrative modeling capabilities.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add Aetherra to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))

try:
    from Aetherra.lyrixa.memory.fractal_mesh.base import (
        MemoryFragment,
        MemoryFragmentType,
    )
    from Aetherra.lyrixa.memory.fractal_mesh.timelines.reflective_timeline_engine import (
        ReflectiveTimelineEngine,
    )

    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_AVAILABLE = False


def create_goal_oriented_fragments():
    """Create sample fragments showing goal pursuit patterns"""
    base_time = datetime.now() - timedelta(days=7)

    fragments = [
        # Goal initiation
        MemoryFragment(
            fragment_id="goal_1",
            content={
                "text": "Decided to learn advanced plugin architecture to improve system performance"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={"timestamp": base_time, "duration": "planning"},
            symbolic_tags={
                "goal_setting",
                "plugin_architecture",
                "learning",
                "performance",
            },
            associative_links=[],
            confidence_score=0.9,
            access_pattern={"frequency": 1, "last_accessed": base_time},
            narrative_role="goal_initiation",
            created_at=base_time,
            last_evolved=base_time,
        ),
        # Initial research
        MemoryFragment(
            fragment_id="research_1",
            content={
                "text": "Started researching async patterns and discovered event-driven architectures"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={
                "timestamp": base_time + timedelta(hours=2),
                "duration": "research",
            },
            symbolic_tags={"research", "async", "learning", "plugin_architecture"},
            associative_links=["goal_1"],
            confidence_score=0.7,
            access_pattern={
                "frequency": 1,
                "last_accessed": base_time + timedelta(hours=2),
            },
            narrative_role="information_gathering",
            created_at=base_time + timedelta(hours=2),
            last_evolved=base_time + timedelta(hours=2),
        ),
        # First challenge
        MemoryFragment(
            fragment_id="challenge_1",
            content={
                "text": "Hit a wall trying to implement async plugin loading - getting race conditions"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={
                "timestamp": base_time + timedelta(days=1),
                "duration": "struggle",
            },
            symbolic_tags={"challenge", "async", "plugin_architecture", "problem"},
            associative_links=["research_1"],
            confidence_score=0.3,
            access_pattern={
                "frequency": 1,
                "last_accessed": base_time + timedelta(days=1),
            },
            narrative_role="obstacle",
            created_at=base_time + timedelta(days=1),
            last_evolved=base_time + timedelta(days=1),
        ),
        # Breakthrough insight
        MemoryFragment(
            fragment_id="insight_1",
            content={
                "text": "Realized the race condition was due to shared state - need proper isolation"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={
                "timestamp": base_time + timedelta(days=2),
                "duration": "insight",
            },
            symbolic_tags={
                "breakthrough",
                "insight",
                "async",
                "solution",
                "plugin_architecture",
            },
            associative_links=["challenge_1"],
            confidence_score=0.85,
            access_pattern={
                "frequency": 1,
                "last_accessed": base_time + timedelta(days=2),
            },
            narrative_role="turning_point",
            created_at=base_time + timedelta(days=2),
            last_evolved=base_time + timedelta(days=2),
        ),
        # Implementation success
        MemoryFragment(
            fragment_id="success_1",
            content={
                "text": "Successfully implemented isolated plugin contexts - 3x performance improvement!"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={
                "timestamp": base_time + timedelta(days=3),
                "duration": "achievement",
            },
            symbolic_tags={
                "success",
                "implementation",
                "performance",
                "plugin_architecture",
                "achievement",
            },
            associative_links=["insight_1"],
            confidence_score=0.95,
            access_pattern={
                "frequency": 1,
                "last_accessed": base_time + timedelta(days=3),
            },
            narrative_role="resolution",
            created_at=base_time + timedelta(days=3),
            last_evolved=base_time + timedelta(days=3),
        ),
        # Reflection and learning
        MemoryFragment(
            fragment_id="reflection_1",
            content={
                "text": "This experience taught me the importance of systematic debugging and state management"
            },
            fragment_type=MemoryFragmentType.SEMANTIC,
            temporal_tags={
                "timestamp": base_time + timedelta(days=4),
                "duration": "reflection",
            },
            symbolic_tags={"reflection", "learning", "growth", "meta_cognition"},
            associative_links=["success_1"],
            confidence_score=0.8,
            access_pattern={
                "frequency": 1,
                "last_accessed": base_time + timedelta(days=4),
            },
            narrative_role="learning_integration",
            created_at=base_time + timedelta(days=4),
            last_evolved=base_time + timedelta(days=4),
        ),
        # New goal emergence
        MemoryFragment(
            fragment_id="goal_2",
            content={
                "text": "Want to apply these patterns to memory system optimization next"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={
                "timestamp": base_time + timedelta(days=5),
                "duration": "planning",
            },
            symbolic_tags={
                "goal_setting",
                "memory_optimization",
                "future_planning",
                "async",
            },
            associative_links=["reflection_1"],
            confidence_score=0.9,
            access_pattern={
                "frequency": 1,
                "last_accessed": base_time + timedelta(days=5),
            },
            narrative_role="goal_evolution",
            created_at=base_time + timedelta(days=5),
            last_evolved=base_time + timedelta(days=5),
        ),
    ]

    return fragments


async def test_enhanced_causality():
    """Test enhanced causality detection and self-narrative modeling"""
    print("🧠 ENHANCED TIMELINE CAUSALITY DEMO")
    print("=" * 60)

    if not IMPORTS_AVAILABLE:
        print("❌ Required imports not available")
        return

    # Initialize timeline engine
    timeline_engine = ReflectiveTimelineEngine("causality_demo.db")
    fragments = create_goal_oriented_fragments()

    print(f"📊 Analyzing {len(fragments)} goal-oriented memory fragments")

    # 🔗 Test Advanced Causal Chain Detection
    print("\n🔗 ADVANCED CAUSAL CHAIN DETECTION")
    print("-" * 50)

    causal_chains = await timeline_engine.detect_advanced_causal_patterns(fragments)
    print(f"✅ Detected {len(causal_chains)} enhanced causal chains")

    for i, chain in enumerate(causal_chains):
        print(f"\n  🔗 Chain {i + 1}: {chain.chain_type}")
        print(f"     Strength: {chain.strength:.3f}")
        print(f"     Sequence: {len(chain.causal_sequence)} fragments")
        print(f"     Goal connections: {chain.goal_connections}")
        print(f"     Causal mechanisms: {chain.causal_mechanisms}")
        print(f"     Branch points: {len(chain.branch_points)}")
        print(
            f"     Confidence evolution: {[f'{c:.2f}' for c in chain.confidence_evolution]}"
        )

    # 🎯 Test Goal Memory Arc Analysis
    print("\n🎯 GOAL MEMORY ARC ANALYSIS")
    print("-" * 50)

    goal_arcs = await timeline_engine.analyze_goal_memory_arcs(fragments)
    print(f"✅ Identified {len(goal_arcs)} goal memory arcs")

    for i, arc in enumerate(goal_arcs):
        print(f"\n  🎯 Arc {i + 1}: {arc.arc_type}")
        print(f"     Goal: {arc.goal_description}")
        print(f"     Memory sequence: {len(arc.memory_sequence)} fragments")
        print(f"     Progress markers: {len(arc.progress_markers)}")
        print(f"     Strategy evolution: {len(arc.strategy_evolution)} changes")
        print(f"     Breakthrough moments: {len(arc.breakthrough_moments)}")
        print(f"     Obstacles: {len(arc.obstacle_patterns)}")
        print(f"     Outcome: {arc.outcome_assessment}")
        print(f"     Emotional journey: {arc.emotional_journey}")

    # 🎭 Test Self-Narrative Model Building
    print("\n🎭 SELF-NARRATIVE MODEL BUILDING")
    print("-" * 50)

    self_model = await timeline_engine.build_self_narrative_model(fragments)
    print(f"✅ Built comprehensive self-narrative model")

    print(f"\n  🎭 Identity & Self-Understanding:")
    print(f"     Identity themes: {self_model.identity_themes}")
    print(f"     Narrative coherence: {self_model.narrative_coherence:.3f}")

    print(f"\n  💪 Competency Mapping:")
    top_competencies = sorted(
        self_model.competency_map.items(), key=lambda x: x[1], reverse=True
    )[:5]
    for comp, score in top_competencies:
        print(f"     {comp}: {score:.3f}")

    print(f"\n  📈 Growth & Development:")
    print(f"     Growth trajectory points: {len(self_model.growth_trajectory)}")
    if self_model.growth_trajectory:
        print(f"     Latest trajectory: {self_model.growth_trajectory[-1]}")

    print(f"\n  ❤️ Value System:")
    top_values = sorted(
        self_model.value_system.items(), key=lambda x: x[1], reverse=True
    )[:5]
    for value, weight in top_values:
        print(f"     {value}: {weight:.3f}")

    print(f"\n  🧠 Learning & Decision Patterns:")
    print(f"     Learning style: {self_model.learning_style}")
    print(f"     Decision patterns: {len(self_model.decision_patterns)}")
    print(f"     Relationship patterns: {len(self_model.relationship_patterns)}")

    print(f"\n  🎯 Aspirations & Fears:")
    print(f"     Aspirations: {len(self_model.aspiration_model)}")
    print(f"     Fear patterns: {len(self_model.fear_patterns)}")

    print(f"\n  📊 Confidence Analysis:")
    top_confidence = sorted(
        self_model.confidence_domains.items(), key=lambda x: x[1], reverse=True
    )[:5]
    for domain, confidence in top_confidence:
        print(f"     {domain}: {confidence:.3f}")

    # 🔄 Integration Summary
    print("\n🔄 CAUSALITY & NARRATIVE INTEGRATION SUMMARY")
    print("-" * 60)
    print("✨ Enhanced capabilities demonstrated:")
    print("   🔗 Multi-step causal relationship detection")
    print("   🎯 Goal-oriented memory arc analysis")
    print("   🎭 Comprehensive self-narrative modeling")
    print("   📊 Confidence and competency mapping")
    print("   💡 Learning pattern recognition")
    print("   🚀 Future goal connection inference")

    print(f"\n📈 System demonstrates sophisticated understanding of:")
    print(
        f"   - Cause-effect chains across {sum(len(c.causal_sequence) for c in causal_chains)} fragments"
    )
    print(
        f"   - Goal pursuit patterns across {sum(len(a.memory_sequence) for a in goal_arcs)} memories"
    )
    print(f"   - Self-identity coherence: {self_model.narrative_coherence:.1%}")
    print(f"   - Competency awareness: {len(self_model.competency_map)} domains")

    return {
        "causal_chains": len(causal_chains),
        "goal_arcs": len(goal_arcs),
        "narrative_coherence": self_model.narrative_coherence,
        "competency_domains": len(self_model.competency_map),
    }


async def main():
    """Main demo execution"""
    try:
        results = await test_enhanced_causality()
        print(f"\n🎉 Demo completed successfully!")
        if results:
            print(f"📊 Results: {results}")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
