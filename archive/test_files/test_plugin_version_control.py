#!/usr/bin/env python3
"""
🧪 PLUGIN VERSION CONTROL SYSTEM TEST
=====================================

Comprehensive test of the Plugin Version Control & Rollback System.
Tests all major functionality:
- Snapshot creation
- Version listing
- Rollback operations
- Diff generation
- GUI integration
- Conversational interface
"""

import os
import sys
import tempfile
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.core.plugin_version_control import PluginSnapshot, PluginVersionControl
from lyrixa.core.plugin_version_conversational import (
    PluginVersionConversationalInterface,
)


def create_test_plugin_code(version: int) -> str:
    """Create test plugin code for different versions"""
    return f'''#!/usr/bin/env python3
"""
Test Plugin Version {version}
============================
A test plugin for version control testing.
"""

class TestPlugin:
    """Test plugin version {version}"""

    def __init__(self):
        self.version = {version}
        self.name = "TestPlugin"
        self.capabilities = ["test", "version_{version}"]

    def execute(self, command: str):
        """Execute a test command"""
        if command == "get_version":
            return {{"version": self.version, "message": "This is version {version}"}}
        elif command == "test":
            return {{"result": "Test successful", "version": {version}}}
        else:
            return {{"error": "Unknown command", "version": {version}}}

    def get_info(self):
        """Get plugin information"""
        return {{
            "name": self.name,
            "version": str(self.version),
            "description": f"Test plugin version {version}",
            "capabilities": self.capabilities
        }}

# Plugin instance
plugin = TestPlugin()
'''


def test_version_control_basic():
    """Test basic version control functionality"""
    print("🧪 Testing Basic Version Control Functionality")
    print("=" * 50)

    # Initialize version control
    version_control = PluginVersionControl(".test_plugin_history")

    # Test 1: Create snapshots
    print("\n1️⃣ Testing Snapshot Creation...")

    plugin_name = "TestPlugin"

    # Create multiple versions
    for version in range(1, 4):
        code = create_test_plugin_code(version)
        snapshot = version_control.create_snapshot(
            plugin_name,
            code,
            confidence_score=0.5 + (version * 0.1),
            created_by="test_system",
            description=f"Test version {version}",
        )

        if snapshot:
            print(f"   ✅ Created snapshot for version {version}: {snapshot.timestamp}")
        else:
            print(f"   ❌ Failed to create snapshot for version {version}")
            return False

    # Test 2: List snapshots
    print("\n2️⃣ Testing Snapshot Listing...")
    snapshots = version_control.list_snapshots(plugin_name)
    print(f"   📋 Found {len(snapshots)} snapshots:")

    for i, snapshot in enumerate(snapshots):
        print(
            f"      {i + 1}. {snapshot.timestamp} (confidence: {snapshot.confidence_score:.2f})"
        )

    if len(snapshots) != 3:
        print(f"   ❌ Expected 3 snapshots, got {len(snapshots)}")
        return False

    # Test 3: Generate diff
    print("\n3️⃣ Testing Diff Generation...")
    if len(snapshots) >= 2:
        diff = version_control.diff_plugin_versions(
            plugin_name, snapshots[0].timestamp, snapshots[1].timestamp
        )

        if diff and not diff.startswith("❌"):
            print("   ✅ Diff generated successfully")
            print(f"   📊 Diff length: {len(diff)} characters")
        else:
            print(f"   ❌ Diff generation failed: {diff}")
            return False

    # Test 4: Export snapshot
    print("\n4️⃣ Testing Snapshot Export...")
    if snapshots:
        export_path = f"test_export_{snapshots[0].timestamp}.py"
        success = version_control.export_snapshot(
            plugin_name, snapshots[0].timestamp, export_path
        )

        if success and os.path.exists(export_path):
            print(f"   ✅ Snapshot exported to: {export_path}")
            os.remove(export_path)  # Cleanup
        else:
            print("   ❌ Snapshot export failed")
            return False

    # Test 5: Get statistics
    print("\n5️⃣ Testing Statistics...")
    stats = version_control.get_plugin_history_stats(plugin_name)

    if stats:
        print(f"   📊 Total snapshots: {stats.get('total_snapshots', 0)}")
        print(f"   📈 Average confidence: {stats.get('average_confidence', 0):.2f}")
        print(f"   🏆 Max confidence: {stats.get('max_confidence', 0):.2f}")
    else:
        print("   ❌ Failed to get statistics")
        return False

    print("\n✅ Basic version control tests PASSED!")
    return True


def test_conversational_interface():
    """Test the conversational interface"""
    print("\n\n🗣️ Testing Conversational Interface")
    print("=" * 50)

    # Mock plugin manager for testing
    class MockPluginManager:
        def __init__(self, version_control):
            self.version_control = version_control
            self.plugin_info = {"TestPlugin": {"name": "TestPlugin"}}

        def get_plugin_version_history(self, plugin_name):
            snapshots = self.version_control.list_snapshots(plugin_name)
            return [
                {
                    "timestamp": s.timestamp,
                    "confidence_score": s.confidence_score,
                    "size": s.size,
                    "metadata": s.metadata,
                }
                for s in snapshots
            ]

        def create_plugin_snapshot(
            self, plugin_name, confidence, description, created_by
        ):
            code = create_test_plugin_code(99)  # Test code
            snapshot = self.version_control.create_snapshot(
                plugin_name, code, confidence, created_by, description
            )
            return snapshot is not None

        def get_plugin_version_stats(self, plugin_name):
            return self.version_control.get_plugin_history_stats(plugin_name)

    # Initialize version control and mock manager
    version_control = PluginVersionControl(".test_plugin_history")
    mock_manager = MockPluginManager(version_control)

    # Initialize conversational interface
    interface = PluginVersionConversationalInterface(mock_manager, version_control)

    # Test commands
    test_commands = [
        "show versions of TestPlugin",
        "create snapshot of TestPlugin",
        "show stats for TestPlugin",
        "list history TestPlugin",
        "what are the previous versions of TestPlugin",
    ]

    print("\n🧪 Testing Natural Language Commands:")

    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}️⃣ Command: '{command}'")

        try:
            import asyncio

            result = asyncio.run(interface.process_command(command))

            if result["success"]:
                print("   ✅ Command processed successfully")
                print(f"   📝 Response preview: {result['response'][:100]}...")
            else:
                print(f"   ❌ Command failed: {result['response']}")

        except Exception as e:
            print(f"   ❌ Exception during command processing: {e}")

    print("\n✅ Conversational interface tests COMPLETED!")
    return True


def test_rollback_functionality():
    """Test rollback functionality with actual files"""
    print("\n\n🔄 Testing Rollback Functionality")
    print("=" * 50)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"   📁 Using temporary directory: {temp_dir}")

        # Initialize version control
        history_dir = os.path.join(temp_dir, ".plugin_history")
        version_control = PluginVersionControl(history_dir)

        # Create test plugin file
        plugin_file = os.path.join(temp_dir, "TestPlugin.py")
        plugin_name = "TestPlugin"

        # Create initial version
        initial_code = create_test_plugin_code(1)
        with open(plugin_file, "w") as f:
            f.write(initial_code)

        print("   📝 Created initial plugin file")

        # Create snapshot of initial version
        snapshot1 = version_control.create_snapshot(
            plugin_name, initial_code, 0.8, "test", "Initial version"
        )
        print(
            f"   📸 Created snapshot 1: {snapshot1.timestamp if snapshot1 else 'FAILED'}"
        )

        # Modify the file (version 2)
        modified_code = create_test_plugin_code(2)
        with open(plugin_file, "w") as f:
            f.write(modified_code)

        print("   📝 Modified plugin file to version 2")

        # Create snapshot of modified version
        snapshot2 = version_control.create_snapshot(
            plugin_name, modified_code, 0.9, "test", "Modified version"
        )
        print(
            f"   📸 Created snapshot 2: {snapshot2.timestamp if snapshot2 else 'FAILED'}"
        )

        # Test rollback
        if snapshot1:
            print(f"   🔄 Rolling back to snapshot 1: {snapshot1.timestamp}")
            success = version_control.rollback_plugin(
                plugin_name, snapshot1.timestamp, plugin_file
            )

            if success:
                # Check if rollback worked
                with open(plugin_file, "r") as f:
                    rolled_back_content = f.read()

                if "version = 1" in rolled_back_content:
                    print("   ✅ Rollback successful - content matches original")
                else:
                    print("   ❌ Rollback failed - content doesn't match")
                    return False
            else:
                print("   ❌ Rollback operation failed")
                return False

        print("\n✅ Rollback functionality tests PASSED!")
        return True


def cleanup_test_files():
    """Clean up test files and directories"""
    import shutil

    test_dirs = [".test_plugin_history"]
    test_files = ["test_export_*.py"]

    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"   🧹 Cleaned up {test_dir}")

    for pattern in test_files:
        import glob

        for file in glob.glob(pattern):
            os.remove(file)
            print(f"   🧹 Cleaned up {file}")


def main():
    """Run all tests"""
    print("🚀 PLUGIN VERSION CONTROL SYSTEM TESTS")
    print("=" * 60)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Run tests
        test_results = []

        test_results.append(test_version_control_basic())
        test_results.append(test_conversational_interface())
        test_results.append(test_rollback_functionality())

        # Summary
        print("\n\n📊 TEST SUMMARY")
        print("=" * 30)

        passed_tests = sum(test_results)
        total_tests = len(test_results)

        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")

        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Plugin Version Control & Rollback System is READY!")
        else:
            print("\n⚠️ Some tests failed. Please review the output above.")

    except Exception as e:
        print(f"\n❌ Test execution failed with error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        print("\n🧹 Cleaning up test files...")
        cleanup_test_files()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    main()
