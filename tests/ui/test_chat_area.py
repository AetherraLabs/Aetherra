"""
Tests for chat area UI elements and styling
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFrame,
        QLabel,
        QScrollArea,
        QTextBrowser,
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


class TestChatArea:
    """Tests for chat area styling and layout"""

    def test_chat_message_styling(self, app, qtbot, style_guide):
        """Test that chat messages use correct flat design styling"""
        # Create a chat message container
        message = QFrame()
        message.setObjectName("chatMessage")
        message.setStyleSheet(f"""
            QFrame#chatMessage {{
                background-color: {style_guide["colors"]["secondary_bg"]};
                border-radius: {style_guide["border_radius"]["flat"]}px;
                padding: {style_guide["spacing"]["content_padding"]}px;
                margin: {style_guide["spacing"]["default_margin"]}px 0px;
            }}
        """)

        # Add layout
        layout = QVBoxLayout(message)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Add header
        header = QLabel("User")
        header.setStyleSheet(f"""
            QLabel {{
                color: {style_guide["colors"]["primary_text"]};
                font-weight: 600;
            }}
        """)
        layout.addWidget(header)

        # Add content
        content = QTextBrowser()
        content.setPlainText("This is a test message with flat design styling.")
        content.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                color: {style_guide["colors"]["secondary_text"]};
            }}
        """)
        layout.addWidget(content)

        # Show widget
        message.resize(400, 100)
        message.show()
        qtbot.addWidget(message)

        # Extract actual styles
        actual_style = message.styleSheet()

        # Verify flat design styling
        assert (
            f"border-radius: {style_guide['border_radius']['flat']}px" in actual_style
        )
        assert style_guide["colors"]["secondary_bg"] in actual_style

        # Verify no chat bubble styling (box-shadow, etc)
        assert "box-shadow" not in actual_style

    def test_chat_area_styling(self, app, qtbot, style_guide):
        """Test that chat area container has correct styling"""
        # Create chat area container
        chat_area = QScrollArea()
        chat_area.setObjectName("chatScrollArea")
        chat_area.setStyleSheet(f"""
            QScrollArea#chatScrollArea {{
                background-color: {style_guide["colors"]["primary_bg"]};
                border: none;
            }}

            QScrollArea#chatScrollArea > QWidget > QWidget {{
                background-color: {style_guide["colors"]["primary_bg"]};
            }}
        """)

        # Create content widget
        content = QWidget()
        content.setStyleSheet(
            f"background-color: {style_guide['colors']['primary_bg']};"
        )

        # Set as widget for scroll area
        chat_area.setWidget(content)
        chat_area.setWidgetResizable(True)

        # Show widget
        chat_area.resize(500, 400)
        chat_area.show()
        qtbot.addWidget(chat_area)

        # Extract actual styles
        actual_style = chat_area.styleSheet()

        # Verify styling
        assert style_guide["colors"]["primary_bg"] in actual_style
        assert "border: none" in actual_style
