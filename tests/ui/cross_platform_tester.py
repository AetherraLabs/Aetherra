"""
Cross-Platform UI Testing Module
===============================

This module provides utilities for testing the UI across different platforms
to ensure consistency and proper appearance regardless of operating system.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import QSize, QSysInfo, Qt
    from PySide6.QtGui import QImage, QPixmap, QScreen
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("PySide6 not available - cross-platform testing limited")


class PlatformInfo:
    """
    Provides information about the current platform.
    """

    @staticmethod
    def get_os_name() -> str:
        """Get the name of the operating system."""
        return platform.system()

    @staticmethod
    def get_os_version() -> str:
        """Get the version of the operating system."""
        if platform.system() == "Windows":
            return platform.win32_ver()[0]
        elif platform.system() == "Darwin":  # macOS
            return platform.mac_ver()[0]
        else:  # Linux
            return platform.release()

    @staticmethod
    def get_qt_platform() -> str:
        """Get the Qt platform name."""
        if not QT_AVAILABLE:
            return "Unknown (Qt not available)"

        return QSysInfo.productType()

    @staticmethod
    def get_screen_info() -> Dict[str, Any]:
        """Get information about the screens."""
        if not QT_AVAILABLE:
            return {"error": "Qt not available"}

        app = QApplication.instance() or QApplication([])
        screens = app.screens()

        screen_info = []
        for i, screen in enumerate(screens):
            geometry = screen.geometry()
            screen_info.append(
                {
                    "index": i,
                    "name": screen.name(),
                    "width": geometry.width(),
                    "height": geometry.height(),
                    "dpi": screen.physicalDotsPerInch(),
                    "scale_factor": screen.devicePixelRatio(),
                }
            )

        return {"primary_screen": app.primaryScreen().name(), "screens": screen_info}

    @staticmethod
    def get_platform_summary() -> Dict[str, Any]:
        """Get a summary of the platform information."""
        return {
            "os_name": PlatformInfo.get_os_name(),
            "os_version": PlatformInfo.get_os_version(),
            "python_version": platform.python_version(),
            "qt_platform": PlatformInfo.get_qt_platform(),
            "screen_info": PlatformInfo.get_screen_info(),
        }


class CrossPlatformTester:
    """
    Tests UI components across different platforms.
    """

    def __init__(self, test_data_dir: Optional[str] = None):
        """
        Initialize the cross-platform tester.

        Args:
            test_data_dir: Directory to store test data and screenshots
        """
        self.platform_info = PlatformInfo.get_platform_summary()

        # Set default test data directory if none provided
        if test_data_dir is None:
            self.test_data_dir = Path(project_root) / "tests" / "ui" / "platform_data"
        else:
            self.test_data_dir = Path(test_data_dir)

        # Create directory if it doesn't exist
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

        # Platform-specific directories
        self.platform_dir = self.test_data_dir / self.platform_info["os_name"]
        self.platform_dir.mkdir(exist_ok=True)

    def capture_widget(self, widget: QWidget, name: str) -> Optional[str]:
        """
        Capture a screenshot of a widget.

        Args:
            widget: The widget to capture
            name: Name for the screenshot

        Returns:
            Path to the saved screenshot or None if failed
        """
        if not QT_AVAILABLE or widget is None:
            return None

        # Make sure widget is visible
        if not widget.isVisible():
            return None

        # Create a QPixmap from the widget
        pixmap = widget.grab()

        # Create filename based on platform and widget name
        filename = f"{name}_{self.platform_info['os_name']}_{self.platform_info['os_version']}.png"
        filepath = self.platform_dir / filename

        # Save the pixmap
        if pixmap.save(str(filepath)):
            return str(filepath)

        return None

    def compare_with_reference(
        self, current_image_path: str, reference_platform: str = "Windows"
    ) -> Dict[str, Any]:
        """
        Compare a screenshot with a reference from another platform.

        Args:
            current_image_path: Path to the current screenshot
            reference_platform: Platform to compare with

        Returns:
            Dictionary with comparison results
        """
        if not QT_AVAILABLE:
            return {"error": "Qt not available"}

        # Extract name from current path
        current_path = Path(current_image_path)
        name_parts = current_path.stem.split("_")
        widget_name = name_parts[0]

        # Find reference image
        reference_dir = self.test_data_dir / reference_platform

        if not reference_dir.exists():
            return {
                "error": f"Reference platform directory not found: {reference_platform}"
            }

        # Look for matching widget name in reference directory
        reference_files = list(reference_dir.glob(f"{widget_name}_*.png"))

        if not reference_files:
            return {"error": f"No reference image found for {widget_name}"}

        reference_path = reference_files[0]

        # Load images
        current_image = QImage(current_image_path)
        reference_image = QImage(str(reference_path))

        if current_image.isNull() or reference_image.isNull():
            return {"error": "Failed to load images"}

        # Resize reference to match current if needed
        if current_image.size() != reference_image.size():
            reference_image = reference_image.scaled(
                current_image.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        # Compare images pixel by pixel (simplified)
        # In a real implementation, you'd use a more sophisticated image comparison
        width = current_image.width()
        height = current_image.height()

        different_pixels = 0
        max_pixels = width * height

        for y in range(height):
            for x in range(width):
                if current_image.pixel(x, y) != reference_image.pixel(x, y):
                    different_pixels += 1

        difference_ratio = different_pixels / max_pixels if max_pixels > 0 else 1.0

        return {
            "current_image": current_image_path,
            "reference_image": str(reference_path),
            "difference_ratio": difference_ratio,
            "different_pixels": different_pixels,
            "total_pixels": max_pixels,
            "identical": difference_ratio < 0.01,  # Less than 1% difference
        }

    def test_component(
        self, widget: QWidget, name: str, reference_platform: str = "Windows"
    ) -> Dict[str, Any]:
        """
        Test a component across platforms.

        Args:
            widget: The widget to test
            name: Name for the test
            reference_platform: Platform to compare with

        Returns:
            Dictionary with test results
        """
        if not QT_AVAILABLE or widget is None:
            return {"error": "Qt not available or widget is None"}

        # Capture the widget
        image_path = self.capture_widget(widget, name)

        if image_path is None:
            return {"error": "Failed to capture widget"}

        # Compare with reference if not on the reference platform
        if self.platform_info["os_name"] != reference_platform:
            comparison_result = self.compare_with_reference(
                image_path, reference_platform
            )
            return {
                "platform": self.platform_info["os_name"],
                "widget": name,
                "screenshot": image_path,
                "comparison": comparison_result,
            }
        else:
            # This is the reference platform, no comparison needed
            return {
                "platform": self.platform_info["os_name"],
                "widget": name,
                "screenshot": image_path,
                "is_reference": True,
            }

    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a report from test results.

        Args:
            results: List of test results

        Returns:
            Formatted report string
        """
        report = "Cross-Platform UI Test Report\n"
        report += "============================\n\n"

        report += f"Platform: {self.platform_info['os_name']} {self.platform_info['os_version']}\n"
        report += f"Python: {self.platform_info['python_version']}\n"
        report += f"Qt Platform: {self.platform_info['qt_platform']}\n\n"

        report += "Test Results:\n"
        report += "-------------\n\n"

        for result in results:
            report += f"Widget: {result.get('widget', 'Unknown')}\n"
            report += f"Platform: {result.get('platform', 'Unknown')}\n"
            report += f"Screenshot: {result.get('screenshot', 'None')}\n"

            if result.get("is_reference", False):
                report += "Status: Reference Image\n"
            else:
                comparison = result.get("comparison", {})
                if "error" in comparison:
                    report += f"Error: {comparison['error']}\n"
                else:
                    identical = comparison.get("identical", False)
                    diff_ratio = comparison.get("difference_ratio", 1.0)
                    status = "PASS" if identical else "FAIL"
                    report += f"Status: {status} (Difference: {diff_ratio:.2%})\n"

            report += "\n"

        return report


def test_platform_compatibility():
    """Run platform compatibility tests for the NeuroCode UI."""
    if not QT_AVAILABLE:
        print("PySide6 not available - cannot run platform compatibility tests")
        return

    # Create QApplication if needed
    app = QApplication.instance() or QApplication([])

    # Create tester
    tester = CrossPlatformTester()

    # Get platform info
    platform_info = PlatformInfo.get_platform_summary()
    print(f"Testing on {platform_info['os_name']} {platform_info['os_version']}")

    # Test results will be collected here
    results = []

    # Import UI components dynamically to avoid import errors
    try:
        from src.aethercode.ui.enhancement_controller import ui_enhancer

        # Create test window
        window = QMainWindow()
        window.setWindowTitle("Cross-Platform Test")
        window.resize(800, 600)

        # Add some test widgets here
        # ...

        # Apply UI enhancements
        ui_enhancer.enhance_window(window)

        # Show window briefly for screenshot
        window.show()
        app.processEvents()

        # Test the window
        result = tester.test_component(window, "main_window")
        results.append(result)

        # Test other components here
        # ...

        # Generate report
        report = tester.generate_report(results)
        print(report)

        # Save report
        report_path = tester.platform_dir / f"report_{platform_info['os_name']}.txt"
        with open(report_path, "w") as f:
            f.write(report)

        print(f"Report saved to {report_path}")

    except Exception as e:
        print(f"Error testing platform compatibility: {e}")
    finally:
        # Clean up
        app.quit()


if __name__ == "__main__":
    test_platform_compatibility()
