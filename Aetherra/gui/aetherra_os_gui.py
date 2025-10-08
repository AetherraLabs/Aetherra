#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🖥️ Aetherra OS Monitor GUI
===========================
Minimal, focused GUI to visualize Aetherra OS status while running.

Sources:
- Hub (http://localhost:3001): /health, /status, /api/stats, /api/plugins
- Optional Web UI (http://localhost:8686): /api/system/status, /api/metrics/realtime

Notes:
- If PySide6 is not installed, supports a --once console snapshot mode.
"""

from __future__ import annotations

# Standard library imports
import argparse
import contextlib
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Optional auth token (bearer) for secured Hub endpoints
HUB_TOKEN = os.getenv("AETHERRA_HUB_TOKEN")

HUB_BASE = os.getenv("AETHERRA_HUB_BASE", "http://localhost:3001")
WEB_BASE = os.getenv("AETHERRA_WEB_BASE", "http://localhost:8686")


def _fetch_json(url: str, timeout: float = 1.8) -> Optional[Dict[str, Any]]:
    try:
        # Third party imports
        import requests  # Lazy import in case only --once is used

        headers = {}
        if HUB_TOKEN:  # Inject auth header if token present
            headers["Authorization"] = f"Bearer {HUB_TOKEN}"
        r = requests.get(url, timeout=timeout, headers=headers)
        if r.ok:
            data = r.json()
            if isinstance(data, dict):  # best-effort narrowing
                return data
        return None
    except Exception:
        return None


def _snapshot() -> Dict[str, Any]:
    health = _fetch_json(f"{HUB_BASE}/health") or {}
    status = _fetch_json(f"{HUB_BASE}/status") or {}
    stats = _fetch_json(f"{HUB_BASE}/api/stats") or {}
    plugins = _fetch_json(f"{HUB_BASE}/api/plugins") or {}

    web_status = _fetch_json(f"{WEB_BASE}/api/system/status") or {}
    web_metrics = _fetch_json(f"{WEB_BASE}/api/metrics/realtime") or {}

    return {
        "hub": {
            "ok": bool(health or status),
            "uptime": int(health.get("uptime_seconds") or status.get("uptime_seconds") or 0),
            "requests": health.get("requests_served") or stats.get("requests_served") or 0,
            "plugins": (
                len(plugins.get("plugins", []))
                if isinstance(plugins.get("plugins"), list)
                else (health.get("plugins_registered") or 0)
            ),
        },
        "web": {
            "ok": bool(web_status or web_metrics),
            "cpu": web_metrics.get("cpu_usage"),
            "mem": web_metrics.get("memory_usage"),
            "rt": web_metrics.get("response_time"),
        },
    }


def console_once() -> None:
    snap = _snapshot()
    print("🖥️ Aetherra OS Monitor Snapshot")
    print("=" * 42)
    now = datetime.now().strftime("%H:%M:%S")
    print(f"🕐 {now}")
    if snap["hub"]["ok"]:
        print(
            "🟢 HUB ONLINE "
            f"| ⏱️ {snap['hub']['uptime']}s | 📈 {snap['hub']['requests']} req | 🔌 {snap['hub']['plugins']} plugins"
        )
    else:
        print("🔴 HUB OFFLINE (http://localhost:3001)")
    if snap["web"]["ok"]:
        parts = []
        if isinstance(snap["web"]["cpu"], int | float):
            parts.append(f"CPU {snap['web']['cpu']}%")
        if isinstance(snap["web"]["mem"], int | float):
            parts.append(f"MEM {snap['web']['mem']}%")
        if isinstance(snap["web"]["rt"], int | float):
            parts.append(f"RT {snap['web']['rt']}ms")
        extras = " | ".join(parts)
        print("🟢 WEB ACTIVE" + (f" | {extras}" if extras else ""))
    else:
        print("🟡 WEB not detected (optional) http://localhost:8686")


def _tail_log(path: str, lines: int = 12) -> list[str]:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            buf = f.readlines()
        return [ln.rstrip() for ln in buf[-lines:] if ln.strip()]
    except FileNotFoundError:
        return []


def _ensure_utf8_console() -> None:
    if os.name == "nt":
        with contextlib.suppress(Exception):
            os.system("chcp 65001 > nul")


def launch_gui(interval_ms: int = 2000) -> int:
    try:
        # Third party imports
        from PySide6.QtCore import Qt, QTimer  # noqa: F401 (optional runtime import)
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import (
            QApplication,
            QFrame,
            QGridLayout,
            QLabel,
            QMainWindow,
            QTextEdit,
            QWidget,
        )
    except Exception as e:
        print("❌ PySide6 not available. Install with: pip install PySide6")
        print(f"Reason: {e}")
        console_once()
        return 1

    # Lazy import of event bus only in GUI mode
    try:
        from .event_bus import EventFactory, get_event_bus
    except Exception:  # pragma: no cover - fallback if relative import context differs
        EventFactory = None  # type: ignore
        get_event_bus = None  # type: ignore

    class MonitorWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Aetherra OS Monitor")
            self.resize(900, 600)
            self._event_bus = None
            if EventFactory is not None and callable(get_event_bus):
                with contextlib.suppress(Exception):  # pragma: no cover
                    self._event_bus = get_event_bus()

            cw = QWidget()
            self.setCentralWidget(cw)
            grid = QGridLayout(cw)
            grid.setContentsMargins(12, 12, 12, 12)
            grid.setHorizontalSpacing(16)
            grid.setVerticalSpacing(10)

            # Hub panel
            self.hub_title = QLabel("HUB")
            self.hub_title.setStyleSheet("font-weight: 700; font-size: 16px;")
            self.hub_status = QLabel("🔴 OFFLINE")
            self.hub_meta = QLabel("")

            # Web panel
            web_frame = QFrame()
            web_grid = QGridLayout(web_frame)
            self.web_title = QLabel("WEB UI")
            self.web_title.setStyleSheet("font-weight: 700; font-size: 16px;")
            self.web_status = QLabel("🟡 Not detected")
            self.web_metrics = QLabel("")
            web_grid.addWidget(self.web_title, 0, 0)
            web_grid.addWidget(self.web_status, 0, 1)
            web_grid.addWidget(self.web_metrics, 1, 0, 1, 2)

            # Log panel
            self.log_title = QLabel("Recent Activity (aetherra_os.log)")
            self.log_title.setStyleSheet("font-weight: 700; font-size: 16px;")
            self.log_view = QTextEdit()
            self.log_view.setReadOnly(True)
            self.log_view.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")

            # Layout
            grid.addWidget(self.hub_title, 0, 0)
            grid.addWidget(self.hub_status, 0, 1)
            grid.addWidget(self.hub_meta, 1, 0, 1, 2)
            grid.addWidget(web_frame, 0, 2, 2, 1)
            grid.addWidget(self.log_title, 2, 0, 1, 3)
            grid.addWidget(self.log_view, 3, 0, 1, 3)

            # Timer to refresh
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh)
            self.timer.start(max(500, interval_ms))

            # Initial refresh
            self.refresh()

        def _publish_metric(self, metric_name: str, value: Any, unit: str = "count") -> None:
            """Publish a performance/status metric if event bus available."""
            if self._event_bus and EventFactory is not None:
                try:
                    # Reuse performance_metric factory for simplicity
                    evt = EventFactory.performance_metric(
                        metric_name, float(value or 0), unit, "os_monitor"
                    )
                    self._event_bus.publish(evt)
                except Exception:
                    pass

        def refresh(self) -> None:
            snap = _snapshot()

            if snap["hub"]["ok"]:
                self.hub_status.setText("🟢 ONLINE")
                self.hub_meta.setText(
                    f"⏱️ {snap['hub']['uptime']}s   •   📈 {snap['hub']['requests']} req   •   🔌 {snap['hub']['plugins']} plugins"
                )
                # Emit hub metrics
                self._publish_metric("hub_uptime_seconds", snap["hub"]["uptime"], "s")
                self._publish_metric("hub_requests_total", snap["hub"]["requests"], "count")
                self._publish_metric("hub_plugins_active", snap["hub"]["plugins"], "count")
            else:
                self.hub_status.setText("🔴 OFFLINE")
                self.hub_meta.setText("Hub not responding at localhost:3001")

            if snap["web"]["ok"]:
                parts = []
                cpu = snap["web"]["cpu"]
                mem = snap["web"]["mem"]
                rt = snap["web"]["rt"]
                if isinstance(cpu, int | float):
                    parts.append(f"CPU {cpu}%")
                if isinstance(mem, int | float):
                    parts.append(f"MEM {mem}%")
                if isinstance(rt, int | float):
                    parts.append(f"RT {rt}ms")
                self.web_status.setText("🟢 ACTIVE")
                self.web_metrics.setText("   •   ".join(parts))
                # Publish web metrics
                if isinstance(cpu, int | float):
                    self._publish_metric("web_cpu_percent", cpu, "%")
                if isinstance(mem, int | float):
                    self._publish_metric("web_mem_percent", mem, "%")
                if isinstance(rt, int | float):
                    self._publish_metric("web_rt_ms", rt, "ms")
            else:
                self.web_status.setText("🟡 Not detected")
                self.web_metrics.setText("Web UI optional at localhost:8686")

            recent = _tail_log("aetherra_os.log", lines=18)
            if recent:
                self.log_view.setPlainText("\n".join(recent))
                with contextlib.suppress(Exception):
                    # Prefer explicit enum path for type checkers
                    self.log_view.moveCursor(QTextCursor.MoveOperation.End)
                # Fallback attempt (older bindings) in separate suppress block
                with contextlib.suppress(Exception):
                    self.log_view.moveCursor(QTextCursor.End)  # type: ignore[attr-defined]
            else:
                self.log_view.setPlainText("(no recent log lines or log missing)")

    _ensure_utf8_console()
    app = QApplication.instance() or QApplication(sys.argv)
    win = MonitorWindow()
    win.show()
    return app.exec()  # nosec B102: Qt application execution


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Aetherra OS Monitor GUI")
    parser.add_argument("--once", action="store_true", help="Print a one-time snapshot and exit")
    parser.add_argument(
        "--interval", type=int, default=2000, help="Refresh interval in ms (GUI mode)"
    )
    args = parser.parse_args(argv)

    if args.once:
        console_once()
        return 0

    return launch_gui(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
