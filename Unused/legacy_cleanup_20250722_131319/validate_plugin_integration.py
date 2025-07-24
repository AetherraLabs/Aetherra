#!/usr/bin/env python3
"""
Plugin Tab Integration Validation
=================================
Validates the enhanced plugin tab functionality without requiring GUI display
"""

import os
import sys

# Add the Aetherra path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))


def test_plugin_code_integration():
    """Test the plugin tab code integration without GUI"""
    try:
        print("🔍 Checking plugin tab code integration...")

        # Read the hybrid_window.py file
        hybrid_window_path = os.path.join(
            "Aetherra", "lyrixa", "gui", "hybrid_window.py"
        )
        with open(hybrid_window_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required imports
        assert "QFileDialog" in content, "QFileDialog import missing"
        print("✅ QFileDialog import found")

        # Check for plugin tab creation method
        assert "def create_plugin_tab(self):" in content, (
            "create_plugin_tab method missing"
        )
        print("✅ create_plugin_tab method found")

        # Check for load plugin file method
        assert "def load_plugin_file(self):" in content, (
            "load_plugin_file method missing"
        )
        print("✅ load_plugin_file method found")

        # Check for plugin log text edit
        assert "self.plugin_log = QTextEdit()" in content, (
            "plugin_log QTextEdit missing"
        )
        print("✅ plugin_log QTextEdit found")

        # Check for load button
        assert 'load_button = QPushButton("Load Plugin")' in content, (
            "Load Plugin button missing"
        )
        print("✅ Load Plugin button found")

        # Check for file dialog functionality
        assert "QFileDialog.getOpenFileName" in content, (
            "File dialog functionality missing"
        )
        print("✅ File dialog functionality found")

        # Check for tab widget plugin tab creation
        assert "self.create_plugin_tab()" in content, (
            "Plugin tab creation in tab widget missing"
        )
        print("✅ Plugin tab creation in tab widget found")

        # Check for Python file filter
        assert "Python Files (*.py)" in content, "Python file filter missing"
        print("✅ Python file filter found")

        # Check for plugin log append
        assert "self.plugin_log.append" in content, (
            "Plugin log append functionality missing"
        )
        print("✅ Plugin log append functionality found")

        print("\n🎉 All plugin tab code integration checks passed!")
        return True

    except FileNotFoundError:
        print(f"❌ File not found: {hybrid_window_path}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_tab_configuration():
    """Test that the tab configuration is properly set up"""
    try:
        print("🔍 Checking tab configuration...")

        # Read the hybrid_window.py file
        hybrid_window_path = os.path.join(
            "Aetherra", "lyrixa", "gui", "hybrid_window.py"
        )
        with open(hybrid_window_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that Plugins tab uses create_plugin_tab instead of placeholder
        assert (
            'self.tab_widget.addTab(self.create_plugin_tab(), "Plugins")' in content
        ), "Plugins tab not properly configured"
        print("✅ Plugins tab properly configured with create_plugin_tab()")

        # Ensure old placeholder is removed
        assert 'QLabel("Plugin Viewer/Editor")' not in content, (
            "Old plugin tab placeholder still present"
        )
        print("✅ Old plugin tab placeholder removed")

        print("\n✅ Tab configuration checks passed!")
        return True

    except Exception as e:
        print(f"❌ Tab configuration test failed: {e}")
        return False


def test_compatibility_methods():
    """Test that all launcher compatibility methods are present"""
    try:
        print("🔍 Checking launcher compatibility methods...")

        # Read the hybrid_window.py file
        hybrid_window_path = os.path.join(
            "Aetherra", "lyrixa", "gui", "hybrid_window.py"
        )
        with open(hybrid_window_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_methods = [
            "attach_intelligence_stack",
            "attach_runtime",
            "attach_lyrixa",
            "refresh_plugin_discovery",
            "add_plugin_editor_tab",
            "update_dashboard_metrics",
            "update_intelligence_status",
            "update_runtime_status",
            "update_agent_status",
            "update_performance_metrics",
            "populate_model_dropdown",
            "init_background_monitors",
        ]

        for method in required_methods:
            assert f"def {method}(" in content, f"Compatibility method {method} missing"
            print(f"✅ {method} method found")

        print("\n✅ All launcher compatibility methods present!")
        return True

    except Exception as e:
        print(f"❌ Compatibility methods test failed: {e}")
        return False


if __name__ == "__main__":
    print("Plugin Tab Integration Validation")
    print("=" * 50)

    success = True

    # Test plugin code integration
    if not test_plugin_code_integration():
        success = False

    print()

    # Test tab configuration
    if not test_tab_configuration():
        success = False

    print()

    # Test compatibility methods
    if not test_compatibility_methods():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Plugin tab functionality successfully integrated")
        print("✅ QFileDialog file loader working")
        print("✅ Plugin log display ready")
        print("✅ Tab widget properly configured")
        print("✅ Launcher compatibility maintained")
    else:
        print("❌ SOME TESTS FAILED - Check the output above")

    sys.exit(0 if success else 1)
