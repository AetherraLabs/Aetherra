# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from __future__ import annotations

# Standard library imports
from typing import Any, Callable, Dict, List, Optional

# Third party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class NavPanel(QWidget):
    """
    Compact left navigation panel for Lyrixa UI.

    Exposes:
    - navigationRequested(panel_id: str) signal for standard panels
    - add_auto_panels(panels, on_click) to attach auto-generated panels
    - set_status(text) to update the status pill at the bottom
    """

    navigationRequested = Signal(str)

    def __init__(
        self, button_style: Optional[str] = None, parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("left_panel")
        self._button_style = button_style or self._default_button_style()
        self._auto_sep_added = False
        self._auto_buttons: Dict[str, QPushButton] = {}

        self._root = QFrame()
        self._root.setFixedWidth(280)
        self._layout = QVBoxLayout(self._root)

        # Title
        title = QLabel("🎙️ LYRIXA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00ff88;
                padding: 20px;
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
                margin-bottom: 10px;
            }
            """
        )
        self._layout.addWidget(title)

        # Built-in navigation
        nav_buttons = [
            ("🧠 Neural Interface", "dashboard"),
            ("🔌 Plugin Manager", "plugins"),
            ("📈 Metrics", "metrics"),
            ("💭 Memory", "memory"),
            ("🔐 Security Alerts", "alerts"),
            ("🧠 Cognitive UI", "cognitive"),
            ("⚛️ Consciousness", "consciousness"),
            ("🔁 Plugin Demo", "plugin_demo"),
            ("💬 Chat with Lyrixa", "chat"),
            ("⚙️ Settings", "settings"),
        ]
        for text, panel_id in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName(f"nav_{panel_id}")
            btn.setStyleSheet(self._button_style)
            btn.clicked.connect(
                lambda _c=False, pid=panel_id: self.navigationRequested.emit(pid)
            )
            self._layout.addWidget(btn)

        # Spacer
        self._layout.addStretch()

        # Status pill
        self._status_label = QLabel("🌟 All Systems Online")
        self._status_label.setStyleSheet(
            """
            QLabel {
                color: #00ff88;
                font-weight: bold;
                padding: 10px;
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
            }
            """
        )
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        status_layout.addWidget(self._status_label)
        self._layout.addWidget(status_frame)

        # Adopt root frame layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._root)

    def set_status(self, text: str) -> None:
        self._status_label.setText(text)

    def add_auto_panels(
        self,
        panels: List[Dict[str, Any]],
        on_click: Optional[Callable[[str], None]] = None,
        limit: int = 5,
    ) -> None:
        """Add buttons for auto-generated panels (id, title)."""
        if not panels:
            return

        # Add separator and label once
        if not self._auto_sep_added:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(
                "border: 1px solid rgba(0, 255, 136, 0.3); margin: 10px 0;"
            )
            # Insert before spacer and status (at index count-2)
            self._layout.insertWidget(self._layout.count() - 2, sep)

            auto_label = QLabel("[AUTO] Auto-Generated")
            auto_label.setStyleSheet(
                """
                QLabel {
                    color: #00ff88;
                    font-weight: bold;
                    font-size: 12px;
                    margin: 5px 0;
                }
                """
            )
            self._layout.insertWidget(self._layout.count() - 2, auto_label)
            self._auto_sep_added = True

        for info in panels[:limit]:
            pid = str(info.get("id"))
            title = str(info.get("title", pid))
            if pid in self._auto_buttons:
                continue

            btn = QPushButton(f"[AUTO] {title}")
            btn.setObjectName(f"auto_nav_{pid}")
            btn.setStyleSheet(
                self._button_style
                + """
                QPushButton {
                    background: rgba(0, 255, 136, 0.1);
                    border-left: 3px solid #00ff88;
                }
                """
            )
            if on_click:
                btn.clicked.connect(lambda _c=False, p=pid: on_click(p))
            else:
                btn.clicked.connect(
                    lambda _c=False, p=pid: self.navigationRequested.emit(p)
                )

            # Insert before spacer and status
            self._layout.insertWidget(self._layout.count() - 2, btn)
            self._auto_buttons[pid] = btn

    @staticmethod
    def _default_button_style() -> str:
        return """
            QPushButton {
                background: rgba(26, 26, 26, 0.8);
                color: #ffffff;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                margin: 4px 0;
                text-align: left;
            }

            QPushButton:hover {
                background: rgba(0, 255, 136, 0.1);
                border-color: rgba(0, 255, 136, 0.6);
            }

            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.2);
            }
            """
