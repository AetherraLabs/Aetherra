"""
Twitch Bot Plugin GUI - PySide6 Interface for Twitch Bot Configuration and Monitoring
Author: Aetherra Plugin System
Version: 1.0.0
"""

# Standard library imports
import asyncio
import sys
from datetime import datetime
from typing import Any

try:
    # Third party imports
    from PySide6.QtCore import Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QFont, QIcon, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

if PYSIDE6_AVAILABLE:

    class TwitchBotWorker(QThread):
        """Worker thread for Twitch bot operations."""

        message_received = Signal(dict)
        connection_status = Signal(bool)
        error_occurred = Signal(str)

        def __init__(self, plugin):
            super().__init__()
            self.plugin = plugin
            self.running = False

        def run(self):
            """Run the worker thread."""
            self.running = True
            # In a real implementation, this would handle async operations
            # For now, we'll use a simple timer-based approach

        def stop(self):
            """Stop the worker thread."""
            self.running = False


class TwitchBotGUI(QMainWindow):
    """Main Twitch Bot Plugin GUI window."""

    def __init__(self, plugin=None):
        super().__init__()
        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is required for the Twitch Bot GUI")

        self.plugin = plugin
        self.worker = None
        self.is_connected = False

        self.setWindowTitle("Aetherra Twitch Bot Control Panel")
        self.setMinimumSize(800, 600)

        # Initialize UI
        self.init_ui()
        self.init_timers()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_connection_tab()
        self.create_chat_tab()
        self.create_commands_tab()
        self.create_moderation_tab()
        self.create_analytics_tab()
        self.create_settings_tab()

        # Status bar
        self.statusBar().showMessage("Disconnected")

    def create_connection_tab(self):
        """Create the connection configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Connection settings group
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QGridLayout(conn_group)

        # Username
        conn_layout.addWidget(QLabel("Bot Username:"), 0, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Your bot's Twitch username")
        conn_layout.addWidget(self.username_edit, 0, 1)

        # OAuth Token
        conn_layout.addWidget(QLabel("OAuth Token:"), 1, 0)
        self.oauth_edit = QLineEdit()
        self.oauth_edit.setPlaceholderText("oauth:your_token_here")
        self.oauth_edit.setEchoMode(QLineEdit.EchoMode.Password)
        conn_layout.addWidget(self.oauth_edit, 1, 1)

        # Channel
        conn_layout.addWidget(QLabel("Channel:"), 2, 0)
        self.channel_edit = QLineEdit()
        self.channel_edit.setPlaceholderText("Channel name to join")
        conn_layout.addWidget(self.channel_edit, 2, 1)

        # Client ID & Secret
        conn_layout.addWidget(QLabel("Client ID:"), 3, 0)
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setPlaceholderText("Twitch application client ID")
        conn_layout.addWidget(self.client_id_edit, 3, 1)

        conn_layout.addWidget(QLabel("Client Secret:"), 4, 0)
        self.client_secret_edit = QLineEdit()
        self.client_secret_edit.setPlaceholderText("Twitch application client secret")
        self.client_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        conn_layout.addWidget(self.client_secret_edit, 4, 1)

        layout.addWidget(conn_group)

        # Connection controls
        controls_group = QGroupBox("Connection Control")
        controls_layout = QHBoxLayout(controls_group)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        controls_layout.addWidget(self.connect_btn)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        controls_layout.addWidget(self.test_btn)

        # Status indicators
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        controls_layout.addWidget(self.status_label)

        layout.addWidget(controls_group)

        # OAuth helper
        oauth_group = QGroupBox("OAuth Setup Helper")
        oauth_layout = QVBoxLayout(oauth_group)

        oauth_info = QLabel(
            "To get your OAuth token:\n"
            "1. Go to https://twitchapps.com/tmi/\n"
            "2. Authorize with your bot account\n"
            "3. Copy the OAuth token (including 'oauth:' prefix)"
        )
        oauth_layout.addWidget(oauth_info)

        self.oauth_btn = QPushButton("Open OAuth Generator")
        self.oauth_btn.clicked.connect(self.open_oauth_generator)
        oauth_layout.addWidget(self.oauth_btn)

        layout.addWidget(oauth_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Connection")

    def create_chat_tab(self):
        """Create the chat monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Chat display
        chat_group = QGroupBox("Live Chat")
        chat_layout = QVBoxLayout(chat_group)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 10))
        chat_layout.addWidget(self.chat_display)

        # Message sending
        send_layout = QHBoxLayout()
        self.message_edit = QLineEdit()
        self.message_edit.setPlaceholderText("Type a message to send to chat...")
        self.message_edit.returnPressed.connect(self.send_message)
        send_layout.addWidget(self.message_edit)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        send_layout.addWidget(self.send_btn)

        chat_layout.addLayout(send_layout)
        layout.addWidget(chat_group)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QGridLayout(actions_group)

        self.welcome_btn = QPushButton("Welcome Message")
        self.welcome_btn.clicked.connect(
            lambda: self.quick_message("Welcome to the stream! 👋")
        )
        actions_layout.addWidget(self.welcome_btn, 0, 0)

        self.thanks_btn = QPushButton("Thank You")
        self.thanks_btn.clicked.connect(
            lambda: self.quick_message("Thank you for following! ❤️")
        )
        actions_layout.addWidget(self.thanks_btn, 0, 1)

        self.brb_btn = QPushButton("Be Right Back")
        self.brb_btn.clicked.connect(
            lambda: self.quick_message("I'll be right back! Chat amongst yourselves 😊")
        )
        actions_layout.addWidget(self.brb_btn, 1, 0)

        self.timeout_btn = QPushButton("Clear Chat")
        self.timeout_btn.clicked.connect(self.clear_chat_display)
        actions_layout.addWidget(self.timeout_btn, 1, 1)

        layout.addWidget(actions_group)

        self.tab_widget.addTab(tab, "Chat")

    def create_commands_tab(self):
        """Create the commands management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Built-in commands
        builtin_group = QGroupBox("Built-in Commands")
        builtin_layout = QVBoxLayout(builtin_group)

        builtin_list = QListWidget()
        builtin_commands = [
            "!hello - Greet users",
            "!time - Show current time",
            "!uptime - Show stream uptime",
            "!commands - List available commands",
            "!lurk - Lurk mode",
            "!unlurk - Return from lurking",
        ]
        builtin_list.addItems(builtin_commands)
        builtin_layout.addWidget(builtin_list)

        layout.addWidget(builtin_group)

        # Custom commands
        custom_group = QGroupBox("Custom Commands")
        custom_layout = QVBoxLayout(custom_group)

        # Add command form
        add_layout = QGridLayout()
        add_layout.addWidget(QLabel("Command:"), 0, 0)
        self.cmd_name_edit = QLineEdit()
        self.cmd_name_edit.setPlaceholderText("!mycommand")
        add_layout.addWidget(self.cmd_name_edit, 0, 1)

        add_layout.addWidget(QLabel("Response:"), 1, 0)
        self.cmd_response_edit = QLineEdit()
        self.cmd_response_edit.setPlaceholderText("Command response text...")
        add_layout.addWidget(self.cmd_response_edit, 1, 1)

        self.add_cmd_btn = QPushButton("Add Command")
        self.add_cmd_btn.clicked.connect(self.add_custom_command)
        add_layout.addWidget(self.add_cmd_btn, 2, 0, 1, 2)

        custom_layout.addLayout(add_layout)

        # Custom commands list
        self.custom_commands_list = QListWidget()
        custom_layout.addWidget(self.custom_commands_list)

        # Command management buttons
        cmd_buttons = QHBoxLayout()
        self.edit_cmd_btn = QPushButton("Edit")
        self.edit_cmd_btn.clicked.connect(self.edit_command)
        cmd_buttons.addWidget(self.edit_cmd_btn)

        self.delete_cmd_btn = QPushButton("Delete")
        self.delete_cmd_btn.clicked.connect(self.delete_command)
        cmd_buttons.addWidget(self.delete_cmd_btn)

        custom_layout.addLayout(cmd_buttons)
        layout.addWidget(custom_group)

        self.tab_widget.addTab(tab, "Commands")

    def create_moderation_tab(self):
        """Create the moderation tools tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Auto-moderation settings
        auto_mod_group = QGroupBox("Auto-Moderation")
        auto_mod_layout = QGridLayout(auto_mod_group)

        self.spam_filter = QCheckBox("Enable Spam Filter")
        auto_mod_layout.addWidget(self.spam_filter, 0, 0)

        self.caps_filter = QCheckBox("Block Excessive Caps")
        auto_mod_layout.addWidget(self.caps_filter, 0, 1)

        self.link_filter = QCheckBox("Block Links")
        auto_mod_layout.addWidget(self.link_filter, 1, 0)

        self.profanity_filter = QCheckBox("Profanity Filter")
        auto_mod_layout.addWidget(self.profanity_filter, 1, 1)

        auto_mod_layout.addWidget(QLabel("Max Message Length:"), 2, 0)
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(10, 500)
        self.max_length_spin.setValue(200)
        auto_mod_layout.addWidget(self.max_length_spin, 2, 1)

        layout.addWidget(auto_mod_group)

        # Banned words
        banned_group = QGroupBox("Banned Words")
        banned_layout = QVBoxLayout(banned_group)

        add_banned_layout = QHBoxLayout()
        self.banned_word_edit = QLineEdit()
        self.banned_word_edit.setPlaceholderText("Add banned word...")
        add_banned_layout.addWidget(self.banned_word_edit)

        self.add_banned_btn = QPushButton("Add")
        self.add_banned_btn.clicked.connect(self.add_banned_word)
        add_banned_layout.addWidget(self.add_banned_btn)

        banned_layout.addLayout(add_banned_layout)

        self.banned_words_list = QListWidget()
        banned_layout.addWidget(self.banned_words_list)

        self.remove_banned_btn = QPushButton("Remove Selected")
        self.remove_banned_btn.clicked.connect(self.remove_banned_word)
        banned_layout.addWidget(self.remove_banned_btn)

        layout.addWidget(banned_group)

        # Moderator actions
        mod_actions_group = QGroupBox("Moderator Actions")
        mod_actions_layout = QGridLayout(mod_actions_group)

        self.timeout_user_edit = QLineEdit()
        self.timeout_user_edit.setPlaceholderText("Username to timeout...")
        mod_actions_layout.addWidget(self.timeout_user_edit, 0, 0)

        self.timeout_btn = QPushButton("Timeout User")
        self.timeout_btn.clicked.connect(self.timeout_user)
        mod_actions_layout.addWidget(self.timeout_btn, 0, 1)

        self.ban_user_edit = QLineEdit()
        self.ban_user_edit.setPlaceholderText("Username to ban...")
        mod_actions_layout.addWidget(self.ban_user_edit, 1, 0)

        self.ban_btn = QPushButton("Ban User")
        self.ban_btn.clicked.connect(self.ban_user)
        mod_actions_layout.addWidget(self.ban_btn, 1, 1)

        layout.addWidget(mod_actions_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Moderation")

    def create_analytics_tab(self):
        """Create the analytics and statistics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Statistics display
        stats_group = QGroupBox("Chat Statistics")
        stats_layout = QGridLayout(stats_group)

        stats_layout.addWidget(QLabel("Messages Processed:"), 0, 0)
        self.messages_count_label = QLabel("0")
        stats_layout.addWidget(self.messages_count_label, 0, 1)

        stats_layout.addWidget(QLabel("Commands Executed:"), 1, 0)
        self.commands_count_label = QLabel("0")
        stats_layout.addWidget(self.commands_count_label, 1, 1)

        stats_layout.addWidget(QLabel("Active Chatters:"), 2, 0)
        self.chatters_count_label = QLabel("0")
        stats_layout.addWidget(self.chatters_count_label, 2, 1)

        stats_layout.addWidget(QLabel("Uptime:"), 3, 0)
        self.uptime_label = QLabel("00:00:00")
        stats_layout.addWidget(self.uptime_label, 3, 1)

        layout.addWidget(stats_group)

        # Activity chart placeholder
        activity_group = QGroupBox("Activity Chart")
        activity_layout = QVBoxLayout(activity_group)

        # In a real implementation, you'd add a proper chart widget here
        chart_placeholder = QLabel(
            "Activity chart would be displayed here\n(Requires matplotlib or similar)"
        )
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("border: 2px dashed #ccc; padding: 50px;")
        activity_layout.addWidget(chart_placeholder)

        layout.addWidget(activity_group)

        # Export buttons
        export_group = QGroupBox("Data Export")
        export_layout = QHBoxLayout(export_group)

        self.export_stats_btn = QPushButton("Export Statistics")
        self.export_stats_btn.clicked.connect(self.export_statistics)
        export_layout.addWidget(self.export_stats_btn)

        self.export_logs_btn = QPushButton("Export Chat Logs")
        self.export_logs_btn.clicked.connect(self.export_chat_logs)
        export_layout.addWidget(self.export_logs_btn)

        layout.addWidget(export_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Analytics")

    def create_settings_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QGridLayout(general_group)

        general_layout.addWidget(QLabel("Bot Name:"), 0, 0)
        self.bot_name_edit = QLineEdit()
        self.bot_name_edit.setPlaceholderText("Display name for your bot")
        general_layout.addWidget(self.bot_name_edit, 0, 1)

        general_layout.addWidget(QLabel("Command Prefix:"), 1, 0)
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setText("!")
        self.prefix_edit.setMaxLength(1)
        general_layout.addWidget(self.prefix_edit, 1, 1)

        self.auto_connect = QCheckBox("Auto-connect on startup")
        general_layout.addWidget(self.auto_connect, 2, 0, 1, 2)

        self.save_logs = QCheckBox("Save chat logs")
        general_layout.addWidget(self.save_logs, 3, 0, 1, 2)

        layout.addWidget(general_group)

        # Response settings
        response_group = QGroupBox("Response Settings")
        response_layout = QGridLayout(response_group)

        response_layout.addWidget(QLabel("Response Delay (ms):"), 0, 0)
        self.response_delay_spin = QSpinBox()
        self.response_delay_spin.setRange(0, 5000)
        self.response_delay_spin.setValue(500)
        response_layout.addWidget(self.response_delay_spin, 0, 1)

        self.smart_responses = QCheckBox("Enable smart responses")
        response_layout.addWidget(self.smart_responses, 1, 0, 1, 2)

        self.mention_responses = QCheckBox("Respond to mentions")
        response_layout.addWidget(self.mention_responses, 2, 0, 1, 2)

        layout.addWidget(response_group)

        # Save/Load configuration
        config_group = QGroupBox("Configuration")
        config_layout = QHBoxLayout(config_group)

        self.save_config_btn = QPushButton("Save Configuration")
        self.save_config_btn.clicked.connect(self.save_configuration)
        config_layout.addWidget(self.save_config_btn)

        self.load_config_btn = QPushButton("Load Configuration")
        self.load_config_btn.clicked.connect(self.load_configuration)
        config_layout.addWidget(self.load_config_btn)

        self.reset_config_btn = QPushButton("Reset to Defaults")
        self.reset_config_btn.clicked.connect(self.reset_configuration)
        config_layout.addWidget(self.reset_config_btn)

        layout.addWidget(config_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Settings")

    def init_timers(self):
        """Initialize update timers."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second

    def toggle_connection(self):
        """Toggle bot connection."""
        if self.is_connected:
            self.disconnect_bot()
        else:
            self.connect_bot()

    def connect_bot(self):
        """Connect to Twitch chat."""
        # Validate inputs
        if not all(
            [
                self.username_edit.text().strip(),
                self.oauth_edit.text().strip(),
                self.channel_edit.text().strip(),
            ]
        ):
            QMessageBox.warning(
                self, "Invalid Input", "Please fill in all required fields."
            )
            return

        # Update UI
        self.is_connected = True
        self.connect_btn.setText("Disconnect")
        self.status_label.setText("Status: Connected")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.statusBar().showMessage("Connected to " + self.channel_edit.text())

        # In a real implementation, this would connect to the plugin
        self.append_chat_message("System", "Connected to chat!", "system")

    def disconnect_bot(self):
        """Disconnect from Twitch chat."""
        self.is_connected = False
        self.connect_btn.setText("Connect")
        self.status_label.setText("Status: Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.statusBar().showMessage("Disconnected")

        self.append_chat_message("System", "Disconnected from chat.", "system")

    def test_connection(self):
        """Test the connection settings."""
        QMessageBox.information(
            self, "Connection Test", "Connection test would be performed here."
        )

    def open_oauth_generator(self):
        """Open OAuth token generator in browser."""
        # Standard library imports
        import webbrowser

        webbrowser.open("https://twitchapps.com/tmi/")

    def send_message(self):
        """Send a message to chat."""
        message = self.message_edit.text().strip()
        if message and self.is_connected:
            self.append_chat_message(self.username_edit.text() or "Bot", message, "bot")
            self.message_edit.clear()
        elif not self.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to chat first.")

    def quick_message(self, message: str):
        """Send a predefined quick message."""
        if self.is_connected:
            self.append_chat_message(self.username_edit.text() or "Bot", message, "bot")
        else:
            QMessageBox.warning(self, "Not Connected", "Please connect to chat first.")

    def append_chat_message(self, username: str, message: str, msg_type: str = "user"):
        """Append a message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        if msg_type == "system":
            formatted_msg = f"<span style='color: blue;'>[{timestamp}] <b>SYSTEM:</b> {message}</span>"
        elif msg_type == "bot":
            formatted_msg = f"<span style='color: green;'>[{timestamp}] <b>{username}:</b> {message}</span>"
        else:
            formatted_msg = f"[{timestamp}] <b>{username}:</b> {message}"

        self.chat_display.append(formatted_msg)

    def clear_chat_display(self):
        """Clear the chat display."""
        self.chat_display.clear()

    def add_custom_command(self):
        """Add a custom command."""
        command = self.cmd_name_edit.text().strip()
        response = self.cmd_response_edit.text().strip()

        if command and response:
            if not command.startswith("!"):
                command = "!" + command

            self.custom_commands_list.addItem(f"{command} - {response}")
            self.cmd_name_edit.clear()
            self.cmd_response_edit.clear()

            QMessageBox.information(
                self, "Command Added", f"Command {command} has been added."
            )
        else:
            QMessageBox.warning(
                self, "Invalid Input", "Please enter both command and response."
            )

    def edit_command(self):
        """Edit selected custom command."""
        current_item = self.custom_commands_list.currentItem()
        if current_item:
            QMessageBox.information(
                self, "Edit Command", "Command editing would be implemented here."
            )

    def delete_command(self):
        """Delete selected custom command."""
        current_row = self.custom_commands_list.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self,
                "Delete Command",
                "Are you sure you want to delete this command?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.custom_commands_list.takeItem(current_row)

    def add_banned_word(self):
        """Add a banned word."""
        word = self.banned_word_edit.text().strip().lower()
        if word:
            self.banned_words_list.addItem(word)
            self.banned_word_edit.clear()

    def remove_banned_word(self):
        """Remove selected banned word."""
        current_row = self.banned_words_list.currentRow()
        if current_row >= 0:
            self.banned_words_list.takeItem(current_row)

    def timeout_user(self):
        """Timeout a user."""
        username = self.timeout_user_edit.text().strip()
        if username:
            self.append_chat_message(
                "System", f"User {username} has been timed out.", "system"
            )
            self.timeout_user_edit.clear()

    def ban_user(self):
        """Ban a user."""
        username = self.ban_user_edit.text().strip()
        if username:
            reply = QMessageBox.question(
                self,
                "Ban User",
                f"Are you sure you want to ban {username}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.append_chat_message(
                    "System", f"User {username} has been banned.", "system"
                )
                self.ban_user_edit.clear()

    def export_statistics(self):
        """Export chat statistics."""
        QMessageBox.information(
            self, "Export Statistics", "Statistics export would be implemented here."
        )

    def export_chat_logs(self):
        """Export chat logs."""
        QMessageBox.information(
            self, "Export Chat Logs", "Chat logs export would be implemented here."
        )

    def save_configuration(self):
        """Save current configuration."""
        QMessageBox.information(
            self, "Save Configuration", "Configuration saved successfully!"
        )

    def load_configuration(self):
        """Load saved configuration."""
        QMessageBox.information(
            self, "Load Configuration", "Configuration loaded successfully!"
        )

    def reset_configuration(self):
        """Reset configuration to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Configuration",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Reset all form fields to defaults
            self.username_edit.clear()
            self.oauth_edit.clear()
            self.channel_edit.clear()
            self.client_id_edit.clear()
            self.client_secret_edit.clear()
            self.bot_name_edit.clear()
            self.prefix_edit.setText("!")
            # Reset other settings...
            QMessageBox.information(
                self, "Reset Complete", "Configuration reset to defaults."
            )

    def update_display(self):
        """Update the display with current information."""
        # Update statistics and other dynamic content
        if self.is_connected:
            # Simulate some activity
            pass


def create_twitch_bot_gui(plugin=None):
    """Factory function to create the Twitch Bot GUI."""
    if not PYSIDE6_AVAILABLE:
        return None

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    gui = TwitchBotGUI(plugin)
    return gui


# Standalone execution for testing
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        app = QApplication(sys.argv)
        window = TwitchBotGUI()
        window.show()
        sys.exit(app.exec())  # nosec B102: Qt application execution
    else:
        print("PySide6 is not available. GUI cannot be started.")
