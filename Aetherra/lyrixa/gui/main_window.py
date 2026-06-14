#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Minimal compatibility main window for the legacy Lyrixa GUI import path.

This preserves import compatibility for transitional tests and launchers while
the canonical user interface is moved to Aetherra-first entrypoints.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Aetherra Interface Compatibility Window")
        self.resize(960, 640)

        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Aetherra Interface")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 700;")

        subtitle = QLabel(
            "Legacy Lyrixa GUI imports now route through this compatibility window during the Aetherra UI transition."
        )
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #666;")

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)

        self.setCentralWidget(wrapper)


class LyrixaHybridWindow(MainWindow):
    pass
