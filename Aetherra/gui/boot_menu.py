#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧭 Aetherra OS Boot Menu (BIOS-like)
====================================

Keyboard-driven, minimal GUI for early boot selection, similar to a BIOS/boot menu.

Options include:
- Boot Lyrixa Basic (default)
- Boot Lyrixa Hybrid
- Boot CLI (headless)
- Diagnostics (console snapshot)
- Safe Mode (toggle)
- Exit

Usage from launcher:
    from Aetherra.gui.boot_menu import show_boot_menu_and_get_choice
    choice = show_boot_menu_and_get_choice()

Returns a dict like: {"mode": "basic|hybrid|cli|diagnostics|exit", "safe_mode": bool}
"""

from __future__ import annotations

# Standard library imports
import sys
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class BootChoice:
    mode: str = "basic"  # basic | hybrid | cli | diagnostics | exit
    safe_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"mode": self.mode, "safe_mode": self.safe_mode}


def show_boot_menu_and_get_choice() -> Dict[str, Any]:
    """Show a BIOS-like boot menu and return the user's choice.

    If PySide6 is not available, fall back to a simple console menu.
    This function may create a QApplication if one does not exist yet.
    """
    try:
        # Third party imports
        from PySide6.QtGui import QKeySequence, QShortcut
        from PySide6.QtWidgets import (
            QApplication,
            QCheckBox,
            QHBoxLayout,
            QLabel,
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )
    except Exception:
        return _console_menu_fallback().to_dict()

    app = QApplication.instance() or QApplication(sys.argv)

    choice = BootChoice()

    class BootMenuWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Aetherra OS Boot Menu")
            self.resize(820, 520)

            # BIOS-like styling
            self.setStyleSheet(
                """
                QWidget { background: #0b1022; color: #e6eefc; font-family: Consolas, 'Cascadia Mono', monospace; }
                QLabel#title { color: #88b3ff; font-size: 20px; font-weight: 700; padding: 8px 0; }
                QLabel#subtitle { color: #aac4ff; font-size: 12px; }
                QListWidget { background: #0f1733; border: 1px solid #1d2a5a; }
                QListWidget::item { padding: 10px 12px; }
                QListWidget::item:selected { background: #173069; color: #ffffff; }
                QCheckBox { padding: 8px 0; }
                QPushButton { background: #153066; border: 1px solid #2a4ca3; padding: 6px 14px; }
                QPushButton:hover { background: #1a3a7a; }
                QPushButton:pressed { background: #102a5a; }
                """
            )

            cw = QWidget()
            self.setCentralWidget(cw)
            layout = QVBoxLayout(cw)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(10)

            title = QLabel("Aetherra OS Boot Menu (F12)")
            title.setObjectName("title")
            subtitle = QLabel(
                "Use ↑/↓ to navigate, Enter to select • F1: Help • F10: Save + Boot • Esc: Exit"
            )
            subtitle.setObjectName("subtitle")
            layout.addWidget(title)
            layout.addWidget(subtitle)

            self.list = QListWidget()
            for text in [
                "Boot Lyrixa Basic (default)",
                "Boot Lyrixa Hybrid",
                "Boot CLI (headless)",
                "Diagnostics (console snapshot)",
                "Exit",
            ]:
                QListWidgetItem(text, self.list)
            self.list.setCurrentRow(0)
            layout.addWidget(self.list)

            # Safe mode toggle
            self.safe = QCheckBox("Boot in Safe Mode (load minimal systems)")
            layout.addWidget(self.safe)

            # Buttons row
            row = QHBoxLayout()
            self.btn_boot = QPushButton("Boot")
            self.btn_boot.clicked.connect(self._accept)
            self.btn_help = QPushButton("Help")
            self.btn_help.clicked.connect(self._help)
            self.btn_exit = QPushButton("Exit")
            self.btn_exit.clicked.connect(self._exit_no_boot)
            row.addWidget(self.btn_boot)
            row.addWidget(self.btn_help)
            row.addWidget(self.btn_exit)
            layout.addLayout(row)

            # Shortcuts
            sh_return = QShortcut(QKeySequence("Return"), self)
            sh_return.activated.connect(self._accept)
            sh_enter = QShortcut(QKeySequence("Enter"), self)
            sh_enter.activated.connect(self._accept)
            sh_esc = QShortcut(QKeySequence("Escape"), self)
            sh_esc.activated.connect(self._exit_no_boot)
            sh_f1 = QShortcut(QKeySequence("F1"), self)
            sh_f1.activated.connect(self._help)
            sh_f10 = QShortcut(QKeySequence("F10"), self)
            sh_f10.activated.connect(self._accept)

        def _accept(self) -> None:
            idx = self.list.currentRow()
            choice.safe_mode = self.safe.isChecked()
            if idx == 0:
                choice.mode = "basic"
            elif idx == 1:
                choice.mode = "hybrid"
            elif idx == 2:
                choice.mode = "cli"
            elif idx == 3:
                choice.mode = "diagnostics"
            else:
                choice.mode = "exit"
            self.close()

        def _help(self) -> None:
            # Inline help text at bottom via subtitle replacement
            help_text = (
                "F12-style BIOS menu. Options: Basic (default), Hybrid, CLI, Diagnostics, Exit. "
                "Safe Mode reduces subsystem loading."
            )
            self.statusBar().showMessage(help_text, 8000)

        def _exit_no_boot(self) -> None:
            choice.mode = "exit"
            self.close()

    win = BootMenuWindow()
    win.show()
    # Run a modal event loop until the window closes
    app.exec()  # nosec B102: Qt application execution
    return choice.to_dict()


def _console_menu_fallback() -> BootChoice:
    print("Aetherra OS Boot Menu (console)")
    print("==============================")
    print("1) Boot Lyrixa Basic (default)")
    print("2) Boot Lyrixa Hybrid")
    print("3) Boot CLI (headless)")
    print("4) Diagnostics (console snapshot)")
    print("5) Exit")
    safe = input("Safe Mode? (y/N): ").strip().lower().startswith("y")
    sel = input("Select [1-5]: ").strip()
    choice = BootChoice(safe_mode=safe)
    mapping = {"1": "basic", "2": "hybrid", "3": "cli", "4": "diagnostics", "5": "exit"}
    choice.mode = mapping.get(sel, "basic")
    return choice
