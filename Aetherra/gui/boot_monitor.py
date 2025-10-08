#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Aetherra Boot Monitor — stays open after boot to show live status

from __future__ import annotations

import os
import sys
import time
from typing import Dict, Any


def _http_get_json(url: str, timeout: float = 0.8) -> Dict[str, Any] | None:
    try:
        from urllib.request import Request, urlopen
        import json

        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as resp:  # nosec B310 (local)
            data = resp.read()
        return json.loads(data.decode("utf-8", errors="ignore"))
    except Exception:
        return None


def run_monitor() -> int:
    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QTextEdit, QVBoxLayout, QWidget
    except Exception:
        # Console fallback: print status periodically
        base = os.environ.get("AETHERRA_BASE_URL", "http://127.0.0.1:3001").rstrip("/")
        qfac = os.environ.get("AETHERRA_QFAC_URL", "http://127.0.0.1:4020").rstrip("/")
        try:
            for _ in range(30):
                hub_ok = _http_get_json(base + "/api/agents") is not None
                qfac_ok = _http_get_json(qfac + "/api/status") is not None
                print(f"[MON] Hub={'OK' if hub_ok else 'down'} QFAC={'OK' if qfac_ok else 'down'}")
                time.sleep(2)
        except KeyboardInterrupt:
            return 0
        return 0

    app = QApplication.instance() or QApplication(sys.argv)

    class Monitor(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Aetherra — Boot Monitor")
            self.resize(720, 460)
            self.setStyleSheet(
                """
                QWidget { background:#0a0a0f; color:#e6f7ff; font-family:Consolas, 'Cascadia Mono', monospace; }
                QLabel#title { color:#00e5ff; font-size:18px; font-weight:700; padding:6px 0; }
                QTextEdit { background:#0f0f1a; border:1px solid #22224a; border-radius:6px; }
                """
            )
            cw = QWidget()
            self.setCentralWidget(cw)
            lay = QVBoxLayout(cw)
            self.title = QLabel("Aetherra Boot Monitor — Live Status")
            self.title.setObjectName("title")
            self.text = QTextEdit()
            self.text.setReadOnly(True)
            lay.addWidget(self.title)
            lay.addWidget(self.text)

            self.base = os.environ.get("AETHERRA_BASE_URL", "http://127.0.0.1:3001").rstrip("/")
            self.qfac = os.environ.get("AETHERRA_QFAC_URL", "http://127.0.0.1:4020").rstrip("/")

            self.timer = QTimer(self)
            self.timer.setInterval(1500)
            self.timer.timeout.connect(self.refresh)
            self.timer.start()
            self.refresh()

        def refresh(self) -> None:
            hub = _http_get_json(self.base + "/api/agents")
            qfs = _http_get_json(self.qfac + "/api/status")
            qfp = _http_get_json(self.qfac + "/api/performance")
            lines = []
            lines.append(f"Hub: {'online' if hub is not None else 'offline'} — {self.base}")
            if hub and isinstance(hub, list):
                lines.append(f"  Agents: {len(hub)} active")
            lines.append(f"QFAC: {'online' if qfs is not None else 'offline'} — {self.qfac}")
            if qfs:
                st = qfs.get('system_health') or qfs.get('status')
                lines.append(f"  Health: {st}")
            if qfp:
                perf = qfp.get('performance') or qfp
                total = perf.get('total_memories') if isinstance(perf, dict) else None
                if total is not None:
                    lines.append(f"  Memories: {total}")
            self.text.setPlainText("\n".join(lines))

    win = Monitor()
    win.show()
    app.exec()  # nosec B102
    return 0


if __name__ == "__main__":
    sys.exit(run_monitor())
