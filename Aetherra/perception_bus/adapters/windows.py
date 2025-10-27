# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Windows Perception Adapters
============================

Real-world telemetry from Windows using PowerShell and WMI.
No simulation—only actual system metrics.
"""

from __future__ import annotations

import contextlib
import subprocess
import threading
import time

from Aetherra.consciousness.core.types import Event

from ..event_types import (
    DISK_STATUS,
    ERR_LOG,
    PERF_CPU,
    PERF_MEMORY,
    PROC_SNAPSHOT,
    SVC_HEALTH,
)
from .common import AdapterBase


class WindowsProcAdapter(AdapterBase):
    """Windows process monitoring via Get-Process."""

    name = "windows.proc"

    def start(self) -> None:
        """Start background process monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            while self.is_running:
                with contextlib.suppress(Exception):
                    # Get process count and top CPU process
                    result = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-Command",
                            "Get-Process | Measure-Object | Select-Object -ExpandProperty Count",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    proc_count = int(result.stdout.strip()) if result.stdout.strip() else 0

                    # Top CPU process
                    top_result = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-Command",
                            "Get-Process | Sort-Object CPU -Descending | Select-Object -First 1 | Format-Table ProcessName, CPU -HideTableHeaders",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    self.bus.publish(
                        Event(
                            type=PROC_SNAPSHOT,
                            payload={
                                "proc_count": proc_count,
                                "top": top_result.stdout.strip(),
                            },
                            source=self.name,
                        )
                    )

                time.sleep(5)

        threading.Thread(target=run, daemon=True, name=self.name).start()


class WindowsDiskAdapter(AdapterBase):
    """Windows disk monitoring via Get-Volume."""

    name = "windows.disk"

    def start(self) -> None:
        """Start background disk monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            while self.is_running:
                with contextlib.suppress(Exception):
                    # Get C: drive info
                    result = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-Command",
                            "(Get-Volume -DriveLetter C | Select-Object @{N='Free';E={[math]::Round($_.SizeRemaining/$_.Size*100,2)}}).Free",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    pct_free = float(result.stdout.strip()) if result.stdout.strip() else 100.0

                    self.bus.publish(
                        Event(
                            type=DISK_STATUS,
                            payload={"mount": "C:", "pct_free": pct_free},
                            source=self.name,
                        )
                    )

                time.sleep(30)

        threading.Thread(target=run, daemon=True, name=self.name).start()


class WindowsEventLogAdapter(AdapterBase):
    """Windows Event Log monitoring (Error/Warning)."""

    name = "windows.eventlog"

    def start(self) -> None:
        """Start background event log monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            last_check = time.time()

            while self.is_running:
                with contextlib.suppress(Exception):
                    # Get recent errors/warnings from System log
                    since_minutes = int((time.time() - last_check) / 60) + 1
                    result = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-Command",
                            f"Get-EventLog -LogName System -EntryType Error,Warning -Newest 10 -After (Get-Date).AddMinutes(-{since_minutes}) | "
                            "Select-Object -First 5 | ForEach-Object { $_.Message }",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if result.stdout.strip():
                        for line in result.stdout.strip().split("\n"):
                            if line.strip():
                                self.bus.publish(
                                    Event(
                                        type=ERR_LOG,
                                        payload={"line": line.strip()[:200]},
                                        source=self.name,
                                    )
                                )

                    last_check = time.time()

                time.sleep(60)

        threading.Thread(target=run, daemon=True, name=self.name).start()


class WindowsPerfAdapter(AdapterBase):
    """Windows performance counters (CPU, Memory)."""

    name = "windows.perf"

    def start(self) -> None:
        """Start background performance monitoring."""
        self.is_running = True

        def run() -> None:
            self.emit_online()
            while self.is_running:
                with contextlib.suppress(Exception):
                    # CPU usage
                    cpu_result = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-Command",
                            "(Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval 1 -MaxSamples 1).CounterSamples.CookedValue",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    cpu_pct = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0

                    self.bus.publish(
                        Event(
                            type=PERF_CPU,
                            payload={"cpu_pct": round(cpu_pct, 2)},
                            source=self.name,
                        )
                    )

                    # Memory usage
                    mem_result = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-Command",
                            "$os = Get-CimInstance Win32_OperatingSystem; "
                            "[math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize * 100, 2)",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    mem_pct = float(mem_result.stdout.strip()) if mem_result.stdout.strip() else 0.0

                    self.bus.publish(
                        Event(
                            type=PERF_MEMORY,
                            payload={"mem_pct": round(mem_pct, 2)},
                            source=self.name,
                        )
                    )

                time.sleep(10)

        threading.Thread(target=run, daemon=True, name=self.name).start()


class WindowsServiceAdapter(AdapterBase):
    """Windows service health monitoring."""

    name = "windows.svc"

    def __init__(self, bus, watch_services: list[str] | None = None):
        """Initialize service adapter.

        Args:
            bus: PerceptionBus instance
            watch_services: List of service names to monitor (default: critical services)
        """
        super().__init__(bus)
        self.watch_services = watch_services or [
            "EventLog",
            "Winmgmt",
            "WSearch",
            "W32Time",
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
                            [
                                "powershell.exe",
                                "-NoProfile",
                                "-Command",
                                f"(Get-Service -Name {svc} -ErrorAction SilentlyContinue).Status",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )

                        status = result.stdout.strip()
                        if status and status != "Running":
                            self.bus.publish(
                                Event(
                                    type=SVC_HEALTH,
                                    payload={
                                        "service": svc,
                                        "status": status,
                                    },
                                    source=self.name,
                                )
                            )

                time.sleep(30)

        threading.Thread(target=run, daemon=True, name=self.name).start()
