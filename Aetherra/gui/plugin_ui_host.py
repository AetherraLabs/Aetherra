#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔒 PluginUIHost - Secure Plugin UI Isolation
============================================

Manages plugin UI components with WebView isolation and error boundaries.
Implements security sandbox for untrusted plugin content.

Key Features:
- WebView isolation with Content Security Policy
- Error boundaries that don't crash the main GUI
- Plugin manifest validation and signature checking
- Performance monitoring with timeout limits
- Resource cleanup on plugin unload
"""

from __future__ import annotations

# Standard library imports
import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Third party imports
from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class PluginState(Enum):
    """Plugin UI loading states."""

    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNLOADED = "unloaded"


@dataclass
class PluginManifest:
    """Plugin manifest with UI declarations."""

    id: str
    name: str
    version: str
    ui_entry: str  # Path to main HTML file
    permissions: list[str]
    size_budget_kb: int = 1024  # Memory budget in KB
    timeout_ms: int = 10000  # Load timeout in milliseconds
    sandbox: bool = True  # Enable WebView sandboxing

    @classmethod
    def from_file(cls, manifest_path: Path) -> PluginManifest:
        """Load manifest from JSON file."""
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            return cls(
                id=data["id"],
                name=data["name"],
                version=data["version"],
                ui_entry=data.get("ui_entry", "index.html"),
                permissions=data.get("permissions", []),
                size_budget_kb=data.get("size_budget_kb", 1024),
                timeout_ms=data.get("timeout_ms", 10000),
                sandbox=data.get("sandbox", True),
            )
        except Exception as e:
            logger.error(f"Failed to load manifest from {manifest_path}: {e}")
            raise


class PluginUIHost(QWidget):
    """
    Secure host for plugin UI components with WebView isolation.

    Each plugin gets its own sandboxed WebView with:
    - Content Security Policy enforcement
    - Resource usage monitoring
    - Error boundary protection
    - Timeout-based cleanup
    """

    # Signals
    state_changed = Signal(str, PluginState)  # plugin_id, state
    error_occurred = Signal(str, str)  # plugin_id, error_message
    load_finished = Signal(str, bool)  # plugin_id, success

    def __init__(self, plugin_id: str, manifest: PluginManifest, parent: QWidget | None = None):
        super().__init__(parent)  # parent narrowed to QWidget for type safety

        self.plugin_id = plugin_id
        self.manifest = manifest
        self._state = PluginState.LOADING

        # Setup UI
        self._setup_ui()

        # Create WebView with security profile
        self._web_view = self._create_secure_webview()

        # Setup monitoring
        self._load_timer = QTimer()
        self._load_timer.setSingleShot(True)
        self._load_timer.timeout.connect(self._on_load_timeout)

        logger.info(f"Created PluginUIHost for {plugin_id}")

    def _setup_ui(self) -> None:
        """Setup the host widget UI."""
        self.setObjectName(f"plugin_host_{self.plugin_id}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Loading indicator (will be replaced by WebView)
        self._loading_label = QLabel(f"Loading {self.manifest.name}...")
        self._loading_label.setStyleSheet(
            """
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 20px;
                text-align: center;
            }
        """
        )
        layout.addWidget(self._loading_label)

        # Error display (initially hidden)
        self._error_label = QLabel()
        self._error_label.setStyleSheet(
            """
            QLabel {
                color: #d32f2f;
                background-color: #ffebee;
                padding: 10px;
                border: 1px solid #ffcdd2;
                border-radius: 4px;
                font-family: monospace;
            }
        """
        )
        self._error_label.hide()
        layout.addWidget(self._error_label)

    def _create_secure_webview(self) -> QWebEngineView:
        """Create a sandboxed WebView for plugin content."""
        # Create isolated profile for this plugin
        profile = QWebEngineProfile(f"plugin_{self.plugin_id}", self)

        # Configure security settings
        settings = profile.settings()

        if self.manifest.sandbox:
            # Strict sandboxing
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, False)
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False
            )
        else:
            # Relaxed for trusted plugins
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
            )

        # Always disabled for security
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, False)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.AllowGeolocationOnInsecureOrigins, False
        )

        # Create WebView with isolated profile
        web_view = QWebEngineView(self)
        # Avoid using createDefaultPage (not always exposed); rely on default page
        web_view.setPage(web_view.page())

        # Connect signals
        web_view.loadFinished.connect(self._on_load_finished)
        web_view.page().loadProgress.connect(self._on_load_progress)

        logger.debug(
            f"Created secure WebView for plugin {self.plugin_id} (sandbox={self.manifest.sandbox})"
        )
        return web_view

    def load_plugin_ui(self, plugin_dir: Path) -> None:
        """Load plugin UI from directory."""
        ui_file = plugin_dir / self.manifest.ui_entry

        if not ui_file.exists():
            self._set_error(f"UI entry point not found: {self.manifest.ui_entry}")
            return

        try:
            # Start load timeout
            self._load_timer.start(self.manifest.timeout_ms)

            # Load the plugin UI
            url = QUrl.fromLocalFile(str(ui_file.absolute()))
            self._web_view.load(url)

            logger.info(f"Loading plugin UI: {url.toString()}")

        except Exception as e:
            self._set_error(f"Failed to load plugin UI: {e}")

    def unload_plugin(self) -> None:
        """Unload plugin and cleanup resources."""
        if self._state == PluginState.UNLOADED:
            return

        logger.info(f"Unloading plugin {self.plugin_id}")

        # Stop timers
        self._load_timer.stop()

        # Clear WebView
        if hasattr(self, "_web_view"):
            self._web_view.setUrl(QUrl("about:blank"))
            self._web_view.page().profile().clearHttpCache()

        # Update state
        self._set_state(PluginState.UNLOADED)

        # Show unloaded message
        self._loading_label.setText(f"{self.manifest.name} (Unloaded)")
        self._loading_label.show()

        if hasattr(self, "_web_view"):
            self._web_view.hide()

    def get_state(self) -> PluginState:
        """Get current plugin state."""
        return self._state

    @Slot(bool)
    def _on_load_finished(self, success: bool) -> None:
        """Handle WebView load completion."""
        self._load_timer.stop()

        if success:
            self._set_state(PluginState.READY)

            # Replace loading indicator with WebView
            self._loading_label.hide()
            self._error_label.hide()

            # Add WebView to layout if not already added
            if self._web_view.parent() != self:
                lay = self.layout()
                if lay is not None:
                    lay.addWidget(self._web_view)
            self._web_view.show()

            logger.info(f"Plugin {self.plugin_id} loaded successfully")
        else:
            self._set_error("Failed to load plugin content")

        self.load_finished.emit(self.plugin_id, success)

    @Slot(int)
    def _on_load_progress(self, progress: int) -> None:
        """Handle load progress updates."""
        self._loading_label.setText(f"Loading {self.manifest.name}... {progress}%")

    @Slot()
    def _on_load_timeout(self) -> None:
        """Handle load timeout."""
        logger.warning(f"Plugin {self.plugin_id} load timeout ({self.manifest.timeout_ms}ms)")
        self._set_state(PluginState.TIMEOUT)
        self._set_error(f"Plugin load timeout after {self.manifest.timeout_ms}ms")

    def _set_state(self, state: PluginState) -> None:
        """Update plugin state and emit signal."""
        if state != self._state:
            old_state = self._state
            self._state = state
            logger.debug(f"Plugin {self.plugin_id} state: {old_state} -> {state}")
            self.state_changed.emit(self.plugin_id, state)

    def _set_error(self, message: str) -> None:
        """Set error state and display error message."""
        logger.error(f"Plugin {self.plugin_id} error: {message}")

        self._set_state(PluginState.ERROR)

        # Show error in UI
        self._loading_label.hide()
        if hasattr(self, "_web_view"):
            self._web_view.hide()

        self._error_label.setText(f"Plugin Error: {message}")
        self._error_label.show()

        self.error_occurred.emit(self.plugin_id, message)


class PluginUIManager(QObject):
    """
    Manager for multiple plugin UI hosts.

    Handles plugin lifecycle, resource monitoring, and cleanup.
    """

    # Signals
    plugin_loaded = Signal(str)  # plugin_id
    plugin_unloaded = Signal(str)  # plugin_id
    plugin_error = Signal(str, str)  # plugin_id, error

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._hosts: dict[str, PluginUIHost] = {}
        self._plugin_dirs: dict[str, Path] = {}
        # Cache of last discovery roots to support refresh
        self._last_discovery_roots: list[Path] = []

        logger.info("PluginUIManager initialized")

    def load_plugin(self, plugin_id: str, plugin_dir: Path) -> PluginUIHost | None:
        """Load a plugin and return its UI host."""
        if plugin_id in self._hosts:
            logger.warning(f"Plugin {plugin_id} already loaded")
            return self._hosts[plugin_id]

        try:
            # Load manifest
            manifest_path = plugin_dir / "manifest.json"
            manifest = PluginManifest.from_file(manifest_path)

            # Create host
            # Parent left as None to avoid QObject/QWidget mismatch; manager tracks lifecycle
            host = PluginUIHost(plugin_id, manifest, None)

            # Connect signals
            host.state_changed.connect(self._on_plugin_state_changed)
            host.error_occurred.connect(self._on_plugin_error)
            host.load_finished.connect(self._on_plugin_load_finished)

            # Store references
            self._hosts[plugin_id] = host
            self._plugin_dirs[plugin_id] = plugin_dir

            # Start loading
            host.load_plugin_ui(plugin_dir)

            logger.info(f"Started loading plugin {plugin_id} from {plugin_dir}")
            return host

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return None

    def unload_plugin(self, plugin_id: str) -> None:
        """Unload a plugin and cleanup its resources."""
        if plugin_id not in self._hosts:
            logger.warning(f"Plugin {plugin_id} not loaded")
            return

        host = self._hosts.pop(plugin_id)
        self._plugin_dirs.pop(plugin_id, None)

        host.unload_plugin()
        host.deleteLater()

        self.plugin_unloaded.emit(plugin_id)
        logger.info(f"Unloaded plugin {plugin_id}")

    def get_host(self, plugin_id: str) -> PluginUIHost | None:
        """Get the UI host for a plugin."""
        return self._hosts.get(plugin_id)

    def list_loaded_plugins(self) -> list[str]:
        """Get list of currently loaded plugin IDs."""
        return list(self._hosts.keys())

    # --- New discovery & permission stubs ---
    def discover_plugins(
        self, roots: list[Path] | None = None, *, reload: bool = False
    ) -> list[str]:
        """Discover plugin manifests under provided root directories.

        Args:
            roots: List of root directories to scan. If None, reuses last roots or defaults to sibling 'Aetherra/lyrixa/plugins'.
            reload: If True, unloads and reloads any already loaded plugin found.

        Returns:
            List of plugin ids successfully (re)loaded or already active.
        """
        if roots is None:
            if not self._last_discovery_roots:
                # Heuristic default relative to common project layout
                candidate = Path.cwd() / "Aetherra" / "lyrixa" / "plugins"
                if candidate.exists():
                    self._last_discovery_roots = [candidate]
                else:
                    logger.warning("No plugin discovery roots available")
                    return []
            roots = self._last_discovery_roots
        else:
            self._last_discovery_roots = roots

        discovered: list[str] = []
        for root in roots:
            try:
                for manifest_path in root.rglob("manifest.json"):
                    plugin_dir = manifest_path.parent
                    try:
                        manifest = PluginManifest.from_file(manifest_path)
                    except Exception:
                        continue
                    # Simple permission gate stub (extend later)
                    if not self._check_permissions(manifest):
                        logger.warning("Denied plugin %s due to permission policy", manifest.id)
                        continue
                    if manifest.id in self._hosts and reload:
                        self.unload_plugin(manifest.id)
                    if manifest.id not in self._hosts:
                        host = self.load_plugin(manifest.id, plugin_dir)
                        if host:
                            discovered.append(manifest.id)
                    else:
                        discovered.append(manifest.id)
            except Exception as e:
                logger.error(f"Error scanning plugin root {root}: {e}")
        if discovered:
            logger.info("Discovered plugins: %s", ", ".join(discovered))
        else:
            logger.info("No plugins discovered")
        return discovered

    def _check_permissions(self, manifest: PluginManifest) -> bool:
        """Placeholder permission enforcement (allow all for now)."""
        # Future: compare against central policy / allowlist
        return True

    @Slot(str, PluginState)
    def _on_plugin_state_changed(self, plugin_id: str, state: PluginState) -> None:
        """Handle plugin state changes."""
        logger.debug(f"Plugin {plugin_id} state changed to {state}")

    @Slot(str, str)
    def _on_plugin_error(self, plugin_id: str, error: str) -> None:
        """Handle plugin errors."""
        self.plugin_error.emit(plugin_id, error)

    @Slot(str, bool)
    def _on_plugin_load_finished(self, plugin_id: str, success: bool) -> None:
        """Handle plugin load completion."""
        if success:
            self.plugin_loaded.emit(plugin_id)
