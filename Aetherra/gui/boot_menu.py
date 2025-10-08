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

import os

# Standard library imports
import sys
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class BootChoice:
    mode: str = "basic"  # basic | hybrid | cli | diagnostics | exit
    safe_mode: bool = False
    # Optional advanced flags (None means leave as-is)
    no_fake_data: bool | None = None
    enable_qfac: bool | None = None
    start_qfac_dashboard: bool | None = None
    strict_security: bool | None = None
    profile: str | None = None
    keep_monitor: bool | None = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"mode": self.mode, "safe_mode": self.safe_mode}
        if self.no_fake_data is not None:
            d["no_fake_data"] = self.no_fake_data
        if self.enable_qfac is not None:
            d["enable_qfac"] = self.enable_qfac
        if self.start_qfac_dashboard is not None:
            d["start_qfac_dashboard"] = self.start_qfac_dashboard
        if self.strict_security is not None:
            d["strict_security"] = self.strict_security
        if self.profile:
            d["profile"] = self.profile
        if self.keep_monitor is not None:
            d["keep_monitor"] = self.keep_monitor
        return d


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
            QFormLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
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

            # Cyberpunk neon styling
            self.setStyleSheet(
                """
                QWidget { background: #0a0a0f; color: #e6f7ff; font-family: Consolas, 'Cascadia Mono', monospace; }
                QLabel#title { color: #00e5ff; font-size: 22px; font-weight: 800; padding: 8px 0; text-shadow: 0 0 8px #00e5ff; }
                QLabel#subtitle { color: #9adfff; font-size: 12px; }
                QListWidget { background: #0f0f1a; border: 1px solid #22224a; border-radius: 6px; }
                QListWidget::item { padding: 12px 14px; }
                QListWidget::item:selected { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7a00ff, stop:1 #00e5ff); color: #0b0b12; }
                QCheckBox { padding: 10px 0; }
                QPushButton { background: #121225; border: 1px solid #7a00ff; padding: 8px 16px; border-radius: 4px; color:#d8cfff; }
                QPushButton:hover { background: #1a1a33; border-color: #00e5ff; color:#ffffff; box-shadow: 0 0 10px #00e5ff; }
                QPushButton:pressed { background: #0d0d1a; }
                QStatusBar { color:#9adfff; }
                """
            )

            cw = QWidget()
            self.setCentralWidget(cw)
            layout = QVBoxLayout(cw)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(10)

            title = QLabel("Aetherra OS Boot Menu — Cyberpunk")
            title.setObjectName("title")
            subtitle = QLabel(
                "Use ↑/↓ to navigate, Enter to select • F1: Help • F10: Boot • Esc: Exit • F4–F9 toggle options"
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

            # Options & toggles (with env-derived defaults)
            opts = QWidget()
            opts_layout = QFormLayout(opts)
            opts_layout.setContentsMargins(0, 0, 0, 0)
            opts_layout.setSpacing(6)

            def _is_on(key: str, default: bool = False) -> bool:
                v = os.environ.get(key)
                if v is None:
                    return default
                return str(v).strip().lower() in {"1", "true", "yes", "on"}

            self.safe = QCheckBox("[F5] Safe Mode (load minimal systems)")
            self.safe.setChecked(False)
            self.safe.setToolTip("Toggle Safe Mode with F5")
            opts_layout.addRow("", self.safe)

            self.chk_no_fake = QCheckBox("[F7] Enforce No-Fake-Data (all systems real)")
            self.chk_no_fake.setChecked(_is_on("AETHERRA_NO_FAKE_DATA", False))
            self.chk_no_fake.setToolTip("Toggle No-Fake-Data with F7")
            opts_layout.addRow("", self.chk_no_fake)

            self.chk_qfac = QCheckBox("[F6] Enable QFAC Memory System")
            self.chk_qfac.setChecked(_is_on("AETHERRA_ENABLE_QFAC", True))
            self.chk_qfac.setToolTip("Toggle QFAC enablement with F6")
            opts_layout.addRow("", self.chk_qfac)

            self.chk_qfac_dash = QCheckBox("[F9] Auto-start QFAC Dashboard")
            self.chk_qfac_dash.setChecked(_is_on("AETHERRA_QFAC_DASHBOARD", False))
            self.chk_qfac_dash.setToolTip("Toggle QFAC Dashboard auto-start with F9")
            opts_layout.addRow("", self.chk_qfac_dash)

            self.chk_strict = QCheckBox("[F8] Strict Security Checks")
            self.chk_strict.setChecked(
                _is_on("AETHERRA_NET_STRICT", False)
                or _is_on("AETHERRA_SCRIPT_VERIFY_STRICT", False)
            )
            self.chk_strict.setToolTip("Toggle Strict Security with F8")
            opts_layout.addRow("", self.chk_strict)

            self.chk_keep_monitor = QCheckBox("[F4] Keep window open after boot (monitor)")
            # Default to ON so users can watch stats during boot
            self.chk_keep_monitor.setChecked(True)
            self.chk_keep_monitor.setToolTip("Keep this window open as a monitor after boot (F4)")
            opts_layout.addRow("", self.chk_keep_monitor)

            self.edit_profile = QLineEdit()
            self.edit_profile.setPlaceholderText("profile (e.g., dev/test/prod)")
            self.edit_profile.setText(os.environ.get("AETHERRA_PROFILE", ""))
            opts_layout.addRow("Profile:", self.edit_profile)

            layout.addWidget(opts)

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

            # Live status panel + refresh
            self.status = QLabel()
            self.status.setWordWrap(True)
            self.status.setStyleSheet("color:#9adfff; padding-top:6px;")
            layout.addWidget(self.status)

            tools_row = QHBoxLayout()
            self.btn_refresh = QPushButton("Refresh Status")
            self.btn_refresh.clicked.connect(self._probe)
            tools_row.addWidget(self.btn_refresh)
            layout.addLayout(tools_row)

            # Initial probe
            self._probe()

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

            # Option toggles (F5–F9)
            sh_f4 = QShortcut(QKeySequence("F4"), self)
            sh_f4.activated.connect(self.chk_keep_monitor.toggle)
            sh_f5 = QShortcut(QKeySequence("F5"), self)
            sh_f5.activated.connect(self.safe.toggle)
            sh_f6 = QShortcut(QKeySequence("F6"), self)
            sh_f6.activated.connect(self.chk_qfac.toggle)
            sh_f7 = QShortcut(QKeySequence("F7"), self)
            sh_f7.activated.connect(self.chk_no_fake.toggle)
            sh_f8 = QShortcut(QKeySequence("F8"), self)
            sh_f8.activated.connect(self.chk_strict.toggle)
            sh_f9 = QShortcut(QKeySequence("F9"), self)
            sh_f9.activated.connect(self.chk_qfac_dash.toggle)

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
            # Advanced flags
            choice.no_fake_data = self.chk_no_fake.isChecked()
            choice.enable_qfac = self.chk_qfac.isChecked()
            choice.start_qfac_dashboard = self.chk_qfac_dash.isChecked()
            choice.strict_security = self.chk_strict.isChecked()
            choice.keep_monitor = self.chk_keep_monitor.isChecked()
            prof = self.edit_profile.text().strip()
            choice.profile = prof or None
            self.close()

        def _help(self) -> None:
            # Inline help text at bottom via subtitle replacement
            help_text = (
                "F12-style boot menu. Options: Basic (default), Hybrid, CLI, Diagnostics, Exit. "
                "Toggles: Keep Monitor (F4), Safe Mode (F5), Enable QFAC (F6), No-Fake-Data (F7), Strict Security (F8), QFAC Dashboard (F9)."
            )
            self.statusBar().showMessage(help_text, 8000)

        def _exit_no_boot(self) -> None:
            choice.mode = "exit"
            self.close()

        def _probe(self) -> None:
            """Probe kernel, hub, and QFAC endpoints for quick status."""
            base = os.environ.get("AETHERRA_BASE_URL", "http://127.0.0.1:3001").rstrip("/")
            qfac = os.environ.get("AETHERRA_QFAC_URL", "http://127.0.0.1:4020").rstrip("/")

            def _ping(url: str) -> str:
                try:
                    from urllib.request import Request, urlopen

                    req = Request(url, method="GET")
                    with urlopen(req, timeout=0.6):  # nosec B310 (local)
                        return "online"
                except Exception:
                    return "offline"

            # Kernel
            try:
                from aetherra_kernel_loop import get_kernel  # type: ignore

                kernel = get_kernel()
                k_status = "running" if getattr(kernel, "running", False) else "stopped"
            except Exception:
                k_status = "unavailable"

            hub_status = _ping(base + "/api/agents")
            qfac_status = _ping(qfac + "/api/status")

            summary = (
                f"<b>Kernel:</b> {k_status} • "
                f"<b>Hub:</b> {hub_status} • "
                f"<b>QFAC:</b> {qfac_status} • "
                f"<b>Profile:</b> {os.environ.get('AETHERRA_PROFILE', 'default')} • "
                f"<b>Mode:</b> {os.environ.get('AETHERRA_MODE', 'full')} • "
                f"<b>No-Fake-Data:</b> {'ON' if os.environ.get('AETHERRA_NO_FAKE_DATA') in ['1', 'true', 'yes', 'on'] else 'off'} • "
                f"<b>QFAC Enabled:</b> {'ON' if os.environ.get('AETHERRA_ENABLE_QFAC', '1') in ['1', 'true', 'yes', 'on'] else 'off'}"
            )
            self.status.setText(summary)

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
    no_fake = input("Enforce No-Fake-Data? (y/N): ").strip().lower().startswith("y")
    qfac_on = input("Enable QFAC Memory System? (Y/n): ").strip().lower()
    qfac_on = qfac_on not in {"n", "no"}
    qfac_dash = input("Auto-start QFAC Dashboard? (y/N): ").strip().lower().startswith("y")
    strict = input("Strict Security Checks? (y/N): ").strip().lower().startswith("y")
    profile = input("Profile [blank=default]: ").strip()
    sel = input("Select [1-5]: ").strip()
    choice = BootChoice(safe_mode=safe)
    choice.no_fake_data = no_fake
    choice.enable_qfac = qfac_on
    choice.start_qfac_dashboard = qfac_dash
    choice.strict_security = strict
    choice.profile = profile or None
    mapping = {"1": "basic", "2": "hybrid", "3": "cli", "4": "diagnostics", "5": "exit"}
    choice.mode = mapping.get(sel, "basic")
    return choice
