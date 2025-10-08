#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Lyrixa GUI (clean baseline with plugin discovery and event bus publish)."""

from __future__ import annotations

import logging
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication as QtApplication,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .event_bus import EventFactory, LayoutEvent, PluginEvent, get_event_bus
from .plugin_ui_host import PluginUIManager
from .zone_manager import LayoutMode, ZoneManager, ZoneType

logger = logging.getLogger(__name__)


class LyrixaGUI(QMainWindow):
    layout_mode_changed = Signal(LayoutMode)
    plugin_zone_added = Signal(str)
    plugin_zone_removed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_bus = get_event_bus()
        self.zone_manager = ZoneManager(self)
        self.plugin_manager = PluginUIManager(self)
        self._core_widgets: dict[str, QWidget] = {}
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_shortcuts()
        self._setup_event_connections()
        self._performance_timer = QTimer()
        self._performance_timer.timeout.connect(self._monitor_performance)
        self._performance_timer.start(5000)
        logger.info("LyrixaGUI initialized")
        # Auto-discover plugins on startup (non-fatal if it fails)
        self._auto_discover_startup()

    def _auto_discover_startup(self) -> None:
        """Attempt initial plugin discovery on startup."""
        try:
            discovered = self.plugin_manager.discover_plugins(reload=False)
            if discovered:
                self.statusBar().showMessage(
                    f"Discovered {len(discovered)} plugin(s) on startup", 4000
                )
                logger.info(
                    "Startup discovery loaded plugins: %s", ", ".join(discovered)
                )
            else:
                logger.info("No plugins discovered at startup")
        except Exception as e:  # pragma: no cover - defensive
            logger.error("Startup plugin discovery failed: %s", e)

    def _setup_ui(self) -> None:
        self.setWindowTitle("Lyrixa - AI Operating System GUI")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.main_splitter = QSplitter()
        layout.addWidget(self.main_splitter)
        self._create_zone_containers()
        self._setup_status_bar()
        self.zone_manager.register_core_widgets(self._core_widgets)

    def _create_zone_containers(self) -> None:
        from PySide6.QtCore import Qt
        self.chat_container = QTabWidget()
        self.chat_container.setObjectName("chat_zone")
        self.chat_container.setMinimumWidth(300)
        self._core_widgets["chat_zone"] = self.chat_container
        self.right_splitter = QSplitter()
        self.right_splitter.setOrientation(Qt.Orientation.Vertical)
        self.plugin_container = QTabWidget()
        self.plugin_container.setObjectName("plugin_zone")
        self._core_widgets["plugin_zone"] = self.plugin_container
        self.inspector_container = QTabWidget()
        self.inspector_container.setObjectName("inspector_zone")
        self.inspector_container.setMaximumHeight(300)
        self._core_widgets["inspector_zone"] = self.inspector_container
        self.right_splitter.addWidget(self.plugin_container)
        self.right_splitter.addWidget(self.inspector_container)
        self.right_splitter.setSizes([500, 200])
        self.main_splitter.addWidget(self.chat_container)
        self.main_splitter.addWidget(self.right_splitter)
        self.main_splitter.setSizes([720, 480])
        self.main_splitter.splitterMoved.connect(self._on_main_splitter_moved)
        self.right_splitter.splitterMoved.connect(self._on_right_splitter_moved)

    def _setup_menu_bar(self) -> None:
        bar = self.menuBar()
        view_menu = bar.addMenu("&View")
        act_chat = QAction("&Chat Focus", self)
        act_chat.setShortcut(QKeySequence("Ctrl+1"))
        act_chat.triggered.connect(lambda: self.set_layout_mode(LayoutMode.CHAT_FOCUS))
        view_menu.addAction(act_chat)
        act_plugin = QAction("&Plugin Focus", self)
        act_plugin.setShortcut(QKeySequence("Ctrl+2"))
        act_plugin.triggered.connect(lambda: self.set_layout_mode(LayoutMode.PLUGIN_FOCUS))
        view_menu.addAction(act_plugin)
        act_split = QAction("&Split View", self)
        act_split.setShortcut(QKeySequence("Ctrl+3"))
        act_split.triggered.connect(lambda: self.set_layout_mode(LayoutMode.SPLIT))
        view_menu.addAction(act_split)
        plugin_menu = bar.addMenu("&Plugins")
        refresh = QAction("&Refresh Plugins", self)
        refresh.setShortcut(QKeySequence("F5"))
        refresh.triggered.connect(self._refresh_plugins)
        plugin_menu.addAction(refresh)
        help_menu = bar.addMenu("&Help")
        about = QAction("&About Lyrixa", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("F11"), self, self._toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, self._toggle_inspector)

    def _setup_event_connections(self) -> None:
        self.zone_manager.layout_changed.connect(self._on_layout_changed)
        self.zone_manager.mode_changed.connect(self._on_mode_changed)
        self.plugin_manager.plugin_loaded.connect(self._on_plugin_loaded)
        self.plugin_manager.plugin_unloaded.connect(self._on_plugin_unloaded)
        self.plugin_manager.plugin_error.connect(self._on_plugin_error)
        self.event_bus.subscribe(LayoutEvent, self._handle_layout_event)
        self.event_bus.subscribe(PluginEvent, self._handle_plugin_event)

    def _setup_status_bar(self) -> None:
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Lyrixa GUI Ready")
        self._update_status_bar()

    def set_layout_mode(self, mode: LayoutMode) -> None:
        if mode == LayoutMode.CHAT_FOCUS:
            self.main_splitter.setSizes([1000, 200])
            self.right_splitter.setSizes([150, 50])
        elif mode == LayoutMode.PLUGIN_FOCUS:
            self.main_splitter.setSizes([300, 900])
            self.right_splitter.setSizes([700, 200])
        else:
            self.main_splitter.setSizes([720, 480])
            self.right_splitter.setSizes([400, 200])
        self.zone_manager.set_mode(mode)
        self.layout_mode_changed.emit(mode)
        self.event_bus.publish(EventFactory.layout_mode_changed(mode.value, "lyrixa_gui"))
        self._update_status_bar()

    def _update_status_bar(self) -> None:
        mode = self.zone_manager.get_mode()
        plugin_count = len(self.plugin_manager.list_loaded_plugins())
        self.statusBar().showMessage(f"Mode: {mode.value.title()} | Plugins: {plugin_count}")

    def _monitor_performance(self) -> None:
        app = QtApplication.instance()
        if app:
            widget_count = len(getattr(app, "allWidgets", lambda: [])())
            self.event_bus.publish(
                EventFactory.performance_metric("widget_count", widget_count, "count", "lyrixa_gui")
            )

    # Event handlers
    @Slot(object)
    def _on_layout_changed(self, diff) -> None:  # noqa: D401
        self._update_status_bar()

    @Slot(LayoutMode)
    def _on_mode_changed(self, mode: LayoutMode) -> None:  # noqa: D401
        self._update_status_bar()

    @Slot(str)
    def _on_plugin_loaded(self, plugin_id: str) -> None:
        self.plugin_zone_added.emit(plugin_id)
        self._update_status_bar()

    @Slot(str)
    def _on_plugin_unloaded(self, plugin_id: str) -> None:
        self.plugin_zone_removed.emit(plugin_id)
        self._update_status_bar()

    @Slot(str, str)
    def _on_plugin_error(self, plugin_id: str, error: str) -> None:
        self.statusBar().showMessage(f"Plugin error: {plugin_id} - {error}", 8000)

    @Slot(int, int)
    def _on_main_splitter_moved(self, pos: int, index: int) -> None:  # noqa: ARG002
        sizes = self.main_splitter.sizes()
        if sum(sizes) > 0:
            self.zone_manager.set_split_ratio("main", sizes[0] / sum(sizes))

    @Slot(int, int)
    def _on_right_splitter_moved(self, pos: int, index: int) -> None:  # noqa: ARG002
        sizes = self.right_splitter.sizes()
        if sum(sizes) > 0:
            self.zone_manager.set_split_ratio("right", sizes[0] / sum(sizes))

    def _handle_layout_event(self, event: LayoutEvent) -> None:  # noqa: D401
        logger.debug("layout event %s", event.type)

    def _handle_plugin_event(self, event: PluginEvent) -> None:  # noqa: D401
        logger.debug("plugin event %s", event.type)

    # Actions
    def _refresh_plugins(self) -> None:
        self.statusBar().showMessage("Discovering plugins...", 2000)
        discovered = self.plugin_manager.discover_plugins(reload=False)
        self.statusBar().showMessage(
            f"Plugins active: {len(self.plugin_manager.list_loaded_plugins())}", 4000
        )
        logger.info("Plugin discovery complete (active=%d)", len(discovered))

    def _show_about(self) -> None:
        self.statusBar().showMessage("Lyrixa GUI v1.0 - AI Operating System Interface", 5000)

    def _toggle_fullscreen(self) -> None:
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def _toggle_inspector(self) -> None:
        self.inspector_container.setVisible(not self.inspector_container.isVisible())


def create_lyrixa_gui() -> LyrixaGUI:
    return LyrixaGUI()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = QtApplication(sys.argv)
    gui = create_lyrixa_gui()
    gui.show()
    sys.exit(app.exec())
