"""
Test module for dark mode UI elements
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

# Skip these tests if Qt is not available
pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="PySide6 is not installed, UI tests will be skipped"
)


class TestDarkMode:
    """Tests for dark mode appearance and consistency"""

    def test_button_dark_mode(self, app, qtbot, style_guide):
        """Test that buttons use correct dark mode styling"""
        # Create button with dark mode styling
        button = QPushButton("Test Button")
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {style_guide["colors"]["control_bg"]};
                color: {style_guide["colors"]["primary_text"]};
                border: none;
                padding: {style_guide["spacing"]["control_padding"]}px;
                border-radius: {style_guide["border_radius"]["small"]}px;
            }}
            QPushButton:hover {{
                background-color: {style_guide["colors"]["primary_accent"]};
            }}
        """)

        # Show widget
        button.show()
        qtbot.addWidget(button)

        # Extract actual styles from widget
        actual_style = button.styleSheet()

        # Verify colors match dark mode spec
        assert style_guide["colors"]["control_bg"] in actual_style
        assert style_guide["colors"]["primary_text"] in actual_style
        assert (
            f"border-radius: {style_guide['border_radius']['small']}px" in actual_style
        )

    def test_text_field_dark_mode(self, app, qtbot, style_guide):
        """Test that text input fields use correct dark mode styling"""
        # Create text field with dark mode styling
        text_field = QLineEdit()
        text_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {style_guide["colors"]["tertiary_bg"]};
                color: {style_guide["colors"]["primary_text"]};
                border: 1px solid {style_guide["colors"]["control_bg"]};
                padding: {style_guide["spacing"]["control_padding"]}px;
                border-radius: {style_guide["border_radius"]["small"]}px;
            }}
        """)

        # Show widget
        text_field.show()
        qtbot.addWidget(text_field)

        # Extract actual styles from widget
        actual_style = text_field.styleSheet()

        # Verify colors match dark mode spec
        assert style_guide["colors"]["tertiary_bg"] in actual_style
        assert style_guide["colors"]["primary_text"] in actual_style

    def test_main_window_dark_mode(self, app, qtbot, style_guide):
        """Test that main window uses correct dark mode styling"""
        # Create window with dark mode styling
        window = QMainWindow()
        window.setWindowTitle("Dark Mode Test")

        central_widget = QWidget()
        central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {style_guide["colors"]["primary_bg"]};
                color: {style_guide["colors"]["primary_text"]};
            }}
        """)
        window.setCentralWidget(central_widget)

        # Add some content
        layout = QVBoxLayout(central_widget)

        label = QLabel("Dark Mode Test")
        label.setStyleSheet(f"color: {style_guide['colors']['primary_text']};")
        layout.addWidget(label)

        # Show window
        window.resize(400, 300)
        window.show()
        qtbot.addWidget(window)

        # Extract actual styles from widget
        actual_style = central_widget.styleSheet()

        # Verify colors match dark mode spec
        assert style_guide["colors"]["primary_bg"] in actual_style
        assert style_guide["colors"]["primary_text"] in actual_style

    def test_tab_widget_dark_mode(self, app, qtbot, style_guide):
        """Test that tab widgets use correct dark mode styling"""
        # Create tab widget with dark mode styling
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {style_guide["colors"]["tertiary_bg"]};
                background-color: {style_guide["colors"]["secondary_bg"]};
                padding: {style_guide["spacing"]["content_padding"]}px;
            }}

            QTabBar::tab {{
                background-color: {style_guide["colors"]["control_bg"]};
                color: {style_guide["colors"]["secondary_text"]};
                padding: {style_guide["spacing"]["control_padding"]}px;
                border-top-left-radius: {style_guide["border_radius"]["small"]}px;
                border-top-right-radius: {style_guide["border_radius"]["small"]}px;
            }}

            QTabBar::tab:selected {{
                background-color: {style_guide["colors"]["primary_accent"]};
                color: {style_guide["colors"]["primary_text"]};
            }}
        """)

        # Add tabs
        tab1 = QWidget()
        tab1.setStyleSheet(
            f"background-color: {style_guide['colors']['secondary_bg']};"
        )
        tabs.addTab(tab1, "Tab 1")

        tab2 = QWidget()
        tab2.setStyleSheet(
            f"background-color: {style_guide['colors']['secondary_bg']};"
        )
        tabs.addTab(tab2, "Tab 2")

        # Show widget
        tabs.resize(400, 300)
        tabs.show()
        qtbot.addWidget(tabs)

        # Extract actual styles from widget
        actual_style = tabs.styleSheet()

        # Verify colors match dark mode spec
        assert style_guide["colors"]["secondary_bg"] in actual_style
        assert style_guide["colors"]["control_bg"] in actual_style
        assert style_guide["colors"]["primary_accent"] in actual_style
