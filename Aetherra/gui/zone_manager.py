#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🏗️ ZoneManager - Dynamic Layout Management for Lyrixa GUI
===========================================================

Manages GUI zones and applies layout diffs for plugin hot-add/remove.
Implements the core architecture from the Stable Release Spec.

Key Features:
- Diff-based layout patching (idempotent)
- Preserves user state (split ratios, tab indices)
- Zone-based organization (Chat, Plugin, Inspector, StatusBar)
- Hot plugin mount/unmount without restart
"""

from __future__ import annotations

# Standard library imports
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Third party imports
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QSplitter, QTabWidget, QWidget

logger = logging.getLogger(__name__)


class ZoneType(Enum):
    """Standard GUI zones as defined in the spec."""

    TOP_BAR = "top_bar"
    LEFT_CHAT = "left_chat"
    RIGHT_PLUGIN = "right_plugin"
    RIGHT_DRAWER = "right_drawer"
    RIGHT_INSPECTOR = "right_inspector"
    BOTTOM_STATUS = "bottom_status"


class LayoutMode(Enum):
    """GUI layout modes with keyboard shortcuts."""

    CHAT_FOCUS = "chat_focus"  # Ctrl+1: Right zone collapsed
    PLUGIN_FOCUS = "plugin_focus"  # Ctrl+2: Plugin full width
    SPLIT = "split"  # Ctrl+3: 60/40 split


@dataclass
class ZoneDeclaration:
    """Plugin UI zone declaration from manifest."""

    id: str
    zone_type: ZoneType
    title: str
    size_hint: int = 300
    components: list[dict[str, Any]] = field(default_factory=list)
    persistent: bool = False  # Survives plugin uninstall


@dataclass
class LayoutDiff:
    """Result of layout diff computation."""

    created: set[str] = field(default_factory=set)
    moved: set[str] = field(default_factory=set)
    removed: set[str] = field(default_factory=set)
    updated: set[str] = field(default_factory=set)
    preserved_state: dict[str, Any] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.created or self.moved or self.removed or self.updated)


class ZoneManager(QObject):
    """
    Manages dynamic GUI layout with diff-based patching.

    Core responsibilities:
    1. Apply UI declarations from plugin manifests
    2. Compute minimal layout diffs
    3. Preserve user state during transitions
    4. Support hot plugin mount/unmount
    """

    # Signals
    layout_changed = Signal(object)  # Emits LayoutDiff
    mode_changed = Signal(LayoutMode)
    zone_added = Signal(str)  # zone_id
    zone_removed = Signal(str)  # zone_id

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        # Current layout state
        self._zones: dict[str, ZoneDeclaration] = {}
        self._widgets: dict[str, QWidget] = {}
        self._current_mode = LayoutMode.SPLIT

        # User preferences (preserved across sessions)
        self._split_ratios: dict[str, float] = {
            "main": 0.6,  # Chat:Plugin ratio in split mode
            "right": 0.7,  # Plugin:Inspector ratio
        }
        self._tab_indices: dict[str, int] = {}

        # Core widgets (always present)
        self._core_widgets: dict[str, QWidget] = {}

        logger.info("ZoneManager initialized")

    def register_core_widgets(self, widgets: dict[str, QWidget]) -> None:
        """Register core widgets that are always present."""
        self._core_widgets.update(widgets)
        logger.info(f"Registered core widgets: {list(widgets.keys())}")

    def apply(self, ui_declarations: list[dict[str, Any]]) -> LayoutDiff:
        """
        Apply UI declarations and return diff of changes made.

        This is the main entry point for plugin UI registration.
        Idempotent - safe to call multiple times with same input.
        """
        logger.debug(f"Applying {len(ui_declarations)} UI declarations")

        # Parse declarations
        new_zones = {}
        for decl_data in ui_declarations:
            try:
                zone = self._parse_zone_declaration(decl_data)
                new_zones[zone.id] = zone
            except Exception as e:
                logger.error(f"Failed to parse UI declaration: {e}")
                continue

        # Compute diff
        diff = self._compute_diff(new_zones)

        if not diff.has_changes:
            logger.debug("No layout changes needed")
            return diff

        # Preserve user state before changes
        self._preserve_user_state(diff)

        # Apply changes
        self._apply_diff(diff, new_zones)

        # Update internal state
        self._zones = new_zones

        # Emit signals
        self.layout_changed.emit(diff)
        logger.info(f"Applied layout diff: {diff}")

        return diff

    def set_mode(self, mode: LayoutMode) -> None:
        """Change layout mode (Chat Focus, Plugin Focus, Split)."""
        if mode == self._current_mode:
            return

        logger.info(f"Changing layout mode: {self._current_mode} -> {mode}")
        self._current_mode = mode

        # Apply mode-specific layout changes
        self._apply_mode_layout(mode)

        self.mode_changed.emit(mode)

    def get_mode(self) -> LayoutMode:
        """Get current layout mode."""
        return self._current_mode

    def get_split_ratio(self, splitter_id: str) -> float:
        """Get saved split ratio for a splitter."""
        return self._split_ratios.get(splitter_id, 0.6)

    def set_split_ratio(self, splitter_id: str, ratio: float) -> None:
        """Save split ratio for persistence."""
        self._split_ratios[splitter_id] = max(0.1, min(0.9, ratio))
        logger.debug(f"Saved split ratio {splitter_id}: {ratio}")

    def get_tab_index(self, tab_widget_id: str) -> int:
        """Get saved tab index."""
        return self._tab_indices.get(tab_widget_id, 0)

    def set_tab_index(self, tab_widget_id: str, index: int) -> None:
        """Save tab index for persistence."""
        self._tab_indices[tab_widget_id] = max(0, index)
        logger.debug(f"Saved tab index {tab_widget_id}: {index}")

    def remove_plugin_zones(self, plugin_id: str) -> LayoutDiff:
        """Remove all zones belonging to a plugin."""
        plugin_zones = {
            zone_id: zone
            for zone_id, zone in self._zones.items()
            if zone_id.startswith(f"{plugin_id}.")
        }

        if not plugin_zones:
            return LayoutDiff()

        logger.info(f"Removing {len(plugin_zones)} zones for plugin {plugin_id}")

        # Create new zone dict without plugin zones
        new_zones = {
            zone_id: zone
            for zone_id, zone in self._zones.items()
            if not zone_id.startswith(f"{plugin_id}.")
        }

        return self.apply([zone.__dict__ for zone in new_zones.values()])

    def _parse_zone_declaration(self, data: dict[str, Any]) -> ZoneDeclaration:
        """Parse zone declaration from manifest data."""
        try:
            zone_type = ZoneType(data.get("zone_type", "right_plugin"))
        except ValueError:
            zone_type = ZoneType.RIGHT_PLUGIN

        return ZoneDeclaration(
            id=data["id"],
            zone_type=zone_type,
            title=data.get("title", "Untitled"),
            size_hint=data.get("size_hint", 300),
            components=data.get("components", []),
            persistent=data.get("persistent", False),
        )

    def _compute_diff(self, new_zones: dict[str, ZoneDeclaration]) -> LayoutDiff:
        """Compute minimal diff between current and desired layout."""
        current_ids = set(self._zones.keys())
        new_ids = set(new_zones.keys())

        created = new_ids - current_ids
        removed = current_ids - new_ids

        # Check for updates in existing zones
        updated = set()
        for zone_id in current_ids & new_ids:
            current = self._zones[zone_id]
            new = new_zones[zone_id]

            # Simple comparison - in practice, might need deeper diff
            if (
                current.title != new.title
                or current.size_hint != new.size_hint
                or current.components != new.components
            ):
                updated.add(zone_id)

        return LayoutDiff(created=created, removed=removed, updated=updated)

    def _preserve_user_state(self, diff: LayoutDiff) -> None:
        """Preserve user state before applying diff."""
        # Save current split ratios
        for widget_id, widget in self._widgets.items():
            if isinstance(widget, QSplitter):
                sizes = widget.sizes()
                if len(sizes) == 2 and sum(sizes) > 0:
                    ratio = sizes[0] / sum(sizes)
                    diff.preserved_state[f"split_ratio_{widget_id}"] = ratio

        # Save current tab indices
        for widget_id, widget in self._widgets.items():
            if isinstance(widget, QTabWidget):
                index = widget.currentIndex()
                diff.preserved_state[f"tab_index_{widget_id}"] = index

        logger.debug(f"Preserved state: {diff.preserved_state}")

    def _apply_diff(
        self, diff: LayoutDiff, new_zones: dict[str, ZoneDeclaration]
    ) -> None:
        """Apply the computed diff to the actual layout."""
        # Remove widgets for removed zones
        for zone_id in diff.removed:
            if zone_id in self._widgets:
                widget = self._widgets.pop(zone_id)
                # Don't delete core widgets
                if zone_id not in self._core_widgets:
                    widget.setParent(None)
                    widget.deleteLater()
                logger.debug(f"Removed zone widget: {zone_id}")

        # Create widgets for new zones
        for zone_id in diff.created:
            zone = new_zones[zone_id]
            widget = self._create_zone_widget(zone)
            if widget:
                self._widgets[zone_id] = widget
                logger.debug(f"Created zone widget: {zone_id}")

        # Update existing widgets
        for zone_id in diff.updated:
            zone = new_zones[zone_id]
            self._update_zone_widget(zone_id, zone)
            logger.debug(f"Updated zone widget: {zone_id}")

        # Restore user state
        self._restore_user_state(diff.preserved_state)

    def _create_zone_widget(self, zone: ZoneDeclaration) -> QWidget | None:
        """Create a widget for a zone declaration."""
        # This is a placeholder - actual implementation would create
        # appropriate widgets based on zone type and components
        widget = QWidget()
        widget.setObjectName(f"zone_{zone.id}")
        return widget

    def _update_zone_widget(self, zone_id: str, zone: ZoneDeclaration) -> None:
        """Update an existing zone widget."""
        widget = self._widgets.get(zone_id)
        if not widget:
            return

        # Update widget properties based on zone changes
        if hasattr(widget, "setWindowTitle"):
            widget.setWindowTitle(zone.title)

        # Update components would happen here
        logger.debug(f"Updated zone {zone_id} with {len(zone.components)} components")

    def _restore_user_state(self, preserved_state: dict[str, Any]) -> None:
        """Restore user state after layout changes."""
        for key, value in preserved_state.items():
            if key.startswith("split_ratio_"):
                widget_id = key.replace("split_ratio_", "")
                self._split_ratios[widget_id] = value
            elif key.startswith("tab_index_"):
                widget_id = key.replace("tab_index_", "")
                self._tab_indices[widget_id] = value

        logger.debug(f"Restored user state: {len(preserved_state)} items")

    def _apply_mode_layout(self, mode: LayoutMode) -> None:
        """Apply layout changes for the specified mode."""
        # This would interact with the main window's layout
        # Implementation depends on the actual widget hierarchy
        logger.debug(f"Applied layout for mode: {mode}")
