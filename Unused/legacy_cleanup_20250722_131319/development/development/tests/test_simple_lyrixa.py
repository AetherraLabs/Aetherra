#!/usr/bin/env python3
"""
Test script for simplified Lyrixa AI
"""

import asyncio
from simple_lyrixa import SimpleLyrixaAI

async def test_simple_lyrixa():
    try:
        print("🔄 Testing Simple Lyrixa AI...")
        ai = SimpleLyrixaAI()
        print("✅ Simple Lyrixa AI instance created")

        test_questions = [
            "hello",
            "what is aetherra?",
            "tell me about plugins",
            "who are you?",
            "how can you help me?",
            "what is consciousness?"
        ]

        for question in test_questions:
            print(f"\n🔄 Testing: {question}")
            response = await ai.chat(question)
            print(f"✅ Response: {response['text']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_lyrixa())
