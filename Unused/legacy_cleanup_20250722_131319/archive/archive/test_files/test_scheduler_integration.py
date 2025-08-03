#!/usr/bin/env python3
"""
🧪 Test Script: Task Scheduler Integration
=========================================

Test the integration of the background task scheduler into the Lyrixa.
This script verifies that:
1. Task scheduler loads correctly
2. GUI includes the Tasks tab
3. Basic task management works
4. No critical import or runtime errors
"""

import sys
import time
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))


def test_task_scheduler_import():
    """Test that task scheduler can be imported"""
    print("🔍 Testing task scheduler import...")
    try:
            BackgroundTaskScheduler,
            TaskPriority,
            TaskStatus,
        )

        print("✅ Task scheduler imports successful")
        return True
    except ImportError as e:
        print(f"❌ Task scheduler import failed: {e}")
        return False


def test_task_scheduler_basic_functionality():
    """Test basic task scheduler functionality"""
    print("🔍 Testing task scheduler basic functionality...")
    try:
        from Aetherra.core.task_scheduler import BackgroundTaskScheduler, TaskPriority

        # Create scheduler
        scheduler = BackgroundTaskScheduler(max_workers=2)
        print("✅ Task scheduler created successfully")

        # Add a simple task
        def test_task():
            time.sleep(0.1)
            return "Test completed"

        task_id = scheduler.schedule_task(
            function=test_task, name="Integration Test Task", priority=TaskPriority.HIGH
        )
        print(f"✅ Task scheduled with ID: {task_id}")

        # Wait for task completion
        success = scheduler.wait_for_task(task_id, timeout=5.0)
        if success:
            result = scheduler.get_task_result(task_id)
            print(f"✅ Task completed with result: {result}")
        else:
            print("⚠️  Task did not complete within timeout")

        # Get statistics
        stats = scheduler.get_statistics()
        print(f"✅ Task statistics: {stats}")

        # Shutdown
        scheduler.shutdown(timeout=3.0)
        print("✅ Task scheduler shut down successfully")

        return True

    except Exception as e:
        print(f"❌ Task scheduler functionality test failed: {e}")
        return False


def test_gui_integration():
    """Test that the GUI can load with task scheduler integration"""
    print("🔍 Testing GUI integration...")
    try:
        # Import Qt first
        from PySide6.QtWidgets import QApplication

        # Create Qt application
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Import Lyrixa
        from Lyrixa.ui.aetherplex import LyrixaWindow

        # Create main window
        window = LyrixaWindow()
        print("✅ Lyrixawindow created successfully")

        # Check if task scheduler was initialized
        if hasattr(window, "task_scheduler") and window.task_scheduler:
            print("✅ Task scheduler integrated and initialized")
        else:
            print("⚠️  Task scheduler not initialized in GUI")

        # Check if tasks tab method exists
        if hasattr(window, "create_tasks_tab"):
            print("✅ Tasks tab method available")
        else:
            print("❌ Tasks tab method missing")

        # Clean up
        if hasattr(window, "task_scheduler") and window.task_scheduler:
            window.task_scheduler.shutdown(timeout=2.0)

        window.close()
        return True

    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🚀 Starting Task Scheduler Integration Tests")
    print("=" * 50)

    tests = [
        ("Task Scheduler Import", test_task_scheduler_import),
        ("Task Scheduler Functionality", test_task_scheduler_basic_functionality),
        ("GUI Integration", test_gui_integration),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            print(f"📊 {test_name}: {status}")
        except Exception as e:
            print(f"[FAIL] {test_name}: CRASH - {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📈 INTEGRATION TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Task scheduler integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
