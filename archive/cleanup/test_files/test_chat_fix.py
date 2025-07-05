#!/usr/bin/env python3
"""
Quick test to verify the chat functionality fix
"""

import os


def test_chat_functionality():
    """Test if the chat functionality has been properly implemented"""
    print("🔧 TESTING CHAT FUNCTIONALITY FIX")
    print("=" * 50)

    if not os.path.exists("script.js"):
        print("❌ script.js not found")
        return False

    with open("script.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Check for the required elements
    checks = {
        "Modal creation": "ai-demo-modal" in content,
        "Suggestion buttons": "ai-suggestion" in content,
        "Event listeners": "addEventListener" in content
        and "querySelectorAll('.ai-suggestion')" in content,
        "Chat interaction": "chatDemo.appendChild" in content,
        "Button disable": "disabled = true" in content,
        "User message creation": "ai-message-user" in content,
        "Assistant response": "ai-message-assistant" in content,
    }

    print("📋 FUNCTIONALITY CHECKS:")
    passed = 0
    total = len(checks)

    for check_name, result in checks.items():
        if result:
            print(f"✅ {check_name}: PASS")
            passed += 1
        else:
            print(f"❌ {check_name}: FAIL")

    success_rate = (passed / total) * 100
    print(f"\n📊 IMPLEMENTATION CHECK: {success_rate:.1f}% ({passed}/{total})")

    if success_rate >= 85:
        print("🎉 Chat functionality fix appears to be complete!")
        return True
    else:
        print("⚠️ Some functionality may still be missing")
        return False


def main():
    """Run the test"""
    success = test_chat_functionality()

    if success:
        print("\n🚀 READY FOR TESTING:")
        print("1. The chat modal should now open when clicking 'Lyrixa AI'")
        print("2. Suggestion buttons should be clickable")
        print("3. New messages should appear when buttons are clicked")
        print("4. Buttons should be disabled after clicking")
        print("\n✅ Please test the website again!")
    else:
        print("\n❌ Fix may not be complete. Manual verification needed.")


if __name__ == "__main__":
    main()
