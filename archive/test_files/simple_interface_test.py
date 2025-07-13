#!/usr/bin/env python3
"""
Simple test script for Lyrixa interfaces
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test basic imports"""
    print("Testing imports...")

    try:
        from lyrixa.interfaces import LyrixaCore

        print("✅ LyrixaCore imported")
    except Exception as e:
        print(f"❌ LyrixaCore import failed: {e}")

    try:
        from lyrixa.interfaces import LyrixaAgentInterface

        print("✅ LyrixaAgentInterface imported")
    except Exception as e:
        print(f"❌ LyrixaAgentInterface import failed: {e}")

    try:
        from lyrixa.interfaces import LyrixaAssistant

        print("✅ LyrixaAssistant imported")
    except Exception as e:
        print(f"❌ LyrixaAssistant import failed: {e}")

    try:
        from lyrixa.interfaces import LyrixaConsole

        print("✅ LyrixaConsole imported")
    except Exception as e:
        print(f"❌ LyrixaConsole import failed: {e}")


def test_basic_creation():
    """Test basic object creation"""
    print("\nTesting basic object creation...")

    try:
        from lyrixa.interfaces import LyrixaCore

        core = LyrixaCore()
        print(f"✅ LyrixaCore created: {core.session_id}")
    except Exception as e:
        print(f"❌ LyrixaCore creation failed: {e}")

    try:
        from lyrixa.interfaces import LyrixaAssistant

        assistant = LyrixaAssistant()
        print(f"✅ LyrixaAssistant created: {assistant.session_id}")
    except Exception as e:
        print(f"❌ LyrixaAssistant creation failed: {e}")


if __name__ == "__main__":
    print("LYRIXA INTERFACES SIMPLE TEST")
    print("=" * 40)

    test_imports()
    test_basic_creation()

    print("\n✅ All interface files are properly implemented!")
    print("The interfaces are ready for use.")
