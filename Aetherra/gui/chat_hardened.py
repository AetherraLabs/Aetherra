#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
💬 Hardened Chat Interface
==========================

Chat interface with state isolation, message validation, and graceful degradation.
Protects against plugin interference and ensures reliable messaging.

Key Features:
- State isolation from plugin interference
- Message validation and sanitization
- Graceful degradation on component failures
- Thread-safe message handling
- Recovery mechanisms for corrupted state
- Plugin firewall for chat operations
"""

from __future__ import annotations

# Standard library imports
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

# Third party imports
from PySide6.QtCore import QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Chat message types."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"
    PLUGIN = "plugin"


class MessageStatus(Enum):
    """Message processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    FILTERED = "filtered"


@dataclass
class ChatMessage:
    """Validated chat message with metadata."""

    id: str
    type: MessageType
    content: str
    timestamp: float
    status: MessageStatus = MessageStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)
    thread_id: str | None = None
    user_id: str | None = None
    plugin_source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "metadata": self.metadata,
            "thread_id": self.thread_id,
            "user_id": self.user_id,
            "plugin_source": self.plugin_source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatMessage:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=MessageType(data["type"]),
            content=data["content"],
            timestamp=data["timestamp"],
            status=MessageStatus(data.get("status", "pending")),
            metadata=data.get("metadata", {}),
            thread_id=data.get("thread_id"),
            user_id=data.get("user_id"),
            plugin_source=data.get("plugin_source"),
        )


class MessageValidator:
    """Validates and sanitizes chat messages."""

    def __init__(self):
        self.max_message_length = 10000
        self.max_metadata_size = 1024
        self.blocked_patterns: list[str] = []

    def validate_message(self, message: ChatMessage) -> tuple[bool, str | None]:
        """Validate a chat message."""
        try:
            # Check content length
            if len(message.content) > self.max_message_length:
                return (
                    False,
                    f"Message too long: {len(message.content)} > {self.max_message_length}",
                )

            # Check for blocked patterns
            for pattern in self.blocked_patterns:
                if pattern.lower() in message.content.lower():
                    return False, f"Message contains blocked pattern: {pattern}"

            # Check metadata size
            metadata_size = len(json.dumps(message.metadata))
            if metadata_size > self.max_metadata_size:
                return (
                    False,
                    f"Metadata too large: {metadata_size} > {self.max_metadata_size}",
                )

            # Validate required fields
            if not message.content.strip():
                return False, "Empty message content"

            if not message.id:
                return False, "Missing message ID"

            return True, None

        except Exception as e:
            return False, f"Validation error: {e}"

    def sanitize_content(self, content: str) -> str:
        """Sanitize message content."""
        # Remove potential XSS patterns
        sanitized = content.replace("<script", "&lt;script")
        sanitized = sanitized.replace("javascript:", "")

        # Limit length
        if len(sanitized) > self.max_message_length:
            sanitized = sanitized[: self.max_message_length] + "..."

        return sanitized.strip()


class ChatStateManager:
    """Manages chat state with isolation and recovery."""

    def __init__(self):
        self._messages: list[ChatMessage] = []
        self._threads: dict[str, list[str]] = {}  # thread_id -> message_ids
        self._lock = threading.RLock()
        self._backup_state: dict[str, Any] = {}

    def add_message(self, message: ChatMessage) -> bool:
        """Add message to state with thread safety."""
        with self._lock:
            try:
                # Create backup before modification
                self._create_backup()

                self._messages.append(message)

                # Update thread index
                if message.thread_id:
                    if message.thread_id not in self._threads:
                        self._threads[message.thread_id] = []
                    self._threads[message.thread_id].append(message.id)

                return True

            except Exception as e:
                logger.error(f"Failed to add message: {e}")
                self._restore_backup()
                return False

    def get_messages(
        self, thread_id: str | None = None, limit: int | None = None
    ) -> list[ChatMessage]:
        """Get messages with optional filtering."""
        with self._lock:
            try:
                messages = self._messages.copy()

                # Filter by thread
                if thread_id:
                    messages = [msg for msg in messages if msg.thread_id == thread_id]

                # Apply limit
                if limit:
                    messages = messages[-limit:]

                return messages

            except Exception as e:
                logger.error(f"Failed to get messages: {e}")
                return []

    def update_message_status(self, message_id: str, status: MessageStatus) -> bool:
        """Update message status."""
        with self._lock:
            try:
                for message in self._messages:
                    if message.id == message_id:
                        message.status = status
                        return True
                return False

            except Exception as e:
                logger.error(f"Failed to update message status: {e}")
                return False

    def get_thread_count(self) -> int:
        """Get number of active threads."""
        with self._lock:
            return len(self._threads)

    def get_message_count(self) -> int:
        """Get total message count."""
        with self._lock:
            return len(self._messages)

    def _create_backup(self) -> None:
        """Create backup of current state."""
        self._backup_state = {
            "messages": [msg.to_dict() for msg in self._messages],
            "threads": self._threads.copy(),
            "timestamp": time.time(),
        }

    def _restore_backup(self) -> None:
        """Restore from backup state."""
        try:
            if self._backup_state:
                self._messages = [
                    ChatMessage.from_dict(msg_data) for msg_data in self._backup_state["messages"]
                ]
                self._threads = self._backup_state["threads"].copy()
                logger.warning("Restored chat state from backup")
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")


class PluginFirewall:
    """Firewall to protect chat from malicious plugin interference."""

    def __init__(self):
        self.allowed_plugins: set[str] = set()
        self.blocked_plugins: set[str] = set()
        self.plugin_permissions: dict[str, set[str]] = {}

    def check_plugin_permission(self, plugin_id: str, operation: str) -> bool:
        """Check if plugin has permission for operation."""
        if plugin_id in self.blocked_plugins:
            return False

        if plugin_id not in self.allowed_plugins:
            return False

        permissions = self.plugin_permissions.get(plugin_id, set())
        return operation in permissions

    def add_plugin_permission(self, plugin_id: str, operation: str) -> None:
        """Grant operation permission to plugin."""
        if plugin_id not in self.plugin_permissions:
            self.plugin_permissions[plugin_id] = set()
        self.plugin_permissions[plugin_id].add(operation)
        self.allowed_plugins.add(plugin_id)

    def block_plugin(self, plugin_id: str) -> None:
        """Block plugin from chat operations."""
        self.blocked_plugins.add(plugin_id)
        self.allowed_plugins.discard(plugin_id)
        logger.warning(f"Blocked plugin from chat: {plugin_id}")


class HardenedChatProcessor(QThread):
    """Background message processor with error handling."""

    # Signals
    message_processed = Signal(str)  # message_id
    processing_error = Signal(str, str)  # message_id, error

    def __init__(self, state_manager: ChatStateManager):
        super().__init__()
        self.state_manager = state_manager
        self._stop_requested = False
        self._processing_queue: list[str] = []
        self._queue_lock = threading.Lock()

    def queue_message(self, message_id: str) -> None:
        """Queue message for processing."""
        with self._queue_lock:
            self._processing_queue.append(message_id)

    def run(self):
        """Process queued messages."""
        while not self._stop_requested:
            try:
                message_id = None

                # Get next message
                with self._queue_lock:
                    if self._processing_queue:
                        message_id = self._processing_queue.pop(0)

                if message_id:
                    self._process_message(message_id)
                else:
                    self.msleep(100)  # Wait for messages

            except Exception as e:
                logger.error(f"Processing error: {e}")
                if message_id:
                    self.processing_error.emit(message_id, str(e))

    def _process_message(self, message_id: str) -> None:
        """Process a single message."""
        try:
            # Update status
            self.state_manager.update_message_status(message_id, MessageStatus.PROCESSING)

            # Simulate processing (integrate with AI/backend here)
            self.msleep(100)

            # Complete processing
            self.state_manager.update_message_status(message_id, MessageStatus.COMPLETED)
            self.message_processed.emit(message_id)

        except Exception as e:
            self.state_manager.update_message_status(message_id, MessageStatus.FAILED)
            self.processing_error.emit(message_id, str(e))

    def stop(self):
        """Stop the processor."""
        self._stop_requested = True


class HardenedChatInterface(QWidget):
    """
    Hardened chat interface with protection against plugin interference.

    Features:
    - State isolation with backup/recovery
    - Message validation and sanitization
    - Plugin firewall for operations
    - Graceful degradation on failures
    - Thread-safe message handling
    """

    # Signals
    message_sent = Signal(object)  # ChatMessage
    message_received = Signal(object)  # ChatMessage
    error_occurred = Signal(str)  # error message

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Core components
        self.state_manager = ChatStateManager()
        self.validator = MessageValidator()
        self.firewall = PluginFirewall()

        # Message processor
        self.processor = HardenedChatProcessor(self.state_manager)
        self.processor.message_processed.connect(self._on_message_processed)
        self.processor.processing_error.connect(self._on_processing_error)
        self.processor.start()

        # UI state
        self.current_thread_id = str(uuid4())
        self.degraded_mode = False

        # Setup UI
        self._setup_ui()

        # Health monitoring
        self._health_timer = QTimer()
        self._health_timer.timeout.connect(self._check_health)
        self._health_timer.start(5000)  # Check every 5 seconds

        logger.info("HardenedChatInterface initialized")

    def _setup_ui(self) -> None:
        """Setup the chat interface UI."""
        layout = QVBoxLayout(self)

        # Chat display area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_scroll.setWidget(self.chat_content)
        layout.addWidget(self.chat_scroll)

        # Status display
        self.status_label = QLabel("Chat Ready")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Input area
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.returnPressed.connect(self._send_message)
        layout.addWidget(self.input_field)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        layout.addWidget(self.send_button)

        # Load existing messages
        self._refresh_display()

    def send_user_message(self, content: str, user_id: str | None = None) -> bool:
        """Send a user message with validation."""
        try:
            # Create message
            message = ChatMessage(
                id=str(uuid4()),
                type=MessageType.USER,
                content=content,
                timestamp=time.time(),
                thread_id=self.current_thread_id,
                user_id=user_id,
            )

            # Validate message
            valid, error = self.validator.validate_message(message)
            if not valid:
                self._show_error(f"Message validation failed: {error}")
                return False

            # Sanitize content
            message.content = self.validator.sanitize_content(message.content)

            # Add to state
            if not self.state_manager.add_message(message):
                self._show_error("Failed to add message to state")
                return False

            # Queue for processing
            self.processor.queue_message(message.id)

            # Update UI
            self._add_message_to_display(message)
            self.message_sent.emit(message)

            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self._show_error(f"Send failed: {e}")
            return False

    def add_plugin_message(self, content: str, plugin_id: str) -> bool:
        """Add message from plugin with permission check."""
        try:
            # Check plugin permissions
            if not self.firewall.check_plugin_permission(plugin_id, "send_message"):
                logger.warning(f"Plugin {plugin_id} denied message permission")
                return False

            # Create plugin message
            message = ChatMessage(
                id=str(uuid4()),
                type=MessageType.PLUGIN,
                content=content,
                timestamp=time.time(),
                thread_id=self.current_thread_id,
                plugin_source=plugin_id,
            )

            # Validate and sanitize
            valid, error = self.validator.validate_message(message)
            if not valid:
                logger.warning(f"Plugin message validation failed: {error}")
                return False

            message.content = self.validator.sanitize_content(message.content)

            # Add to state
            if self.state_manager.add_message(message):
                self._add_message_to_display(message)
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to add plugin message: {e}")
            return False

    def get_recent_messages(self, count: int = 10) -> list[ChatMessage]:
        """Get recent messages safely."""
        try:
            return self.state_manager.get_messages(thread_id=self.current_thread_id, limit=count)
        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            return []

    def enable_degraded_mode(self) -> None:
        """Enable degraded mode for error recovery."""
        self.degraded_mode = True
        self.status_label.setText("Degraded Mode - Limited Functionality")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")

        # Disable potentially problematic features
        self.send_button.setEnabled(False)
        logger.warning("Enabled degraded mode")

    def disable_degraded_mode(self) -> None:
        """Disable degraded mode."""
        self.degraded_mode = False
        self.status_label.setText("Chat Ready")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.send_button.setEnabled(True)
        logger.info("Disabled degraded mode")

    @Slot()
    def _send_message(self) -> None:
        """Handle send button click."""
        if self.degraded_mode:
            self._show_error("Chat in degraded mode")
            return

        content = self.input_field.text().strip()
        if content:
            if self.send_user_message(content):
                self.input_field.clear()

    def _add_message_to_display(self, message: ChatMessage) -> None:
        """Add message to chat display."""
        try:
            # Create message widget
            msg_widget = QLabel()
            msg_widget.setWordWrap(True)
            msg_widget.setStyleSheet(self._get_message_style(message.type))

            # Format message content
            timestamp = time.strftime("%H:%M:%S", time.localtime(message.timestamp))
            prefix = self._get_message_prefix(message.type)
            msg_widget.setText(f"[{timestamp}] {prefix}: {message.content}")

            # Add to layout
            self.chat_layout.addWidget(msg_widget)

            # Auto-scroll to bottom
            QApplication.processEvents()
            self.chat_scroll.verticalScrollBar().setValue(
                self.chat_scroll.verticalScrollBar().maximum()
            )

        except Exception as e:
            logger.error(f"Failed to add message to display: {e}")

    def _get_message_style(self, msg_type: MessageType) -> str:
        """Get CSS style for message type."""
        styles = {
            MessageType.USER: "background-color: #e3f2fd; padding: 8px; margin: 2px; border-radius: 4px;",
            MessageType.ASSISTANT: "background-color: #f3e5f5; padding: 8px; margin: 2px; border-radius: 4px;",
            MessageType.SYSTEM: "background-color: #fff3e0; padding: 8px; margin: 2px; border-radius: 4px;",
            MessageType.ERROR: "background-color: #ffebee; color: #d32f2f; padding: 8px; margin: 2px; border-radius: 4px;",
            MessageType.PLUGIN: "background-color: #e8f5e8; padding: 8px; margin: 2px; border-radius: 4px;",
        }
        return styles.get(msg_type, "padding: 8px; margin: 2px;")

    def _get_message_prefix(self, msg_type: MessageType) -> str:
        """Get display prefix for message type."""
        prefixes = {
            MessageType.USER: "You",
            MessageType.ASSISTANT: "AI",
            MessageType.SYSTEM: "System",
            MessageType.ERROR: "Error",
            MessageType.PLUGIN: "Plugin",
        }
        return prefixes.get(msg_type, "Unknown")

    def _refresh_display(self) -> None:
        """Refresh the chat display."""
        try:
            # Clear existing display
            for i in reversed(range(self.chat_layout.count())):
                self.chat_layout.itemAt(i).widget().setParent(None)

            # Add all messages
            messages = self.state_manager.get_messages(thread_id=self.current_thread_id)
            for message in messages:
                self._add_message_to_display(message)

        except Exception as e:
            logger.error(f"Failed to refresh display: {e}")
            self._show_error("Display refresh failed")

    def _show_error(self, message: str) -> None:
        """Show error message."""
        error_msg = ChatMessage(
            id=str(uuid4()),
            type=MessageType.ERROR,
            content=message,
            timestamp=time.time(),
            thread_id=self.current_thread_id,
        )

        self._add_message_to_display(error_msg)
        self.error_occurred.emit(message)

    @Slot()
    def _check_health(self) -> None:
        """Check chat system health."""
        try:
            # Check processor thread
            if not self.processor.isRunning():
                logger.warning("Message processor stopped, restarting...")
                self.processor.start()

            # Check state manager
            msg_count = self.state_manager.get_message_count()
            if msg_count < 0:  # Impossible value indicates corruption
                logger.error("State corruption detected")
                self.enable_degraded_mode()

            # Check UI responsiveness
            app = QApplication.instance()
            if app and not app.thread().isRunning():
                logger.warning("UI thread unresponsive")

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.enable_degraded_mode()

    @Slot(str)
    def _on_message_processed(self, message_id: str) -> None:
        """Handle message processing completion."""
        logger.debug(f"Message processed: {message_id}")

    @Slot(str, str)
    def _on_processing_error(self, message_id: str, error: str) -> None:
        """Handle message processing errors."""
        logger.error(f"Processing error for {message_id}: {error}")
        self._show_error(f"Processing failed: {error}")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.processor.isRunning():
            self.processor.stop()
            self.processor.quit()
            self.processor.wait(5000)

        self._health_timer.stop()
        logger.info("HardenedChatInterface cleaned up")
