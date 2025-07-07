#!/usr/bin/env python3
"""
🧠🎭 SIMPLE PERSONALITY TEST
===========================

Quick test to verify personality processor integration works.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from lyrixa.assistant import LyrixaAI

async def simple_test():
    print("🧠🎭 Simple Brain Loop + Personality Test")
    print("=" * 40)

    # Initialize Lyrixa
    lyrixa = LyrixaAI(workspace_path="./")
    await lyrixa.initialize()

    # Test 1: Default persona
    print("\n🎭 Testing default persona:")
    response = await lyrixa.brain_loop("Hello Lyrixa, how are you?", "text")
    print(f"Response: {response['lyrixa_response'][:100]}...")

    # Test 2: Switch to Developer persona
    print("\n🎭 Testing Developer persona:")
    lyrixa.set_persona_mode("Developer")
    response = await lyrixa.brain_loop("I have a coding problem", "text")
    print(f"Response: {response['lyrixa_response'][:100]}...")

    # Test 3: Adjust personality
    print("\n🎛️ Testing personality adjustment:")
    lyrixa.adjust_personality(warmth=0.9, humor_level=0.8)
    response = await lyrixa.brain_loop("Tell me a joke", "text")
    print(f"Response: {response['lyrixa_response'][:100]}...")

    # Test 4: Check status
    print("\n📊 Testing status:")
    status = lyrixa.get_personality_status()
    print(f"Current persona: {status['personality_processor']['current_persona']}")

    print("\n✅ Integration test complete!")

if __name__ == "__main__":
    asyncio.run(simple_test())
