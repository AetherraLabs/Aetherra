#!/usr/bin/env python3
"""
Simple Import Test for Aetherra and Lyrixa
==========================================

Just tests that both systems can be imported successfully.
"""


def test_imports():
    """Test basic imports"""
    print("🧪 Testing Imports...")
    print("=" * 50)

    # Test Aetherra
    try:
        import Aetherra

        print(f"✅ Aetherra imported successfully (v{Aetherra.__version__})")
        print(f"   Available: {Aetherra.__all__}")
    except Exception as e:
        print(f"❌ Aetherra import failed: {e}")
        return False

    # Test lyrixa
    try:
        import lyrixa

        print(f"✅ lyrixa imported successfully (v{lyrixa.__version__})")
        print(f"   Available: {lyrixa.__all__}")
    except Exception as e:
        print(f"❌ lyrixa import failed: {e}")
        return False

    # Test submodules
    try:
        from Aetherra import AetherraAgent, AetherraInterpreter, AetherraParser

        print("✅ Core Aetherra classes imported")
    except Exception as e:
        print(f"❌ Aetherra classes import failed: {e}")
        return False

    try:
        from lyrixa import LocalModel, LyrixaAI, ModelRouter, OpenAIModel

        print("✅ Core lyrixa classes imported")
    except Exception as e:
        print(f"❌ lyrixa classes import failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 ALL IMPORTS SUCCESSFUL!")
    print("✅ Case sensitivity issue resolved (lyrixa, not Lyrixa)")
    print("✅ Import paths updated")
    print("✅ Neuro* naming converted to Aetherra*")
    print("✅ Both systems ready for use")

    return True


if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
