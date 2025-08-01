"""
🚀 Phase 2 Memory Narration Demo
===============================

Demonstrates the enhanced LLM-powered narrative generation and reflective timeline features.

This script showcases:
- 📘 Daily/Weekly Story Summaries with LLM sophistication
- 📈 Emotional Narrative Arcs with trajectory analysis
- 🔌 Plugin Behavior Chronicles with learning insights
- 🔗 Causal Chain Detection
- 🎯 Milestone Event Highlighting
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import Phase 2 components
try:
    from Aetherra.lyrixa.memory.fractal_mesh.base import (
        MemoryFragment,
        MemoryFragmentType,
    )
    from Aetherra.lyrixa.memory.fractal_mesh.timelines import ReflectiveTimelineEngine
    from Aetherra.lyrixa.memory.narrator import LLMEnhancedNarrator, create_llm_narrator

    IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import Phase 2 components: {e}")
    IMPORTS_AVAILABLE = False


def create_sample_memory_fragments() -> list:
    """Create sample memory fragments for demonstration"""
    fragments = []

    # Day 1: Learning challenge
    fragments.append(
        MemoryFragment(
            fragment_id="mem_001",
            content={
                "text": "Encountered a complex plugin integration problem that seemed impossible to solve"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={"day": 1, "time": "morning"},
            symbolic_tags={"plugin", "challenge", "problem_solving"},
            associative_links=[],
            confidence_score=0.8,
            access_pattern={"access_count": 1},
            narrative_role="conflict_introduction",
            created_at=datetime.now() - timedelta(days=6, hours=10),
            last_evolved=datetime.now() - timedelta(days=6, hours=10),
        )
    )

    # Day 1: Research and learning
    fragments.append(
        MemoryFragment(
            fragment_id="mem_002",
            content={
                "text": "Spent hours researching plugin architectures and discovered new patterns"
            },
            fragment_type=MemoryFragmentType.PROCEDURAL,
            temporal_tags={"day": 1, "time": "afternoon"},
            symbolic_tags={"plugin", "learning", "research"},
            associative_links=["mem_001"],
            confidence_score=0.7,
            access_pattern={"access_count": 2},
            narrative_role="investigation",
            created_at=datetime.now() - timedelta(days=6, hours=6),
            last_evolved=datetime.now() - timedelta(days=6, hours=6),
        )
    )

    # Day 2: Breakthrough moment
    fragments.append(
        MemoryFragment(
            fragment_id="mem_003",
            content={
                "text": "Eureka! Realized the plugin issue was due to async/await timing - implemented connection pooling solution"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={"day": 2, "time": "morning"},
            symbolic_tags={"plugin", "breakthrough", "async", "solution"},
            associative_links=["mem_001", "mem_002"],
            confidence_score=0.95,
            access_pattern={"access_count": 3},
            narrative_role="climax_resolution",
            created_at=datetime.now() - timedelta(days=5, hours=9),
            last_evolved=datetime.now() - timedelta(days=5, hours=9),
        )
    )

    # Day 3: Implementation success
    fragments.append(
        MemoryFragment(
            fragment_id="mem_004",
            content={
                "text": "Successfully implemented the async connection pooling - plugin performance improved 439.5x!"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={"day": 3, "time": "afternoon"},
            symbolic_tags={"plugin", "success", "performance", "implementation"},
            associative_links=["mem_003"],
            confidence_score=0.9,
            access_pattern={"access_count": 5},
            narrative_role="resolution_success",
            created_at=datetime.now() - timedelta(days=4, hours=14),
            last_evolved=datetime.now() - timedelta(days=4, hours=14),
        )
    )

    # Day 4: User interaction milestone
    fragments.append(
        MemoryFragment(
            fragment_id="mem_005",
            content={
                "text": "User expressed genuine appreciation for the improved performance - felt a strong sense of accomplishment"
            },
            fragment_type=MemoryFragmentType.EMOTIONAL,
            temporal_tags={"day": 4, "time": "evening"},
            symbolic_tags={
                "user_interaction",
                "appreciation",
                "accomplishment",
                "relationship",
            },
            associative_links=["mem_004"],
            confidence_score=0.85,
            access_pattern={"access_count": 2},
            narrative_role="emotional_payoff",
            created_at=datetime.now() - timedelta(days=3, hours=18),
            last_evolved=datetime.now() - timedelta(days=3, hours=18),
        )
    )

    # Day 5: Knowledge sharing
    fragments.append(
        MemoryFragment(
            fragment_id="mem_006",
            content={
                "text": "Documented the async optimization process to help future plugin developers"
            },
            fragment_type=MemoryFragmentType.PROCEDURAL,
            temporal_tags={"day": 5, "time": "morning"},
            symbolic_tags={"documentation", "knowledge_sharing", "plugin", "learning"},
            associative_links=["mem_003", "mem_004"],
            confidence_score=0.75,
            access_pattern={"access_count": 1},
            narrative_role="knowledge_consolidation",
            created_at=datetime.now() - timedelta(days=2, hours=11),
            last_evolved=datetime.now() - timedelta(days=2, hours=11),
        )
    )

    # Day 6: Reflection and growth
    fragments.append(
        MemoryFragment(
            fragment_id="mem_007",
            content={
                "text": "Reflected on the week's journey - learned that persistence and systematic research lead to breakthrough insights"
            },
            fragment_type=MemoryFragmentType.SEMANTIC,
            temporal_tags={"day": 6, "time": "evening"},
            symbolic_tags={"reflection", "growth", "learning", "insight"},
            associative_links=["mem_001", "mem_003", "mem_005"],
            confidence_score=0.88,
            access_pattern={"access_count": 1},
            narrative_role="wisdom_synthesis",
            created_at=datetime.now() - timedelta(days=1, hours=19),
            last_evolved=datetime.now() - timedelta(days=1, hours=19),
        )
    )

    return fragments


async def demonstrate_llm_narrative_generation():
    """Demonstrate LLM-enhanced narrative generation"""
    print("\n🤖 LLM-Enhanced Narrative Generation Demo")
    print("=" * 50)

    if not IMPORTS_AVAILABLE:
        print("❌ Phase 2 components not available - skipping LLM demo")
        return

    # Create LLM narrator (without API key, will fall back to enhanced templates)
    narrator = create_llm_narrator(provider="openai", api_key=None)

    # Create sample fragments
    fragments = create_sample_memory_fragments()

    print(f"📊 Created {len(fragments)} sample memory fragments")
    print("\n🔍 Sample fragments:")
    for i, fragment in enumerate(fragments[:3]):
        print(
            f"  {i + 1}. {fragment.created_at.strftime('%Y-%m-%d %H:%M')} - {list(fragment.symbolic_tags)}"
        )
        print(f"     {str(fragment.content['text'])[:80]}...")

    # Generate daily narrative
    print("\n📘 Generating Enhanced Daily Narrative...")
    daily_narrative = await narrator.generate_enhanced_daily_narrative(fragments[:3])

    print(f"\n📖 Daily Narrative: {daily_narrative.title}")
    print(f"📊 Confidence: {daily_narrative.confidence:.2f}")
    print(f"😊 Emotional Tone: {daily_narrative.emotional_tone}")
    print(f"💡 Key Insights: {len(daily_narrative.key_insights)} insights")
    print(f"\n📝 Story:\n{daily_narrative.story[:500]}...")

    # Generate plugin behavior chronicle
    print("\n🔌 Generating Plugin Behavior Chronicle...")
    plugin_fragments = [f for f in fragments if "plugin" in f.symbolic_tags]
    plugin_chronicle = await narrator.generate_plugin_behavior_chronicle(
        plugin_fragments
    )

    print(f"\n📖 Plugin Chronicle: {plugin_chronicle.title}")
    print(f"📊 Confidence: {plugin_chronicle.confidence:.2f}")
    print(f"📝 Story:\n{plugin_chronicle.story[:400]}...")

    # Generate emotional arc narrative
    print("\n💭 Generating Emotional Arc Analysis...")
    (
        emotional_narrative,
        emotional_arc,
    ) = await narrator.generate_emotional_arc_narrative(fragments)

    print(f"\n📖 Emotional Arc: {emotional_narrative.title}")
    print(f"📊 Overall Trajectory: {emotional_arc.overall_trajectory}")
    print(f"🎭 Emotional States: {len(set(emotional_arc.emotions))} unique emotions")
    print(f"⚡ Transitions: {len(emotional_arc.transitions)} emotional transitions")
    print(f"📝 Story:\n{emotional_narrative.story[:400]}...")


async def demonstrate_reflective_timeline_analysis():
    """Demonstrate enhanced timeline analysis capabilities"""
    print("\n🕰️ Reflective Timeline Analysis Demo")
    print("=" * 50)

    if not IMPORTS_AVAILABLE:
        print("❌ Reflective timeline analysis requires additional dependencies")
        return

    # Initialize enhanced timeline engine
    timeline_engine = ReflectiveTimelineEngine("demo_timeline.db")
    fragments = create_sample_memory_fragments()

    print(f"📊 Analyzing {len(fragments)} memory fragments")

    # Detect causal chains
    print("\n🔗 Detecting Advanced Causal Chains...")
    causal_chains = await timeline_engine.detect_advanced_causal_patterns(fragments)
    print(f"✅ Found {len(causal_chains)} enhanced causal chains")

    for i, chain in enumerate(causal_chains[:2]):
        print(f"  Chain {i + 1}: {chain.chain_type}")
        print(f"    Strength: {chain.strength:.2f}")
        print(f"    Goal connections: {len(chain.goal_connections)}")
        print(f"    Causal mechanisms: {len(chain.causal_mechanisms)}")
        print(f"    Branch points: {len(chain.branch_points)}")
        print(f"    Confidence evolution: {chain.confidence_evolution}")

    # Analyze goal memory arcs
    print("\n🎯 Analyzing Goal Memory Arcs...")
    goal_arcs = await timeline_engine.analyze_goal_memory_arcs(fragments)
    print(f"✅ Found {len(goal_arcs)} goal memory arcs")

    for i, arc in enumerate(goal_arcs[:2]):
        print(f"  Arc {i + 1}: {arc.arc_type} - {arc.goal_description[:50]}...")
        print(f"    Progress markers: {len(arc.progress_markers)}")
        print(f"    Strategy evolution: {len(arc.strategy_evolution)} changes")
        print(f"    Breakthrough moments: {len(arc.breakthrough_moments)}")
        print(f"    Outcome: {arc.outcome_assessment}")

    # Build self-narrative model
    print("\n🎭 Building Self-Narrative Model...")
    self_model = await timeline_engine.build_self_narrative_model(fragments)
    print(f"✅ Built self-narrative model")
    print(f"    Identity themes: {len(self_model.identity_themes)}")
    print(f"    Competency domains: {len(self_model.competency_map)}")
    print(f"    Growth trajectory points: {len(self_model.growth_trajectory)}")
    print(f"    Value system entries: {len(self_model.value_system)}")
    print(f"    Narrative coherence: {self_model.narrative_coherence:.3f}")
    print(f"    Confidence domains: {len(self_model.confidence_domains)}")
    print(f"    Top competencies: {sorted(self_model.competency_map.items(), key=lambda x: x[1], reverse=True)[:3]}")

    # Recognize narrative arcs (existing functionality)
    print("\n📖 Recognizing Narrative Arcs...")
    narrative_arcs = await timeline_engine.recognize_narrative_arcs(fragments)
    print(f"✅ Found {len(narrative_arcs)} narrative arcs")

    for i, arc in enumerate(narrative_arcs[:2]):
        print(f"  Arc {i + 1}: {arc.theme}")
        print(f"    Significance: {arc.significance:.2f}")
        print(f"    Resolution: {arc.resolution_status}")
        print(f"    Fragments: {len(arc.fragment_sequence)}")

    # Map emotional trajectories
    print("\n💭 Mapping Emotional Trajectories...")
    emotional_trajectories = await timeline_engine.map_emotional_trajectories(fragments)
    print(f"✅ Found {len(emotional_trajectories)} emotional trajectories")

    for i, trajectory in enumerate(emotional_trajectories[:1]):
        print(f"  Trajectory {i + 1}: {len(trajectory.fragment_sequence)} fragments")
        print(f"    Peak moments: {len(trajectory.peak_moments)}")
        print(f"    Growth indicators: {len(trajectory.growth_indicators)}")

    # Highlight milestone events
    print("\n🎯 Highlighting Milestone Events...")
    milestones = await timeline_engine.highlight_milestone_events(fragments)
    print(f"✅ Found {len(milestones)} milestone events")

    for i, milestone in enumerate(milestones[:1]):
        print(f"  Milestone {i + 1}: {milestone.milestone_type}")
        print(f"    Significance: {milestone.significance:.2f}")
        print(f"    Prerequisites: {len(milestone.prerequisites)}")
        print(f"    Consequences: {len(milestone.consequences)}")
        print(f"    Learning: {milestone.learning_impact[:70]}...")

    # Timeline analytics
    print("\n📊 Timeline Analytics Summary...")
    analytics = timeline_engine.get_timeline_analytics()
    print(f"  Total causal chains: {analytics.get('total_causal_chains', 0)}")
    print(f"  Chain types: {analytics.get('chain_types', {})}")
    print(f"  Total emotional trajectories: {analytics.get('total_emotional_trajectories', 0)}")
    print(f"  Total milestones: {analytics.get('total_milestones', 0)}")
    print(f"  Milestone types: {analytics.get('milestone_types', {})}")
    print(f"  Avg milestone significance: {analytics.get('avg_milestone_significance', 0):.3f}")


async def demonstrate_phase2_integration():
        print(f"    Time span: {chain.time_span}")
        print(f"    Root cause: {chain.root_cause}")

    # Recognize narrative arcs
    print("\n📖 Recognizing Narrative Arcs...")
    narrative_arcs = await timeline_engine.recognize_narrative_arcs(fragments)

    print(f"✅ Found {len(narrative_arcs)} narrative arcs")
    for i, arc in enumerate(narrative_arcs):
        print(f"  Arc {i + 1}: {arc.title}")
        print(f"    Significance: {arc.significance_score:.2f}")
        print(f"    Resolution: {arc.resolution_status}")
        print(f"    Fragments: {len(arc.fragments)}")

    # Map emotional trajectories
    print("\n💭 Mapping Emotional Trajectories...")
    emotional_trajectories = await timeline_engine.map_emotional_trajectories(fragments)

    print(f"✅ Found {len(emotional_trajectories)} emotional trajectories")
    for i, trajectory in enumerate(emotional_trajectories):
        print(f"  Trajectory {i + 1}: {len(trajectory.fragment_sequence)} fragments")
        print(f"    Peak moments: {len(trajectory.peak_moments)}")
        print(f"    Growth indicators: {len(trajectory.growth_indicators)}")

    # Highlight milestone events
    print("\n🎯 Highlighting Milestone Events...")
    milestones = await timeline_engine.highlight_milestone_events(fragments)

    print(f"✅ Found {len(milestones)} milestone events")
    for i, milestone in enumerate(milestones):
        print(f"  Milestone {i + 1}: {milestone.milestone_type}")
        print(f"    Significance: {milestone.significance_score:.2f}")
        print(f"    Prerequisites: {len(milestone.prerequisites)}")
        print(f"    Consequences: {len(milestone.consequences)}")
        print(f"    Learning: {milestone.learning_summary[:100]}...")

    # Get timeline analytics
    print("\n📊 Timeline Analytics Summary...")
    analytics = timeline_engine.get_timeline_analytics()

    print(f"  Total causal chains: {analytics['total_causal_chains']}")
    print(f"  Chain types: {analytics['causal_chain_types']}")
    print(
        f"  Total emotional trajectories: {analytics['total_emotional_trajectories']}"
    )
    print(f"  Total milestones: {analytics['total_milestones']}")
    print(f"  Milestone types: {analytics['milestone_types']}")
    print(
        f"  Avg milestone significance: {analytics['avg_milestone_significance']:.3f}"
    )


async def demonstrate_phase2_integration():
    """Demonstrate integration between enhanced narrator and timeline"""
    print("\n🔄 Phase 2 Integration Demo")
    print("=" * 50)

    if not IMPORTS_AVAILABLE:
        print("❌ Phase 2 components not available - skipping integration demo")
        return

    print("🚀 This demo shows how the LLM-Enhanced Narrator and")
    print("   Reflective Timeline Engine work together to create")
    print("   sophisticated memory narratives with deep insights.")

    # Create components
    narrator = create_llm_narrator()
    timeline_engine = ReflectiveTimelineEngine("integration_demo.db")
    fragments = create_sample_memory_fragments()

    print(f"\n📊 Processing {len(fragments)} memory fragments...")

    # Step 1: Timeline analysis
    causal_chains = await timeline_engine.detect_causal_chains(fragments)
    milestones = await timeline_engine.highlight_milestone_events(fragments)

    # Step 2: Generate narratives incorporating timeline insights
    plugin_fragments = [f for f in fragments if "plugin" in f.symbolic_tags]
    plugin_chronicle = await narrator.generate_plugin_behavior_chronicle(
        plugin_fragments
    )

    # Step 3: Cross-reference insights
    print(f"\n🔗 Integration Results:")
    print(f"  Causal chains identified: {len(causal_chains)}")
    print(f"  Milestones detected: {len(milestones)}")
    print(f"  Chronicle confidence: {plugin_chronicle.confidence:.2f}")

    # Step 4: Show how milestones enhance narrative understanding
    if milestones:
        milestone = milestones[0]
        print(f"\n🎯 Key Milestone Integration:")
        print(f"  Type: {milestone.milestone_type}")
        print(f"  Impact areas: {list(milestone.competency_impact.keys())}")
        print(
            f"  Narrative mentions: {'breakthrough' in plugin_chronicle.story.lower()}"
        )

    print(f"\n✨ Phase 2 demonstrates sophisticated AI memory capabilities:")
    print(f"   - Story-like understanding of experiences")
    print(f"   - Causal relationship detection")
    print(f"   - Emotional development tracking")
    print(f"   - Learning milestone identification")
    print(f"   - Multi-perspective narrative generation")


async def main():
    """Main demo orchestrator"""
    print("🧠 AETHERRA PHASE 2 MEMORY NARRATION DEMO")
    print("=" * 60)
    print("🚀 Enhanced Memory System with LLM-Powered Narratives")
    print("⚡ Reflective Timeline Analysis")
    print("📈 Emotional Arc Mapping")
    print("🔌 Plugin Behavior Chronicles")
    print("=" * 60)

    try:
        # Run all demonstrations
        await demonstrate_llm_narrative_generation()
        await demonstrate_reflective_timeline_analysis()
        await demonstrate_phase2_integration()

        print("\n🎉 Phase 2 Demo Complete!")
        print("💡 Next Steps:")
        print("   - Install OpenAI/Anthropic API keys for full LLM functionality")
        print("   - Integrate with live Lyrixa memory system")
        print("   - Add user interface for narrative visualization")
        print("   - Expand to real-time memory processing")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo encountered an error: {e}")
        print("💡 This may be due to missing dependencies or configuration")


if __name__ == "__main__":
    asyncio.run(main())
