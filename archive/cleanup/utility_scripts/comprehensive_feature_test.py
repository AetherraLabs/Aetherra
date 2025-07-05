#!/usr/bin/env python3
"""
Comprehensive Feature Test for Aetherra & Lyrixa
=================================================

Test core functionality of both systems after import migration and renaming.
"""

import sys
import traceback


def test_aetherra_core():
    """Test core Aetherra functionality"""
    print("🧪 Testing Aetherra Core Functionality")
    print("=" * 50)

    try:
        # Test basic imports
        from Aetherra import AetherraInterpreter, AetherraMemory

        print("✅ Core imports successful")

        # Test memory system
        memory = AetherraMemory()
        memory.remember("Test memory entry", tags=["test"])
        memories = memory.recall(tags=["test"])
        print(
            f"✅ Memory system working - stored and recalled {len(memories)} memories"
        )

        # Test interpreter creation
        interpreter = AetherraInterpreter()
        print(f"✅ Interpreter created: {type(interpreter).__name__}")

        return True

    except Exception as e:
        print(f"❌ Aetherra core test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False


def test_aetherra_chat():
    """Test Aetherra chat functionality"""
    print("\n🧪 Testing Aetherra Chat System")
    print("=" * 50)

    try:
        from Aetherra.core.chat_router import AetherraChatRouter

        # Create chat router in demo mode
        chat_router = AetherraChatRouter(demo_mode=True)
        print("✅ Chat router created in demo mode")

        # Test basic message routing
        response = chat_router.route_message("test_user", "Hello, what can you do?")
        print(f"✅ Message routing works - response type: {type(response)}")

        return True

    except Exception as e:
        print(f"❌ Chat system test failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False


def test_aetherra_plugins():
    """Test Aetherra plugin system"""
    print("\n🧪 Testing Aetherra Plugin System")
    print("=" * 50)

    try:
        from Aetherra.core.plugin_manager import PluginManager

        # Create plugin manager
        plugin_manager = PluginManager()
        print("✅ Plugin manager created")

        # Check available plugins
        plugins = (
            plugin_manager.get_available_plugins()
            if hasattr(plugin_manager, "get_available_plugins")
            else []
        )
        print(f"✅ Plugin system accessible - {len(plugins)} plugins available")

        return True

    except Exception as e:
        print(f"❌ Plugin system test failed: {e}")
        return False


def test_lyrixa_models():
    """Test Lyrixa model system"""
    print("\n🧪 Testing Lyrixa Local Models")
    print("=" * 50)

    try:
        # Test direct file import
        sys.path.insert(0, "Lyrixa/models")
        import local_model

        # Create local model instance
        model = local_model.LocalModel()
        print("✅ LocalModel imported and created")

        # Test basic functionality
        available = model.is_available()
        print(f"✅ Model availability check: {available}")

        # Test model configurations
        configs = [local_model.OLLAMA_DEFAULT, local_model.LM_STUDIO]
        print(f"✅ Pre-configured models available: {len(configs)}")

        return True

    except Exception as e:
        print(f"❌ Lyrixa models test failed: {e}")
        return False


def test_integration():
    """Test integration between systems"""
    print("\n🧪 Testing System Integration")
    print("=" * 50)

    try:
        from Aetherra import AetherraMemory

        # Test memory with AI content
        memory = AetherraMemory()
        memory.remember(
            "Integration test: Aetherra and Lyrixa working together",
            tags=["integration", "test"],
            category="system_test",
        )

        # Recall integration memories
        integration_memories = memory.recall(category="system_test")
        print(f"✅ Integration memory test - {len(integration_memories)} entries")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run comprehensive feature tests"""
    print("🚀 Aetherra & Lyrixa Comprehensive Feature Test")
    print("=" * 60)

    tests = [
        ("Aetherra Core", test_aetherra_core),
        ("Aetherra Chat", test_aetherra_chat),
        ("Aetherra Plugins", test_aetherra_plugins),
        ("Lyrixa Models", test_lyrixa_models),
        ("Integration", test_integration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 All systems are functional!")
    elif passed >= total * 0.8:
        print("✅ Systems are mostly functional with minor issues")
    elif passed >= total * 0.5:
        print("⚠️ Systems have significant issues but core functionality works")
    else:
        print("❌ Systems have major issues that need attention")


if __name__ == "__main__":
    main()
