#!/usr/bin/env python3
"""
Modern Card Component for Neuroplex
===================================

Base card widget for organizing content with modern styling.
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
ui_dir = current_dir.parent
project_root = ui_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ui_dir))

try:
    from ui.components.theme import ModernTheme
    from ui.components.utils.qt_imports import get_qt_widgets

    QtWidgets = get_qt_widgets()
except ImportError:
    # Fallback for direct Qt import
    try:
        from PySide6 import QtWidgets
    except ImportError:
        from PyQt6 import QtWidgets

    class ModernTheme:
        @staticmethod
        def get_card_style():
            return ""


class ModernCard(QtWidgets.QWidget):
    """A modern card widget for organizing content"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(ModernTheme.get_card_style())

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)  # Reduced margins for more space
        layout.setSpacing(6)  # Reduced spacing

        if title:
            title_label = QtWidgets.QLabel(title)
            title_label.setProperty("role", "heading")
            title_label.setWordWrap(True)  # Allow text wrapping
            title_label.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum
            )
            title_label.setMaximumHeight(30)  # Limit title height
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget):
        """Add a widget to the card"""
        if widget:
            self.content_layout.addWidget(widget)
