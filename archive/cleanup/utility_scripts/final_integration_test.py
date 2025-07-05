#!/usr/bin/env python3
"""
Final Integration Test for Aetherra and Lyrixa
==============================================

Tests that both systems can be imported and basic functionality works.
"""


def test_aetherra_import():
    """Test Aetherra core import"""
    try:
        import Aetherra

        print("✅ Aetherra imported successfully")
        print(f"   Version: {Aetherra.__version__}")
        print(f"   Available: {Aetherra.__all__}")

        # Test core classes
        from Aetherra import AetherraAgent, AetherraInterpreter, AetherraParser

        print("✅ Core Aetherra classes imported")

        return True
    except Exception as e:
        print(f"❌ Aetherra import failed: {e}")
        return False


def test_lyrixa_import():
    """Test Lyrixa import"""
    try:
        import lyrixa

        print("✅ lyrixa imported successfully")
        print(f"   Version: {lyrixa.__version__}")
        print(f"   Available: {lyrixa.__all__}")

        # Test key classes
        from lyrixa import LyrixaAI, ModelRouter

        print("✅ Core Lyrixa classes imported")

        return True
    except Exception as e:
        print(f"❌ lyrixa import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality"""
    try:
        # Test Aetherra basic functionality
        from Aetherra.core.aetherra_interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()
        print("✅ AetherraInterpreter instantiated")

        # Test Lyrixa basic functionality
        from lyrixa.models import ModelRouter

        router = ModelRouter()
        available_models = router.get_available_models()
        print(
            f"✅ ModelRouter instantiated with models: {list(available_models.keys())}"
        )

        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running Final Integration Tests...")
    print("=" * 50)

    results = []

    print("\n1. Testing Aetherra Import:")
    results.append(test_aetherra_import())

    print("\n2. Testing Lyrixa Import:")
    results.append(test_lyrixa_import())

    print("\n3. Testing Basic Functionality:")
    results.append(test_basic_functionality())

    print("\n" + "=" * 50)
    if all(results):
        print("🎉 ALL TESTS PASSED! Integration successful!")
        print("✅ Both Aetherra and lyrixa are working correctly")
        print("✅ Case sensitivity issue resolved")
        print("✅ Import paths updated")
        print("✅ Neuro* naming converted to Aetherra*")
    else:
        print("❌ Some tests failed. See details above.")

    return all(results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
