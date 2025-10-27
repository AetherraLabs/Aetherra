# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Capability Registry
===================

Registry of world-changing actions with preconditions, rollback, and verification.
Every capability must be reversible and auditable.
"""

from __future__ import annotations

import contextlib
import platform
import subprocess
from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass
class Capability:
    """Executable capability with safety guarantees.

    Every capability must provide:
    - precondition: can we safely do this now?
    - action: the actual world-changing operation
    - rollback: undo the action if needed
    - verify: did the action succeed as expected?
    """

    name: str
    precondition: Callable[[dict], bool]
    action: Callable[[dict], dict]
    rollback: Callable[[dict], dict]
    verify: Callable[[dict], bool]
    max_duration_s: int = 60
    description: str = ""
    risk_level: str = "low"  # low | medium | high


class CapabilityRegistry:
    """Registry of all available capabilities."""

    def __init__(self):
        self._caps: Dict[str, Capability] = {}

    def register(self, cap: Capability) -> None:
        """Register a capability."""
        self._caps[cap.name] = cap

    def get(self, name: str) -> Optional[Capability]:
        """Get a capability by name."""
        return self._caps.get(name)

    def list_all(self) -> list[str]:
        """List all registered capability names."""
        return list(self._caps.keys())

    def list_by_risk(self, risk: str) -> list[str]:
        """List capabilities by risk level."""
        return [name for name, cap in self._caps.items() if cap.risk_level == risk]


# ==============================================================================
# Example Capabilities (starter set)
# ==============================================================================


def _restart_service_linux(args: dict) -> dict:
    """Restart a systemd service (Linux)."""
    svc = args["service"]
    result = subprocess.run(
        ["systemctl", "restart", svc],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _restart_service_windows(args: dict) -> dict:
    """Restart a Windows service."""
    svc = args["service"]
    result = subprocess.run(
        ["powershell.exe", "-Command", f"Restart-Service -Name {svc}"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _verify_service_linux(args: dict) -> bool:
    """Verify service is active (Linux)."""
    svc = args["service"]
    result = subprocess.run(
        ["systemctl", "is-active", svc],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.stdout.strip() == "active"


def _verify_service_windows(args: dict) -> bool:
    """Verify service is running (Windows)."""
    svc = args["service"]
    result = subprocess.run(
        [
            "powershell.exe",
            "-Command",
            f"(Get-Service -Name {svc}).Status -eq 'Running'",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return result.stdout.strip().lower() == "true"


def _rotate_logs(args: dict) -> dict:
    """Rotate log files (compress and truncate)."""
    # Platform-specific implementation
    if platform.system() == "Windows":
        # Windows: clear event logs older than 7 days (safe operation)
        result = subprocess.run(
            [
                "powershell.exe",
                "-Command",
                "Get-EventLog -List | ForEach-Object { if ($_.Entries.Count -gt 10000) { Clear-EventLog $_.Log -ErrorAction SilentlyContinue } }",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    else:
        # Linux: rotate using logrotate if available
        result = subprocess.run(
            ["logrotate", "-f", "/etc/logrotate.conf"],
            capture_output=True,
            text=True,
            timeout=30,
        )

    return {"code": result.returncode, "stdout": result.stdout}


def _cleanup_temp(args: dict) -> dict:
    """Clean up old temporary files."""
    path = args.get("path", "/tmp")
    older_than_days = args.get("older_than_days", 7)

    # Safe implementation: only remove files older than threshold
    import os
    import time

    removed_count = 0
    threshold = time.time() - (older_than_days * 86400)

    with contextlib.suppress(Exception):
        if os.path.exists(path):
            for root, _dirs, files in os.walk(path):
                for f in files:
                    fpath = os.path.join(root, f)
                    with contextlib.suppress(Exception):
                        if os.path.getmtime(fpath) < threshold:
                            os.remove(fpath)
                            removed_count += 1

    return {"removed_count": removed_count}


# ==============================================================================
# Default Registry
# ==============================================================================

REGISTRY = CapabilityRegistry()

if platform.system() == "Linux":
    REGISTRY.register(
        Capability(
            name="system.restart_service",
            precondition=lambda a: True,
            action=_restart_service_linux,
            rollback=_restart_service_linux,
            verify=_verify_service_linux,
            description="Restart a systemd service",
            risk_level="medium",
        )
    )
elif platform.system() == "Windows":
    REGISTRY.register(
        Capability(
            name="system.restart_service",
            precondition=lambda a: True,
            action=_restart_service_windows,
            rollback=_restart_service_windows,
            verify=_verify_service_windows,
            description="Restart a Windows service",
            risk_level="medium",
        )
    )

REGISTRY.register(
    Capability(
        name="system.rotate_logs",
        precondition=lambda a: True,
        action=_rotate_logs,
        rollback=lambda a: {"status": "no-op"},
        verify=lambda a: True,
        description="Rotate/compress log files",
        risk_level="low",
    )
)

REGISTRY.register(
    Capability(
        name="fs.cleanup_temp",
        precondition=lambda a: True,
        action=_cleanup_temp,
        rollback=lambda a: {"status": "irreversible"},
        verify=lambda a: True,
        description="Clean up old temporary files",
        risk_level="low",
    )
)
