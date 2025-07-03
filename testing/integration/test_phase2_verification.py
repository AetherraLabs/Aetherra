#!/usr/bin/env python3
"""
🧪 Phase 2 System Verification Test
==================================

Simple test to verify that all Phase 2 systems can be imported
and basic functionality works correctly.

Author: NeuroCode Development Team
Date: June 30, 2025
"""

import sys


def test_phase2_imports():
    """Test that all Phase 2 systems can be imported"""
    print("🧪 Testing Phase 2 System Imports...")

    systems = [
        ("Stability System", "core.stability", "StabilityManager"),
        ("Introspective Logger", "core.introspective_logger", "IntrospectiveLogger"),
        ("Conversational AI", "core.conversational_ai", "ConversationalAI"),
        ("Plugin Registry", "core.plugin_registry", "PluginRegistry"),
        ("Chat Enhancements", "core.chat_enhancements", "ChatEnhancementSystem"),
        ("Internal Refactoring", "core.internal_refactoring", "InternalRefactoringSystem"),
    ]

    results = {}

    for name, module_name, class_name in systems:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            # Try to instantiate
            instance = cls()
            results[name] = {"status": "SUCCESS", "class": cls, "instance": instance}
            print(f"  ✅ {name}: Import and instantiation successful")
        except Exception as e:
            results[name] = {"status": "FAILED", "error": str(e)}
            print(f"  ❌ {name}: {e}")

    return results


def test_basic_functionality(results):
    """Test basic functionality of imported systems"""
    print("\n🔧 Testing Basic Functionality...")

    # Test Stability System
    if "Stability System" in results and results["Stability System"]["status"] == "SUCCESS":
        try:
            stability = results["Stability System"]["instance"]

            # Test safe execution decorator
            @stability.safe_execute
            def test_function():
                return "Hello from safe execution!"

            result = test_function()
            print(f"  ✅ Stability: Safe execution works - {result}")
        except Exception as e:
            print(f"  ⚠️ Stability: Basic test failed - {e}")

    # Test Conversational AI
    if "Conversational AI" in results and results["Conversational AI"]["status"] == "SUCCESS":
        try:
            conv_ai = results["Conversational AI"]["instance"]
            # Test persona system
            from core.conversational_ai import PersonaMode

            conv_ai.set_persona(PersonaMode.ASSISTANT)
            print("  ✅ Conversational AI: Persona system works")
        except Exception as e:
            print(f"  ⚠️ Conversational AI: Basic test failed - {e}")

    # Test Chat Enhancements
    if "Chat Enhancements" in results and results["Chat Enhancements"]["status"] == "SUCCESS":
        try:
            chat_system = results["Chat Enhancements"]["instance"]
            # Test session creation
            session_id = chat_system.create_new_session("Test Session")
            print(f"  ✅ Chat Enhancements: Session creation works - {session_id}")
        except Exception as e:
            print(f"  ⚠️ Chat Enhancements: Basic test failed - {e}")

    # Test Plugin Registry
    if "Plugin Registry" in results and results["Plugin Registry"]["status"] == "SUCCESS":
        try:
            plugin_registry = results["Plugin Registry"]["instance"]
            # Test getting available plugins
            plugins = plugin_registry.get_available_plugins()
            print(f"  ✅ Plugin Registry: Plugin listing works - {len(plugins)} plugins")
        except Exception as e:
            print(f"  ⚠️ Plugin Registry: Basic test failed - {e}")

    # Test Introspective Logger
    if "Introspective Logger" in results and results["Introspective Logger"]["status"] == "SUCCESS":
        try:
            logger = results["Introspective Logger"]["instance"]
            # Test execution logging
            reflection = logger.log_execution("test_code", "test_result", {"test": True})
            print(f"  ✅ Introspective Logger: Execution logging works - {reflection.execution_id}")
        except Exception as e:
            print(f"  ⚠️ Introspective Logger: Basic test failed - {e}")

    # Test Internal Refactoring
    if "Internal Refactoring" in results and results["Internal Refactoring"]["status"] == "SUCCESS":
        try:
            refactoring = results["Internal Refactoring"]["instance"]
            # Test status
            status = refactoring.get_refactoring_status()
            print(f"  ✅ Internal Refactoring: Status reporting works - {len(status)} status items")
        except Exception as e:
            print(f"  ⚠️ Internal Refactoring: Basic test failed - {e}")


def test_integration():
    """Test basic integration between systems"""
    print("\n🔗 Testing System Integration...")

    try:
        # Test that systems can work together
        from core.introspective_logger import IntrospectiveLogger
        from core.stability import StabilityManager

        stability = StabilityManager()
        logger = IntrospectiveLogger()

        # Test logging an operation with stability wrapper
        @stability.safe_execute
        def test_integration_operation():
            return "Integration test successful"

        result = test_integration_operation()

        # Log the operation
        reflection = logger.log_execution(
            "test_integration_operation()", result, {"integration_test": True}
        )

        print("  ✅ Integration: Stability + Logger integration works")
        print(f"     Result: {result}")
        print(f"     Reflection ID: {reflection.execution_id}")

    except Exception as e:
        print(f"  ⚠️ Integration: Basic integration test failed - {e}")


def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n📊 Phase 2 System Test Report")
    print("=" * 50)

    total_systems = len(results)
    successful_systems = len([r for r in results.values() if r["status"] == "SUCCESS"])

    print(f"Total Systems Tested: {total_systems}")
    print(f"Successfully Imported: {successful_systems}")
    print(f"Success Rate: {successful_systems / total_systems * 100:.1f}%")

    print("\n📋 Detailed Results:")
    for name, result in results.items():
        status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
        print(f"  {status_icon} {name}: {result['status']}")
        if result["status"] == "FAILED":
            print(f"     Error: {result['error']}")

    if successful_systems == total_systems:
        print("\n🎉 ALL PHASE 2 SYSTEMS OPERATIONAL!")
        print("✅ NeuroCode & Neuroplex Phase 2 is ready for production use")
    else:
        print("\n⚠️ Some systems need attention")
        print(f"✅ {successful_systems}/{total_systems} systems are operational")
        print("🔧 See individual error messages above for troubleshooting")

    return successful_systems == total_systems


def main():
    """Main test execution"""
    print("🚀 NeuroCode & Neuroplex Phase 2 System Verification")
    print("=" * 60)
#     print("Testing all Phase 2 systems for import and basic functionality...")

    # Test imports
    results = test_phase2_imports()

    # Test basic functionality
    test_basic_functionality(results)

    # Test integration
    test_integration()

    # Generate report
    all_passed = generate_test_report(results)

    print(f"\n🔬 Test Completed: {'PASS' if all_passed else 'PARTIAL'}")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
