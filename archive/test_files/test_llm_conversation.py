#!/usr/bin/env python3
"""
Test the new LLM-powered conversation system for Lyrixa
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lyrixa.conversation_manager import LyrixaConversationManager
    from lyrixa.intelligence_integration import LyrixaIntelligenceStack

    async def test_llm_conversation():
        """Test the LLM-powered conversation manager"""
        print("🧪 Testing LLM-Powered Lyrixa Conversation System")
        print("=" * 60)

        # Initialize conversation manager
        print("🔄 Initializing conversation manager...")
        conversation_manager = LyrixaConversationManager(
            workspace_path=str(project_root)
        )

        # Check if LLM is available
        if conversation_manager.llm_enabled:
            print(f"✅ LLM enabled with model: {conversation_manager.current_model}")
        else:
            print("⚠️ LLM not available, using fallback responses")

        # Test questions
        test_questions = [
            "Hello! What is Aetherra?",
            "How can you help me with development?",
            "What plugins are currently active?",
            "Tell me about the memory system",
            "What's your current status?",
        ]

        print("\n💬 Testing conversation responses:")
        print("-" * 40)

        for i, question in enumerate(test_questions, 1):
            print(f"\n[{i}] 👤 User: {question}")
            try:
                response = await conversation_manager.generate_response(question)
                print(
                    f"    🎙️ Lyrixa: {response[:200]}{'...' if len(response) > 200 else ''}"
                )
            except Exception as e:
                print(f"    ❌ Error: {e}")

        # Test intelligence stack integration
        print("\n🧠 Testing intelligence stack integration:")
        print("-" * 40)

        intelligence_stack = LyrixaIntelligenceStack(workspace_path=str(project_root))

        if (
            hasattr(intelligence_stack, "conversation_manager")
            and intelligence_stack.conversation_manager
        ):
            print("✅ Intelligence stack has conversation manager")
        else:
            print("⚠️ Intelligence stack using fallback system")

        # Test through intelligence stack
        test_question = "What is Aetherra and how can you help me?"
        print(f"\n👤 User (via intelligence stack): {test_question}")
        try:
            response = intelligence_stack.generate_response(test_question)
            print(f"🎙️ Lyrixa: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Show conversation summary
        if conversation_manager.llm_enabled:
            summary = conversation_manager.get_conversation_summary()
            print(f"\n📊 Conversation Summary:")
            print(f"    • Session: {summary['session_id']}")
            print(f"    • Messages: {summary['conversation_count']}")
            print(f"    • Model: {summary['current_model']}")
            print(f"    • History Length: {summary['history_length']}")

        print("\n✅ LLM conversation test completed!")

    def test_sync_integration():
        """Test synchronous integration"""
        print("\n🔄 Testing synchronous integration...")

        # Test through intelligence stack (sync)
        intelligence_stack = LyrixaIntelligenceStack(workspace_path=str(project_root))

        test_question = "Hello, can you explain what you are?"
        print(f"👤 User: {test_question}")

        try:
            response = intelligence_stack.generate_response(test_question)
            print(f"🎙️ Lyrixa: {response}")
            print("✅ Synchronous integration working!")
        except Exception as e:
            print(f"❌ Synchronous integration error: {e}")

    async def main():
        """Main test function"""
        await test_llm_conversation()
        test_sync_integration()

    if __name__ == "__main__":
        asyncio.run(main())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all dependencies are installed.")
except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback

    traceback.print_exc()
