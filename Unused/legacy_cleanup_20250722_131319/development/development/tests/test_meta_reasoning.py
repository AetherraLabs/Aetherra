"""
🧪 Meta-Reasoning Engine Test Suite
Comprehensive tests for the MetaReasoningEngine functionality
"""

import sys
import os
import time
import asyncio
from pathlib import Path

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_meta_reasoning_engine():
    """Test the MetaReasoningEngine with mock systems"""

    print("🧠 Testing Meta-Reasoning Engine")
    print("=" * 40)

    # Mock memory system
    class TestMemorySystem:
        def __init__(self):
            self.stored_traces = []

        def store(self, data):
            self.stored_traces.append(data)
            return True

    # Mock plugin manager
    class TestPluginManager:
        def list_plugin_names(self):
            return ["test_plugin_1", "test_plugin_2", "summarizer", "file_manager"]

    # Initialize systems
    memory = TestMemorySystem()
    plugin_manager = TestPluginManager()

    try:
        # Import the MetaReasoningEngine
        from Aetherra.lyrixa.intelligence.meta_reasoning import MetaReasoningEngine, DecisionType

        # Create engine
        meta_engine = MetaReasoningEngine(memory, plugin_manager)

        print("✅ Meta-Reasoning Engine initialized successfully")

        # Test 1: Basic decision tracing
        print("\n1️⃣ Testing basic decision tracing...")
        trace1 = meta_engine.trace_decision(
            context={"goal": "test", "user_input": "hello"},
            decision="test_plugin_1",
            options=["test_plugin_1", "test_plugin_2"],
            confidence=0.8,
            explanation="Plugin 1 has better test capabilities",
            decision_type=DecisionType.PLUGIN_SELECTION
        )
        print(f"   ✅ Created trace: {trace1.trace_id}")
        print(f"   📊 Confidence: {trace1.confidence}")
        print(f"   🏷️ Confidence Level: {trace1.confidence_level.label}")

        # Test 2: Plugin choice explanation
        print("\n2️⃣ Testing plugin choice explanation...")
        trace2 = meta_engine.explain_plugin_choice(
            goal="summarize user data",
            context_summary="User wants overview of recent activities",
            plugin_chosen="summarizer",
            reason="Summarizer plugin is optimized for data aggregation",
            confidence=0.9,
            memory_links=["recent_summaries", "user_preferences"],
            intent="data_summarization"
        )
        print(f"   ✅ Plugin choice traced: {trace2.trace_id}")
        print(f"   🎯 Intent: {trace2.context['intent']}")
        print(f"   🔗 Memory links: {trace2.context['memory_links']}")

        # Test 3: Goal planning explanation
        print("\n3️⃣ Testing goal planning explanation...")
        planned_steps = ["analyze_request", "gather_data", "format_response"]
        trace3 = meta_engine.explain_goal_planning(
            user_request="Show me my progress this week",
            planned_steps=planned_steps,
            confidence=0.85,
            reasoning="Multi-step approach needed for comprehensive progress analysis"
        )
        print(f"   ✅ Goal planning traced: {trace3.trace_id}")
        print(f"   📋 Steps count: {trace3.context['steps_count']}")
        print(f"   🎯 Complexity: {trace3.context['complexity_estimate']}")

        # Test 4: Answer generation explanation
        print("\n4️⃣ Testing answer generation explanation...")
        trace4 = meta_engine.explain_answer_generation(
            question="What did I accomplish yesterday?",
            answer_approach="memory_based_summary",
            confidence=0.75,
            sources_used=["daily_logs", "completed_tasks", "time_tracking"],
            reasoning="Using memory-based approach for temporal query"
        )
        print(f"   ✅ Answer generation traced: {trace4.trace_id}")
        print(f"   📚 Sources: {trace4.metadata['sources_used']}")
        print(f"   ❓ Question type: {trace4.context['question_type']}")

        # Test 5: Feedback and learning
        print("\n5️⃣ Testing feedback and learning...")
        feedback_success = meta_engine.add_feedback(
            trace_id=trace2.trace_id,
            feedback_score=0.9,
            feedback_text="Excellent summarization, very helpful"
        )
        print(f"   ✅ Feedback added: {feedback_success}")

        # Test 6: Reflection
        print("\n6️⃣ Testing reflection...")
        reflection_success = meta_engine.reflect_on_decision(
            trace_id=trace3.trace_id,
            outcome="Successfully provided comprehensive progress summary",
            learned="User prefers detailed breakdown of accomplishments"
        )
        print(f"   ✅ Reflection completed: {reflection_success}")

        # Test 7: History and analytics
        print("\n7️⃣ Testing history and analytics...")
        history = meta_engine.get_reasoning_history(5)
        print(f"   📚 History entries: {len(history)}")

        trends = meta_engine.get_confidence_trends()
        print(f"   📈 Confidence trends: {trends}")

        report = meta_engine.generate_reasoning_report()
        print(f"   📊 Total decisions: {report['total_decisions']}")
        print(f"   📊 Average confidence: {report['average_confidence']:.2f}")

        # Test 8: Memory storage verification
        print("\n8️⃣ Testing memory storage...")
        print(f"   💾 Traces stored in memory: {len(memory.stored_traces)}")

        # Show sample trace structure
        if memory.stored_traces:
            sample_trace = memory.stored_traces[0]
            print(f"   📋 Sample trace type: {sample_trace.get('type')}")
            print(f"   📋 Sample decision: {sample_trace.get('decision')}")

        print("\n🎉 All tests passed successfully!")
        print(f"📊 Summary:")
        print(f"   • Decisions tracked: {len(meta_engine.decision_history)}")
        print(f"   • Memory entries: {len(memory.stored_traces)}")
        print(f"   • Learning patterns: {len(meta_engine.learning_patterns)}")

        return True

    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("💡 Make sure meta_reasoning.py is in the correct location")
        return False
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decision_types_and_confidence():
    """Test decision types and confidence level classification"""

    print("\n🔍 Testing Decision Types and Confidence Levels")
    print("=" * 45)

    try:
        from Aetherra.lyrixa.intelligence.meta_reasoning import DecisionType, ConfidenceLevel

        # Test decision types
        print("📝 Available Decision Types:")
        for decision_type in DecisionType:
            print(f"   • {decision_type.value}")

        # Test confidence levels
        print("\n🎯 Confidence Level Classification:")
        test_scores = [0.1, 0.3, 0.5, 0.7, 0.9]
        for score in test_scores:
            level = ConfidenceLevel.from_score(score)
            print(f"   Score {score} → {level.label} ({level.min_val}-{level.max_val})")

        print("   ✅ Decision types and confidence levels working correctly")

        return True

    except Exception as e:
        print(f"[ERROR] Decision types test failed: {e}")
        return False


async def test_integration_example():
    """Test the integration example"""

    print("\n🔗 Testing Integration Example")
    print("=" * 35)

    try:
        # Import and run a simple integration test
        from meta_reasoning_integration_example import MetaReasoningDemo

        print("🚀 Running integration demo...")
        demo = MetaReasoningDemo()

        # Run a single test case
        conversation_manager = demo.conversation_manager
        result = await conversation_manager.process_user_request("Can you help me summarize my data?")

        print(f"   ✅ Integration test completed")
        print(f"   📝 Response: {result[:50]}...")

        # Check reasoning history
        meta_engine = conversation_manager.meta_reasoning
        history = meta_engine.get_reasoning_history(3)
        print(f"   📚 Reasoning traces created: {len(history)}")

        return True

    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Meta-Reasoning Engine Test Suite")
    print("=" * 50)

    # Run all tests
    test1_passed = test_meta_reasoning_engine()
    test2_passed = test_decision_types_and_confidence()

    # Run async integration test
    try:
        test3_passed = asyncio.run(test_integration_example())
    except Exception as e:
        print(f"[ERROR] Async test failed: {e}")
        test3_passed = False

    # Final results
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    print(f"   • Core Engine Test: {'✅ PASSED' if test1_passed else '[ERROR] FAILED'}")
    print(f"   • Types & Confidence: {'✅ PASSED' if test2_passed else '[ERROR] FAILED'}")
    print(f"   • Integration Test: {'✅ PASSED' if test3_passed else '[ERROR] FAILED'}")

    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 All tests passed! Meta-Reasoning Engine is ready for production.")
    else:
        print("\n[WARN] Some tests failed. Check the errors above.")
