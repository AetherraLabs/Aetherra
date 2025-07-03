"""
Example usage of UI Enhancement Controller
=========================================

This script demonstrates how to use the UI enhancement controller
to apply consistent styling and optimizations to a simple UI.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    # Import UI enhancement modules
    from src.aethercode.ui.enhancement_controller import (
        apply_enhanced_theme,
        enhance_application,
        get_performance_report,
        ui_enhancer,
    )

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("PySide6 is not available. This example requires Qt.")
    sys.exit(1)


class ExampleWindow(QMainWindow):
    """Example window demonstrating UI enhancements."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("UI Enhancement Example")
        self.resize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_form_tab()
        self.create_chat_tab()
        self.create_performance_tab()

        # Add status display
        self.status_label = QLabel("UI Enhancement Example")
        layout.addWidget(self.status_label)

        # Show performance report every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_performance)
        self.timer.start(1000)

    def create_form_tab(self):
        """Create a tab with form controls."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add heading
        heading = QLabel("Form Controls")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        # Add form fields
        form_layout = QVBoxLayout()

        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        form_layout.addLayout(name_layout)

        # Email field
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(email_input)
        form_layout.addLayout(email_layout)

        # Message field
        message_layout = QVBoxLayout()
        message_label = QLabel("Message:")
        message_input = QTextEdit()
        message_layout.addWidget(message_label)
        message_layout.addWidget(message_input)
        form_layout.addLayout(message_layout)

        # Add dropdown
        dropdown_layout = QHBoxLayout()
        dropdown_label = QLabel("Category:")
        dropdown = QComboBox()
        dropdown.addItems(["General", "Support", "Feedback", "Other"])
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(dropdown)
        form_layout.addLayout(dropdown_layout)

        # Add button
        submit_button = QPushButton("Submit")
        form_layout.addWidget(submit_button)

        layout.addLayout(form_layout)

        # Add to tabs
        self.tabs.addTab(tab, "Form")

    def create_chat_tab(self):
        """Create a tab with chat messages."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add scroll area for messages
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create message container
        message_container = QWidget()
        message_layout = QVBoxLayout(message_container)

        # Add some example messages
        self.add_chat_message(
            message_layout,
            "User",
            "Hello! This is a test message with standard styling.",
        )
        self.add_chat_message(
            message_layout,
            "Assistant",
            "Hi there! I'm responding with properly styled text using our enhanced UI controller.",
        )
        self.add_chat_message(
            message_layout,
            "User",
            "How does the styling look? Is it consistent with our design system?",
        )
        self.add_chat_message(
            message_layout,
            "Assistant",
            "Yes, the styling is now consistent! We've removed chat bubbles, standardized spacing, and ensured proper contrast for accessibility.",
        )

        # Set message container as scroll area widget
        scroll_area.setWidget(message_container)
        layout.addWidget(scroll_area)

        # Add input area
        input_layout = QHBoxLayout()
        chat_input = QLineEdit()
        chat_input.setPlaceholderText("Type a message...")
        send_button = QPushButton("Send")

        input_layout.addWidget(chat_input)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

        # Add to tabs
        self.tabs.addTab(tab, "Chat")

    def add_chat_message(self, layout, sender, text):
        """Add a chat message to the layout."""
        message_frame = QFrame()
        message_frame.setObjectName("chatMessage")

        message_layout = QVBoxLayout(message_frame)

        # Add sender label
        sender_label = QLabel(sender)
        sender_label.setObjectName("messageSender")
        message_layout.addWidget(sender_label)

        # Add message text
        message_text = QLabel(text)
        message_text.setWordWrap(True)
        message_text.setObjectName("messageText")
        message_layout.addWidget(message_text)

        # Add to parent layout
        layout.addWidget(message_frame)

        # Apply enhanced theme
        apply_enhanced_theme(message_frame, "chat_message")

    def create_performance_tab(self):
        """Create a tab showing performance metrics."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add heading
        heading = QLabel("Performance Metrics")
        layout.addWidget(heading)

        # Add performance display
        self.performance_text = QTextEdit()
        self.performance_text.setReadOnly(True)
        layout.addWidget(self.performance_text)

        # Add to tabs
        self.tabs.addTab(tab, "Performance")

    def update_performance(self):
        """Update performance metrics display."""
        report = get_performance_report()

        # Format report as text
        text = "UI Performance Report\n"
        text += "====================\n\n"

        text += f"Average Frame Time: {report.get('avg_frame_time', 0):.2f}ms\n"
        text += f"Frame Count: {report.get('frame_count', 0)}\n\n"

        text += "Component Performance:\n"

        components = report.get("components", {})
        for component_id, stats in components.items():
            text += f"- {component_id}:\n"
            text += f"  Avg: {stats.get('avg', 0):.2f}ms\n"
            text += f"  Min: {stats.get('min', 0):.2f}ms\n"
            text += f"  Max: {stats.get('max', 0):.2f}ms\n\n"

        self.performance_text.setText(text)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Apply application-wide UI enhancements
    enhance_application(app)

    # Create and show window
    window = ExampleWindow()

    # Apply enhancements to main window
    ui_enhancer.enhance_window(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
