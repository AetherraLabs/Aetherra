#!/usr/bin/env python3
"""
Modern Theme for Neuroplex v2.0
===============================

Ultra-modern dark theme with consistent color palette and styling.
"""


class ModernTheme:
    """Ultra-modern dark theme for Neuroplex v2.0"""

    # Primary color palette
    BACKGROUND = "#0a0a0a"  # Pure dark
    SURFACE = "#1a1a1a"  # Dark surface
    SURFACE_VARIANT = "#2a2a2a"  # Lighter surface
    CARD = "#1e1e1e"  # Card background

    # Accent colors
    PRIMARY = "#3b82f6"  # Blue
    PRIMARY_VARIANT = "#1e40af"  # Dark blue
    SECONDARY = "#06d6a0"  # Emerald
    SECONDARY_VARIANT = "#059669"  # Dark emerald
    ACCENT = "#8b5cf6"  # Purple
    ACCENT_VARIANT = "#7c3aed"  # Dark purple

    # Text colors
    TEXT_PRIMARY = "#ffffff"  # White
    TEXT_SECONDARY = "#a3a3a3"  # Light gray
    TEXT_TERTIARY = "#6b7280"  # Gray
    TEXT_DISABLED = "#4b5563"  # Dark gray

    # Status colors
    SUCCESS = "#10b981"  # Green
    WARNING = "#f59e0b"  # Amber
    ERROR = "#ef4444"  # Red
    INFO = "#06b6d4"  # Cyan

    # Border and divider colors
    BORDER = "#374151"  # Gray border
    DIVIDER = "#4b5563"  # Divider

    @staticmethod
    def get_main_stylesheet() -> str:
        """Get the main application stylesheet"""
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {ModernTheme.BACKGROUND};
            color: {ModernTheme.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        }}

        /* General Widget Styling */
        QWidget {{
            background-color: {ModernTheme.BACKGROUND};
            color: {ModernTheme.TEXT_PRIMARY};
            font-size: 13px;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {ModernTheme.PRIMARY};
            color: {ModernTheme.TEXT_PRIMARY};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 14px;
        }}

        QPushButton:hover {{
            background-color: {ModernTheme.PRIMARY_VARIANT};
        }}

        QPushButton:pressed {{
            background-color: {ModernTheme.ACCENT};
        }}

        QPushButton:disabled {{
            background-color: {ModernTheme.SURFACE_VARIANT};
            color: {ModernTheme.TEXT_DISABLED};
        }}

        /* Secondary Buttons */
        QPushButton[buttonRole="secondary"] {{
            background-color: {ModernTheme.SURFACE_VARIANT};
            color: {ModernTheme.TEXT_PRIMARY};
            border: 1px solid {ModernTheme.BORDER};
        }}

        QPushButton[buttonRole="secondary"]:hover {{
            background-color: {ModernTheme.CARD};
            border-color: {ModernTheme.PRIMARY};
        }}

        /* Text Inputs */
        QTextEdit, QLineEdit {{
            background-color: {ModernTheme.SURFACE};
            color: {ModernTheme.TEXT_PRIMARY};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            selection-background-color: {ModernTheme.PRIMARY};
        }}

        QTextEdit:focus, QLineEdit:focus {{
            border-color: {ModernTheme.PRIMARY};
            background-color: {ModernTheme.CARD};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 8px;
            background-color: {ModernTheme.SURFACE};
            margin-top: -1px;
        }}

        QTabBar::tab {{
            background-color: {ModernTheme.SURFACE_VARIANT};
            color: {ModernTheme.TEXT_SECONDARY};
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
        }}

        QTabBar::tab:selected {{
            background-color: {ModernTheme.PRIMARY};
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {ModernTheme.CARD};
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        /* Lists and Trees */
        QListWidget, QTreeWidget {{
            background-color: {ModernTheme.SURFACE};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 4px;
            alternate-background-color: {ModernTheme.CARD};
        }}

        QListWidget::item, QTreeWidget::item {{
            padding: 8px;
            border-radius: 4px;
            margin: 1px;
        }}

        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {ModernTheme.PRIMARY};
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {ModernTheme.CARD};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {ModernTheme.SURFACE};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {ModernTheme.BORDER};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {ModernTheme.TEXT_TERTIARY};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        /* Labels */
        QLabel {{
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QLabel[role="heading"] {{
            font-size: 18px;
            font-weight: bold;
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QLabel[role="subheading"] {{
            font-size: 14px;
            font-weight: 600;
            color: {ModernTheme.TEXT_SECONDARY};
        }}

        /* Group Boxes */
        QGroupBox {{
            background-color: {ModernTheme.CARD};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 10px;
            font-weight: 600;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        /* Progress Bars */
        QProgressBar {{
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            background-color: {ModernTheme.SURFACE};
            text-align: center;
            font-weight: 600;
        }}

        QProgressBar::chunk {{
            background-color: {ModernTheme.PRIMARY};
            border-radius: 5px;
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {ModernTheme.SURFACE};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 100px;
        }}

        QComboBox:hover {{
            border-color: {ModernTheme.PRIMARY};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {ModernTheme.TEXT_SECONDARY};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {ModernTheme.SURFACE};
            border-bottom: 1px solid {ModernTheme.BORDER};
            padding: 4px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:selected {{
            background-color: {ModernTheme.PRIMARY};
        }}

        /* Menus */
        QMenu {{
            background-color: {ModernTheme.CARD};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 20px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {ModernTheme.PRIMARY};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {ModernTheme.SURFACE};
            border-top: 1px solid {ModernTheme.BORDER};
        }}
        """

    @staticmethod
    def get_card_style() -> str:
        """Get card styling for panels"""
        return f"""
        QWidget {{
            background-color: {ModernTheme.CARD};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 6px;
        }}

        QLabel {{
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 1px;
            margin: 1px;
        }}

        QLabel[role="heading"] {{
            font-size: 14px;
            font-weight: bold;
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 4px;
            margin-bottom: 4px;
        }}

        QLineEdit, QComboBox {{
            min-height: 20px;
            padding: 2px 6px;
            font-size: 12px;
        }}

        QPushButton {{
            min-height: 24px;
            padding: 4px 8px;
            font-size: 11px;
        }}
        """

    @staticmethod
    def get_accent_button_style() -> str:
        """Get accent button styling"""
        return f"""
        QPushButton {{
            background-color: {ModernTheme.SECONDARY};
            color: {ModernTheme.TEXT_PRIMARY};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {ModernTheme.SECONDARY_VARIANT};
        }}
        """
