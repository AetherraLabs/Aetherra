#!/usr/bin/env python3
"""Test script for ChatHistoryManager."""

import os
import tempfile

from lyrixa.gui.chat_history_manager import ChatHistoryManager


def test_chat_history_manager():
    """Test ChatHistoryManager functionality."""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Test basic initialization
        print("Testing ChatHistoryManager initialization...")
        chm = ChatHistoryManager(tmp_path)
        print(
            f"✅ ChatHistoryManager created successfully with session: {chm.current_session_id}"
        )

        # Test adding messages
        print("\nTesting message addition...")
        msg_hash = chm.add_message("user", "Hello, this is a test message!")
        print(f"✅ Message added with hash: {msg_hash}")

        # Test getting recent messages
        print("\nTesting message retrieval...")
        messages = chm.get_recent_messages(10)
        print(f"✅ Retrieved {len(messages)} messages")
        if messages:
            print(f"   Latest message: {messages[-1]['content']}")

        # Test conversation summary
        print("\nTesting conversation summary...")
        summary = chm.get_conversation_summary()
        print(f"✅ Summary generated: {summary['total_messages']} messages")

        # Test search functionality
        print("\nTesting search functionality...")
        search_results = chm.search_history("test")
        print(f"✅ Search returned {len(search_results)} results")

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    test_chat_history_manager()
