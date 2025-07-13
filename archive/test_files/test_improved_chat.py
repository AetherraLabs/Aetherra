#!/usr/bin/env python3
"""
Test the improved chat response generation with debugging.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Aetherra.runtime.aether_runtime import AetherRuntime
from lyrixa import LyrixaAI
from lyrixa.intelligence_integration import LyrixaIntelligenceStack


async def test_full_integration():
    """Test full integration with actual Lyrixa instance."""
    print("🧪 Testing full integration...")

    try:
        # Initialize full system
        workspace_path = str(project_root)
        print(f"📁 Workspace: {workspace_path}")

        # Create Lyrixa instance
        lyrixa = LyrixaAI(workspace_path=workspace_path)
        print("🔄 Initializing Lyrixa...")
        await lyrixa.initialize()
        print("✅ Lyrixa initialized")

        # Create AetherRuntime
        aether_runtime = AetherRuntime()
        aether_runtime.register_context(
            memory=lyrixa.memory,
            plugins=lyrixa.plugins,
            agents=lyrixa.agents,
        )
        await aether_runtime.initialize()
        print("✅ AetherRuntime initialized")

        # Create intelligence stack
        intelligence_stack = LyrixaIntelligenceStack(
            workspace_path=workspace_path, aether_runtime=aether_runtime
        )
        print("✅ Intelligence stack created")

        # Test various messages
        test_messages = [
            "Hello, how are you?",
            "What can you help me with?",
            "Tell me about my project",
            "How do I get started?",
            "What's the status of my work?",
        ]

        for message in test_messages:
            print(f"\n💬 Testing: {message}")
            response = await intelligence_stack.generate_response_async(message)
            print(f"🎙️ Response: {response}")
            print("-" * 50)

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🔧 Testing Improved Chat Response Generation")
    print("=" * 60)

    asyncio.run(test_full_integration())
