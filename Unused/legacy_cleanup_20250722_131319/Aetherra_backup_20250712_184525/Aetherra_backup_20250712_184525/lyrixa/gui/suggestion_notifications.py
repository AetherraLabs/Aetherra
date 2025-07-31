# type: ignore
"""
Suggestion Notification System for Lyrixa AI Assistant

Provides non-intrusive, real-time notification system for:
- Proactive suggestions from the anticipation engine
- User feedback collection
- Suggestion history management
- Customizable notification settings
"""

import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check Qt availability first
PYSIDE6_AVAILABLE = False

try:
    from PySide6.QtCore import (
        QEasingCurve,
        QPropertyAnimation,
        QRect,
        Qt,
        QTimer,
    )
    from PySide6.QtCore import (
        Signal as QtSignal,
    )
    from PySide6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMenu,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QSplitter,
        QSystemTrayIcon,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    logger.warning("PySide6 not available. Using mock classes.")

# Mock classes for when PySide6 is not available
if not PYSIDE6_AVAILABLE:

    class MockWidget:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def setLayout(self, layout):
            pass

        def setMaximumHeight(self, height):
            pass

        def setMinimumHeight(self, height):
            pass

        def setStyleSheet(self, style):
            pass

        def setFont(self, font):
            pass

        def setAlignment(self, alignment):
            pass

        def setText(self, text):
            pass

        def setWordWrap(self, wrap):
            pass

        def setMaximumWidth(self, width):
            pass

        def setChecked(self, checked):
            pass

        def isChecked(self):
            return False

        def setRange(self, min_val, max_val):
            pass

        def setValue(self, value):
            pass

        def value(self):
            return 0

        def setSpecialValueText(self, text):
            pass

        def addWidget(self, widget, *args, **kwargs):
            pass

        def addLayout(self, layout, *args, **kwargs):
            pass

        def addStretch(self, stretch=0):
            pass

        def setContentsMargins(self, left, top, right, bottom):
            pass

        def setSpacing(self, spacing):
            pass

        def insertWidget(self, index, widget):
            pass

        def setWidgetResizable(self, resizable):
            pass

        def setHorizontalScrollBarPolicy(self, policy):
            pass

        def setVerticalScrollBarPolicy(self, policy):
            pass

        def setWidget(self, widget):
            pass

        def addItem(self, item):
            pass

        def takeItem(self, row):
            pass

        def count(self):
            return 0

        def itemAt(self, index):
            return self

        def widget(self):
            return self

        def setParent(self, parent):
            pass

        def setVisible(self, visible):
            pass

        def setReadOnly(self, readonly):
            pass

        def setHtml(self, html):
            pass

        def currentItemChanged(self):
            return MockSignal()

        def clicked(self):
            return MockSignal()

        def addAction(self, action, *args):
            pass

        def addSeparator(self):
            pass

        def setContextMenu(self, menu):
            pass

        def setIcon(self, icon):
            pass

        def setToolTip(self, tooltip):
            pass

        def showMessage(self, title, message, icon, duration):
            pass

        def show(self):
            pass

        def hide(self):
            pass

        def resize(self, width, height):
            pass

        def exec(self):
            return 0

        def quit(self):
            pass

        def data(self, role):
            return None

        def setData(self, role, value):
            pass

        def addPixmap(self, pixmap):
            pass

        def fill(self, color):
            pass

        def setStretchFactor(self, index, factor):
            pass

        def addTab(self, widget, title):
            pass

        def connect(self, slot):
            pass

        def disconnect(self, slot=None):
            pass

        def emit(self, *args):
            pass

        def singleShot(self, interval, callback):
            pass

        def isSystemTrayAvailable(self):
            return False

        # Context manager support
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockSignal:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, slot):
            pass

        def disconnect(self, slot=None):
            pass

        def emit(self, *args):
            pass

    class MockFont:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def setPointSize(self, size):
            pass

        def setBold(self, bold):
            pass

        Bold = 75

    class MockColor:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    class MockIcon:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def addPixmap(self, pixmap):
            pass

    class MockPixmap:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def fill(self, color):
            pass

    class MockQt:  # type: ignore
        AlignCenter = 0x84
        ScrollBarAlwaysOff = 0
        ScrollBarAsNeeded = 1
        Horizontal = 1
        UserRole = 256
        Information = 1

    class MockMenu:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def addAction(self, text, callback=None):
            pass

        def addSeparator(self):
            pass

    class MockListWidgetItem:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def setData(self, role, value):
            pass

        def data(self, role):
            return None

    class MockTimer:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def singleShot(interval, callback):
            pass

    # Assign mock classes
    QWidget = MockWidget
    QLabel = MockWidget
    QTextEdit = MockWidget
    QPushButton = MockWidget
    QCheckBox = MockWidget
    QSpinBox = MockWidget
    QListWidget = MockWidget
    QScrollArea = MockWidget
    QGroupBox = MockWidget
    QFrame = MockWidget
    QApplication = MockWidget
    QSystemTrayIcon = MockWidget
    QSplitter = MockWidget
    QVBoxLayout = MockWidget
    QHBoxLayout = MockWidget
    QtSignal = MockSignal
    QFont = MockFont
    QColor = MockColor
    QIcon = MockIcon
    QPixmap = MockPixmap
    Qt = MockQt
    QMenu = MockMenu
    QListWidgetItem = MockListWidgetItem
    QTimer = MockTimer

    # Unused imports that would be available in real PySide6
    QEasingCurve = MockWidget
    QPropertyAnimation = MockWidget
    QRect = MockWidget
    QLinearGradient = MockWidget
    QPainter = MockWidget
    QMessageBox = MockWidget


class SuggestionType(Enum):
    """Types of suggestions that can be displayed."""

    PRODUCTIVITY = "productivity"
    LEARNING = "learning"
    WELLBEING = "wellbeing"
    WORKFLOW = "workflow"
    SYSTEM = "system"


class SuggestionPriority(Enum):
    """Priority levels for suggestions."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Suggestion:
    """Data class representing a suggestion."""

    id: str
    title: str
    content: str
    suggestion_type: SuggestionType
    priority: SuggestionPriority
    confidence: float
    timestamp: datetime
    actions: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    accepted: Optional[bool] = None
    feedback: Optional[str] = None


class SuggestionWidget(QWidget):  # type: ignore
    """Individual suggestion display widget."""

    def __init__(self, suggestion: Suggestion, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)  # type: ignore
        self.suggestion = suggestion
        self.setMaximumHeight(120)  # type: ignore
        self.setMinimumHeight(80)  # type: ignore

        # Signals
        self.suggestion_accepted = QtSignal(str)  # type: ignore
        self.suggestion_rejected = QtSignal(str)  # type: ignore
        self.suggestion_dismissed = QtSignal(str)  # type: ignore
        self.feedback_provided = QtSignal(str, str)  # type: ignore

        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Initialize the suggestion widget UI."""
        layout = QVBoxLayout()  # type: ignore
        layout.setContentsMargins(10, 8, 10, 8)  # type: ignore
        layout.setSpacing(5)  # type: ignore

        # Header with title and priority
        header_layout = QHBoxLayout()  # type: ignore

        # Priority indicator
        priority_color = self.get_priority_color()
        priority_label = QLabel("●")  # type: ignore
        priority_label.setStyleSheet(  # type: ignore
            f"color: {priority_color}; font-size: 16px; font-weight: bold;"
        )
        header_layout.addWidget(priority_label)  # type: ignore

        # Title
        title_label = QLabel(self.suggestion.title)  # type: ignore
        title_label.setFont(QFont("Arial", 10, QFont.Bold))  # type: ignore
        title_label.setWordWrap(True)  # type: ignore
        header_layout.addWidget(title_label)  # type: ignore

        # Confidence score
        confidence_label = QLabel(f"{self.suggestion.confidence:.0%}")  # type: ignore
        confidence_label.setFont(QFont("Arial", 8))  # type: ignore
        confidence_label.setStyleSheet("color: #666; font-weight: bold;")  # type: ignore
        header_layout.addWidget(confidence_label)  # type: ignore

        header_layout.addStretch()  # type: ignore
        layout.addLayout(header_layout)  # type: ignore

        # Content
        content_label = QLabel(self.suggestion.content)  # type: ignore
        content_label.setFont(QFont("Arial", 9))  # type: ignore
        content_label.setWordWrap(True)  # type: ignore
        content_label.setMaximumHeight(30)  # type: ignore
        layout.addWidget(content_label)  # type: ignore

        # Action buttons
        button_layout = QHBoxLayout()  # type: ignore
        button_layout.setSpacing(5)  # type: ignore

        # Accept button
        accept_btn = QPushButton("✓ Accept")  # type: ignore
        accept_btn.setMaximumWidth(80)  # type: ignore
        accept_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)  # type: ignore
        accept_btn.clicked.connect(self.accept_suggestion)  # type: ignore
        button_layout.addWidget(accept_btn)  # type: ignore

        # Reject button
        reject_btn = QPushButton("✗ Reject")  # type: ignore
        reject_btn.setMaximumWidth(80)  # type: ignore
        reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)  # type: ignore
        reject_btn.clicked.connect(self.reject_suggestion)  # type: ignore
        button_layout.addWidget(reject_btn)  # type: ignore

        # Dismiss button
        dismiss_btn = QPushButton("— Later")  # type: ignore
        dismiss_btn.setMaximumWidth(80)  # type: ignore
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)  # type: ignore
        dismiss_btn.clicked.connect(self.dismiss_suggestion)  # type: ignore
        button_layout.addWidget(dismiss_btn)  # type: ignore

        button_layout.addStretch()  # type: ignore

        # Timestamp
        time_label = QLabel(self.suggestion.timestamp.strftime("%H:%M"))  # type: ignore
        time_label.setFont(QFont("Arial", 7))  # type: ignore
        time_label.setStyleSheet("color: #999;")  # type: ignore
        button_layout.addWidget(time_label)  # type: ignore

        layout.addLayout(button_layout)  # type: ignore
        self.setLayout(layout)  # type: ignore

    def get_priority_color(self) -> str:
        """Get color for priority indicator."""
        colors = {
            SuggestionPriority.LOW: "#4CAF50",
            SuggestionPriority.MEDIUM: "#FF9800",
            SuggestionPriority.HIGH: "#FF5722",
            SuggestionPriority.URGENT: "#F44336",
        }
        return colors.get(self.suggestion.priority, "#9E9E9E")  # type: ignore

    def apply_styling(self):
        """Apply visual styling to the widget."""
        self.setStyleSheet("""
            SuggestionWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin: 2px;
            }
            SuggestionWidget:hover {
                background-color: #e9ecef;
                border-color: #6c757d;
            }
        """)  # type: ignore

    def accept_suggestion(self):
        """Handle suggestion acceptance."""
        self.suggestion.accepted = True
        if hasattr(self, "suggestion_accepted") and self.suggestion_accepted:
            self.suggestion_accepted.emit(self.suggestion.id)  # type: ignore
        logger.info(f"Suggestion {self.suggestion.id} accepted")

    def reject_suggestion(self):
        """Handle suggestion rejection."""
        self.suggestion.accepted = False
        if hasattr(self, "suggestion_rejected") and self.suggestion_rejected:
            self.suggestion_rejected.emit(self.suggestion.id)  # type: ignore
        logger.info(f"Suggestion {self.suggestion.id} rejected")

    def dismiss_suggestion(self):
        """Handle suggestion dismissal."""
        if hasattr(self, "suggestion_dismissed") and self.suggestion_dismissed:
            self.suggestion_dismissed.emit(self.suggestion.id)  # type: ignore
        logger.info(f"Suggestion {self.suggestion.id} dismissed")


class SuggestionPanel(QWidget):  # type: ignore
    """Main panel for displaying suggestions."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)  # type: ignore
        self.suggestions = {}
        self.max_suggestions = 5

        self.init_ui()

    def init_ui(self):
        """Initialize the suggestion panel UI."""
        layout = QVBoxLayout()  # type: ignore
        layout.setContentsMargins(5, 5, 5, 5)  # type: ignore
        layout.setSpacing(3)  # type: ignore

        # Header
        header_label = QLabel("💡 Suggestions")  # type: ignore
        header_label.setFont(QFont("Arial", 12, QFont.Bold))  # type: ignore
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")  # type: ignore
        layout.addWidget(header_label)  # type: ignore

        # Scroll area for suggestions
        scroll_area = QScrollArea()  # type: ignore
        scroll_area.setWidgetResizable(True)  # type: ignore
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # type: ignore
        scroll_area.setMaximumHeight(400)  # type: ignore

        self.suggestions_widget = QWidget()  # type: ignore
        self.suggestions_layout = QVBoxLayout(self.suggestions_widget)  # type: ignore
        self.suggestions_layout.setSpacing(2)  # type: ignore
        self.suggestions_layout.addStretch()  # type: ignore

        scroll_area.setWidget(self.suggestions_widget)  # type: ignore
        layout.addWidget(scroll_area)  # type: ignore

        # Empty state
        self.empty_label = QLabel("No suggestions available")  # type: ignore
        self.empty_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.empty_label.setStyleSheet(
            "color: #6c757d; font-style: italic; margin: 20px;"
        )  # type: ignore
        layout.addWidget(self.empty_label)  # type: ignore

        self.setLayout(layout)  # type: ignore
        self.update_display()

    def add_suggestion(self, suggestion: Suggestion):
        """Add a new suggestion to the panel."""
        if len(self.suggestions) >= self.max_suggestions:
            # Remove oldest suggestion
            oldest_id = min(
                self.suggestions.keys(), key=lambda k: self.suggestions[k].timestamp
            )
            self.remove_suggestion(oldest_id)

        # Create suggestion widget
        widget = SuggestionWidget(suggestion)
        if hasattr(widget, "suggestion_accepted"):
            widget.suggestion_accepted.connect(self.handle_suggestion_accepted)  # type: ignore
        if hasattr(widget, "suggestion_rejected"):
            widget.suggestion_rejected.connect(self.handle_suggestion_rejected)  # type: ignore
        if hasattr(widget, "suggestion_dismissed"):
            widget.suggestion_dismissed.connect(self.handle_suggestion_dismissed)  # type: ignore

        self.suggestions[suggestion.id] = suggestion

        # Insert at the top (most recent first)
        self.suggestions_layout.insertWidget(0, widget)  # type: ignore

        self.update_display()
        logger.info(f"Added suggestion: {suggestion.title}")

    def remove_suggestion(self, suggestion_id: str):
        """Remove a suggestion from the panel."""
        if suggestion_id in self.suggestions:
            # Find and remove the widget
            for i in range(self.suggestions_layout.count()):  # type: ignore
                widget = self.suggestions_layout.itemAt(i).widget()  # type: ignore
                if (
                    isinstance(widget, SuggestionWidget)
                    and widget.suggestion.id == suggestion_id
                ):
                    widget.setParent(None)  # type: ignore
                    break

            del self.suggestions[suggestion_id]
            self.update_display()
            logger.info(f"Removed suggestion: {suggestion_id}")

    def handle_suggestion_accepted(self, suggestion_id: str):
        """Handle when a suggestion is accepted."""
        self.remove_suggestion(suggestion_id)

    def handle_suggestion_rejected(self, suggestion_id: str):
        """Handle when a suggestion is rejected."""
        self.remove_suggestion(suggestion_id)

    def handle_suggestion_dismissed(self, suggestion_id: str):
        """Handle when a suggestion is dismissed."""
        self.remove_suggestion(suggestion_id)

    def update_display(self):
        """Update the panel display state."""
        has_suggestions = len(self.suggestions) > 0
        self.empty_label.setVisible(not has_suggestions)  # type: ignore
        self.suggestions_widget.setVisible(has_suggestions)  # type: ignore

    def clear_suggestions(self):
        """Clear all suggestions."""
        for suggestion_id in list(self.suggestions.keys()):
            self.remove_suggestion(suggestion_id)


class NotificationSettings(QWidget):  # type: ignore
    """Settings widget for notification preferences."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)  # type: ignore
        self.init_ui()

    def init_ui(self):
        """Initialize the settings UI."""
        layout = QVBoxLayout()  # type: ignore

        # Notification preferences
        notif_group = QGroupBox("Notification Preferences")  # type: ignore
        notif_layout = QVBoxLayout()  # type: ignore

        self.enable_notifications = QCheckBox("Enable notifications")  # type: ignore
        self.enable_notifications.setChecked(True)  # type: ignore
        notif_layout.addWidget(self.enable_notifications)  # type: ignore

        self.enable_system_tray = QCheckBox("Show in system tray")  # type: ignore
        self.enable_system_tray.setChecked(False)  # type: ignore
        notif_layout.addWidget(self.enable_system_tray)  # type: ignore

        self.enable_sounds = QCheckBox("Play notification sounds")  # type: ignore
        self.enable_sounds.setChecked(False)  # type: ignore
        notif_layout.addWidget(self.enable_sounds)  # type: ignore

        notif_group.setLayout(notif_layout)  # type: ignore
        layout.addWidget(notif_group)  # type: ignore

        # Display settings
        display_group = QGroupBox("Display Settings")  # type: ignore
        display_layout = QVBoxLayout()  # type: ignore

        # Max suggestions
        max_layout = QHBoxLayout()  # type: ignore
        max_layout.addWidget(QLabel("Maximum suggestions:"))  # type: ignore
        self.max_suggestions_spin = QSpinBox()  # type: ignore
        self.max_suggestions_spin.setRange(1, 10)  # type: ignore
        self.max_suggestions_spin.setValue(5)  # type: ignore
        max_layout.addWidget(self.max_suggestions_spin)  # type: ignore
        max_layout.addStretch()  # type: ignore
        display_layout.addLayout(max_layout)  # type: ignore

        # Auto-dismiss
        dismiss_layout = QHBoxLayout()  # type: ignore
        dismiss_layout.addWidget(QLabel("Auto-dismiss after (minutes):"))  # type: ignore
        self.auto_dismiss_spin = QSpinBox()  # type: ignore
        self.auto_dismiss_spin.setRange(0, 60)  # type: ignore
        self.auto_dismiss_spin.setValue(10)  # type: ignore
        self.auto_dismiss_spin.setSpecialValueText("Never")  # type: ignore
        dismiss_layout.addWidget(self.auto_dismiss_spin)  # type: ignore
        dismiss_layout.addStretch()  # type: ignore
        display_layout.addLayout(dismiss_layout)  # type: ignore

        display_group.setLayout(display_layout)  # type: ignore
        layout.addWidget(display_group)  # type: ignore

        layout.addStretch()  # type: ignore
        self.setLayout(layout)  # type: ignore


class SuggestionHistory(QWidget):  # type: ignore
    """Widget for viewing suggestion history."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)  # type: ignore
        self.history = []
        self.init_ui()

    def init_ui(self):
        """Initialize the history UI."""
        layout = QVBoxLayout()  # type: ignore

        # Header
        header_label = QLabel("📋 Suggestion History")  # type: ignore
        header_label.setFont(QFont("Arial", 12, QFont.Bold))  # type: ignore
        layout.addWidget(header_label)  # type: ignore

        # History list
        self.history_list = QListWidget()  # type: ignore
        layout.addWidget(self.history_list)  # type: ignore

        # Details area
        self.details_text = QTextEdit()  # type: ignore
        self.details_text.setMaximumHeight(100)  # type: ignore
        self.details_text.setReadOnly(True)  # type: ignore
        layout.addWidget(self.details_text)  # type: ignore

        self.setLayout(layout)  # type: ignore

        # Connect signals
        self.history_list.currentItemChanged.connect(self.show_details)  # type: ignore

    def add_to_history(self, suggestion: Suggestion):
        """Add a suggestion to the history."""
        self.history.append(suggestion)

        # Create list item
        status_icon = (
            "✓" if suggestion.accepted else "✗" if suggestion.accepted is False else "—"
        )
        item_text = f"{status_icon} {suggestion.title} ({suggestion.timestamp.strftime('%Y-%m-%d %H:%M')})"

        item = QListWidgetItem(item_text)  # type: ignore
        item.setData(Qt.UserRole, suggestion)  # type: ignore
        self.history_list.addItem(item)  # type: ignore

        # Keep only last 100 items
        if self.history_list.count() > 100:  # type: ignore
            self.history_list.takeItem(0)  # type: ignore
            self.history.pop(0)

    def show_details(self, current, previous):
        """Show details for selected suggestion."""
        if current:
            suggestion = current.data(Qt.UserRole)  # type: ignore
            if suggestion:
                details = f"""
                <b>Title:</b> {suggestion.title}<br>
                <b>Type:</b> {suggestion.suggestion_type.value}<br>
                <b>Priority:</b> {suggestion.priority.name}<br>
                <b>Confidence:</b> {suggestion.confidence:.0%}<br>
                <b>Content:</b> {suggestion.content}<br>
                <b>Status:</b> {"Accepted" if suggestion.accepted else "Rejected" if suggestion.accepted is False else "Pending"}<br>
                """
                if suggestion.feedback:
                    details += f"<b>Feedback:</b> {suggestion.feedback}<br>"

                self.details_text.setHtml(details)  # type: ignore


class SuggestionNotificationSystem(QWidget):  # type: ignore
    """
    Main suggestion notification system for Lyrixa AI Assistant.

    Provides comprehensive notification management including:
    - Real-time suggestion display
    - User interaction handling
    - Notification settings
    - Suggestion history
    """

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            logger.warning(
                "PySide6 not available. Suggestion notification system will not function."
            )
            return

        super().__init__(parent)  # type: ignore

        # Signals
        self.suggestion_processed = QtSignal(str, bool)  # type: ignore
        self.settings_changed = QtSignal()  # type: ignore

        self.callbacks = {}
        self.init_ui()

        # System tray icon (optional)
        self.tray_icon = None
        self.setup_system_tray()

        logger.info("Suggestion Notification System initialized successfully")

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()  # type: ignore

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)  # type: ignore

        # Left panel - Live suggestions
        left_widget = QWidget()  # type: ignore
        left_layout = QVBoxLayout()  # type: ignore

        self.suggestion_panel = SuggestionPanel()
        left_layout.addWidget(self.suggestion_panel)  # type: ignore

        left_widget.setLayout(left_layout)  # type: ignore
        splitter.addWidget(left_widget)  # type: ignore

        # Right panel - Settings and history
        right_widget = QWidget()  # type: ignore
        right_layout = QVBoxLayout()  # type: ignore

        # Settings
        self.settings_widget = NotificationSettings()
        right_layout.addWidget(self.settings_widget)  # type: ignore

        # History
        self.history_widget = SuggestionHistory()
        right_layout.addWidget(self.history_widget)  # type: ignore

        right_widget.setLayout(right_layout)  # type: ignore
        splitter.addWidget(right_widget)  # type: ignore

        # Set splitter proportions
        splitter.setStretchFactor(0, 2)  # type: ignore
        splitter.setStretchFactor(1, 1)  # type: ignore

        layout.addWidget(splitter)  # type: ignore
        self.setLayout(layout)  # type: ignore

        # Generate sample suggestions for demonstration
        self.generate_sample_suggestions()

    def setup_system_tray(self):
        """Setup system tray icon if available."""
        if (
            hasattr(QSystemTrayIcon, "isSystemTrayAvailable")
            and QSystemTrayIcon.isSystemTrayAvailable()
        ):  # type: ignore
            self.tray_icon = QSystemTrayIcon(self)  # type: ignore

            # Create tray menu
            tray_menu = QMenu()  # type: ignore
            tray_menu.addAction("Show Suggestions", self.show)  # type: ignore
            tray_menu.addSeparator()  # type: ignore
            tray_menu.addAction("Exit", QApplication.quit)  # type: ignore

            self.tray_icon.setContextMenu(tray_menu)  # type: ignore

            # Set tray icon (placeholder)
            icon = QIcon()  # type: ignore
            pixmap = QPixmap(16, 16)  # type: ignore
            pixmap.fill(QColor(0, 120, 215))  # type: ignore
            icon.addPixmap(pixmap)  # type: ignore
            self.tray_icon.setIcon(icon)  # type: ignore

            self.tray_icon.setToolTip("Lyrixa Suggestions")  # type: ignore

    def show_suggestion(self, suggestion: Suggestion):
        """Display a new suggestion."""
        if hasattr(self, "suggestion_panel"):
            self.suggestion_panel.add_suggestion(suggestion)
        if hasattr(self, "history_widget"):
            self.history_widget.add_to_history(suggestion)

        # Show system tray notification if enabled
        if (
            self.tray_icon
            and hasattr(self, "settings_widget")
            and hasattr(self.settings_widget, "enable_system_tray")
            and self.settings_widget.enable_system_tray.isChecked()
        ):  # type: ignore
            self.tray_icon.showMessage(
                "New Suggestion",
                suggestion.title,
                Qt.Information,
                3000,  # type: ignore
            )

    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for suggestion events."""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)

    def trigger_callback(self, event_type: str, *args, **kwargs):
        """Trigger callbacks for an event type."""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in callback for {event_type}: {e}")

    def generate_sample_suggestions(self):
        """Generate sample suggestions for demonstration."""
        import uuid

        sample_suggestions = [
            {
                "title": "Take a break",
                "content": "You've been working for 90 minutes. Consider taking a 10-minute break to maintain productivity.",
                "type": SuggestionType.WELLBEING,
                "priority": SuggestionPriority.MEDIUM,
                "confidence": 0.85,
            },
            {
                "title": "Review your progress",
                "content": "It's a good time to review what you've accomplished today and plan next steps.",
                "type": SuggestionType.PRODUCTIVITY,
                "priority": SuggestionPriority.LOW,
                "confidence": 0.72,
            },
            {
                "title": "Learning opportunity",
                "content": "Based on your recent work, you might benefit from learning about advanced Python patterns.",
                "type": SuggestionType.LEARNING,
                "priority": SuggestionPriority.LOW,
                "confidence": 0.68,
            },
        ]

        for i, sample in enumerate(sample_suggestions):
            suggestion = Suggestion(
                id=str(uuid.uuid4()),
                title=sample["title"],
                content=sample["content"],
                suggestion_type=sample["type"],
                priority=sample["priority"],
                confidence=sample["confidence"],
                timestamp=datetime.now() - timedelta(minutes=i * 5),
                actions=[],
                metadata={},
            )

            # Add with slight delay for visual effect
            QTimer.singleShot(i * 500, lambda s=suggestion: self.show_suggestion(s))  # type: ignore


# Example usage
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        app = QApplication(sys.argv)  # type: ignore

        notification_system = SuggestionNotificationSystem()
        notification_system.show()  # type: ignore
        notification_system.resize(800, 600)  # type: ignore

        sys.exit(app.exec())  # type: ignore
    else:
        print("PySide6 is required to run the Suggestion Notification System")
