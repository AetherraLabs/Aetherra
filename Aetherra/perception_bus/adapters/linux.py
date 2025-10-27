# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Linux Perception Adapters
==========================

Real-world telemetry from Linux using proc, journald, and inotify.
No simulation—only actual system metrics.
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import threading
import time

from Aetherra.consciousness.core.types import Event

from ..event_types import (
    DISK_STATUS,
    ERR_LOG,
    FS_CHANGE,
    PROC_SNAPSHOT,
    SVC_HEALTH,
)
from .common import AdapterBase


class LinuxProcAdapter(AdapterBase):
    """Linux process monitoring via /proc."""

    name = "linux.proc"

    def start(self) -> None:
        """Start background process monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            while self.is_running:
                with contextlib.suppress(Exception):
                    # Count processes
                    pids = [p for p in os.listdir("/proc") if p.isdigit()]

                    # Top CPU process
                    top = subprocess.run(
                        [
                            "bash",
                            "-lc",
                            "ps -eo pid,pcpu,comm --sort=-pcpu | head -n 2 | tail -n 1",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )

                    self.bus.publish(
                        Event(
                            type=PROC_SNAPSHOT,
                            payload={
                                "proc_count": len(pids),
                                "top": top.stdout.strip(),
                            },
                            source=self.name,
                        )
                    )

                time.sleep(5)

        threading.Thread(target=run, daemon=True, name=self.name).start()


class LinuxDiskAdapter(AdapterBase):
    """Linux disk monitoring via statvfs."""

    name = "linux.disk"

    def start(self) -> None:
        """Start background disk monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            while self.is_running:
                with contextlib.suppress(Exception):
                    # Only available on Unix-like systems
                    if hasattr(os, "statvfs"):
                        st = os.statvfs("/")  # type: ignore
                        free = st.f_bavail * st.f_frsize
                        total = st.f_blocks * st.f_frsize
                        pct_free = (free / total) * 100 if total else 0

                        self.bus.publish(
                            Event(
                                type=DISK_STATUS,
                                payload={"mount": "/", "pct_free": pct_free},
                                source=self.name,
                            )
                        )

                time.sleep(30)

        threading.Thread(target=run, daemon=True, name=self.name).start()


class LinuxJournalAdapter(AdapterBase):
    """Linux journald log monitoring."""

    name = "linux.journal"

    def start(self) -> None:
        """Start background journald monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            # Follow syslog or journalctl
            cmd = [
                "bash",
                "-lc",
                "command -v journalctl >/dev/null 2>&1 && journalctl -f -n 0 || tail -f /var/log/syslog",
            ]

            with contextlib.suppress(Exception):
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
                if proc.stdout:
                    for line in proc.stdout:
                        if not self.is_running:
                            proc.kill()
                            break
                        self.bus.publish(
                            Event(
                                type=ERR_LOG,
                                payload={"line": line.strip()[:200]},
                                source=self.name,
                            )
                        )

        threading.Thread(target=run, daemon=True, name=self.name).start()


class LinuxFSAdapter(AdapterBase):
    """Linux filesystem change monitoring."""

    name = "linux.fs"

    def __init__(self, bus, watch_paths: list[str] | None = None):
        """Initialize FS adapter.

        Args:
            bus: PerceptionBus instance
            watch_paths: Paths to monitor (default: /etc, /var/log)
        """
        super().__init__(bus)
        self.watch_paths = watch_paths or ["/etc", "/var/log"]

    def start(self) -> None:
        """Start background FS monitoring (polling fallback)."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            snapshots: dict[str, float] = {}

            while self.is_running:
                with contextlib.suppress(Exception):
                    for path in self.watch_paths:
                        with contextlib.suppress(FileNotFoundError):
                            mtime = os.stat(path).st_mtime
                            last = snapshots.get(path)
                            if last and last != mtime:
                                self.bus.publish(
                                    Event(
                                        type=FS_CHANGE,
                                        payload={"path": path, "mtime": mtime},
                                        source=self.name,
                                    )
                                )
                            snapshots[path] = mtime

                time.sleep(5)

        threading.Thread(target=run, daemon=True, name=self.name).start()


class LinuxServiceAdapter(AdapterBase):
    """Linux systemd service health monitoring."""

    name = "linux.svc"

    def __init__(self, bus, watch_services: list[str] | None = None):
        """Initialize service adapter.

        Args:
            bus: PerceptionBus instance
            watch_services: Service names to monitor (default: common services)
        """
        super().__init__(bus)
        self.watch_services = watch_services or [
            "sshd",
            "cron",
            "systemd-journald",
        ]

    def start(self) -> None:
        """Start background service monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            while self.is_running:
                with contextlib.suppress(Exception):
                    for svc in self.watch_services:
                        result = subprocess.run(
                            ["systemctl", "is-active", svc],
                            capture_output=True,
                            text=True,
                            timeout=2,
                        )

                        status = result.stdout.strip()
                        if status != "active":
                            self.bus.publish(
                                Event(
                                    type=SVC_HEALTH,
                                    payload={"service": svc, "status": status},
                                    source=self.name,
                                )
                            )

                time.sleep(30)

        threading.Thread(target=run, daemon=True, name=self.name).start()
