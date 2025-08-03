#!/usr/bin/env python3
"""
Panel Integration Diagnostic
===========================
Test panels specifically in the main GUI context to find integration issues
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QTabWidget, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Aetherra"))

def test_main_gui_integration():
    """Test panels in the exact same context as main GUI"""
    print("🔍 Testing Main GUI Integration...")

    app = QApplication(sys.argv)

    # Create main window exactly like AetherraMainWindow
    window = QMainWindow()
    window.setWindowTitle("Aetherra Panel Integration Test")
    window.setGeometry(100, 100, 1600, 1000)

    # Setup central widget and layout exactly like main GUI
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)

    # Create tab widget exactly like main GUI
    panel_tabs = QTabWidget()
    panel_tabs.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2a2a2a;
            border-radius: 4px;
        }
        QTabWidget::tab-bar {
            alignment: left;
        }
        QTabBar::tab {
            background-color: #3a3a3a;
            color: #d4d4d4;
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 14px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background-color: #00ff88;
            color: #1e1e1e;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background-color: #4a4a4a;
        }
    """)
    main_layout.addWidget(panel_tabs)

    # Test each problematic panel
    test_panels = [
        ("system_health_panel", "SystemHealthPanel", "📋 System Health"),
        ("settings_personality_panel", "SettingsPersonalityPanel", "📋 Settings Personality"),
        ("workflow_script_panel", "WorkflowScriptPanel", "🔄 Workflow & Scripts")
    ]

    for panel_name, class_name, tab_name in test_panels:
        try:
            print(f"\n🧪 Testing {panel_name}...")

            # Import the panel exactly like main GUI does
            module_path = f"Aetherra.lyrixa.gui.panels.{panel_name}"
            module = __import__(module_path, fromlist=[class_name])
            panel_class = getattr(module, class_name)

            # Create panel instance
            print(f"  [DISC] Creating {class_name} instance...")
            panel_instance = panel_class()

            # Check panel properties
            print(f"  🔍 Panel size: {panel_instance.size()}")
            print(f"  🔍 Panel visible: {panel_instance.isVisible()}")
            print(f"  🔍 Panel enabled: {panel_instance.isEnabled()}")

            # Add to tabs exactly like main GUI
            print(f"  📋 Adding to tab widget as '{tab_name}'...")
            panel_tabs.addTab(panel_instance, tab_name)

            # Force visibility and update
            panel_instance.show()
            panel_instance.update()

            print(f"  ✅ Successfully added {panel_name} to tabs")

        except Exception as e:
            print(f"  [ERROR] Error with {panel_name}: {e}")
            import traceback
            traceback.print_exc()

    # Add a simple test tab for comparison
    test_widget = QLabel("🧪 TEST TAB - This should be visible!")
    test_widget.setStyleSheet("""
        QLabel {
            background-color: #1a1a1a;
            color: #00ff88;
            font-size: 24px;
            font-weight: bold;
            padding: 50px;
            border: 3px solid #00ff88;
        }
    """)
    test_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    panel_tabs.addTab(test_widget, "🧪 Test")

    print(f"\n📊 Total tabs: {panel_tabs.count()}")

    # Set the first tab as current and show window
    if panel_tabs.count() > 0:
        panel_tabs.setCurrentIndex(0)

    window.show()

    print("✅ Main GUI Integration Test window displayed!")
    print("🔍 Check if all panels are visible in their tabs...")

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    test_main_gui_integration()
