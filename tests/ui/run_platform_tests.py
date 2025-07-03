"""
Cross-Platform Test Runner
=========================

This script runs the cross-platform tests and generates comparison reports.
It should be run on each target platform to collect reference images and results.
"""

import argparse
import os
import platform
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("PySide6 not available - cross-platform testing limited")

from tests.ui.cross_platform_tester import CrossPlatformTester, PlatformInfo


class ComponentTestWindow(QMainWindow):
    """
    Test window with standard UI components for cross-platform testing.
    """

    def __init__(self):
        """Initialize the test window."""
        super().__init__()

        self.setWindowTitle("NeuroCode UI Cross-Platform Test")
        self.resize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Add header
        header = QLabel("UI Component Test")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(header)

        # Add standard button
        standard_button = QPushButton("Standard Button")
        standard_button.setObjectName("standard_button")
        layout.addWidget(standard_button)

        # Add primary button
        primary_button = QPushButton("Primary Button")
        primary_button.setObjectName("primary_button")
        primary_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        layout.addWidget(primary_button)

        # Add label
        test_label = QLabel("This is a test label for cross-platform testing")
        test_label.setObjectName("test_label")
        layout.addWidget(test_label)

        # Add dark panel
        dark_panel = QWidget()
        dark_panel.setObjectName("dark_panel")
        dark_panel.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-radius: 6px;
                padding: 16px;
                margin: 8px 0;
            }
        """)
        dark_panel_layout = QVBoxLayout(dark_panel)
        dark_panel_label = QLabel("Dark Panel Content")
        dark_panel_layout.addWidget(dark_panel_label)
        layout.addWidget(dark_panel)

        # Add spacer
        layout.addStretch()

        # Apply dark theme to entire window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)


def run_cross_platform_tests(output_dir: str = None):
    """
    Run cross-platform UI tests.

    Args:
        output_dir: Directory to save test results
    """
    if not QT_AVAILABLE:
        print("PySide6 not available - cannot run cross-platform tests")
        return

    print(f"Running tests on {platform.system()} {platform.release()}")

    # Create QApplication if needed
    app = QApplication.instance() or QApplication([])

    # Create tester
    tester = CrossPlatformTester(output_dir)

    try:
        # Create test window
        test_window = ComponentTestWindow()

        # Show window
        test_window.show()
        app.processEvents()
        time.sleep(0.5)  # Give time for window to render properly

        # Test results
        results = []

        # Test whole window
        window_result = tester.test_component(test_window, "main_window")
        results.append(window_result)

        # Test individual components
        standard_button = test_window.findChild(QPushButton, "standard_button")
        if standard_button:
            button_result = tester.test_component(standard_button, "standard_button")
            results.append(button_result)

        primary_button = test_window.findChild(QPushButton, "primary_button")
        if primary_button:
            primary_result = tester.test_component(primary_button, "primary_button")
            results.append(primary_result)

        test_label = test_window.findChild(QLabel, "test_label")
        if test_label:
            label_result = tester.test_component(test_label, "test_label")
            results.append(label_result)

        dark_panel = test_window.findChild(QWidget, "dark_panel")
        if dark_panel:
            panel_result = tester.test_component(dark_panel, "dark_panel")
            results.append(panel_result)

        # Generate report
        report = tester.generate_report(results)
        print("\nTest Results:")
        print("-------------")
        print(report)

        # Save report
        platform_info = PlatformInfo.get_platform_summary()
        report_path = tester.platform_dir / f"report_{platform_info['os_name']}.txt"
        with open(report_path, "w") as f:
            f.write(report)

        print(f"Report saved to {report_path}")

        # Clean up
        test_window.close()

    except Exception as e:
        print(f"Error running cross-platform tests: {e}")
    finally:
        app.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run cross-platform UI tests")
    parser.add_argument("--output", help="Directory to save test results")
    args = parser.parse_args()

    run_cross_platform_tests(args.output)
