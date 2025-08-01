#!/usr/bin/env python3
"""
Individual Panel Tester
======================
Test each panel in isolation to debug blank panel issues
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Aetherra"))

def test_system_health_panel():
    """Test system health panel in isolation"""
    print("🔍 Testing System Health Panel...")

    try:
        from Aetherra.lyrixa.gui.panels.system_health_panel import SystemHealthPanel

        app = QApplication(sys.argv)

        # Create main window
        window = QMainWindow()
        window.setWindowTitle("System Health Panel Test")
        window.setGeometry(100, 100, 1000, 700)

        # Create and set the panel as central widget
        panel = SystemHealthPanel()
        window.setCentralWidget(panel)

        # Show window
        window.show()

        print("✅ System Health Panel created and displayed successfully!")

        # Run the application
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Error testing System Health Panel: {e}")
        import traceback
        traceback.print_exc()

def test_settings_personality_panel():
    """Test settings personality panel in isolation"""
    print("🔍 Testing Settings Personality Panel...")

    try:
        from Aetherra.lyrixa.gui.panels.settings_personality_panel import SettingsPersonalityPanel

        app = QApplication(sys.argv)

        # Create main window
        window = QMainWindow()
        window.setWindowTitle("Settings Personality Panel Test")
        window.setGeometry(100, 100, 1000, 700)

        # Create and set the panel as central widget
        panel = SettingsPersonalityPanel()
        window.setCentralWidget(panel)

        # Show window
        window.show()

        print("✅ Settings Personality Panel created and displayed successfully!")

        # Run the application
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Error testing Settings Personality Panel: {e}")
        import traceback
        traceback.print_exc()

def test_workflow_script_panel():
    """Test workflow script panel in isolation"""
    print("🔍 Testing Workflow Script Panel...")

    try:
        from Aetherra.lyrixa.gui.panels.workflow_script_panel import WorkflowScriptPanel

        app = QApplication(sys.argv)

        # Create main window
        window = QMainWindow()
        window.setWindowTitle("Workflow Script Panel Test")
        window.setGeometry(100, 100, 1000, 700)

        # Create and set the panel as central widget
        panel = WorkflowScriptPanel()
        window.setCentralWidget(panel)

        # Show window
        window.show()

        print("✅ Workflow Script Panel created and displayed successfully!")

        # Run the application
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Error testing Workflow Script Panel: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🧪 Individual Panel Tester")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_individual_panels.py system_health")
        print("  python test_individual_panels.py settings_personality")
        print("  python test_individual_panels.py workflow_script")
        return

    panel_name = sys.argv[1].lower()

    if panel_name == "system_health":
        test_system_health_panel()
    elif panel_name == "settings_personality":
        test_settings_personality_panel()
    elif panel_name == "workflow_script":
        test_workflow_script_panel()
    else:
        print(f"❌ Unknown panel: {panel_name}")
        print("Available panels: system_health, settings_personality, workflow_script")

if __name__ == "__main__":
    main()
