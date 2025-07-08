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
    PYSIDE6_AVAILABLE = False

    # Mock classes for when PySide6 is not available
    class QWidget:
        pass

    class Signal:
        pass

    class Enum:
        pass


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class SuggestionWidget(QWidget if PYSIDE6_AVAILABLE else object):
    """Individual suggestion display widget."""

    # Signals
    suggestion_accepted = QtSignal(str) if PYSIDE6_AVAILABLE else None
    suggestion_rejected = QtSignal(str) if PYSIDE6_AVAILABLE else None
    suggestion_dismissed = QtSignal(str) if PYSIDE6_AVAILABLE else None
    feedback_provided = QtSignal(str, str) if PYSIDE6_AVAILABLE else None

    def __init__(self, suggestion: Suggestion, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.suggestion = suggestion
        self.setMaximumHeight(120)
        self.setMinimumHeight(80)

        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Initialize the suggestion widget UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        # Header with title and priority
        header_layout = QHBoxLayout()

        # Priority indicator
        priority_color = self.get_priority_color()
        priority_label = QLabel("●")
        priority_label.setStyleSheet(
            f"color: {priority_color}; font-size: 16px; font-weight: bold;"
        )
        header_layout.addWidget(priority_label)

        # Title
        title_label = QLabel(self.suggestion.title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)

        # Confidence score
        confidence_label = QLabel(f"{self.suggestion.confidence:.0%}")
        confidence_label.setFont(QFont("Arial", 8))
        confidence_label.setStyleSheet("color: #666; font-weight: bold;")
        header_layout.addWidget(confidence_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Content
        content_label = QLabel(self.suggestion.content)
        content_label.setFont(QFont("Arial", 9))
        content_label.setWordWrap(True)
        content_label.setMaximumHeight(30)
        layout.addWidget(content_label)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        # Accept button
        accept_btn = QPushButton("✓ Accept")
        accept_btn.setMaximumWidth(80)
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
        """)
        accept_btn.clicked.connect(self.accept_suggestion)
        button_layout.addWidget(accept_btn)

        # Reject button
        reject_btn = QPushButton("✗ Reject")
        reject_btn.setMaximumWidth(80)
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
        """)
        reject_btn.clicked.connect(self.reject_suggestion)
        button_layout.addWidget(reject_btn)

        # Dismiss button
        dismiss_btn = QPushButton("— Later")
        dismiss_btn.setMaximumWidth(80)
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
        """)
        dismiss_btn.clicked.connect(self.dismiss_suggestion)
        button_layout.addWidget(dismiss_btn)

        button_layout.addStretch()

        # Timestamp
        time_label = QLabel(self.suggestion.timestamp.strftime("%H:%M"))
        time_label.setFont(QFont("Arial", 7))
        time_label.setStyleSheet("color: #999;")
        button_layout.addWidget(time_label)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_priority_color(self) -> str:
        """Get color for priority indicator."""
        colors = {
            SuggestionPriority.LOW: "#4CAF50",
            SuggestionPriority.MEDIUM: "#FF9800",
            SuggestionPriority.HIGH: "#FF5722",
            SuggestionPriority.URGENT: "#F44336",
        }
        return colors.get(self.suggestion.priority, "#9E9E9E")

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
        """)

    def accept_suggestion(self):
        """Handle suggestion acceptance."""
        self.suggestion.accepted = True
        if self.suggestion_accepted:
            self.suggestion_accepted.emit(self.suggestion.id)
        logger.info(f"Suggestion {self.suggestion.id} accepted")

    def reject_suggestion(self):
        """Handle suggestion rejection."""
        self.suggestion.accepted = False
        if self.suggestion_rejected:
            self.suggestion_rejected.emit(self.suggestion.id)
        logger.info(f"Suggestion {self.suggestion.id} rejected")

    def dismiss_suggestion(self):
        """Handle suggestion dismissal."""
        if self.suggestion_dismissed:
            self.suggestion_dismissed.emit(self.suggestion.id)
        logger.info(f"Suggestion {self.suggestion.id} dismissed")


class SuggestionPanel(QWidget if PYSIDE6_AVAILABLE else object):
    """Main panel for displaying suggestions."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.suggestions = {}
        self.max_suggestions = 5

        self.init_ui()

    def init_ui(self):
        """Initialize the suggestion panel UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Header
        header_label = QLabel("💡 Suggestions")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(header_label)

        # Scroll area for suggestions
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(400)

        self.suggestions_widget = QWidget()
        self.suggestions_layout = QVBoxLayout(self.suggestions_widget)
        self.suggestions_layout.setSpacing(2)
        self.suggestions_layout.addStretch()

        scroll_area.setWidget(self.suggestions_widget)
        layout.addWidget(scroll_area)

        # Empty state
        self.empty_label = QLabel("No suggestions available")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: #6c757d; font-style: italic; margin: 20px;"
        )
        layout.addWidget(self.empty_label)

        self.setLayout(layout)
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
        widget.suggestion_accepted.connect(self.handle_suggestion_accepted)
        widget.suggestion_rejected.connect(self.handle_suggestion_rejected)
        widget.suggestion_dismissed.connect(self.handle_suggestion_dismissed)

        self.suggestions[suggestion.id] = suggestion

        # Insert at the top (most recent first)
        self.suggestions_layout.insertWidget(0, widget)

        self.update_display()
        logger.info(f"Added suggestion: {suggestion.title}")

    def remove_suggestion(self, suggestion_id: str):
        """Remove a suggestion from the panel."""
        if suggestion_id in self.suggestions:
            # Find and remove the widget
            for i in range(self.suggestions_layout.count()):
                widget = self.suggestions_layout.itemAt(i).widget()
                if (
                    isinstance(widget, SuggestionWidget)
                    and widget.suggestion.id == suggestion_id
                ):
                    widget.setParent(None)
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
        self.empty_label.setVisible(not has_suggestions)
        self.suggestions_widget.setVisible(has_suggestions)

    def clear_suggestions(self):
        """Clear all suggestions."""
        for suggestion_id in list(self.suggestions.keys()):
            self.remove_suggestion(suggestion_id)


class NotificationSettings(QWidget if PYSIDE6_AVAILABLE else object):
    """Settings widget for notification preferences."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the settings UI."""
        layout = QVBoxLayout()

        # Notification preferences
        notif_group = QGroupBox("Notification Preferences")
        notif_layout = QVBoxLayout()

        self.enable_notifications = QCheckBox("Enable notifications")
        self.enable_notifications.setChecked(True)
        notif_layout.addWidget(self.enable_notifications)

        self.enable_system_tray = QCheckBox("Show in system tray")
        self.enable_system_tray.setChecked(False)
        notif_layout.addWidget(self.enable_system_tray)

        self.enable_sounds = QCheckBox("Play notification sounds")
        self.enable_sounds.setChecked(False)
        notif_layout.addWidget(self.enable_sounds)

        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)

        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout()

        # Max suggestions
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Maximum suggestions:"))
        self.max_suggestions_spin = QSpinBox()
        self.max_suggestions_spin.setRange(1, 10)
        self.max_suggestions_spin.setValue(5)
        max_layout.addWidget(self.max_suggestions_spin)
        max_layout.addStretch()
        display_layout.addLayout(max_layout)

        # Auto-dismiss
        dismiss_layout = QHBoxLayout()
        dismiss_layout.addWidget(QLabel("Auto-dismiss after (minutes):"))
        self.auto_dismiss_spin = QSpinBox()
        self.auto_dismiss_spin.setRange(0, 60)
        self.auto_dismiss_spin.setValue(10)
        self.auto_dismiss_spin.setSpecialValueText("Never")
        dismiss_layout.addWidget(self.auto_dismiss_spin)
        dismiss_layout.addStretch()
        display_layout.addLayout(dismiss_layout)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        layout.addStretch()
        self.setLayout(layout)


class SuggestionHistory(QWidget if PYSIDE6_AVAILABLE else object):
    """Widget for viewing suggestion history."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.history = []
        self.init_ui()

    def init_ui(self):
        """Initialize the history UI."""
        layout = QVBoxLayout()

        # Header
        header_label = QLabel("📋 Suggestion History")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header_label)

        # History list
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        # Details area
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)

        self.setLayout(layout)

        # Connect signals
        self.history_list.currentItemChanged.connect(self.show_details)

    def add_to_history(self, suggestion: Suggestion):
        """Add a suggestion to the history."""
        self.history.append(suggestion)

        # Create list item
        status_icon = (
            "✓" if suggestion.accepted else "✗" if suggestion.accepted is False else "—"
        )
        item_text = f"{status_icon} {suggestion.title} ({suggestion.timestamp.strftime('%Y-%m-%d %H:%M')})"

        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, suggestion)
        self.history_list.addItem(item)

        # Keep only last 100 items
        if self.history_list.count() > 100:
            self.history_list.takeItem(0)
            self.history.pop(0)

    def show_details(self, current, previous):
        """Show details for selected suggestion."""
        if current:
            suggestion = current.data(Qt.UserRole)
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

            self.details_text.setHtml(details)


class SuggestionNotificationSystem(QWidget if PYSIDE6_AVAILABLE else object):
    """
    Main suggestion notification system for Lyrixa AI Assistant.

    Provides comprehensive notification management including:
    - Real-time suggestion display
    - User interaction handling
    - Notification settings
    - Suggestion history
    """

    # Signals
    suggestion_processed = QtSignal(str, bool) if PYSIDE6_AVAILABLE else None
    settings_changed = QtSignal() if PYSIDE6_AVAILABLE else None

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            logger.warning(
                "PySide6 not available. Suggestion notification system will not function."
            )
            return

        super().__init__(parent)
        self.callbacks = {}
        self.init_ui()

        # System tray icon (optional)
        self.tray_icon = None
        self.setup_system_tray()

        logger.info("Suggestion Notification System initialized successfully")

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Live suggestions
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        self.suggestion_panel = SuggestionPanel()
        left_layout.addWidget(self.suggestion_panel)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right panel - Settings and history
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # Settings
        self.settings_widget = NotificationSettings()
        right_layout.addWidget(self.settings_widget)

        # History
        self.history_widget = SuggestionHistory()
        right_layout.addWidget(self.history_widget)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setLayout(layout)

        # Generate sample suggestions for demonstration
        self.generate_sample_suggestions()

    def setup_system_tray(self):
        """Setup system tray icon if available."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)

            # Create tray menu
            tray_menu = QMenu()
            tray_menu.addAction("Show Suggestions", self.show)
            tray_menu.addSeparator()
            tray_menu.addAction("Exit", QApplication.quit)

            self.tray_icon.setContextMenu(tray_menu)

            # Set tray icon (placeholder)
            icon = QIcon()
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(0, 120, 215))
            icon.addPixmap(pixmap)
            self.tray_icon.setIcon(icon)

            self.tray_icon.setToolTip("Lyrixa Suggestions")

    def show_suggestion(self, suggestion: Suggestion):
        """Display a new suggestion."""
        self.suggestion_panel.add_suggestion(suggestion)
        self.history_widget.add_to_history(suggestion)

        # Show system tray notification if enabled
        if self.tray_icon and self.settings_widget.enable_system_tray.isChecked():
            self.tray_icon.showMessage(
                "New Suggestion", suggestion.title, QSystemTrayIcon.Information, 3000
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
            QTimer.singleShot(i * 500, lambda s=suggestion: self.show_suggestion(s))


# Example usage
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)

        notification_system = SuggestionNotificationSystem()
        notification_system.show()
        notification_system.resize(800, 600)

        sys.exit(app.exec())
    else:
        print("PySide6 is required to run the Suggestion Notification System")
