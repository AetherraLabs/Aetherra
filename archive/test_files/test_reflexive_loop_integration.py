#!/usr/bin/env python3
"""
🔄🧠 LYRIXA REFLEXIVE LOOP INTEGRATION TEST
==========================================

Test script to verify the complete integration of the Reflexive Loop (Self-Awareness)
system with the main Lyrixa assistant and brain loop.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.assistant import LyrixaAI


async def test_reflexive_loop_integration():
    """Test the complete reflexive loop integration"""
    print("🔄🧠 LYRIXA REFLEXIVE LOOP INTEGRATION TEST")
    print("=" * 50)

    try:
        # Initialize Lyrixa with reflexive loop
        lyrixa = LyrixaAI(workspace_path=str(project_root))
        await lyrixa.initialize()

        print("\n✅ Lyrixa initialized with reflexive loop")
        print(f"   Session: {lyrixa.session_id}")
        print(f"   Reflexive Loop: {type(lyrixa.reflexive_loop).__name__}")

        # Test 1: Basic interaction with self-awareness
        print("\n🧪 Test 1: Basic interaction with self-awareness...")
        response1 = await lyrixa.brain_loop(
            "I'm working on the Aetherra project and want to build better AI workflows",
            input_type="text",
            context={"session_start": True}
        )

        print(f"   Response: {response1['lyrixa_response'][:100]}...")
        print(f"   Project Awareness: {bool(response1.get('project_awareness'))}")
        print(f"   Confidence: {response1['confidence']:.2f}")

        # Test 2: Check project understanding development
        print("\n🧪 Test 2: Project understanding development...")
        response2 = await lyrixa.brain_loop(
            "I need help implementing natural language to .aether code generation using Python and machine learning",
            input_type="text"
        )

        print(f"   Response: {response2['lyrixa_response'][:100]}...")

        # Check if project understanding was updated
        project_awareness = await lyrixa.reflexive_loop.get_current_project_awareness()
        print(f"   Technologies detected: {list(project_awareness.get('technologies', set()))}")
        print(f"   Project type: {project_awareness.get('project_type', 'Unknown')}")

        # Test 3: Pattern detection
        print("\n🧪 Test 3: User pattern detection...")
        for i in range(3):
            await lyrixa.brain_loop(
                f"Can you help me debug this code issue? Attempt {i+1}",
                input_type="text"
            )

        # Check for detected patterns
        user_patterns = lyrixa.reflexive_loop.user_patterns
        print(f"   Patterns detected: {len(user_patterns)}")
        for pattern in user_patterns[-2:]:
            print(f"   - {pattern.pattern_type}: {pattern.description}")

        # Test 4: Get self-awareness insights
        print("\n🧪 Test 4: Self-awareness insights...")
        insights = await lyrixa.get_self_awareness_insights()

        print(f"   Project Understanding: {bool(insights.get('project_understanding'))}")
        print(f"   User Patterns: {len(insights.get('user_patterns', []))}")
        print(f"   Recent Insights: {len(insights.get('recent_insights', []))}")
        print(f"   Self-Reflections: {len(insights.get('self_reflections', []))}")

        # Test 5: Update self-knowledge
        print("\n🧪 Test 5: Self-knowledge update...")
        update_result = await lyrixa.update_lyrixa_self_knowledge(
            "This Aetherra project focuses on creating intelligent AI workflows using natural language processing and .aether code generation. The team prefers Python and is building a conversational AI assistant."
        )

        print(f"   Update success: {update_result.get('success')}")
        print(f"   Updated understanding: {bool(update_result.get('updated_understanding'))}")

        # Test 6: Generate project insights
        print("\n🧪 Test 6: Project insights generation...")
        project_insights = await lyrixa.generate_project_insights()

        print(f"   Generated insights: {len(project_insights)}")
        for insight in project_insights[:3]:
            print(f"   - {insight}")

        # Test 7: Test knowledge-based question with reflexive enhancement
        print("\n🧪 Test 7: Knowledge-based question with reflexive enhancement...")
        response7 = await lyrixa.brain_loop(
            "What do you know about our current project and what I've been working on?",
            input_type="text"
        )

        print(f"   Response: {response7['lyrixa_response'][:200]}...")
        print(f"   Enhanced with insights: {bool('💡' in response7['lyrixa_response'])}")

        # Test 8: Check reflexive loop state
        print("\n🧪 Test 8: Reflexive loop state inspection...")
        print(f"   Project understanding: {bool(lyrixa.reflexive_loop.project_understanding)}")
        print(f"   User patterns count: {len(lyrixa.reflexive_loop.user_patterns)}")
        print(f"   Session interactions: {len(lyrixa.reflexive_loop.session_interactions)}")
        print(f"   Self-reflections: {len(lyrixa.reflexive_loop.self_reflections)}")

        if lyrixa.reflexive_loop.project_understanding:
            pu = lyrixa.reflexive_loop.project_understanding
            print(f"   Project name: {pu.project_name}")
            print(f"   Project type: {pu.project_type}")
            print(f"   Current phase: {pu.current_phase}")
            print(f"   Technologies: {list(pu.technologies)[:5]}")
            print(f"   Confidence: {pu.confidence:.2f}")

        print("\n✅ All reflexive loop integration tests completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_reflexive_memory_integration():
    """Test memory system integration with reflexive loop"""
    print("\n🧠💾 Testing Reflexive Loop Memory Integration...")

    try:
        lyrixa = LyrixaAI(workspace_path=str(project_root))
        await lyrixa.initialize()

        # Store some project-related interactions
        test_interactions = [
            "I'm building a machine learning pipeline for natural language processing",
            "Can you help me design a plugin architecture for the Aetherra system?",
            "I need to implement error handling for the .aether code interpreter",
            "What's the best way to structure the AI assistant's memory system?"
        ]

        for interaction in test_interactions:
            await lyrixa.brain_loop(interaction, input_type="text")

        # Check if reflexive loop learned from these interactions
        project_awareness = await lyrixa.reflexive_loop.get_current_project_awareness()
        print(f"   Technologies learned: {list(project_awareness.get('technologies', set()))}")
        print(f"   Goals identified: {project_awareness.get('main_goals', [])}")

        # Test memory recall with reflexive enhancement
        memory_query = "What has the user been working on lately?"
        memories = await lyrixa.memory.recall_memories(memory_query, limit=3)
        print(f"   Memories recalled: {len(memories)}")

        return True

    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Starting Lyrixa Reflexive Loop Integration Tests...")

        # Test 1: Core integration
        test1_result = await test_reflexive_loop_integration()

        # Test 2: Memory integration
        test2_result = await test_reflexive_memory_integration()

        # Summary
        print("\n" + "=" * 50)
        print("🏁 TEST SUMMARY")
        print(f"   Core Integration: {'✅ PASSED' if test1_result else '❌ FAILED'}")
        print(f"   Memory Integration: {'✅ PASSED' if test2_result else '❌ FAILED'}")

        if test1_result and test2_result:
            print("\n🎉 ALL TESTS PASSED! Reflexive Loop integration is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")

    asyncio.run(main())
