"""
Test configuration and fixtures for UI tests
"""

# Make sure the project root is in the path
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Try to import Qt for testing
try:
    from PySide6.QtWidgets import QApplication

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

# Skip all tests if Qt is not available
pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="PySide6 is not installed, UI tests will be skipped"
)


@pytest.fixture
def app(qtbot):
    """Create a QApplication instance for testing."""
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("NeuroCode Test")
    yield app


@pytest.fixture
def style_guide():
    """Return the standard style guide values for testing."""
    return {
        "colors": {
            "primary_bg": "#1e1e1e",
            "secondary_bg": "#252525",
            "tertiary_bg": "#333333",
            "control_bg": "#2d2d2d",
            "primary_text": "#ffffff",
            "secondary_text": "#cccccc",
            "disabled_text": "#888888",
            "primary_accent": "#0078d4",
            "hover_accent": "#106ebe",
            "success": "#107c10",
            "warning": "#d8a629",
            "error": "#d13438",
        },
        "spacing": {
            "default_margin": 8,
            "compact_margin": 4,
            "content_padding": 8,
            "control_padding": 8,
            "vertical_spacing": 8,
        },
        "border_radius": {
            "standard": 6,
            "small": 4,
            "flat": 0,
        },
        "typography": {
            "window_title_size": 16,
            "header_size": 14,
            "body_size": 13,
            "small_size": 12,
            "code_size": 13,
        },
    }
