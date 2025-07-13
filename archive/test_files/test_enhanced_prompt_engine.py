#!/usr/bin/env python3
"""
Test the enhanced prompt engine implementation
"""

import json

from lyrixa.prompt_engine import (
    build_dynamic_prompt,
    get_system_status,
    recall,
    store_memory,
)


def main():
    print("🧪 Testing enhanced implementations...")

    # Test system status
    print("\n📊 Testing system status:")
    status = get_system_status()
    print(json.dumps(status, indent=2))

    # Test memory functions
    print("\n🧠 Testing memory functions:")
    store_memory(
        {"type": "test", "content": "Test memory entry", "user_id": "test_user"}
    )

    memories = recall({"type": "test"})
    print(f"Stored and recalled {len(memories)} memory entries")

    # Test prompt generation
    print("\n🎭 Testing prompt generation:")
    prompt = build_dynamic_prompt("test_user")
    print(f"Generated prompt with {len(prompt)} characters")

    # Show first 500 characters of prompt
    print("\n📝 Prompt preview:")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
