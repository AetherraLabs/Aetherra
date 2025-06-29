#!/usr/bin/env python3
"""
Qt Import Manager for Neuroplex
==============================

Centralized Qt import handling with PySide6/PyQt6 fallback support.
Exports all commonly used Qt widgets and components.
"""

import sys
from typing import Optional

# Global Qt state
QT_AVAILABLE = False
QT_BACKEND = None

# Try PySide6 first
try:
    from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QAction, QBrush, QColor, QFont, QIcon, QPalette, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QButtonGroup,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDialog,
        QDoubleSpinBox,
        QFileDialog,
        QFontDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpacerItem,
        QSpinBox,
        QSplitter,
        QStatusBar,
        QSystemTrayIcon,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QToolBar,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
    QT_BACKEND = "PySide6"
    print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI v2.0")

except ImportError:
    try:
        # Fallback to PyQt6
        from PyQt6.QtCore import QObject, Qt, QThread, QTimer
        from PyQt6.QtCore import pyqtSignal as Signal
        from PyQt6.QtGui import QAction, QBrush, QColor, QFont, QIcon, QPalette, QPixmap
        from PyQt6.QtWidgets import (
            QApplication,
            QButtonGroup,
            QCheckBox,
            QColorDialog,
            QComboBox,
            QDialog,
            QDoubleSpinBox,
            QFileDialog,
            QFontDialog,
            QFormLayout,
            QFrame,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QInputDialog,
            QLabel,
            QLineEdit,
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QMenu,
            QMenuBar,
            QMessageBox,
            QProgressBar,
            QPushButton,
            QRadioButton,
            QScrollArea,
            QSizePolicy,
            QSlider,
            QSpacerItem,
            QSpinBox,
            QSplitter,
            QStatusBar,
            QSystemTrayIcon,
            QTableWidget,
            QTableWidgetItem,
            QTabWidget,
            QTextEdit,
            QToolBar,
            QTreeWidget,
            QTreeWidgetItem,
            QVBoxLayout,
            QWidget,
        )

        QT_AVAILABLE = True
        QT_BACKEND = "PyQt6"
        print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI v2.0")

    except ImportError:
        print("❌ No Qt library available. Please install PySide6 or PyQt6.")
        print("   pip install PySide6")
        QT_AVAILABLE = False
        QT_BACKEND = None

        # Create dummy classes to prevent import errors
        class DummyQt:
            Horizontal = 1
            Vertical = 2
            UserRole = 256

            class Orientation:
                Horizontal = 1

            class ItemDataRole:
                UserRole = 256

        Qt = DummyQt()

        # Create dummy widget classes
        for widget_name in [
            "QApplication",
            "QMainWindow",
            "QWidget",
            "QDialog",
            "QMessageBox",
            "QVBoxLayout",
            "QHBoxLayout",
            "QGridLayout",
            "QFormLayout",
            "QLabel",
            "QPushButton",
            "QLineEdit",
            "QTextEdit",
            "QComboBox",
            "QListWidget",
            "QListWidgetItem",
            "QTreeWidget",
            "QTreeWidgetItem",
            "QTableWidget",
            "QTableWidgetItem",
            "QTabWidget",
            "QSplitter",
            "QProgressBar",
            "QSlider",
            "QSpinBox",
            "QDoubleSpinBox",
            "QCheckBox",
            "QRadioButton",
            "QButtonGroup",
            "QGroupBox",
            "QFrame",
            "QScrollArea",
            "QSizePolicy",
            "QSpacerItem",
            "QFileDialog",
            "QColorDialog",
            "QFontDialog",
            "QInputDialog",
            "QMenuBar",
            "QMenu",
            "QToolBar",
            "QStatusBar",
            "QSystemTrayIcon",
            "QTimer",
            "QThread",
            "QObject",
            "QIcon",
            "QFont",
            "QPixmap",
            "QPalette",
            "QAction",
            "QBrush",
            "QColor",
        ]:
            globals()[widget_name] = type(
                widget_name, (), {"__init__": lambda self, *args, **kwargs: None}
            )

        def dummy_signal(*args):
            def decorator(func):
                return func

            return decorator

        Signal = dummy_signal


def is_qt_available() -> bool:
    """Check if Qt is available."""
    return QT_AVAILABLE


def get_backend_name() -> Optional[str]:
    """Get the name of the active Qt backend."""
    return QT_BACKEND


def ensure_qt_app() -> Optional["QApplication"]:
    """Ensure QApplication instance exists."""
    if not QT_AVAILABLE:
        return None

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
