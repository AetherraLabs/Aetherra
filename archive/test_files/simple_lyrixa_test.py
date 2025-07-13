#!/usr/bin/env python3
"""
Simple test for Lyrixa conversation engine
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def simple_test():
    print("🧪 Simple Lyrixa Test")

    try:
        # Try to import the conversation engine directly
        from lyrixa.core.conversation import LyrixaConversationalEngine

        print("✅ Successfully imported LyrixaConversationalEngine")

        # Initialize conversation engine
        conv_engine = LyrixaConversationalEngine()
        print("✅ Conversation engine initialized")

        # Test basic conversation
        response = await conv_engine.process_conversation_turn("Hello, Lyrixa!")
        print(f"🎙️ Response: {response.get('text', 'No response')}")

        if response.get("text"):
            print("✅ Conversation engine is working!")
        else:
            print("❌ No response generated")

    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(simple_test())
