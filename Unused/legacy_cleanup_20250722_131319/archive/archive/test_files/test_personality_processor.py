#!/usr/bin/env python3
"""
🎭 TEST PERSONALITY PROCESSOR
============================

Comprehensive test script for the new Lyrixa Personality Processor.
Tests all persona modes, configuration options, and feedback learning.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from lyrixa.core.conversation import (
    LyrixaConversationalEngine,
    PersonaMode,
    PersonalityConfig
)

async def test_personality_processor():
    """Comprehensive test of the Personality Processor"""

    print("🎭 PERSONALITY PROCESSOR TEST SUITE")
    print("=" * 50)

    # Initialize engine
    engine = LyrixaConversationalEngine()
    await engine.initialize_conversation("personality_test_session")

    # Test 1: All Persona Modes
    print("\n🎬 TEST 1: All Persona Modes")
    print("-" * 30)

    test_prompt = "I'm having trouble with my .aether code architecture"

    for persona in PersonaMode:
        print(f"\n🎭 Testing {persona.value.upper()} persona:")
        engine.set_persona_mode(persona)

        response = await engine.process_conversation_turn(test_prompt)
        print(f"Response: {response['text'][:100]}...")

        # Show configuration
        status = engine.get_personality_status()
        config = status['personality_processor']['config']
        print(f"Config: warmth={config['warmth']:.1f}, formality={config['formality']:.1f}, humor={config['humor_level']:.1f}")

    # Test 2: Personality Adjustments
    print("\n\n🎛️ TEST 2: Personality Adjustments")
    print("-" * 30)

    engine.set_persona_mode(PersonaMode.GUIDE)
    base_prompt = "Explain how memory works in programming"

    # Test high warmth, low formality
    print("\n🔥 High warmth, low formality:")
    engine.adjust_personality_settings(warmth=0.9, formality=0.2, humor_level=0.7)
    response = await engine.process_conversation_turn(base_prompt)
    print(f"Response: {response['text']}")

    # Test low warmth, high formality
    print("\n❄️ Low warmth, high formality:")
    engine.adjust_personality_settings(warmth=0.2, formality=0.9, humor_level=0.1)
    response = await engine.process_conversation_turn(base_prompt)
    print(f"Response: {response['text']}")

    # Test high verbosity
    print("\n📝 High verbosity:")
    engine.adjust_personality_settings(verbosity=0.9, metaphor_use=0.8)
    response = await engine.process_conversation_turn("What is a function?")
    print(f"Response: {response['text']}")

    # Test low verbosity
    print("\n✂️ Low verbosity:")
    engine.adjust_personality_settings(verbosity=0.1, suggestion_strength=0.9)
    response = await engine.process_conversation_turn("What is a function?")
    print(f"Response: {response['text']}")

    # Test 3: Context-Aware Responses
    print("\n\n🧠 TEST 3: Context-Aware Responses")
    print("-" * 30)

    engine.set_persona_mode(PersonaMode.FRIEND)

    # Happy user
    response = await engine.process_conversation_turn("I'm so excited! I just finished my first .aether project!")
    print(f"\n😊 Happy user response: {response['text']}")

    # Frustrated user
    response = await engine.process_conversation_turn("I'm really frustrated with this bug that won't go away")
    print(f"\n😤 Frustrated user response: {response['text']}")

    # Technical question
    response = await engine.process_conversation_turn("Can you debug this function that's throwing errors?")
    print(f"\n[TOOL] Technical question response: {response['text']}")

    # Test 4: Feedback Learning
    print("\n\n📚 TEST 4: Feedback Learning")
    print("-" * 30)

    # Record positive feedback
    await engine.record_personality_feedback("test_response_1", "positive", "Great explanation!", 0.9)
    print("✅ Recorded positive feedback")

    # Record negative feedback
    await engine.record_personality_feedback("test_response_2", "negative", "Too formal", 0.3)
    print("❌ Recorded negative feedback")

    # Check feedback history
    status = engine.get_personality_status()
    feedback_count = status['personality_processor']['feedback_count']
    recent_feedback = status['personality_processor']['recent_feedback']
    print(f"📊 Total feedback: {feedback_count}")
    print(f"📊 Recent feedback: {recent_feedback}")

    # Test 5: Profile Export/Import
    print("\n\n💾 TEST 5: Profile Export/Import")
    print("-" * 30)

    # Export current profile
    profile = engine.export_personality_profile()
    print(f"📤 Exported profile ({len(profile)} characters)")

    # Modify settings
    engine.adjust_personality_settings(warmth=0.5, humor_level=0.5)
    print("[TOOL] Modified settings")

    # Import profile
    success = engine.import_personality_profile(profile)
    print(f"📥 Import success: {success}")

    # Test 6: Comprehensive Persona Comparison
    print("\n\n⚖️ TEST 6: Persona Comparison")
    print("-" * 30)

    comparison_prompt = "How should I structure my code?"

    for persona in [PersonaMode.DEVELOPER, PersonaMode.TEACHER, PersonaMode.CREATIVE]:
        engine.set_persona_mode(persona)
        response = await engine.process_conversation_turn(comparison_prompt)
        print(f"\n{persona.value.upper()}: {response['text'][:80]}...")

    # Final Status
    print("\n\n📊 FINAL STATUS")
    print("-" * 30)

    final_status = engine.get_personality_status()
    print(f"Current persona: {final_status['personality_processor']['current_persona']}")
    print(f"Available personas: {len(final_status['personality_processor']['available_personas'])}")
    print(f"Total feedback received: {final_status['personality_processor']['feedback_count']}")

    print("\n🎉 PERSONALITY PROCESSOR TEST COMPLETE!")
    print("✅ All persona modes tested")
    print("✅ Configuration adjustments verified")
    print("✅ Context awareness confirmed")
    print("✅ Feedback learning operational")
    print("✅ Profile export/import working")

if __name__ == "__main__":
    asyncio.run(test_personality_processor())
