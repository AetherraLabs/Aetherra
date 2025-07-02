#!/usr/bin/env python3
"""
Test the enhanced chat router with multi-agent and advanced features
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from chat_router import NeuroCodeChatRouter

    print("🧬 Testing Enhanced NeuroCode Chat Router")
    print("=" * 50)

    # Initialize router
    router = NeuroCodeChatRouter(demo_mode=True, debug_mode=True)
    print("✅ Router initialized successfully")

    # Test basic conversation
    print("\n1. Testing basic conversation:")
    response = router.process_message("Hello, how are you?")
    print(f"Response: {response.get('text', 'No response')[:100]}...")

    # Test memory functionality
    print("\n2. Testing memory functionality:")
    response = router.process_message("Remember that I like Python programming")
    print(f"Memory response: {response.get('text', 'No response')[:100]}...")

    # Test workflow generation
    print("\n3. Testing workflow generation:")
    response = router.process_message("Generate a workflow for data analysis")
    print(f"Workflow response: {response.get('text', 'No response')[:100]}...")

    # Test multi-agent coordination
    print("\n4. Testing multi-agent coordination:")
    response = router.process_message("Coordinate agents to debug a performance issue")
    print(f"Multi-agent response: {response.get('text', 'No response')[:100]}...")

    # Test personality system
    print("\n5. Testing personality system:")
    router.set_personality("mentor")
    response = router.process_message("Teach me about neural networks")
    print(f"Mentor response: {response.get('text', 'No response')[:100]}...")

    print("\n✅ All tests completed successfully!")
    print(f"Chat history length: {len(router.chat_history)}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
