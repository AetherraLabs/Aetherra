#!/usr/bin/env python3
"""
Chat Responsiveness Test
======================

Test that Lyrixa chat is working and responsive after autonomous agent integration.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_chat_responsiveness():
    """Test that chat doesn't hang with autonomous agents"""

    try:
        print("🧪 Testing Lyrixa Chat Responsiveness...")

        # Import minimal components
        from Aetherra.core.memory_manager import MemoryManager
        from Aetherra.core.multi_llm_manager import MultiLLMManager
        from Aetherra.core.prompt_engine import PromptEngine
        from Aetherra.lyrixa.agents.core_agent import LyrixaAI

        # Create minimal components
        memory = MemoryManager()
        llm_manager = MultiLLMManager()
        prompt_engine = PromptEngine()

        # Create Lyrixa agent
        lyrixa = LyrixaAI(
            runtime=None,
            memory=memory,
            prompt_engine=prompt_engine,
            llm_manager=llm_manager,
        )

        print("✅ Lyrixa agent created")

        # Initialize agent
        await lyrixa.initialize()
        print("✅ Lyrixa agent initialized")

        # Test chat responses
        test_messages = [
            "hello",
            "how are you?",
            "what can you do?",
            "scan project",  # Should route to autonomous agent
            "help me",
        ]

        print("\n🧪 Testing Chat Messages:")
        print("=" * 40)

        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Testing: '{message}'")

            try:
                # Test with timeout to detect hanging
                response = await asyncio.wait_for(
                    lyrixa.process_input(message),
                    timeout=10.0,  # 10 second timeout
                )

                print(f"✅ Response received ({len(response.content)} chars)")
                print(f"   Agent: {response.agent_name}")
                print(f"   Confidence: {response.confidence}")

                # Show first 100 chars of response
                preview = (
                    response.content[:100] + "..."
                    if len(response.content) > 100
                    else response.content
                )
                print(f"   Preview: {preview}")

            except asyncio.TimeoutError:
                print(f"❌ TIMEOUT - Chat hanging on: '{message}'")
                return False
            except Exception as e:
                print(f"❌ ERROR: {e}")
                return False

        print("\n🎉 All chat tests passed - Lyrixa is responsive!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run chat responsiveness test"""
    print("🌟 LYRIXA CHAT RESPONSIVENESS TEST")
    print("=" * 50)

    # Run async test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    success = loop.run_until_complete(test_chat_responsiveness())

    print("\n📊 TEST RESULT")
    print("=" * 50)

    if success:
        print("🎉 SUCCESS: Lyrixa chat is working and responsive!")
        print("✅ No hanging or blocking detected")
        print("✅ Autonomous agents integrated without breaking chat")
        print("\n💡 The chat issue should now be fixed in the app!")
    else:
        print("❌ FAILED: Chat still has responsiveness issues")
        print("   Check error messages above for details")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
