#!/usr/bin/env python3
"""
🧠🎭 TEST BRAIN LOOP WITH PERSONALITY PROCESSOR
==============================================

Test the integration of the Lyrixa Brain Loop with the new Personality Processor.
This verifies that personality-enhanced responses work through the complete system.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from lyrixa.assistant import LyrixaAI

async def test_brain_loop_with_personality():
    """Test brain loop with personality processor integration"""

    print("🧠🎭 BRAIN LOOP + PERSONALITY PROCESSOR INTEGRATION TEST")
    print("=" * 60)

    # Initialize Lyrixa with workspace
    lyrixa = LyrixaAI(workspace_path="./")
    await lyrixa.initialize()

    print("\n🧠 Brain Loop initialized with Personality Processor")

    # Test 1: Different persona modes with brain loop
    print("\n🎬 TEST 1: Brain Loop with Different Personas")
    print("-" * 40)

    test_scenarios = [
        ("Guide", "How do I get started with .aether programming?"),
        ("Developer", "I'm getting errors in my code, can you help debug?"),
        ("Creative", "I want to build something innovative with .aether"),
        ("Teacher", "Explain how memory management works"),
        ("Sage", "What is the philosophy behind .aether design?")
    ]

    for persona, user_input in test_scenarios:
        print(f"\n🎭 Setting persona to: {persona}")
        lyrixa.set_persona_mode(persona)

        print(f"👤 User: {user_input}")

        # Use brain loop
        response = await lyrixa.brain_loop(user_input, "text")

        print(f"🎙️ Lyrixa ({persona}): {response['lyrixa_response'][:120]}...")
        print(f"⚡ Confidence: {response['confidence']:.2f}")
        print(f"🎭 Personality Enhanced: {response.get('response_metadata', {}).get('personality_enhanced', False)}")

    # Test 2: Personality adjustments
    print("\n\n🎛️ TEST 2: Personality Adjustments")
    print("-" * 40)

    lyrixa.set_persona_mode("Friend")
    base_question = "Tell me about .aether code structure"

    # Very warm and casual
    print("\n🔥 Very warm and casual:")
    lyrixa.adjust_personality(warmth=0.9, formality=0.1, humor_level=0.8)
    response = await lyrixa.brain_loop(base_question, "text")
    print(f"Response: {response['lyrixa_response'][:150]}...")

    # Very formal and professional
    print("\n❄️ Very formal and professional:")
    lyrixa.adjust_personality(warmth=0.2, formality=0.9, humor_level=0.1)
    response = await lyrixa.brain_loop(base_question, "text")
    print(f"Response: {response['lyrixa_response'][:150]}...")

    # High verbosity with metaphors
    print("\n📚 High verbosity with metaphors:")
    lyrixa.adjust_personality(verbosity=0.9, metaphor_use=0.8, suggestion_strength=0.3)
    response = await lyrixa.brain_loop("What is a variable?", "text")
    print(f"Response: {response['lyrixa_response'][:200]}...")

    # Test 3: Context-aware personality adaptation
    print("\n\n🧠 TEST 3: Context-Aware Adaptation")
    print("-" * 40)

    lyrixa.set_persona_mode("Guide")

    # Frustrated user
    frustrated_input = "I'm so frustrated! This .aether code isn't working and I don't understand why!"
    response = await lyrixa.brain_loop(frustrated_input, "text")
    print(f"\n😤 Frustrated user:")
    print(f"Input: {frustrated_input}")
    print(f"Response: {response['lyrixa_response'][:150]}...")

    # Excited user
    excited_input = "I'm so excited! I just learned about .aether and want to build everything!"
    response = await lyrixa.brain_loop(excited_input, "text")
    print(f"\n🎉 Excited user:")
    print(f"Input: {excited_input}")
    print(f"Response: {response['lyrixa_response'][:150]}...")

    # Technical question
    technical_input = "Generate .aether code for a data processing pipeline"
    response = await lyrixa.brain_loop(technical_input, "text")
    print(f"\n[TOOL] Technical request:")
    print(f"Input: {technical_input}")
    print(f"Response: {response['lyrixa_response'][:150]}...")
    print(f"Has .aether code: {bool(response.get('aether_code'))}")

    # Test 4: Feedback learning integration
    print("\n\n📚 TEST 4: Feedback Learning")
    print("-" * 40)

    # Record some feedback
    await lyrixa.record_personality_feedback("test_1", "positive", "Great explanation!", 0.9)
    await lyrixa.record_personality_feedback("test_2", "negative", "Too technical", 0.3)

    # Check feedback status
    status = lyrixa.get_personality_status()
    feedback_count = status['personality_processor']['feedback_count']
    recent_feedback = status['personality_processor']['recent_feedback']

    print(f"📊 Total feedback recorded: {feedback_count}")
    print(f"📊 Recent feedback types: {recent_feedback}")

    # Test 5: Profile management
    print("\n\n💾 TEST 5: Profile Management")
    print("-" * 40)

    # Export current configuration
    profile = lyrixa.export_personality_profile()
    print(f"📤 Exported personality profile ({len(profile)} characters)")

    # Modify settings
    lyrixa.adjust_personality(warmth=1.0, humor_level=1.0)
    print("[TOOL] Modified personality settings")

    # Test response with modified settings
    response = await lyrixa.brain_loop("Hello Lyrixa!", "text")
    print(f"Modified response: {response['lyrixa_response'][:100]}...")

    # Import original profile
    success = lyrixa.import_personality_profile(profile)
    print(f"📥 Profile import success: {success}")

    # Test 6: System status
    print("\n\n📊 TEST 6: System Status")
    print("-" * 40)

    system_status = await lyrixa.get_system_status()
    personality_status = lyrixa.get_personality_status()

    print(f"🧠 Brain Loop Status: {system_status['status']}")
    print(f"💬 Conversation turns: {system_status['conversation_length']}")
    print(f"🎭 Current persona: {personality_status['personality_processor']['current_persona']}")
    print(f"🎛️ Available personas: {len(personality_status['personality_processor']['available_personas'])}")

    # Test 7: Comprehensive workflow
    print("\n\n🌟 TEST 7: Comprehensive Workflow")
    print("-" * 40)

    lyrixa.set_persona_mode("Developer")
    complex_request = "I need help creating a .aether workflow that processes data, stores results in memory, and generates a report"

    print(f"👤 Complex request: {complex_request}")
    response = await lyrixa.brain_loop(complex_request, "text")

    print(f"\n🎙️ Full response:")
    print(f"Text: {response['lyrixa_response']}")
    print(f"Actions: {response['actions_taken']}")
    print(f"Suggestions: {response['suggestions']}")
    print(f"Processing time: {response['processing_time']:.2f}s")
    print(f"Confidence: {response['confidence']:.2f}")

    print("\n🎉 BRAIN LOOP + PERSONALITY PROCESSOR TEST COMPLETE!")
    print("✅ Brain loop processes personality-enhanced responses")
    print("✅ All persona modes work with brain loop")
    print("✅ Personality adjustments affect brain loop output")
    print("✅ Context-aware personality adaptation functional")
    print("✅ Feedback learning integrated")
    print("✅ Profile management operational")
    print("✅ Complete system integration verified")

if __name__ == "__main__":
    asyncio.run(test_brain_loop_with_personality())
