#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎯 LyrixaGUI - Main GUI Window
=============================

Main GUI window integrating all components from the stable release spec.
Implements zone-based layout with plugin isolation and unified messaging.

Key Features:
- Zone-based layout management with dynamic reconfiguration
- Plugin sandboxing with WebView isolation
- Chat interface with hardened state isolation
- Performance monitoring with resource budgets
- Keyboard shortcuts for layout modes (Ctrl+1/2/3)
- Event-driven architecture with Qt + async integration
"""

from __future__ import annotations

# Standard library imports
import logging
from pathlib import Path

# Third party imports
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Local imports
from .event_bus import EventFactory, LayoutEvent, PluginEvent, get_event_bus
from .plugin_ui_host import PluginUIManager
from .zone_manager import LayoutMode, ZoneManager, ZoneType

logger = logging.getLogger(__name__)


class LyrixaGUI(QMainWindow):
    """
    Main Lyrixa GUI window with zone-based layout management.

    Integrates ZoneManager, PluginUIHost, and EventBus for a cohesive
    plugin-safe GUI experience with chat reliability.
    """

    # Signals
    layout_mode_changed = Signal(LayoutMode)
    plugin_zone_added = Signal(str)
    plugin_zone_removed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize components
        self.event_bus = get_event_bus()
        self.zone_manager = ZoneManager(self)
        self.plugin_manager = PluginUIManager(self)

        # Core widgets
        self._core_widgets = {}

        # Setup UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_shortcuts()
        self._setup_event_connections()

        # Performance monitoring
        self._performance_timer = QTimer()
        self._performance_timer.timeout.connect(self._monitor_performance)
        self._performance_timer.start(5000)  # Check every 5 seconds

        logger.info("LyrixaGUI initialized")

    def _setup_ui(self) -> None:
        """Setup the main UI structure."""
        self.setWindowTitle("Lyrixa - AI Operating System GUI")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter for zones
        self.main_splitter = QSplitter()
        main_layout.addWidget(self.main_splitter)

        # Create zone containers
        self._create_zone_containers()

        # Setup status bar
        self._setup_status_bar()

        # Register core widgets with zone manager
        self.zone_manager.register_core_widgets(self._core_widgets)

        logger.debug("UI structure created")

    def _create_zone_containers(self) -> None:
        """Create the main zone containers."""
        # Left side: Chat zone
        self.chat_container = QTabWidget()
        self.chat_container.setObjectName("chat_zone")
        self.chat_container.setMinimumWidth(300)
        self._core_widgets["chat_zone"] = self.chat_container

        # Right side: Plugin zones (split vertically)
        self.right_splitter = QSplitter()
        self.right_splitter.setOrientation(self.right_splitter.Orientation.Vertical)

        # Plugin main area
        self.plugin_container = QTabWidget()
        self.plugin_container.setObjectName("plugin_zone")
        self._core_widgets["plugin_zone"] = self.plugin_container

        # Inspector/drawer area
        self.inspector_container = QTabWidget()
        self.inspector_container.setObjectName("inspector_zone")
        self.inspector_container.setMaximumHeight(300)
        self._core_widgets["inspector_zone"] = self.inspector_container

        # Setup right splitter
        self.right_splitter.addWidget(self.plugin_container)
        self.right_splitter.addWidget(self.inspector_container)
        self.right_splitter.setSizes([500, 200])  # Plugin larger than inspector

        # Add to main splitter
        self.main_splitter.addWidget(self.chat_container)
        self.main_splitter.addWidget(self.right_splitter)

        # Set initial split ratio (60% chat, 40% plugins)
        self.main_splitter.setSizes([720, 480])

        # Connect splitter signals for state preservation
        self.main_splitter.splitterMoved.connect(self._on_main_splitter_moved)
        self.right_splitter.splitterMoved.connect(self._on_right_splitter_moved)

    def _setup_menu_bar(self) -> None:
        """Setup the application menu bar."""
        menubar = self.menuBar()

        # View menu for layout modes
        view_menu = menubar.addMenu("&View")

        # Layout mode actions
        chat_focus_action = QAction("&Chat Focus", self)
        chat_focus_action.setShortcut(QKeySequence("Ctrl+1"))
        chat_focus_action.triggered.connect(
            lambda: self.set_layout_mode(LayoutMode.CHAT_FOCUS)
        )
        view_menu.addAction(chat_focus_action)

        plugin_focus_action = QAction("&Plugin Focus", self)
        plugin_focus_action.setShortcut(QKeySequence("Ctrl+2"))
        plugin_focus_action.triggered.connect(
            lambda: self.set_layout_mode(LayoutMode.PLUGIN_FOCUS)
        )
        view_menu.addAction(plugin_focus_action)

        split_action = QAction("&Split View", self)
        split_action.setShortcut(QKeySequence("Ctrl+3"))
        split_action.triggered.connect(lambda: self.set_layout_mode(LayoutMode.SPLIT))
        view_menu.addAction(split_action)

        view_menu.addSeparator()

        # Plugin menu
        plugin_menu = menubar.addMenu("&Plugins")

        refresh_action = QAction("&Refresh Plugins", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._refresh_plugins)
        plugin_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About Lyrixa", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Layout mode shortcuts (already in menu, but adding direct shortcuts)
        QShortcut(
            QKeySequence("Ctrl+1"),
            self,
            lambda: self.set_layout_mode(LayoutMode.CHAT_FOCUS),
        )
        QShortcut(
            QKeySequence("Ctrl+2"),
            self,
            lambda: self.set_layout_mode(LayoutMode.PLUGIN_FOCUS),
        )
        QShortcut(
            QKeySequence("Ctrl+3"), self, lambda: self.set_layout_mode(LayoutMode.SPLIT)
        )

        # Additional shortcuts
        QShortcut(QKeySequence("F11"), self, self._toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, self._toggle_inspector)

    def _setup_event_connections(self) -> None:
        """Setup event bus connections."""
        # Zone manager events
        self.zone_manager.layout_changed.connect(self._on_layout_changed)
        self.zone_manager.mode_changed.connect(self._on_mode_changed)

        # Plugin manager events
        self.plugin_manager.plugin_loaded.connect(self._on_plugin_loaded)
        self.plugin_manager.plugin_unloaded.connect(self._on_plugin_unloaded)
        self.plugin_manager.plugin_error.connect(self._on_plugin_error)

        # Subscribe to events on the event bus
        self.event_bus.subscribe(LayoutEvent, self._handle_layout_event)
        self.event_bus.subscribe(PluginEvent, self._handle_plugin_event)

        logger.debug("Event connections established")

    def _setup_status_bar(self) -> None:
        """Setup the status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Initial status
        status_bar.showMessage("Lyrixa GUI Ready")

        # Add permanent widgets
        self.mode_label = status_bar.addPermanentWidget(QWidget())
        self.plugin_count_label = status_bar.addPermanentWidget(QWidget())

        self._update_status_bar()

    def set_layout_mode(self, mode: LayoutMode) -> None:
        """Set the layout mode and emit events."""
        logger.info(f"Setting layout mode: {mode}")

        # Apply layout changes based on mode
        if mode == LayoutMode.CHAT_FOCUS:
            # Collapse right side
            self.main_splitter.setSizes([1000, 200])
            self.right_splitter.setSizes([150, 50])
        elif mode == LayoutMode.PLUGIN_FOCUS:
            # Expand plugin area
            self.main_splitter.setSizes([300, 900])
            self.right_splitter.setSizes([700, 200])
        elif mode == LayoutMode.SPLIT:
            # Balanced split
            self.main_splitter.setSizes([720, 480])
            self.right_splitter.setSizes([400, 200])

        # Update zone manager
        self.zone_manager.set_mode(mode)

        # Emit signal
        self.layout_mode_changed.emit(mode)

        # Emit event
        event = EventFactory.layout_mode_changed(mode.value, "lyrixa_gui")
        self.event_bus.emit(event)

        self._update_status_bar()

    def load_plugin(self, plugin_path: Path) -> bool:
        """Load a plugin from the given path."""
        try:
            plugin_id = plugin_path.name
            host = self.plugin_manager.load_plugin(plugin_id, plugin_path)

            if host:
                # Add to appropriate zone based on manifest
                zone_type = ZoneType.RIGHT_PLUGIN  # Default
                container = self.plugin_container

                if zone_type == ZoneType.LEFT_CHAT:
                    container = self.chat_container
                elif zone_type == ZoneType.RIGHT_INSPECTOR:
                    container = self.inspector_container

                container.addTab(host, host.manifest.name)
                logger.info(f"Loaded plugin {plugin_id} in {zone_type}")
                return True

        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")

        return False

    def unload_plugin(self, plugin_id: str) -> None:
        """Unload a plugin by ID."""
        host = self.plugin_manager.get_host(plugin_id)
        if host:
            # Remove from all containers
            for container in [
                self.chat_container,
                self.plugin_container,
                self.inspector_container,
            ]:
                for i in range(container.count()):
                    if container.widget(i) == host:
                        container.removeTab(i)
                        break

            # Unload from manager
            self.plugin_manager.unload_plugin(plugin_id)
            logger.info(f"Unloaded plugin {plugin_id}")

    def _monitor_performance(self) -> None:
        """Monitor GUI performance and emit metrics."""
        # Simple performance monitoring
        app = QApplication.instance()
        if app:
            # Memory usage estimation
            widget_count = len(app.allWidgets())

            # Emit performance events
            event = EventFactory.performance_metric(
                "widget_count", widget_count, "count", "lyrixa_gui"
            )
            self.event_bus.emit(event)

            if widget_count > 1000:  # Threshold
                logger.warning(f"High widget count: {widget_count}")

    def _update_status_bar(self) -> None:
        """Update status bar information."""
        mode = self.zone_manager.get_mode()
        plugin_count = len(self.plugin_manager.list_loaded_plugins())

        self.statusBar().showMessage(
            f"Mode: {mode.value.title()} | Plugins: {plugin_count}"
        )

    # Event handlers
    @Slot(object)
    def _on_layout_changed(self, diff) -> None:
        """Handle layout changes from zone manager."""
        logger.debug(f"Layout changed: {diff}")
        self._update_status_bar()

    @Slot(LayoutMode)
    def _on_mode_changed(self, mode: LayoutMode) -> None:
        """Handle layout mode changes."""
        logger.debug(f"Layout mode changed to: {mode}")
        self._update_status_bar()

    @Slot(str)
    def _on_plugin_loaded(self, plugin_id: str) -> None:
        """Handle plugin loaded events."""
        logger.info(f"Plugin loaded: {plugin_id}")
        self.plugin_zone_added.emit(plugin_id)
        self._update_status_bar()

    @Slot(str)
    def _on_plugin_unloaded(self, plugin_id: str) -> None:
        """Handle plugin unloaded events."""
        logger.info(f"Plugin unloaded: {plugin_id}")
        self.plugin_zone_removed.emit(plugin_id)
        self._update_status_bar()

    @Slot(str, str)
    def _on_plugin_error(self, plugin_id: str, error: str) -> None:
        """Handle plugin error events."""
        logger.error(f"Plugin {plugin_id} error: {error}")
        self.statusBar().showMessage(f"Plugin error: {plugin_id} - {error}", 10000)

    @Slot(int, int)
    def _on_main_splitter_moved(self, pos: int, index: int) -> None:
        """Handle main splitter movement for state preservation."""
        sizes = self.main_splitter.sizes()
        if sum(sizes) > 0:
            ratio = sizes[0] / sum(sizes)
            self.zone_manager.set_split_ratio("main", ratio)

    @Slot(int, int)
    def _on_right_splitter_moved(self, pos: int, index: int) -> None:
        """Handle right splitter movement for state preservation."""
        sizes = self.right_splitter.sizes()
        if sum(sizes) > 0:
            ratio = sizes[0] / sum(sizes)
            self.zone_manager.set_split_ratio("right", ratio)

    def _handle_layout_event(self, event: LayoutEvent) -> None:
        """Handle layout events from the event bus."""
        logger.debug(f"Received layout event: {event.type}")

    def _handle_plugin_event(self, event: PluginEvent) -> None:
        """Handle plugin events from the event bus."""
        logger.debug(f"Received plugin event: {event.type} for {event.plugin_id}")

    # Menu actions
    def _refresh_plugins(self) -> None:
        """Refresh plugin list and reload."""
        # This would scan plugin directories and reload
        logger.info("Refreshing plugins...")
        self.statusBar().showMessage("Refreshing plugins...", 3000)

    def _show_about(self) -> None:
        """Show about dialog."""
        # Simple about message in status bar for now
        self.statusBar().showMessage(
            "Lyrixa GUI v1.0 - AI Operating System Interface", 5000
        )

    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _toggle_inspector(self) -> None:
        """Toggle inspector panel visibility."""
        if self.inspector_container.isVisible():
            self.inspector_container.hide()
        else:
            self.inspector_container.show()


def create_lyrixa_gui() -> LyrixaGUI:
    """Factory function to create the main GUI."""
    return LyrixaGUI()


if __name__ == "__main__":
    # Standard library imports
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Aetherra Labs")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and show GUI
    gui = create_lyrixa_gui()
    gui.show()

    sys.exit(app.exec())  # nosec B102: Qt application execution
