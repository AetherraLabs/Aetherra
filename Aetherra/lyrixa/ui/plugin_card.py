#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""PluginCard - Phase 1 lightweight visual representation of a plugin.

Intent: prepare for future richer plugin marketplace UI while remaining
non-invasive. If theme active, uses accent colors; otherwise falls back
to simple border + title.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

try:  # Optional import (do not hard fail if theme manager missing)
    from .theme_manager import Theme, get_active_theme  # type: ignore[attr-defined]
except Exception:  # pragma: no cover

    class Theme:  # minimal stub
        pass

    def get_active_theme() -> Theme | None:  # type: ignore[misc]
        return None


@dataclass
class PluginMeta:
    name: str
    display_name: str
    version: str = "1.0.0"
    description: str = ""
    installed: bool = False


class PluginCard(QFrame):
    def __init__(
        self,
        meta: PluginMeta,
        on_install: Callable[[PluginMeta], Any] | None = None,
        on_manage: Callable[[PluginMeta], Any] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.meta = meta
        self.on_install = on_install
        self.on_manage = on_manage
        self.setObjectName("PluginCard")
        self.setProperty("class", "LyrixaGlassPanel")
        self._build_ui()

    def _build_ui(self):
        theme = get_active_theme()
        accent = None
        if theme and hasattr(theme, "color"):
            accent = theme.color("accent_primary", "#0891b2")  # type: ignore[call-arg]
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title = QLabel(
            f"{self.meta.display_name}  <small style='color:#888'>v{self.meta.version}</small>"
        )
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)

        if self.meta.description:
            desc = QLabel(self.meta.description)
            desc.setWordWrap(True)
            layout.addWidget(desc)

        self._btn_row = QHBoxLayout()
        self.install_btn: QPushButton | None = None
        self.manage_btn: QPushButton | None = None
        if not self.meta.installed and self.on_install:
            self.install_btn = QPushButton("Install")
            self.install_btn.setProperty("class", "cyber")
            self.install_btn.setProperty("card-install", "pending")
            if self.on_install:
                self.install_btn.clicked.connect(  # type: ignore[arg-type]
                    lambda: self.on_install(self.meta)
                )
            self._btn_row.addWidget(self.install_btn)
        elif self.meta.installed and self.on_manage:
            self.manage_btn = QPushButton("Manage")
            self.manage_btn.setProperty("class", "cyber")
            self._btn_row.addWidget(self.manage_btn)
        self._btn_row.addStretch(1)
        layout.addLayout(self._btn_row)

        # Minimal inline fallback styling if theme not applied
        if not theme:
            self.setStyleSheet(
                "QFrame#PluginCard { border:1px solid #2d3e50; border-radius:8px; background:#182635; }"
            )
        elif accent:
            # Add subtle hover via dynamic property (theme may extend later)
            self.setStyleSheet(
                f"QFrame#PluginCard {{ border:1px solid {accent}; border-radius:10px; }}"
            )

    # Convenience for future dynamic state updates
    def mark_installed(self, installed: bool = True):
        self.meta.installed = installed
        # Update dynamic properties & buttons
        self.setProperty("installed", bool(installed))
        if installed:
            # --- Animation: fade and scale ---
            try:
                from PySide6.QtCore import QEasingCurve, QPropertyAnimation
                from PySide6.QtWidgets import QGraphicsOpacityEffect

                # Fade effect
                effect = QGraphicsOpacityEffect(self)
                self.setGraphicsEffect(effect)
                fade = QPropertyAnimation(effect, b"opacity", self)
                fade.setDuration(420)
                fade.setStartValue(0.3)
                fade.setEndValue(1.0)
                fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
                fade.start()
                # Subtle scale (simulate with min/max height)
                orig_height = self.height()
                scale_anim = QPropertyAnimation(self, b"maximumHeight", self)
                scale_anim.setDuration(420)
                scale_anim.setStartValue(int(orig_height * 0.92))
                scale_anim.setEndValue(orig_height)
                scale_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
                scale_anim.start()
            except Exception as exc:
                logging.debug(f"[PluginCard] Install animation failed: {exc}")
            if self.install_btn:
                self.install_btn.setText("Installed")
                self.install_btn.setEnabled(False)
                self.install_btn.setProperty("card-install", "installed")
            if self.on_manage and not self.manage_btn:
                self.manage_btn = QPushButton("Manage")
                if self.on_manage:
                    self.manage_btn.clicked.connect(  # type: ignore[arg-type]
                        lambda: self.on_manage(self.meta) if self.on_manage else None
                    )
                self._btn_row.insertWidget(0, self.manage_btn)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


__all__ = ["PluginMeta", "PluginCard"]
