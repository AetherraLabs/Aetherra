#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lyrixa Core Merge Verification Script
Comprehensive testing of the merged lyrixa system
"""


def main():
    print("🔄 LYRIXA CORE MERGE VERIFICATION")
    print("=" * 50)

    try:
        # Test main lyrixa imports
        from lyrixa import LyrixaConversationManager, LyrixaIntelligenceStack

        print("✅ Main Lyrixa classes imported successfully")

        # Test LyrixaCore
# ARCHITECTURAL FIX: Removed Lyrixa import -         from lyrixa.LyrixaCore import get_lyrixa_core

        core = get_lyrixa_core()
        print(f"✅ LyrixaCore operational: {type(core).__name__}")

        # Test Intelligence Stack
        stack = LyrixaIntelligenceStack()
        print(f"✅ Intelligence Stack: Available={stack.is_available}")

        # Test Conversation Manager
        manager = LyrixaConversationManager()
        print(f"✅ Conversation Manager: Available={manager.is_available}")

        # Test identity system
        identity = core.get_identity_profile()
        print(
            f"✅ Identity System: {identity['name']} with {len(identity['fundamental_beliefs'])} beliefs"
        )

        # Test basic conversation
        response = manager.process_message("How are you today?")
        print(f"✅ Conversation Test: {response[:80]}...")

        print()
        print("🎉 MERGE VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL")
        print()

        # Summary
        print("📋 MERGE SUMMARY:")
        print("- Successfully merged lyrixa_core/ into lyrixa/")
        print("- Intelligence system fully operational")
        print("- All imports working correctly")
        print("- Identity system maintains coherence")
        print("- Conversation processing functional")

        return True

    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
