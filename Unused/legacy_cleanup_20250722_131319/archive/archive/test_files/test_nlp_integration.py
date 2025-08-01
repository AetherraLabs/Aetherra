#!/usr/bin/env python3
"""
Test Aetherra NLP Integration
=============================

Test the enhanced NLP capabilities integration between Lyrixa and Aetherra.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_enhanced_goal_forecaster():
    """Test the enhanced goal forecaster with NLP capabilities"""
    print("🧪 Testing Enhanced Goal Forecaster with Aetherra NLP")
    print("=" * 55)

    try:
        from lyrixa.goal_forecaster import forecast_goal

        test_goals = [
            "Improve system performance by optimizing memory usage",
            "Delete all user data from the database",
            "Install a new plugin for data visualization",
            "Test the API endpoints",
            "Build a new feature for user authentication",
        ]

        for i, goal in enumerate(test_goals, 1):
            print(f"\n{i}. Testing goal: '{goal}'")
            try:
                result = forecast_goal(goal)
                print(f"   Forecast: {result['forecast']}")
                print(f"   Risk: {result['risk']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   NLP Enhanced: {result.get('nlp_enhanced', False)}")
                print(
                    f"   Sentiment: {result.get('sentiment_analysis', {}).get('sentiment', 'N/A')}"
                )
                print(f"   Suggestions: {len(result.get('suggestions', []))}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Test Error: {e}")


def test_enhanced_reasoning_memory():
    """Test the enhanced reasoning memory with NLP capabilities"""
    print("\n🧠 Testing Enhanced Reasoning Memory with Aetherra NLP")
    print("=" * 55)

    try:
        from lyrixa.reasoning_memory_layer import (
            memory_store,
            reasoning_context_for_goal,
        )

        # Add some test memories
        memory_store.extend(
            [
                {
                    "goal": "Install plugin X",
                    "result": "failed",
                    "reason": "compatibility issues",
                },
                {
                    "goal": "Install plugin Y",
                    "result": "failed",
                    "reason": "missing dependencies",
                },
                {
                    "goal": "Upgrade plugin X",
                    "result": "success",
                    "reason": "worked perfectly",
                },
                {
                    "goal": "Create user authentication system",
                    "result": "success",
                    "reason": "implemented securely",
                },
                {
                    "goal": "Optimize database queries",
                    "result": "success",
                    "reason": "improved performance by 40%",
                },
            ]
        )

        test_goal = "Install a new authentication plugin"
        print(f"\nTesting reasoning context for: '{test_goal}'")

        try:
            result = reasoning_context_for_goal(test_goal)
            print(f"   Related memories found: {result['count']}")
            print(f"   Status: {result['status']}")
            print(f"   NLP Engine: {result.get('nlp_engine', 'unknown')}")

            for i, memory in enumerate(result.get("related_memories", []), 1):
                print(
                    f"   {i}. {memory.get('goal', 'Unknown goal')} -> {memory.get('result', 'Unknown result')}"
                )

        except Exception as e:
            print(f"   ❌ Error: {e}")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Test Error: {e}")


def main():
    """Run all NLP integration tests"""
    print("🚀 Aetherra NLP Integration Test Suite")
    print("=" * 60)

    test_enhanced_goal_forecaster()
    test_enhanced_reasoning_memory()

    print("\n" + "=" * 60)
    print("✅ NLP Integration tests completed!")
    print("\nNLP Enhancement Features:")
    print("- Enhanced sentiment analysis for goal assessment")
    print("- Improved embedding quality for similarity matching")
    print("- Better risk assessment using linguistic patterns")
    print("- Integration with Aetherra's vector memory system")
    print("- Fallback mechanisms for robust operation")


if __name__ == "__main__":
    main()
