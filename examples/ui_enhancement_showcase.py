"""
UI Enhancement Integration Example
================================

This example demonstrates integration of all UI enhancements:
- Component Library
- Dark Mode Provider
- Performance Optimization
- Type Checking
- Cross-Platform Compatibility

Run this file to see all UI enhancements in action.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QScrollArea,
        QSplitter,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    # Import UI enhancement modules
    from src.aethercode.ui.component_library import (
        Banner,
        Card,
        ChatMessageWidget,
        LoadingIndicator,
        StatusLabel,
        StyledButton,
        StyledComboBox,
        StyledTextArea,
        StyledTextField,
        TabPanel,
    )
    from src.aethercode.ui.dark_mode_provider import apply_dark_mode, dark_mode
    from src.aethercode.ui.enhancement_controller import ui_enhancer
    from src.aethercode.ui.performance_optimizer import (
        measure_performance,
        optimize_widget,
        performance_monitor,
        render_batcher,
    )

    # Import cross-platform testing
    from tests.ui.cross_platform_tester import PlatformInfo

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("PySide6 not available. This example requires Qt.")
    sys.exit(1)


class ComponentShowcaseWindow(QMainWindow):
    """
    Window showcasing all enhanced UI components.
    """

    def __init__(self):
        """Initialize the showcase window."""
        super().__init__()

        self.setWindowTitle("NeuroCode UI Enhancement Showcase")
        self.resize(1024, 768)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)

        # Add header
        header = QLabel("NeuroCode UI Components")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                font-size: {dark_mode.get_font_size("window_title_size")}px;
                font-weight: bold;
                color: {dark_mode.get_color("primary_text")};
                margin-bottom: {dark_mode.get_spacing("default_margin")}px;
            }}
        """)
        main_layout.addWidget(header)

        # Add platform info banner
        platform_info = PlatformInfo.get_platform_summary()
        platform_text = f"Running on {platform_info['os_name']} {platform_info['os_version']} | Python {platform_info['python_version']}"
        platform_banner = Banner(platform_text, "info", False)
        main_layout.addWidget(platform_banner)

        # Create tabs
        tabs = TabPanel()

        # Add component tabs
        self.add_input_components_tab(tabs)
        self.add_button_components_tab(tabs)
        self.add_chat_components_tab(tabs)
        self.add_status_components_tab(tabs)
        self.add_performance_tab(tabs)

        main_layout.addWidget(tabs)

        # Add status bar label
        self.status_label = StatusLabel("All components loaded successfully", "success")
        main_layout.addWidget(self.status_label)

        # Start performance monitoring
        performance_monitor.start()

        # Timer to update performance stats
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_performance)
        self.update_timer.start(1000)  # Update every second

    @measure_performance
    def add_input_components_tab(self, tabs):
        """Add input components tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add card with text inputs
        input_card = Card("Text Input Components")

        # Add text field
        text_field_layout = QHBoxLayout()
        text_field_layout.addWidget(QLabel("Text Field:"))
        text_field_layout.addWidget(StyledTextField(placeholder="Enter text here..."))
        input_card.add_layout(text_field_layout)

        # Add text area
        text_area_layout = QHBoxLayout()
        text_area_layout.addWidget(QLabel("Text Area:"))
        text_area = StyledTextArea(placeholder="Enter multi-line text here...")
        text_area.setMinimumHeight(100)
        text_area_layout.addWidget(text_area)
        input_card.add_layout(text_area_layout)

        # Add combo box
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Combo Box:"))
        combo_box = StyledComboBox(
            items=["Option 1", "Option 2", "Option 3", "Option 4"]
        )
        combo_layout.addWidget(combo_box)
        input_card.add_layout(combo_layout)

        layout.addWidget(input_card)

        # Add form card
        form_card = Card("Sample Form")

        # Add form fields
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(StyledTextField())
        form_card.add_layout(name_layout)

        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        email_layout.addWidget(StyledTextField())
        form_card.add_layout(email_layout)

        # Add submit button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        submit_button = StyledButton("Submit", button_type="primary")
        button_layout.addWidget(submit_button)
        form_card.add_layout(button_layout)

        layout.addWidget(form_card)
        layout.addStretch()

        tabs.add_tab(tab, "Input Components")

    @measure_performance
    def add_button_components_tab(self, tabs):
        """Add button components tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add button card
        button_card = Card("Button Components")

        # Standard buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(StyledButton("Standard Button"))
        button_layout.addWidget(StyledButton("Primary Button", button_type="primary"))
        button_layout.addWidget(StyledButton("Success Button", button_type="success"))
        button_layout.addWidget(StyledButton("Danger Button", button_type="danger"))
        button_card.add_layout(button_layout)

        layout.addWidget(button_card)

        # Add actions card
        actions_card = Card("Button Actions")

        # Action buttons
        action_layout = QVBoxLayout()

        # Row 1
        row1 = QHBoxLayout()
        add_button = StyledButton("Add Item")
        add_button.clicked.connect(
            lambda: self.status_label.set_status("Item added", "success")
        )
        row1.addWidget(add_button)

        delete_button = StyledButton("Delete Item", button_type="danger")
        delete_button.clicked.connect(
            lambda: self.status_label.set_status("Item deleted", "error")
        )
        row1.addWidget(delete_button)
        action_layout.addLayout(row1)

        # Row 2
        row2 = QHBoxLayout()
        save_button = StyledButton("Save Changes", button_type="primary")
        save_button.clicked.connect(lambda: self.show_save_action())
        row2.addWidget(save_button)

        cancel_button = StyledButton("Cancel")
        cancel_button.clicked.connect(
            lambda: self.status_label.set_status("Action cancelled", "info")
        )
        row2.addWidget(cancel_button)
        action_layout.addLayout(row2)

        actions_card.add_layout(action_layout)
        layout.addWidget(actions_card)

        layout.addStretch()

        tabs.add_tab(tab, "Button Components")

    @measure_performance
    def add_chat_components_tab(self, tabs):
        """Add chat components tab."""
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
        message_layout.addWidget(
            ChatMessageWidget(
                sender="User",
                message="Hello! This is a test message with standardized styling.",
                timestamp="10:45 AM",
            )
        )

        message_layout.addWidget(
            ChatMessageWidget(
                sender="Assistant",
                message="Hi there! I'm responding with properly styled text using our enhanced UI components.",
                timestamp="10:46 AM",
            )
        )

        message_layout.addWidget(
            ChatMessageWidget(
                sender="User",
                message="How does the styling look? Is it consistent with our design system?",
                timestamp="10:47 AM",
            )
        )

        message_layout.addWidget(
            ChatMessageWidget(
                sender="Assistant",
                message="Yes, the styling is now consistent! We've removed chat bubbles, standardized spacing, and ensured proper contrast for accessibility. All components are using our dark mode provider for consistent colors.",
                timestamp="10:48 AM",
            )
        )

        # Add stretch to push messages up
        message_layout.addStretch()

        # Set message container as scroll area widget
        scroll_area.setWidget(message_container)
        layout.addWidget(scroll_area)

        # Add input area
        input_layout = QHBoxLayout()
        chat_input = StyledTextField(placeholder="Type a message...")
        send_button = StyledButton("Send", button_type="primary")

        input_layout.addWidget(chat_input)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

        tabs.add_tab(tab, "Chat Components")

    @measure_performance
    def add_status_components_tab(self, tabs):
        """Add status components tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add status labels card
        status_card = Card("Status Labels")

        status_layout = QVBoxLayout()
        status_layout.addWidget(StatusLabel("Success: Operation completed", "success"))
        status_layout.addWidget(StatusLabel("Error: Something went wrong", "error"))
        status_layout.addWidget(StatusLabel("Warning: Proceed with caution", "warning"))
        status_layout.addWidget(StatusLabel("Info: System is updating", "info"))

        status_card.add_layout(status_layout)
        layout.addWidget(status_card)

        # Add banners card
        banner_card = Card("Notification Banners")

        banner_layout = QVBoxLayout()
        banner_layout.addWidget(
            Banner("Success: Your changes have been saved.", "success", True)
        )
        banner_layout.addWidget(
            Banner(
                "Error: Could not connect to server. Please try again.", "error", True
            )
        )
        banner_layout.addWidget(
            Banner("Warning: Your session will expire in 5 minutes.", "warning", True)
        )
        banner_layout.addWidget(
            Banner(
                "Info: New version available. Update now for new features.",
                "info",
                True,
            )
        )

        banner_card.add_layout(banner_layout)
        layout.addWidget(banner_card)

        # Add loading indicators card
        loading_card = Card("Loading Indicators")

        loading_layout = QVBoxLayout()

        # Indeterminate loader
        indeterminate_layout = QHBoxLayout()
        indeterminate_layout.addWidget(QLabel("Indeterminate:"))
        indeterminate_layout.addWidget(LoadingIndicator(is_indeterminate=True))
        loading_layout.addLayout(indeterminate_layout)

        # Determinate loader
        determinate_layout = QHBoxLayout()
        determinate_layout.addWidget(QLabel("Determinate:"))
        self.progress_bar = LoadingIndicator(is_indeterminate=False)
        self.progress_bar.set_progress(75)
        determinate_layout.addWidget(self.progress_bar)
        loading_layout.addLayout(determinate_layout)

        loading_card.add_layout(loading_layout)
        layout.addWidget(loading_card)

        layout.addStretch()

        tabs.add_tab(tab, "Status Components")

    @measure_performance
    def add_performance_tab(self, tabs):
        """Add performance monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add performance card
        performance_card = Card("Performance Metrics")

        # Add performance info
        self.performance_label = QLabel("Collecting performance data...")
        performance_card.add_widget(self.performance_label)

        # Add component timing card
        component_card = Card("Component Render Times")
        self.component_label = QLabel("Collecting component timing data...")
        component_card.add_widget(self.component_label)

        layout.addWidget(performance_card)
        layout.addWidget(component_card)
        layout.addStretch()

        tabs.add_tab(tab, "Performance")

    def show_save_action(self):
        """Simulate save action with loading indicator."""
        # Update status to show loading
        self.status_label.set_status("Saving changes...", "info")

        # After 2 seconds, show success
        QTimer.singleShot(
            2000,
            lambda: self.status_label.set_status(
                "Changes saved successfully", "success"
            ),
        )

    def update_performance(self):
        """Update performance statistics."""
        # Get performance report
        report = performance_monitor.get_report()

        # Update performance label
        self.performance_label.setText(
            f"Average Frame Time: {report.get('avg_frame_time', 0):.2f}ms\n"
            f"Frame Count: {report.get('frame_count', 0)}"
        )

        # Update component timing label
        component_text = "Component Render Times:\n\n"

        components = report.get("components", {})
        for component_id, stats in components.items():
            component_text += f"• {component_id}:\n"
            component_text += f"  Avg: {stats.get('avg', 0):.2f}ms | "
            component_text += f"Min: {stats.get('min', 0):.2f}ms | "
            component_text += f"Max: {stats.get('max', 0):.2f}ms\n\n"

        self.component_label.setText(component_text)

        # Update progress bar for demo purposes
        if hasattr(self, "progress_bar"):
            current = self.progress_bar.value()
            new_value = (current + 5) % 101
            self.progress_bar.set_progress(new_value)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Set application-wide stylesheet using dark mode provider
    app.setStyleSheet(dark_mode.get_global_stylesheet())

    # Create and show window
    window = ComponentShowcaseWindow()

    # Apply UI enhancements to window
    ui_enhancer.enhance_window(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
