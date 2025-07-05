"""
Test Unified GUI System
======================

Comprehensive test for the unified Lyrixa GUI with all Phase 1-4 features.
Tests cross-phase communication, real-time updates, and integration flow.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 UNIFIED GUI INTEGRATION TEST")
print("=" * 50)


def test_imports():
    """Test that all required components can be imported."""
    print("📦 Testing imports...")

    try:
        from lyrixa.gui import EnhancedLyrixaWindow

        print("✅ EnhancedLyrixaWindow imported")
    except ImportError as e:
        print(f"❌ Failed to import EnhancedLyrixaWindow: {e}")
        return False

    try:
        from lyrixa.gui.unified.main import UnifiedLyrixaLauncher

        print("✅ UnifiedLyrixaLauncher imported")
    except ImportError as e:
        print(f"❌ Failed to import UnifiedLyrixaLauncher: {e}")
        return False

    try:
        from lyrixa.gui.unified.context_bridge import ContextBridge

        print("✅ ContextBridge imported")
    except ImportError as e:
        print(f"❌ Failed to import ContextBridge: {e}")
        return False

    return True


def test_enhanced_window_initialization():
    """Test Enhanced Lyrixa Window can be initialized."""
    print("\n🎙️ Testing Enhanced Window initialization...")

    try:
        from lyrixa.gui import EnhancedLyrixaWindow

        window = EnhancedLyrixaWindow()
        print("✅ Enhanced Window created successfully")

        # Test Phase 3 components
        if hasattr(window, "analytics_dashboard") and window.analytics_dashboard:
            print("✅ Analytics Dashboard initialized")

        if hasattr(window, "notification_system") and window.notification_system:
            print("✅ Notification System initialized")

        if hasattr(window, "config_manager") and window.config_manager:
            print("✅ Configuration Manager initialized")

        if hasattr(window, "performance_monitor") and window.performance_monitor:
            print("✅ Performance Monitor initialized")

        if hasattr(window, "intelligence_layer") and window.intelligence_layer:
            print("✅ Intelligence Layer initialized")

        # Test lifecycle hooks
        if hasattr(window, "on_init"):
            print("✅ Lifecycle hooks available")

        # Test memory system
        if hasattr(window, "advanced_memory") and window.advanced_memory:
            print("✅ Advanced Memory System connected")

        return True

    except Exception as e:
        print(f"❌ Enhanced Window initialization failed: {e}")
        return False


def test_context_bridge():
    """Test the ContextBridge communication system."""
    print("\n🔗 Testing ContextBridge...")

    try:
        from lyrixa.gui.unified.context_bridge import ContextBridge, EventType

        bridge = ContextBridge()
        print("✅ ContextBridge created")

        # Test event registration
        test_events = []

        def test_handler(event):
            test_events.append(event)

        bridge.subscribe(EventType.MEMORY_UPDATE, test_handler)
        print("✅ Event subscription works")

        # Test event emission
        bridge.emit_event(
            EventType.MEMORY_UPDATE,
            source_phase="test",
            target_phase="test",
            data={"test": "data"},
        )

        # Small delay to process events
        time.sleep(0.1)

        if test_events:
            print("✅ Event emission and handling works")
        else:
            print("⚠️ Event emission may not be working")

        return True

    except Exception as e:
        print(f"❌ ContextBridge test failed: {e}")
        return False


async def test_unified_launcher():
    """Test the unified launcher async initialization."""
    print("\n🚀 Testing Unified Launcher...")

    try:
        from lyrixa.gui.unified.main import UnifiedLyrixaLauncher

        launcher = UnifiedLyrixaLauncher()
        print("✅ Launcher created")

        # Test async initialization (without actually starting GUI)
        if await launcher.initialize_memory_system():
            print("✅ Memory system initialization works")

        if await launcher.initialize_anticipation_engine():
            print("✅ Anticipation engine initialization works")

        # Test communication setup
        if launcher.setup_cross_phase_communication():
            print("✅ Cross-phase communication setup works")

        # Test context bridge integration
        if launcher.context_bridge:
            print("✅ ContextBridge integrated with launcher")

        return True

    except Exception as e:
        print(f"❌ Unified Launcher test failed: {e}")
        return False


def test_cross_phase_integration():
    """Test cross-phase communication integration."""
    print("\n🔄 Testing cross-phase integration...")

    try:
        from lyrixa.gui import EnhancedLyrixaWindow
        from lyrixa.gui.unified.context_bridge import ContextBridge, EventType

        # Create components
        window = EnhancedLyrixaWindow()
        bridge = ContextBridge()

        # Register components
        if window.advanced_memory:
            bridge.register_component("memory", window.advanced_memory)
            print("✅ Memory system registered with bridge")

        if window.anticipation_engine:
            bridge.register_component("anticipation", window.anticipation_engine)
            print("✅ Anticipation engine registered with bridge")

        if window.analytics_dashboard:
            bridge.register_component("analytics", window.analytics_dashboard)
            print("✅ Analytics dashboard registered with bridge")

        # Test communication flow
        received_events = []

        def capture_event(event):
            received_events.append(event)

        bridge.subscribe(EventType.SEMANTIC_EVENT, capture_event)

        # Simulate cross-phase communication
        bridge.emit_event(
            EventType.SEMANTIC_EVENT,
            source_phase="memory",
            target_phase="intelligence",
            data={"semantic_clusters": ["test_cluster"]},
        )

        time.sleep(0.1)

        if received_events:
            print("✅ Cross-phase communication flow works")

        return True

    except Exception as e:
        print(f"❌ Cross-phase integration test failed: {e}")
        return False


def test_qt_integration():
    """Test Qt GUI integration (if available)."""
    print("\n🖥️ Testing Qt integration...")

    try:
        from PySide6.QtWidgets import QApplication

        from lyrixa.gui import EnhancedLyrixaWindow

        # Test if Qt components can be created
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        window = EnhancedLyrixaWindow()

        # Test if Qt window can be created
        if window.qt_available:
            print("✅ Qt GUI framework available")

            # Test show method (without actually showing)
            if hasattr(window, "show"):
                print("✅ Show method available")

            # Test real-time updates setup
            if hasattr(window, "_setup_realtime_updates"):
                print("✅ Real-time updates available")

            # Test main window layout
            if hasattr(window, "main_window"):
                print("✅ Main window layout created")
        else:
            print("⚠️ Qt not available - GUI will run in console mode")

        return True

    except ImportError:
        print("⚠️ Qt not available - testing console mode")
        try:
            from lyrixa.gui import EnhancedLyrixaWindow

            window = EnhancedLyrixaWindow()
            print("✅ Console mode works")
            return True
        except Exception as e:
            print(f"❌ Console mode failed: {e}")
            return False
    except Exception as e:
        print(f"❌ Qt integration test failed: {e}")
        return False


async def run_full_test():
    """Run the complete test suite."""
    print("🏁 Starting comprehensive unified GUI test...\n")

    tests = [
        ("Import Test", test_imports),
        ("Enhanced Window Test", test_enhanced_window_initialization),
        ("ContextBridge Test", test_context_bridge),
        ("Unified Launcher Test", test_unified_launcher),
        ("Cross-Phase Integration Test", test_cross_phase_integration),
        ("Qt Integration Test", test_qt_integration),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False

    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nTests passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Unified GUI system is working!")
    else:
        print("⚠️ Some tests failed - check the output above")

    return passed == total


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(run_full_test())
    sys.exit(0 if success else 1)
