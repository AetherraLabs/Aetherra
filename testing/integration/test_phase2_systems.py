"""
Simple Phase 2 System Test
==========================

Test the basic functionality of our Phase 2 systems.
"""


def test_imports():
    """Test that all Phase 2 modules can be imported"""
    print("Testing Phase 2 imports...")

    try:
        from core.stability import safe_execute

        print("✅ Stability system imported")
    except ImportError as e:
        print(f"❌ Stability import failed: {e}")

    try:
        from core.introspective_logger import introspective_logger

        print("✅ Introspective logger imported")
    except ImportError as e:
        print(f"❌ Introspective logger import failed: {e}")

    try:
        from core.conversational_ai import conversational_ai

        print("✅ Conversational AI imported")
    except ImportError as e:
        print(f"❌ Conversational AI import failed: {e}")

    try:
        from core.plugin_registry import plugin_registry

        print("✅ Plugin registry imported")
    except ImportError as e:
        print(f"❌ Plugin registry import failed: {e}")


def test_stability_system():
    """Test basic stability features"""
    print("\nTesting stability system...")

    try:
        from core.stability import ErrorSeverity, safe_execute

        @safe_execute(component="test", severity=ErrorSeverity.LOW)
        def test_function():
            return "Success!"

        result = test_function()
        print(f"✅ Safe execution test: {result}")

    except Exception as e:
        print(f"❌ Stability test failed: {e}")


def test_introspective_logging():
    """Test introspective logging"""
    print("\nTesting introspective logging...")

    try:
        from core.introspective_logger import PerformanceMetrics, introspective_logger

        reflection_id = introspective_logger.log_execution(
            operation="test_operation",
            code="print('hello')",
            result="hello",
            performance=PerformanceMetrics(execution_time=0.01),
        )

        print(f"✅ Logging test successful: {reflection_id}")

    except Exception as e:
        print(f"❌ Introspective logging test failed: {e}")


def test_conversational_ai():
    """Test conversational AI"""
    print("\nTesting conversational AI...")

    try:
        from core.conversational_ai import get_available_personas

        personas = get_available_personas()
        print(f"✅ Found {len(personas)} personas")

        for persona in personas[:3]:
            print(f"   • {persona['name']}: {persona['description']}")

    except Exception as e:
        print(f"❌ Conversational AI test failed: {e}")


def test_plugin_registry():
    """Test plugin registry"""
    print("\nTesting plugin registry...")

    try:
        from core.plugin_registry import get_plugin_catalog

        catalog = get_plugin_catalog()
        print("✅ Plugin catalog loaded")
        print(f"   Total plugins: {catalog['stats']['total_plugins']}")
        print(f"   Categories: {len(catalog['categories'])}")

    except Exception as e:
        print(f"❌ Plugin registry test failed: {e}")


if __name__ == "__main__":
    print("🧪 Phase 2 Systems Test")
    print("=" * 30)

    test_imports()
    test_stability_system()
    test_introspective_logging()
    test_conversational_ai()
    test_plugin_registry()

    print("\n✅ Phase 2 testing complete!")
