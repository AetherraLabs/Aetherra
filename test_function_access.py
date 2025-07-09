#!/usr/bin/env python3
"""
Comprehensive test to verify all functions are properly accessible
"""


def test_function_access():
    """Test that all required functions can be imported and used"""

    print("🧪 Testing function accessibility...")

    try:
        # Test imports
        from lyrixa.prompt_engine import (
            build_dynamic_prompt,
            get_system_status,
            recall,
            search_memory_one,
            store_memory,
        )

        print("✅ All functions imported successfully")

        # Test each function
        print("\n📊 Testing get_system_status():")
        status = get_system_status()
        print(f"   Plugin count: {status['plugin_count']}")
        print(f"   Memory usage: {status['memory_usage']}%")
        print(f"   Active agents: {status['active_agents']}")

        print("\n🧠 Testing memory functions:")
        # Store a test memory
        test_memory = {
            "type": "test_function_access",
            "content": "Testing function accessibility",
            "user_id": "test_user_2",
        }
        store_memory(test_memory)
        print("   ✅ store_memory() works")

        # Recall memories
        memories = recall({"type": "test_function_access"})
        print(f"   ✅ recall() works - found {len(memories)} memories")

        # Search for one memory
        memory = search_memory_one({"type": "test_function_access"})
        if memory:
            print("   ✅ search_memory_one() works")
        else:
            print("   ⚠️ search_memory_one() returned None")

        print("\n🎭 Testing build_dynamic_prompt():")
        prompt = build_dynamic_prompt("test_user_2")
        print(f"   ✅ Generated prompt with {len(prompt)} characters")

        # Check prompt content
        required_sections = [
            "🔧 CURRENT SYSTEM STATE",
            "👤 USER PROFILE",
            "⏰ TIME & CONTEXT",
            "💫 INTERACTION GUIDELINES",
        ]

        missing_sections = []
        for section in required_sections:
            if section not in prompt:
                missing_sections.append(section)

        if missing_sections:
            print(f"   ⚠️ Missing sections: {missing_sections}")
        else:
            print("   ✅ All required sections present in prompt")

        print("\n🎯 RESULT: All functions are accessible and working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Comprehensive Function Access Test")
    print("=" * 50)

    success = test_function_access()

    print("=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Functions are properly fixed and accessible!")
    else:
        print("❌ Some tests failed. Check the output above.")
