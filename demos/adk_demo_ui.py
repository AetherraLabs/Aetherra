# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Demo UI Kit (PySide6)
Single-file scaffold to give each CLI demo an independent, runnable UI.

Demos:
  - kernel_status: polls Hub API for status/metrics
  - agent_pipeline: runs a CLI demo and streams logs
  - chat_stream: runs chat stream CLI and shows awareness pane

Usage:
  python demos/adk_demo_ui.py --demo chat_stream --prompt "Explain HMR briefly"
"""

from __future__ import annotations

# Standard library imports
import contextlib
import json
import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from collections.abc import Callable
from typing import Any

# Third party imports
from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

try:
    # Third party imports
    import requests
except Exception:
    requests = None


def get_default_base_url() -> str:
    env_url = os.environ.get("AETHERRA_BASE_URL")
    if env_url:
        return env_url
    host = os.environ.get("AETHERRA_HUB_HOST", "127.0.0.1").strip()
    try:
        port = int(os.environ.get("AETHERRA_HUB_PORT", "3001").strip())
    except Exception:
        port = 3001
    return f"http://{host}:{port}"


class LogPane(QPlainTextEdit):
    def __init__(self, *, read_only: bool = True):
        super().__init__()
        self.setReadOnly(read_only)
        self.setMaximumBlockCount(5000)
        with contextlib.suppress(Exception):
            wrap_mode = getattr(QTextOption, "WrapAtWordBoundaryOrAnywhere", None)
            if wrap_mode is not None:
                self.setWordWrapMode(wrap_mode)
        self.setStyleSheet(
            "QPlainTextEdit { background:#0a0a0a; color:#00ff88; font-family:'JetBrains Mono', monospace; font-size:12px; border-radius:10px; padding:8px; }"
        )

    def println(self, text: str):
        self.appendPlainText(text.rstrip("\n"))


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "—"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame { background:#1a1a1a; border:1px solid #222; border-radius:16px; } QLabel { color:#eaeaea; }"
        )
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setStyleSheet("QLabel { color:#9adbb5; font-size:12px; }")
        self.value = QLabel(value)
        self.value.setStyleSheet(
            "QLabel { color:#fff; font-size:20px; font-weight:700; }"
        )
        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def set_value(self, value: str):
        self.value.setText(value)


class Toolbar(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            "QFrame { background:#0f0f0f; border-bottom:1px solid #222; }"
        )
        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(12, 8, 12, 8)


class Streamer(QObject):
    line = Signal(str)
    finished = Signal(int)

    def __init__(
        self, argv: list[str], cwd: str | None = None, env: dict | None = None
    ):
        super().__init__()
        self.argv = argv
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self._proc: subprocess.Popen | None = None

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
                self.line.emit(f"[ERROR] Command not found: {self.argv!r}")
                self.finished.emit(127)
            except Exception as e:
                self.line.emit(f"[ERROR] {e}")
                self.finished.emit(1)

        threading.Thread(target=run, daemon=True).start()

    def terminate(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()


class KernelStatusWindow(QMainWindow):
    def __init__(self, base_url: str | None = None):
        super().__init__()
        self.setWindowTitle("Aetherra • Kernel Status")
        self.resize(980, 680)

        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)

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

        row = QHBoxLayout()
        v.addLayout(row)
        self.running_card = MetricCard("Running")
        self.uptime_card = MetricCard("Uptime")
        self.queue_card = MetricCard("Queues")
        row.addWidget(self.running_card)
        row.addWidget(self.uptime_card)
        row.addWidget(self.queue_card)

        self.log = LogPane()
        v.addWidget(self.log, 1)
        self.t = QTimer(self)
        self.t.timeout.connect(self.refresh)
        self.refresh_btn.clicked.connect(self.refresh)
        self.auto_spin.valueChanged.connect(self._update_timer)
        self._update_timer(self.auto_spin.value())
        QTimer.singleShot(100, self.refresh)

    def _update_timer(self, secs: int):
        if secs <= 0:
            self.t.stop()
        else:
            self.t.start(secs * 1000)

    def _get(self, path: str) -> dict[str, Any] | None:
        if requests is None:
            self.log.println("[WARN] requests not installed; skipping HTTP calls.")
            return None
        url = self.base_url_edit.text().rstrip("/") + path
        try:
            r = requests.get(url, timeout=4)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                return data
            self.log.println(
                f"[HTTP] GET {url} → unexpected JSON type: {type(data).__name__}"
            )
            return None
        except Exception as e:
            self.log.println(f"[HTTP] GET {url} → ERROR: {e}")
            return None

    def _probe_base_url(self) -> bool:
        if requests is None:
            return False
        candidates: list[str] = []
        cur = (self.base_url_edit.text() or "").strip()
        if cur:
            candidates.append(cur)
        if os.environ.get("AETHERRA_BASE_URL"):
            candidates.append(os.environ["AETHERRA_BASE_URL"])
        host = os.environ.get("AETHERRA_HUB_HOST", "127.0.0.1").strip()
        try:
            port = int(os.environ.get("AETHERRA_HUB_PORT", "3001").strip())
        except Exception:
            port = 3001
        candidates.append(f"http://{host}:{port}")
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
            except Exception as e:
                self.log.println(f"[INFO] Probe failed for {base}: {e}")
                continue
        return False

    def refresh(self):
        status = self._get("/api/kernel/status")
        metrics = self._get("/api/kernel/metrics")
        if (not status and not metrics) and self._probe_base_url():
            status = self._get("/api/kernel/status")
            metrics = self._get("/api/kernel/metrics")
        if status:
            running = "✅" if status.get("running") else "❌"
            self.running_card.set_value(running)
            self.uptime_card.set_value(str(status.get("uptime", "—")))
            qs: dict[str, int] = {}
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


class AgentPipelineWindow(QMainWindow):
    def __init__(self, topic: str = "quantum memory"):
        super().__init__()
        self.setWindowTitle("Aetherra • Agent Pipeline Demo")
        self.resize(980, 680)

        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)

        controls = Toolbar()
        v.addWidget(controls)
        self.topic = QLineEdit(topic)
        self.run_btn = QPushButton("Run Pipeline")
        controls.hbox.addWidget(QLabel("Topic:"))
        controls.hbox.addWidget(self.topic, 1)
        controls.hbox.addWidget(self.run_btn)

        self.log = LogPane()
        v.addWidget(self.log, 1)
        self.streamer: Streamer | None = None
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
        argv = [sys.executable, script_path, "--topic", self.topic.text()]
        self.log.println("$ " + " ".join(argv))
        self.streamer = Streamer(argv)
        self.streamer.line.connect(self.log.println)
        self.streamer.finished.connect(
            lambda code: self.log.println(f"[DONE] exit={code}")
        )
        self.streamer.start()


class ChatStreamWindow(QMainWindow):
    def __init__(self, prompt: str = "Explain HMR in two sentences"):
        super().__init__()
        self.setWindowTitle("Aetherra • Chat Stream Demo")
        self.resize(980, 680)

        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)

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

        content_row = QHBoxLayout()
        v.addLayout(content_row, 1)
        self.log = LogPane()
        content_row.addWidget(self.log, 1)

        self.aw_panel = QFrame()
        self.aw_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.aw_panel.setStyleSheet(
            "QFrame { background:#101010; border:1px solid #222; border-radius:12px; } QLabel { color:#eaeaea; }"
        )
        self.aw_panel.setMinimumWidth(240)
        self.aw_panel.setMaximumWidth(280)
        aw_v = QVBoxLayout(self.aw_panel)
        aw_v.setContentsMargins(10, 10, 10, 10)

        aw_title = QLabel("Awareness")
        aw_title.setStyleSheet(
            "QLabel { color:#9adbb5; font-weight:700; font-size:14px; }"
        )
        aw_v.addWidget(aw_title)

        self.persona_label = QLabel("—")
        self.persona_label.setStyleSheet(
            "QLabel { color:#ffffff; font-size:12px; font-weight:700; }"
        )
        row = QHBoxLayout()
        row.addWidget(QLabel("Persona"))
        row.addStretch(1)
        row.addWidget(self.persona_label)
        aw_v.addLayout(row)

        self.model_label = QLabel("—")
        self.model_label.setStyleSheet(
            "QLabel { color:#ffffff; font-size:12px; font-weight:700; }"
        )
        row = QHBoxLayout()
        row.addWidget(QLabel("Model"))
        row.addStretch(1)
        row.addWidget(self.model_label)
        aw_v.addLayout(row)

        self.chunk_count = 0
        self.chunks_label = QLabel("0")
        self.chunks_label.setStyleSheet(
            "QLabel { color:#ffffff; font-size:12px; font-weight:700; }"
        )
        row = QHBoxLayout()
        row.addWidget(QLabel("Chunks"))
        row.addStretch(1)
        row.addWidget(self.chunks_label)
        aw_v.addLayout(row)

        self.cb_labels: dict[str, QLabel] = {}
        for key in ("model", "grounding", "coherence", "safety"):
            row = QHBoxLayout()
            k = QLabel(key.title())
            k.setStyleSheet("QLabel { color:#9adbb5; font-size:11px; }")
            vlab = QLabel("—")
            vlab.setStyleSheet(
                "QLabel { color:#ffffff; font-size:12px; font-weight:700; }"
            )
            row.addWidget(k)
            row.addStretch(1)
            row.addWidget(vlab)
            aw_v.addLayout(row)
            self.cb_labels[key] = vlab

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("QFrame { color:#222; background:#222; max-height:1px; }")
        aw_v.addWidget(sep)

        ev_title = QLabel("Evidence (top 3)")
        ev_title.setStyleSheet("QLabel { color:#9adbb5; font-size:12px; }")
        aw_v.addWidget(ev_title)

        self.ev_list = QListWidget()
        self.ev_list.setStyleSheet(
            "QListWidget { background:#0a0a0a; border:1px solid #222; border-radius:8px; color:#eaeaea; font-size:11px; }"
        )
        self.ev_list.setMaximumHeight(180)
        self.ev_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ev_list.customContextMenuRequested.connect(self._on_ev_context_menu)
        aw_v.addWidget(self.ev_list, 0)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("QFrame { color:#222; background:#222; max-height:1px; }")
        aw_v.addWidget(sep2)

        sug_title = QLabel("Suggestions")
        sug_title.setStyleSheet("QLabel { color:#9adbb5; font-size:12px; }")
        aw_v.addWidget(sug_title)

        self.sug_list = QListWidget()
        self.sug_list.setStyleSheet(
            "QListWidget { background:#0a0a0a; border:1px solid #222; border-radius:8px; color:#eaeaea; font-size:11px; }"
        )
        self.sug_list.setMaximumHeight(100)
        self.sug_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sug_list.customContextMenuRequested.connect(self._on_sug_context_menu)
        aw_v.addWidget(self.sug_list, 0)

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("QFrame { color:#222; background:#222; max-height:1px; }")
        aw_v.addWidget(sep3)

        appl_title = QLabel("Applied Changes")
        appl_title.setStyleSheet("QLabel { color:#9adbb5; font-size:12px; }")
        aw_v.addWidget(appl_title)

        self.applied_list = QListWidget()
        self.applied_list.setStyleSheet(
            "QListWidget { background:#0a0a0a; border:1px solid #222; border-radius:8px; color:#eaeaea; font-size:11px; }"
        )
        self.applied_list.setMaximumHeight(120)
        self.applied_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.applied_list.customContextMenuRequested.connect(
            self._on_applied_context_menu
        )
        aw_v.addWidget(self.applied_list, 0)

        sep4 = QFrame()
        sep4.setFrameShape(QFrame.Shape.HLine)
        sep4.setStyleSheet("QFrame { color:#222; background:#222; max-height:1px; }")
        aw_v.addWidget(sep4)

        usage_row = QHBoxLayout()
        ulabel = QLabel("Usage")
        ulabel.setStyleSheet("QLabel { color:#9adbb5; font-size:11px; }")
        self.usage_label = QLabel("—")
        self.usage_label.setStyleSheet(
            "QLabel { color:#ffffff; font-size:11px; font-weight:600; }"
        )
        usage_row.addWidget(ulabel)
        usage_row.addStretch(1)
        usage_row.addWidget(self.usage_label)
        aw_v.addLayout(usage_row)

        content_row.addWidget(self.aw_panel, 0)

        self.aw_toggle = QPushButton("Awareness")
        self.aw_toggle.setCheckable(True)
        self.aw_toggle.setChecked(True)
        self.aw_toggle.setToolTip("Show/hide awareness panel")
        controls.hbox.addWidget(self.aw_toggle)

        self.copy_aw_btn = QPushButton("Copy Awareness")
        self.copy_aw_btn.setToolTip(
            "Copy persona/model/confidence/evidence/suggestions/applied/usage to clipboard"
        )
        self.copy_aw_btn.clicked.connect(self._copy_awareness_summary)
        controls.hbox.addWidget(self.copy_aw_btn)

        self.streamer: Streamer | None = None
        self.run_btn.clicked.connect(self.on_run)
        self.aw_toggle.toggled.connect(self.aw_panel.setVisible)
        self.aw_panel.setVisible(True)

    def on_run(self):
        if self.streamer:
            self.streamer.terminate()
            self.streamer = None
        self._reset_awareness()
        script_path = os.path.join(
            os.path.dirname(__file__), "demos", "chat_stream_demo.py"
        )
        if not os.path.exists(script_path):
            self.log.println(f"[ERROR] Missing demo script: {script_path}")
            self.log.println(
                "Please install or adjust the path to a valid chat stream demo."
            )
            return
        argv = [sys.executable, script_path, "--prompt", self.prompt.text()]
        env = os.environ.copy()
        if self.base.text().strip():
            env["AETHERRA_BASE_URL"] = self.base.text().strip()
        if self.token.text().strip():
            env["AETHERRA_AI_API_TOKEN"] = self.token.text().strip()
        self.log.println("$ " + " ".join(argv))
        self.streamer = Streamer(argv, env=env)
        self.streamer.line.connect(self._on_stream_line)
        self.streamer.finished.connect(
            lambda code: self.log.println(f"[DONE] exit={code}")
        )
        self.streamer.start()

    def _reset_awareness(self):
        for lab in (getattr(self, "cb_labels", {}) or {}).values():
            with contextlib.suppress(Exception):
                lab.setText("—")
        with contextlib.suppress(Exception):
            self.ev_list.clear()
        with contextlib.suppress(Exception):
            self.persona_label.setText("—")
            self.model_label.setText("—")
            self.chunks_label.setText("0")
            self.chunk_count = 0
        with contextlib.suppress(Exception):
            self.sug_list.clear()
        with contextlib.suppress(Exception):
            self.applied_list.clear()
        with contextlib.suppress(Exception):
            self.usage_label.setText("—")

    def _on_stream_line(self, line: str):
        with contextlib.suppress(Exception):
            self.log.println(line)
        s = line.strip()
        try:
            if s.startswith("[PERSONA] "):
                self.persona_label.setText(s[len("[PERSONA] ") :].strip() or "—")
                return
            if s.startswith("[MODEL] "):
                self.model_label.setText(s[len("[MODEL] ") :].strip() or "—")
                return
            if s.startswith("[CHUNK] "):
                self.chunk_count = (self.chunk_count or 0) + 1
                with contextlib.suppress(Exception):
                    self.chunks_label.setText(str(self.chunk_count))
            if s.startswith("[CONF] "):
                payload = s[len("[CONF] ") :]
                for part in payload.split("|"):
                    part = part.strip()
                    if (not part) or (":" not in part):
                        continue
                    k, v = part.split(":", 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if k in self.cb_labels:
                        self.cb_labels[k].setText(v)
            elif s.startswith("[EVID "):
                display = s[7:].strip()
                content = display
                rb = content.find("]")
                if rb != -1:
                    content = content[rb + 1 :].strip()
                score_val = None
                lpar = content.rfind("(score ")
                rpar = content.rfind(")")
                if lpar != -1 and rpar != -1 and rpar > lpar:
                    score_val = content[lpar + len("(score ") : rpar].strip()
                    content = (content[:lpar] + content[rpar + 1 :]).strip()
                title = content
                source = ""
                sep = " — "
                if sep in content:
                    title, source = content.split(sep, 1)
                    title = title.strip()
                    source = source.strip()
                item = QListWidgetItem(display)
                tt = [f"Title: {title or '—'}"]
                if source:
                    tt.append(f"Source: {source}")
                if score_val:
                    tt.append(f"Score: {score_val}")
                item.setToolTip("\n".join(tt))
                with contextlib.suppress(Exception):
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        {"title": title, "source": source, "score": score_val},
                    )
                self.ev_list.addItem(item)
                while self.ev_list.count() > 3:
                    self.ev_list.takeItem(0)
            elif s.startswith("[SUG "):
                content = s
                rb = content.find("]")
                if rb != -1:
                    content = content[rb + 1 :].strip()
                item = QListWidgetItem(content)
                item.setToolTip(content)
                self.sug_list.addItem(item)
                while self.sug_list.count() > 3:
                    self.sug_list.takeItem(0)
            elif s.startswith("[APPLIED "):
                content = s
                rb = content.find("]")
                if rb != -1:
                    content = content[rb + 1 :].strip()
                item = QListWidgetItem(content)
                item.setToolTip(content)
                self.applied_list.addItem(item)
                while self.applied_list.count() > 3:
                    self.applied_list.takeItem(0)
            elif s.startswith("[USAGE] "):
                self.usage_label.setText(s[len("[USAGE] ") :].strip() or "—")
        except Exception as e:
            self.log.println(f"[STREAM] Parse error: {e}")

    def _copy_to_clipboard(self, text: str):
        with contextlib.suppress(Exception):
            QApplication.clipboard().setText(text)

    def _is_safe_url(self, url: str) -> bool:
        """Validate that URL is safe and well-formed."""
        # Standard library imports
        import urllib.parse

        if not url:
            return False

        # Must start with safe protocols
        if not (url.startswith("https://") or url.startswith("http://")):
            return False

        try:
            parsed = urllib.parse.urlparse(url)

            # Must have valid scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False

            # Block local/private IPs and dangerous hosts
            dangerous_hosts = [
                "localhost",
                "127.0.0.1",
                "0.0.0.0",  # noqa: S104 - listed to block targets, not to bind
                "::1",
                "10.",
                "172.",
                "192.168.",
                "169.254.",
                "metadata.google.internal",
                "169.254.169.254",
            ]

            netloc_lower = parsed.netloc.lower()
            if any(netloc_lower.startswith(host) for host in dangerous_hosts):
                return False

            # Block non-HTTP schemes
            return parsed.scheme in ("http", "https")

        except Exception:
            return False

    def _open_path(self, path: str):
        try:
            path = os.path.expanduser(path)
            if sys.platform.startswith("win"):
                # Prefer Explorer on Windows to avoid shell execution concerns
                exe = shutil.which("explorer")
                if exe:
                    subprocess.Popen([exe, path])
                else:
                    self.log.println("[OPEN] 'explorer' not found")
            elif sys.platform == "darwin":
                exe = shutil.which("open")
                if exe:
                    subprocess.Popen([exe, path])
                else:
                    self.log.println("[OPEN] 'open' not found")
            else:
                exe = shutil.which("xdg-open")
                if exe:
                    subprocess.Popen([exe, path])
                else:
                    self.log.println("[OPEN] 'xdg-open' not found")
        except Exception as e:
            self.log.println(f"[OPEN] Failed: {e}")

    def _reveal_in_explorer(self, path: str):
        try:
            path = os.path.abspath(path)
            if sys.platform.startswith("win"):
                exe = shutil.which("explorer")
                if not exe:
                    self.log.println("[REVEAL] 'explorer' not found")
                    return
                if os.path.isdir(path):
                    subprocess.Popen([exe, path])
                else:
                    subprocess.Popen([exe, "/select,", path])
            elif sys.platform == "darwin":
                exe = shutil.which("open")
                if exe:
                    subprocess.Popen([exe, "-R", path])
                else:
                    self.log.println("[REVEAL] 'open' not found")
            else:
                folder = path if os.path.isdir(path) else os.path.dirname(path) or "."
                exe = shutil.which("xdg-open")
                if exe:
                    subprocess.Popen([exe, folder])
                else:
                    self.log.println("[REVEAL] 'xdg-open' not found")
        except Exception as e:
            self.log.println(f"[REVEAL] Failed: {e}")

    def _on_ev_context_menu(self, pos):
        try:
            item = self.ev_list.itemAt(pos)
            if not item:
                return
            menu = QMenu(self)
            text = item.text()
            menu.addAction("Copy", lambda: self._copy_to_clipboard(text))
            source = None
            try:
                data = item.data(Qt.ItemDataRole.UserRole) or {}
                source = (data or {}).get("source")
            except Exception:
                source = None
            if not source:
                tt = item.toolTip() or ""
                for line in tt.splitlines():
                    if line.startswith("Source: "):
                        source = line[len("Source: ") :].strip()
                        break
            if source and self._is_safe_url(str(source)):
                menu.addSeparator()
                menu.addAction("Open URL", lambda s=source: webbrowser.open(s))
            if source and os.path.exists(str(source)):
                menu.addSeparator()
                menu.addAction("Open Source", lambda s=source: self._open_path(str(s)))
                menu.addAction(
                    "Reveal in Explorer",
                    lambda s=source: self._reveal_in_explorer(str(s)),
                )
            menu.exec(self.ev_list.mapToGlobal(pos))  # nosec B102: Qt GUI menu execution
        except Exception as e:
            self.log.println(f"[EV MENU] Failed: {e}")

    def _on_sug_context_menu(self, pos):
        try:
            item = self.sug_list.itemAt(pos)
            if not item:
                return
            menu = QMenu(self)
            text = item.text()
            menu.addAction("Copy", lambda: self._copy_to_clipboard(text))
            menu.exec(self.sug_list.mapToGlobal(pos))  # nosec B102: Qt GUI menu execution
        except Exception as e:
            self.log.println(f"[SUG MENU] Failed: {e}")

    def _on_applied_context_menu(self, pos):
        try:
            item = self.applied_list.itemAt(pos)
            if not item:
                return
            menu = QMenu(self)
            text = item.text()
            menu.addAction("Copy", lambda: self._copy_to_clipboard(text))
            path_candidate = text
            if " — " in text:
                path_candidate = text.split(" — ", 1)[0].strip()
            if path_candidate and os.path.exists(path_candidate):
                menu.addSeparator()
                menu.addAction("Open File", lambda p=path_candidate: self._open_path(p))
                menu.addAction(
                    "Reveal in Explorer",
                    lambda p=path_candidate: self._reveal_in_explorer(p),
                )
            menu.exec(self.applied_list.mapToGlobal(pos))  # nosec B102: Qt GUI menu execution
        except Exception as e:
            self.log.println(f"[APPLIED MENU] Failed: {e}")

    def _copy_awareness_summary(self):
        try:
            lines: list[str] = []
            persona = (self.persona_label.text() or "").strip()
            model = (self.model_label.text() or "").strip()
            chunks = (self.chunks_label.text() or "0").strip()
            if persona and persona != "—":
                lines.append(f"Persona: {persona}")
            if model and model != "—":
                lines.append(f"Model: {model}")
            lines.append(f"Chunks: {chunks}")
            parts = []
            for k in ("model", "grounding", "coherence", "safety"):
                with contextlib.suppress(Exception):
                    v = self.cb_labels[k].text().strip()
                    if v:
                        parts.append(f"{k}:{v}")
            if parts:
                lines.append("Confidence: " + " | ".join(parts))
            if self.ev_list is not None:
                ev_lines = []
                for i in range(min(3, self.ev_list.count())):
                    it = self.ev_list.item(i)
                    if it:
                        ev_lines.append(f"- {it.text()}")
                if ev_lines:
                    lines.append("Evidence:\n" + "\n".join(ev_lines))
            if self.sug_list is not None:
                sg_lines = []
                for i in range(min(3, self.sug_list.count())):
                    it = self.sug_list.item(i)
                    if it:
                        sg_lines.append(f"- {it.text()}")
                if sg_lines:
                    lines.append("Suggestions:\n" + "\n".join(sg_lines))
            if self.applied_list is not None:
                ap_lines = []
                for i in range(min(3, self.applied_list.count())):
                    it = self.applied_list.item(i)
                    if it:
                        ap_lines.append(f"- {it.text()}")
                if ap_lines:
                    lines.append("Applied Changes:\n" + "\n".join(ap_lines))
            usage = (self.usage_label.text() or "").strip()
            if usage and usage != "—":
                lines.append(f"Usage: {usage}")
            self._copy_to_clipboard("\n".join(lines))
            self.log.println("[CLIPBOARD] Awareness summary copied")
        except Exception as e:
            self.log.println(f"[CLIPBOARD] Failed: {e}")


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
    sys.exit(app.exec())  # nosec B102: Qt application execution


if __name__ == "__main__":
    demo = None
    argv = sys.argv[1:]
    for i, tok in enumerate(argv):
        if tok == "--demo" and i + 1 < len(argv):
            demo = argv[i + 1]
            break
    if demo is None:
        demo = os.environ.get("AETHERRA_DEMO")
    if not demo:
        print(
            "Usage: python demos/adk_demo_ui.py --demo <kernel_status|agent_pipeline|chat_stream>"
        )
        sys.exit(2)
    launch(demo)
