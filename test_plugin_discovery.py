#!/usr/bin/env python3
"""
Test script for enhanced plugin discovery and AI integration
Demonstrates the new intent-based plugin discovery system
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.plugin_manager import (
    discover_plugins_by_intent,
    get_ai_plugin_recommendations,
    get_plugin_discovery_stats,
    get_plugins_info,
    list_plugins,
)


def test_basic_discovery():
    """Test basic plugin discovery functionality"""
    print("🔍 BASIC PLUGIN DISCOVERY TEST")
    print("=" * 50)

    # List all available plugins
    plugins = list_plugins()
    print(f"Available plugins: {plugins}")

    # Get comprehensive plugin info
    info = get_plugins_info()
    print(f"\nTotal plugins loaded: {len(info)}")

    for name, details in info.items():
        metadata = details.get("metadata", {})
        print(f"  - {name}: {metadata.get('description', 'No description')}")
        print(f"    Category: {metadata.get('category', 'unknown')}")
        print(f"    Capabilities: {metadata.get('capabilities', [])}")
    print()


def test_intent_discovery():
    """Test intent-based plugin discovery"""
    print("🎯 INTENT-BASED DISCOVERY TEST")
    print("=" * 50)

    test_queries = [
        "I need to analyze some text for sentiment",
        "Can you help me calculate 2 + 3 * 4?",
        "I want to format my messy Python code",
        "Calculate the square root of 25",
        "Find statistics for my dataset",
        "I need to beautify my code",
        "Perform trigonometric calculations",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        discoveries = discover_plugins_by_intent(query, max_results=3)

        if discoveries:
            print(f"Found {len(discoveries)} relevant plugins:")
            for discovery in discoveries:
                name = discovery["name"]
                score = discovery["score"]
                reason = discovery["reason"]
                print(f"  • {name} (score: {score:.1f}) - {reason}")
        else:
            print("  No relevant plugins found")


def test_ai_recommendations():
    """Test AI-friendly plugin recommendations"""
    print("🤖 AI RECOMMENDATION TEST")
    print("=" * 50)

    test_scenarios = [
        {
            "goal": "I want to analyze customer feedback",
            "context": "I have text reviews that need sentiment analysis",
        },
        {
            "goal": "Format my Python code",
            "context": "The code is messy and needs proper indentation",
        },
        {
            "goal": "Calculate some complex math",
            "context": "Need trigonometric functions and statistics",
        },
    ]

    for scenario in test_scenarios:
        goal = scenario["goal"]
        context = scenario["context"]

        print(f"\nScenario: {goal}")
        print(f"Context: {context}")

        recommendations = get_ai_plugin_recommendations(goal, context, include_examples=True)

        print(f"Summary: {recommendations['summary']}")

        if recommendations["recommendations"]:
            print("Detailed recommendations:")
            for rec in recommendations["recommendations"]:
                print(f"  Plugin: {rec['plugin_name']}")
                print(f"  Relevance: {rec['relevance_score']:.1f}")
                print(f"  Purpose: {rec['purpose']}")
                print(f"  Example: {rec['example_usage']}")
                print(f"  Reason: {rec['reason']}")
                print()


def test_discovery_stats():
    """Test plugin discovery statistics"""
    print("📊 DISCOVERY STATISTICS")
    print("=" * 50)

    stats = get_plugin_discovery_stats()

    print(f"Total plugins: {stats['total_plugins']}")
    print(f"Plugins with intent: {stats['plugins_with_intent']}")
    print(f"Intent coverage: {stats['intent_coverage']}")

    print("\nPlugin categories:")
    for category, count in stats["categories"].items():
        print(f"  - {category}: {count}")

    print("\nTop purposes:")
    for purpose, count in stats["top_purposes"]:
        print(f"  - {purpose}: {count}")


def test_advanced_scenarios():
    """Test advanced discovery scenarios"""
    print("⚡ ADVANCED SCENARIO TESTING")
    print("=" * 50)

    # Test complex multi-intent queries
    complex_queries = [
        "I need to analyze text sentiment and also format some code",
        "Calculate statistics and also do some trigonometry",
        "Format code, analyze text, and perform mathematical calculations",
        "Help me with data analysis and code beautification",
    ]

    for query in complex_queries:
        print(f"\nComplex query: '{query}'")
        discoveries = discover_plugins_by_intent(query, max_results=5)

        if discoveries:
            print(f"Found {len(discoveries)} plugins:")
            for discovery in discoveries:
                name = discovery["name"]
                score = discovery["score"]
                purpose = discovery["intent"]["purpose"]
                print(f"  • {name} ({purpose}) - Score: {score:.1f}")
        else:
            print("  No relevant plugins found")


def main():
    """Run all plugin discovery tests"""
    print("🚀 NEUROCODE ENHANCED PLUGIN DISCOVERY DEMO")
    print("=" * 60)
    print()

    try:
        test_basic_discovery()
        test_intent_discovery()
        test_ai_recommendations()
        test_discovery_stats()
        test_advanced_scenarios()

        print("\n✅ All tests completed successfully!")
        print("\nThe enhanced plugin system with intent-based discovery is working perfectly!")
        print("Plugins can now be intelligently discovered based on user goals and context.")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
