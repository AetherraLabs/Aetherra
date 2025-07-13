#!/usr/bin/env python3
"""
🔄🧠 LYRIXA REFLEXIVE LOOP DEMO
==============================

Interactive demo showcasing Lyrixa's self-awareness capabilities:
- Project understanding that evolves over time
- User pattern recognition
- Contextual insights and reflections
- Self-knowledge updates
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.assistant import LyrixaAI


async def demo_self_awareness():
    """Interactive demo of Lyrixa's self-awareness system"""
    print("🔄🧠 LYRIXA SELF-AWARENESS DEMO")
    print("=" * 40)
    print("This demo shows how Lyrixa develops understanding of your project")
    print("and recognizes patterns in your work over time.\n")

    # Initialize Lyrixa
    lyrixa = LyrixaAI(workspace_path=str(project_root))
    await lyrixa.initialize()

    print(f"✅ Lyrixa initialized (Session: {lyrixa.session_id})")
    print("🧠 Self-awareness system is active\n")

    # Demo scenario: Building an AI project
    demo_interactions = [
        {
            "input": "I'm starting a new AI project called Aetherra that will create intelligent workflows",
            "description": "Initial project introduction"
        },
        {
            "input": "Can you help me design a natural language processing system using Python and machine learning?",
            "description": "Technical requirements discussion"
        },
        {
            "input": "I need to implement a plugin architecture for extensibility",
            "description": "Architecture planning"
        },
        {
            "input": "What's the best way to handle errors in asynchronous Python code?",
            "description": "Implementation details"
        },
        {
            "input": "I keep running into the same debugging issues with my async functions",
            "description": "Pattern that Lyrixa should detect"
        }
    ]

    print("🎬 Starting demo scenario...\n")

    for i, interaction in enumerate(demo_interactions, 1):
        print(f"👤 User ({interaction['description']}):")
        print(f"   \"{interaction['input']}\"\n")

        # Process the interaction
        response = await lyrixa.brain_loop(interaction['input'], input_type="text")

        print(f"🤖 Lyrixa (Confidence: {response['confidence']:.2f}):")
        print(f"   {response['lyrixa_response']}\n")

        # Show what Lyrixa learned
        if i % 2 == 0:  # Show learning progress every 2 interactions
            print("🧠 What Lyrixa learned so far:")

            # Project understanding
            if lyrixa.reflexive_loop.project_understanding:
                pu = lyrixa.reflexive_loop.project_understanding
                print(f"   📋 Project: {pu.project_name} ({pu.project_type})")
                print(f"   🏗️  Phase: {pu.current_phase}")
                print(f"   🛠️  Technologies: {', '.join(list(pu.technologies)[:4])}")
                print(f"   🎯 Goals: {', '.join(pu.main_goals[:2])}")
                print(f"   📊 Understanding confidence: {pu.confidence:.2f}")

            # User patterns
            if lyrixa.reflexive_loop.user_patterns:
                print(f"   🔍 Detected {len(lyrixa.reflexive_loop.user_patterns)} user patterns:")
                for pattern in lyrixa.reflexive_loop.user_patterns[-2:]:
                    print(f"      - {pattern.pattern_type}: {pattern.description}")

            print()

        await asyncio.sleep(0.5)  # Small delay for readability

    print("🎯 Demo Complete! Now let's see Lyrixa's full self-awareness...\n")

    # Get comprehensive insights
    insights = await lyrixa.get_self_awareness_insights()

    print("🔍 LYRIXA'S CURRENT SELF-AWARENESS:")
    print("-" * 40)

    # Project understanding
    if insights.get('project_understanding'):
        pu = insights['project_understanding']
        print(f"📋 PROJECT UNDERSTANDING:")
        print(f"   Name: {pu.get('project_name', 'Unknown')}")
        print(f"   Type: {pu.get('project_type', 'Unknown')}")
        print(f"   Phase: {pu.get('current_phase', 'Unknown')}")
        print(f"   Technologies: {', '.join(list(pu.get('technologies', [])))}")
        print(f"   Goals: {', '.join(pu.get('main_goals', []))}")
        print(f"   Key Files: {', '.join(pu.get('key_files', []))}")
        print(f"   Confidence: {pu.get('confidence', 0):.2f}")
        print()

    # User patterns
    if insights.get('user_patterns'):
        print(f"🔍 USER PATTERNS DETECTED ({len(insights['user_patterns'])}):")
        for pattern in insights['user_patterns']:
            print(f"   • {pattern.get('pattern_type', 'Unknown')}: {pattern.get('description', 'No description')}")
            print(f"     Evidence: {', '.join(pattern.get('evidence', [])[:2])}")
            print(f"     Frequency: {pattern.get('frequency', 0)}")
        print()

    # Recent insights
    if insights.get('recent_insights'):
        print(f"💡 RECENT INSIGHTS ({len(insights['recent_insights'])}):")
        for insight in insights['recent_insights']:
            print(f"   • {insight.get('insight_type', 'General')}: {insight.get('message', 'No message')}")
        print()

    # Generate project insights
    print("🎯 LYRIXA'S PROJECT INSIGHTS:")
    project_insights = await lyrixa.generate_project_insights()
    for insight in project_insights:
        print(f"   {insight}")
    print()

    # Test self-knowledge update
    print("📝 TESTING SELF-KNOWLEDGE UPDATE:")
    knowledge_update = "The user prefers asynchronous programming patterns and is building an enterprise-grade AI system with plugin support"
    update_result = await lyrixa.update_lyrixa_self_knowledge(knowledge_update)
    print(f"   Update: {knowledge_update}")
    print(f"   Success: {update_result.get('success', False)}")
    print()

    # Test contextual awareness
    print("🤔 TESTING CONTEXTUAL AWARENESS:")
    awareness_response = await lyrixa.brain_loop(
        "What do you understand about my current project and working style?",
        input_type="text"
    )
    print(f"   Lyrixa's self-reflection:")
    print(f"   {awareness_response['lyrixa_response']}")
    print()

    print("🎉 DEMO COMPLETE!")
    print("Lyrixa now has self-awareness and can:")
    print("  • Remember and update project understanding")
    print("  • Detect patterns in user behavior")
    print("  • Generate contextual insights")
    print("  • Reflect on conversations and progress")
    print("  • Provide self-aware responses")


if __name__ == "__main__":
    print("🚀 Starting Lyrixa Self-Awareness Demo...\n")
    asyncio.run(demo_self_awareness())
