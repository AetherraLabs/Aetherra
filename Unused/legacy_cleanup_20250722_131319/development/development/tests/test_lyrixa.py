#!/usr/bin/env python3
"""
Test script to debug Lyrixa AI issues
"""

import asyncio
import sys
import os

# Add the Aetherra directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))

async def test_lyrixa():
    try:
        print("🔄 Testing Lyrixa AI import...")
        from Aetherra.lyrixa.assistant import LyrixaAI
        print("✅ Import successful")

        print("🔄 Creating Lyrixa AI instance...")
        ai = LyrixaAI()
        print("✅ LyrixaAI instance created")

        print("🔄 Testing chat function...")
        response = await ai.chat("hello")
        print(f"✅ Chat response: {response}")

        print("🔄 Testing with a question...")
        response = await ai.chat("what is aetherra?")
        print(f"✅ Question response: {response}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lyrixa())
