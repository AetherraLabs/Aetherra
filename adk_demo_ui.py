"""
Aetherra Demo UI Kit (PySide6)
Single-file scaffold to give each CLI demo an independent, instantly runnable UI.

Usage examples:
  # Kernel Status (polls Hub endpoints)
  python adk_demo_ui.py --demo kernel_status

  # Agent Pipeline (runs existing CLI demo and streams logs)
  python adk_demo_ui.py --demo agent_pipeline --topic "quantum memory"

  # Chat Stream (runs CLI and streams logs)
  python adk_demo_ui.py --demo chat_stream --prompt "Explain HMR in two sentences"

Create tiny per-demo launchers (independent UIs):
  echo "from adk_demo_ui import launch; launch('kernel_status')" > kernel_status_ui.py
  python kernel_status_ui.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

try:
    import requests  # For local Hub/API polling
except Exception:
    requests = None


def get_default_base_url() -> str:
    """Compute default Hub base URL.
    Order of precedence:
      1) Env AETHERRA_BASE_URL (full URL)
      2) Env AETHERRA_HUB_HOST/AETHERRA_HUB_PORT (defaults 127.0.0.1:3001)
      3) Fallback http://127.0.0.1:3001

    Note: config.json web_interface.port is for the Web UI, not the Hub API.
    """
    env_url = os.environ.get("AETHERRA_BASE_URL")
    if env_url:
        return env_url
    hub_host = os.environ.get("AETHERRA_HUB_HOST", "127.0.0.1").strip()
    try:
        hub_port = int(os.environ.get("AETHERRA_HUB_PORT", "3001").strip())
    except Exception:
        hub_port = 3001
    return f"http://{hub_host}:{hub_port}"


# -----------------------
# Utilities / Base Widgets
# -----------------------
class LogPane(QPlainTextEdit):
    def __init__(self, *, read_only: bool = True):
        super().__init__()
        self.setReadOnly(read_only)
        self.setMaximumBlockCount(5000)
        try:
            wrap_mode = getattr(QTextOption, "WrapAtWordBoundaryOrAnywhere", None)
            if wrap_mode is not None:
                self.setWordWrapMode(wrap_mode)
        except Exception:
            # Fallback: ignore if wrap mode API differs
            pass
        self.setStyleSheet(
            "QPlainTextEdit { background: #0a0a0a; color: #00ff88; font-family: 'JetBrains Mono', monospace; font-size: 12px; border-radius: 10px; padding: 8px; }"
        )

    def println(self, text: str):
        self.appendPlainText(text.rstrip("\n"))


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "—"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame { background: #1a1a1a; border: 1px solid #222; border-radius: 16px; } QLabel { color: #eaeaea; }"
        )
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setStyleSheet("QLabel { color: #9adbb5; font-size: 12px; }")
        self.value = QLabel(value)
        self.value.setStyleSheet(
            "QLabel { color: #ffffff; font-size: 20px; font-weight: 700; }"
        )
        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def set_value(self, value: str):
        self.value.setText(value)


class Toolbar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            "QFrame { background: #0f0f0f; border-bottom: 1px solid #222; }"
        )
        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(12, 8, 12, 8)


# -----------------------
# Subprocess streaming
# -----------------------
class Streamer(QObject):
    line = Signal(str)
    finished = Signal(int)

    def __init__(
        self, argv: list[str], cwd: Optional[str] = None, env: Optional[dict] = None
    ):
        super().__init__()
        self.argv = argv
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self._proc: Optional[subprocess.Popen] = None

    def start(self):
        def run():
            try:
                self._proc = subprocess.Popen(
                    self.argv,
                    cwd=self.cwd,
                    env=self.env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,
                    universal_newlines=True,
                )
                for line in self._proc.stdout or []:
                    self.line.emit(line.rstrip("\n"))
                code = self._proc.wait()
                self.finished.emit(code)
            except FileNotFoundError:
                self.line.emit("[ERROR] Command not found: %r" % (self.argv,))
                self.finished.emit(127)
            except Exception as e:
                self.line.emit(f"[ERROR] {e}")
                self.finished.emit(1)

        threading.Thread(target=run, daemon=True).start()

    def terminate(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()


# -----------------------
# Demo 1: Kernel Status Dashboard
# -----------------------
class KernelStatusWindow(QMainWindow):
    def __init__(self, base_url: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("Aetherra • Kernel Status")
        self.resize(980, 680)

        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)

        # Toolbar
        bar = Toolbar()
        v.addWidget(bar)

        if not base_url:
            base_url = get_default_base_url()
        self.base_url_edit = QLineEdit(base_url)
        self.base_url_edit.setPlaceholderText(
            "Hub base URL, e.g. http://127.0.0.1:3001"
        )
        self.refresh_btn = QPushButton("Refresh Now")
        self.auto_spin = QSpinBox()
        self.auto_spin.setRange(0, 3600)
        self.auto_spin.setValue(3)
        self.auto_spin.setToolTip("Auto-refresh seconds (0 = off)")
        bar.hbox.addWidget(QLabel("Base URL:"))
        bar.hbox.addWidget(self.base_url_edit, 1)
        bar.hbox.addWidget(QLabel("Auto(s):"))
        bar.hbox.addWidget(self.auto_spin)
        bar.hbox.addWidget(self.refresh_btn)

        # Metrics row
        row = QHBoxLayout()
        v.addLayout(row)
        self.running_card = MetricCard("Running")
        self.uptime_card = MetricCard("Uptime")
        self.queue_card = MetricCard("Queues")
        row.addWidget(self.running_card)
        row.addWidget(self.uptime_card)
        row.addWidget(self.queue_card)

        # Log pane
        self.log = LogPane()
        v.addWidget(self.log, 1)

        self.t = QTimer(self)
        self.t.timeout.connect(self.refresh)
        self.refresh_btn.clicked.connect(self.refresh)
        self.auto_spin.valueChanged.connect(self._update_timer)
        self._update_timer(self.auto_spin.value())

        # First refresh
        QTimer.singleShot(100, self.refresh)

    def _update_timer(self, secs: int):
        if secs <= 0:
            self.t.stop()
        else:
            self.t.start(secs * 1000)

    def _get(self, path: str) -> Optional[dict]:
        if requests is None:
            self.log.println("[WARN] requests not installed; skipping HTTP calls.")
            return None
        url = self.base_url_edit.text().rstrip("/") + path
        try:
            r = requests.get(url, timeout=4)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            self.log.println(f"[HTTP] GET {url} → ERROR: {e}")
            return None

    def _probe_base_url(self) -> bool:
        """Try a few candidate base URLs and pick the first that responds.
        Returns True if a working base URL was found and set.
        """
        if requests is None:
            return False
        candidates = []
        # Current field value first
        cur = (self.base_url_edit.text() or "").strip()
        if cur:
            candidates.append(cur)
        # Env-provided full URL
        if os.environ.get("AETHERRA_BASE_URL"):
            candidates.append(os.environ["AETHERRA_BASE_URL"])  # type: ignore[index]
        # Hub env host/port
        hub_host = os.environ.get("AETHERRA_HUB_HOST", "127.0.0.1").strip()
        try:
            hub_port = int(os.environ.get("AETHERRA_HUB_PORT", "3001").strip())
        except Exception:
            hub_port = 3001
        candidates.append(f"http://{hub_host}:{hub_port}")
        # Common fallbacks
        for p in (3001, 8686, 8000):
            candidates.append(f"http://127.0.0.1:{p}")
        seen = set()
        for base in candidates:
            base = base.rstrip("/")
            if not base or base in seen:
                continue
            seen.add(base)
            try:
                r = requests.get(base + "/api/kernel/status", timeout=2)
                if r.ok:
                    self.base_url_edit.setText(base)
                    self.log.println(f"[INFO] Using Hub at {base}")
                    return True
            except Exception:
                continue
        return False

    def refresh(self):
        status = self._get("/api/kernel/status")
        metrics = self._get("/api/kernel/metrics")

        # If both failed, try probing other common ports/hosts once per refresh call
        if not status and not metrics:
            if self._probe_base_url():
                status = self._get("/api/kernel/status")
                metrics = self._get("/api/kernel/metrics")

        if status:
            running = "✅" if status.get("running") else "❌"
            self.running_card.set_value(running)
            self.uptime_card.set_value(str(status.get("uptime", "—")))
            # Prefer queue_sizes; fallback to queues
            qs = {}
            try:
                if isinstance(status.get("queue_sizes"), dict):
                    qs = status.get("queue_sizes", {}) or {}
                elif isinstance(status.get("queues"), dict):
                    qs = status.get("queues", {}) or {}
            except Exception:
                qs = {}
            qstr = ", ".join(f"{k}:{v}" for k, v in qs.items()) if qs else "—"
            self.queue_card.set_value(qstr)
            self.log.println("[STATUS] " + json.dumps(status))

        if metrics:
            self.log.println("[METRICS] " + json.dumps(metrics))


# -----------------------
# Demo 2: Agent Pipeline (runs CLI & streams logs)
# -----------------------
class AgentPipelineWindow(QMainWindow):
    def __init__(self, topic: str = "quantum memory"):
        super().__init__()
        self.setWindowTitle("Aetherra • Agent Pipeline Demo")
        self.resize(980, 680)

        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)

        # Controls
        controls = Toolbar()
        v.addWidget(controls)
        self.topic = QLineEdit(topic)
        self.run_btn = QPushButton("Run Pipeline")
        controls.hbox.addWidget(QLabel("Topic:"))
        controls.hbox.addWidget(self.topic, 1)
        controls.hbox.addWidget(self.run_btn)

        # Output
        self.log = LogPane()
        v.addWidget(self.log, 1)
        self.streamer = None
        self.run_btn.clicked.connect(self.on_run)

    def on_run(self):
        if self.streamer:
            self.streamer.terminate()
            self.streamer = None
        script_path = os.path.join(
            os.path.dirname(__file__), "demos", "agent_pipeline_demo.py"
        )
        if not os.path.exists(script_path):
            self.log.println(f"[ERROR] Missing demo script: {script_path}")
            self.log.println(
                "Please install or adjust the path to a valid pipeline demo."
            )
            return
        argv = [
            sys.executable,
            script_path,
            "--topic",
            self.topic.text(),
        ]
        self.log.println("$ " + " ".join(argv))
        self.streamer = Streamer(argv)
        self.streamer.line.connect(self.log.println)
        self.streamer.finished.connect(
            lambda code: self.log.println(f"[DONE] exit={code}")
        )
        self.streamer.start()


# -----------------------
# Demo 3: Chat Stream (runs CLI & streams logs)
# -----------------------
class ChatStreamWindow(QMainWindow):
    def __init__(self, prompt: str = "Explain HMR in two sentences"):
        super().__init__()
        self.setWindowTitle("Aetherra • Chat Stream Demo")
        self.resize(980, 680)

        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)

        # Controls
        controls = Toolbar()
        v.addWidget(controls)
        self.base = QLineEdit(get_default_base_url())
        self.base.setPlaceholderText("http://127.0.0.1:3001")
        self.token = QLineEdit()
        self.token.setPlaceholderText("X-Aetherra-Token (optional)")
        self.prompt = QLineEdit(prompt)
        self.run_btn = QPushButton("Start Stream")
        controls.hbox.addWidget(QLabel("Base URL:"))
        controls.hbox.addWidget(self.base, 1)
        controls.hbox.addWidget(QLabel("Token:"))
        controls.hbox.addWidget(self.token)
        controls.hbox.addWidget(QLabel("Prompt:"))
        controls.hbox.addWidget(self.prompt, 2)
        controls.hbox.addWidget(self.run_btn)

        # Output
        self.log = LogPane()
        v.addWidget(self.log, 1)
        self.streamer = None
        self.run_btn.clicked.connect(self.on_run)

    def on_run(self):
        if self.streamer:
            self.streamer.terminate()
            self.streamer = None
        script_path = os.path.join(
            os.path.dirname(__file__), "demos", "chat_stream_demo.py"
        )
        if not os.path.exists(script_path):
            self.log.println(f"[ERROR] Missing demo script: {script_path}")
            self.log.println(
                "Please install or adjust the path to a valid chat stream demo."
            )
            return
        argv = [
            sys.executable,
            script_path,
            "--prompt",
            self.prompt.text(),
        ]
        # Pass base URL and token to the subprocess via env so it targets the intended Hub
        child_env = os.environ.copy()
        if self.base.text().strip():
            child_env["AETHERRA_BASE_URL"] = self.base.text().strip()
        if self.token.text().strip():
            child_env["AETHERRA_AI_API_TOKEN"] = self.token.text().strip()
        self.log.println("$ " + " ".join(argv))
        self.streamer = Streamer(argv, env=child_env)
        self.streamer.line.connect(self.log.println)
        self.streamer.finished.connect(
            lambda code: self.log.println(f"[DONE] exit={code}")
        )
        self.streamer.start()


# -----------------------
# Registry & Launcher
# -----------------------
_DEMOS: dict[str, Callable[[], QMainWindow]] = {
    "kernel_status": lambda: KernelStatusWindow(),
    "agent_pipeline": lambda: AgentPipelineWindow(),
    "chat_stream": lambda: ChatStreamWindow(),
}


def launch(demo: str):
    app = QApplication.instance() or QApplication(sys.argv)
    ctor = _DEMOS.get(demo)
    if not ctor:
        QMessageBox.critical(
            None,
            "Unknown Demo",
            f"Unknown demo: {demo}\nAvailable: {', '.join(sorted(_DEMOS))}",
        )
        sys.exit(2)
    win = ctor()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # CLI: python adk_demo_ui.py --demo kernel_status
    demo = None
    argv = sys.argv[1:]
    for i, tok in enumerate(argv):
        if tok == "--demo" and i + 1 < len(argv):
            demo = argv[i + 1]
            break
    if demo is None:
        # allow env var for easy per-file launchers
        demo = os.environ.get("AETHERRA_DEMO")
    if not demo:
        print(
            "Usage: python adk_demo_ui.py --demo <kernel_status|agent_pipeline|chat_stream>"
        )
        sys.exit(2)
    launch(demo)
