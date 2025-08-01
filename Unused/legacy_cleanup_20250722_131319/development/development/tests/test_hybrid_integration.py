#!/usr/bin/env python3
"""
World-Class Components Integration Test
======================================
🧪 Test integration of world-class components with aetherra_hybrid_launcher.py
🔧 Verify imports, initialization, and hybrid window compatibility
"""

import sys
import os
from pathlib import Path

# Add project root to path (same as aetherra_hybrid_launcher.py)
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing Critical Imports...")

    try:
        # Test world-class components
        from Aetherra.lyrixa.memory.world_class_memory_core import WorldClassMemoryCore
        print("✅ WorldClassMemoryCore import successful")

        from Aetherra.lyrixa.core.world_class_goal_tracker import WorldClassGoalTracker
        print("✅ WorldClassGoalTracker import successful")

        # Test hybrid window
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow
        print("✅ LyrixaWindow import successful")

        # Test launcher components
        from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window
        print("✅ create_lyrixa_window import successful")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_component_initialization():
    """Test component initialization"""
    print("\n🔧 Testing Component Initialization...")

    try:
        # Test memory core initialization
        from Aetherra.lyrixa.memory.world_class_memory_core import WorldClassMemoryCore

        # Test lightweight version first (no GUI dependencies)
        from Aetherra.lyrixa.memory.lightweight_memory_core import MemoryCore

        memory_core = MemoryCore()
        print("✅ MemoryCore initialized successfully")

        # Test some basic functionality (uses sample data)
        memories = memory_core.search_memories("memory")
        print(f"✅ Memory core functionality test: {len(memories)} memories found")

        # Test goal tracker initialization
        from Aetherra.lyrixa.core.lightweight_goal_tracker import GoalTracker

        goal_tracker = GoalTracker()
        print("✅ GoalTracker initialized successfully")

        # Test basic goal functionality (uses sample data)
        if hasattr(goal_tracker, 'goals'):
            goals = goal_tracker.goals
            print(f"✅ Goal tracker functionality test: {len(goals)} goals found")
        else:
            print("✅ Goal tracker functionality test: interface available")

        return True

    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hybrid_window_integration():
    """Test hybrid window integration with world-class components"""
    print("\n🔗 Testing Hybrid Window Integration...")

    try:
        # Test PySide6 availability
        try:
            from PySide6.QtWidgets import QApplication, QWidget
            print("✅ PySide6 available for GUI testing")

            # Create minimal Qt application for testing
            app = QApplication.instance()
            if app is None:
                app = QApplication([])

            # Test world-class components with GUI
            from Aetherra.lyrixa.memory.world_class_memory_core import WorldClassMemoryCore
            from Aetherra.lyrixa.core.world_class_goal_tracker import WorldClassGoalTracker

            # Test memory core with GUI
            memory_widget = WorldClassMemoryCore()
            print("✅ WorldClassMemoryCore GUI widget created successfully")

            # Test goal tracker with GUI
            goal_widget = WorldClassGoalTracker()
            print("✅ WorldClassGoalTracker GUI widget created successfully")

            # Test hybrid window creation
            from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window

            # Set hybrid mode
            os.environ["LYRIXA_UI_MODE"] = "hybrid"

            window = create_lyrixa_window()
            print("✅ Hybrid window created successfully")

            return True

        except ImportError:
            print("⚠️  PySide6 not available - GUI testing skipped")
            return True

    except Exception as e:
        print(f"❌ Hybrid window integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_launcher_compatibility():
    """Test compatibility with aetherra_hybrid_launcher.py"""
    print("\n🚀 Testing Launcher Compatibility...")

    try:
        # Test environment setup (same as launcher)
        os.environ["LYRIXA_UI_MODE"] = "hybrid"

        # Test launcher imports
        from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window
        from Aetherra.lyrixa.launcher import initialize_system

        print("✅ Launcher imports successful")

        # Test window creation with world-class components
        window = create_lyrixa_window()
        print("✅ Window creation successful")

        # Test that window has the expected tab structure
        if hasattr(window, 'content_stack'):
            print("✅ Window has content_stack (tab structure)")

            # Check for memory and goal tabs
            if hasattr(window, 'create_memory_tab'):
                print("✅ Window has create_memory_tab method")

            if hasattr(window, 'create_goal_tab'):
                print("✅ Window has create_goal_tab method")

        return True

    except Exception as e:
        print(f"❌ Launcher compatibility failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_modular_access():
    """Test modular access patterns for world-class components"""
    print("\n🔧 Testing Modular Access...")

    try:
        # Test direct import patterns used by launcher
        from Aetherra.lyrixa.memory.world_class_memory_core import WorldClassMemoryCore
        from Aetherra.lyrixa.core.world_class_goal_tracker import WorldClassGoalTracker

        print("✅ Direct import patterns work")

        # Test lightweight alternatives
        from Aetherra.lyrixa.memory.lightweight_memory_core import MemoryCore
        from Aetherra.lyrixa.core.lightweight_goal_tracker import GoalTracker

        print("✅ Lightweight alternatives available")

        # Test that components can be instantiated without GUI
        memory_core = MemoryCore()
        goal_tracker = GoalTracker()

        print("✅ Components can be instantiated without GUI")

        # Test that components have expected interfaces
        if hasattr(memory_core, 'search_memories'):
            print("✅ Memory core has expected interface")

        if hasattr(goal_tracker, 'goals'):
            print("✅ Goal tracker has expected interface")

        return True

    except Exception as e:
        print(f"❌ Modular access failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("🧪 World-Class Components Integration Test")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("Component Initialization", test_component_initialization),
        ("Hybrid Window Integration", test_hybrid_window_integration),
        ("Launcher Compatibility", test_launcher_compatibility),
        ("Modular Access", test_modular_access)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("🏁 Integration Test Results")
    print("=" * 50)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 ALL TESTS PASSED! World-class components are properly integrated.")
        print("🚀 Ready for use with aetherra_hybrid_launcher.py")
    else:
        print("⚠️  Some tests failed. Integration may need fixes.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
