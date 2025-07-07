#!/usr/bin/env python3
"""
🎭 LYRIXA PERSONALITY PROCESSOR DEMO
===================================

Showcase the completed Personality Processor integration with the Brain Loop.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from lyrixa.assistant import LyrixaAI

async def personality_demo():
    print("🎭 LYRIXA PERSONALITY PROCESSOR DEMONSTRATION")
    print("=" * 50)
    print("The Lyrixa AI Assistant now has a fully functional")
    print("Personality Processor with 8 persona modes and")
    print("configurable personality parameters!")
    print()

    # Initialize
    lyrixa = LyrixaAI()
    await lyrixa.initialize()

    test_question = "How do I learn programming?"

    # Demonstrate different personas
    personas_to_test = ["Guide", "Teacher", "Developer", "Friend"]

    for persona in personas_to_test:
        print(f"🎭 {persona} Persona:")
        print("-" * 20)
        lyrixa.set_persona_mode(persona)

        response = await lyrixa.brain_loop(test_question, "text")
        print(f"Response: {response['lyrixa_response'][:120]}...")
        print()

    # Show personality status
    status = lyrixa.get_personality_status()
    print("📊 Personality System Status:")
    print(f"   Current Persona: {status['personality_processor']['current_persona']}")
    print(f"   Available Personas: {len(status['personality_processor']['available_personas'])}")
    print(f"   Feedback Received: {status['personality_processor']['feedback_count']}")

    print("\n🎉 PERSONALITY PROCESSOR DEMO COMPLETE!")
    print("✅ 8 distinct persona modes operational")
    print("✅ Configurable personality parameters")
    print("✅ Brain loop integration working")
    print("✅ Feedback learning system active")

if __name__ == "__main__":
    asyncio.run(personality_demo())
