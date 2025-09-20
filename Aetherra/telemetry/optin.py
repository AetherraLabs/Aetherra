# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Telemetry opt-in manager and emitter with privacy guardrails.

- Respects env AETHERRA_TELEMETRY=0/1 and ~/.aetherra/telemetry.json opt-in file.
- Emits anonymized counters and timings; never sends content payloads.
- Sends to local hub /api/telemetry by default; no network if hub down.
"""

from __future__ import annotations

# Standard library imports
import json
import math
import os
import random
import time
from pathlib import Path
from typing import Dict, Optional

try:
    # Third party imports
    import requests  # type: ignore
except Exception:
    requests = None  # type: ignore

APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
CONF_FILE = APP_DIR / "telemetry.json"
DEFAULT_ENDPOINT = os.environ.get(
    "AETHERRA_TELEMETRY_ENDPOINT", "http://localhost:3001/api/telemetry"
)


class Telemetry:
    def __init__(self, endpoint: str = DEFAULT_ENDPOINT):
        self.endpoint = endpoint
        self.enabled = self._load_opt_in()
        self.dp_enabled = os.environ.get("AETHERRA_TELEMETRY_DP", "0") == "1"
        try:
            self.dp_epsilon = float(os.environ.get("AETHERRA_TELEMETRY_DP_EPS", "1.0"))
        except Exception:
            self.dp_epsilon = 1.0

    def _load_opt_in(self) -> bool:
        env = os.environ.get("AETHERRA_TELEMETRY")
        if env is not None:
            return env == "1"
        if CONF_FILE.exists():
            try:
                data = json.loads(CONF_FILE.read_text(encoding="utf-8"))
                return bool(data.get("opt_in", False))
            except Exception:
                return False
        return False

    def set_opt_in(self, value: bool):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        # Merge with any existing config to preserve DP settings
        data = {"opt_in": value}
        try:
            if CONF_FILE.exists():
                existing = json.loads(CONF_FILE.read_text(encoding="utf-8"))
                if isinstance(existing, dict):
                    existing.update(data)
                    data = existing
        except Exception:
            pass
        CONF_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.enabled = value

    def set_dp(self, enabled: bool, epsilon: Optional[float] = None) -> None:
        """Enable/disable Differential Privacy and optionally set epsilon.

        This updates runtime flags and merges values into the telemetry config file
        for continuity across sessions. Environment variables are not modified.
        """
        self.dp_enabled = bool(enabled)
        if epsilon is not None:
            try:
                self.dp_epsilon = float(epsilon)
            except Exception:
                # Leave existing epsilon if parsing fails
                pass
        # Persist alongside opt-in when possible
        try:
            APP_DIR.mkdir(parents=True, exist_ok=True)
            data = {}
            if CONF_FILE.exists():
                try:
                    data = json.loads(CONF_FILE.read_text(encoding="utf-8")) or {}
                except Exception:
                    data = {}
            data.update(
                {
                    "dp": self.dp_enabled,
                    "epsilon": self.dp_epsilon,
                }
            )
            CONF_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            # Best-effort persistence; ignore failures
            pass

    def emit(self, event: str, props: Optional[Dict] = None):
        if not self.enabled or requests is None:
            return False
        payload = {
            "event": event,
            "ts": int(time.time()),
            "props": {
                k: v
                for k, v in (props or {}).items()
                if k not in ("content", "prompt", "message")
            },
        }
        # Optional DP: add Laplace noise to numeric properties and drop IDs
        if self.dp_enabled:

            def _laplace_noise(scale: float) -> float:
                # Inverse transform sampling for Laplace(0, scale)
                u = random.random() - 0.5
                return -scale * math.copysign(math.log(1 - 2 * abs(u)), u)

            scale = 1.0 / max(self.dp_epsilon, 1e-6)
            redacted_keys = {"user_id", "session_id", "ip", "agent_id"}
            for rk in list(payload["props"].keys()):
                if rk in redacted_keys:
                    payload["props"].pop(rk, None)
            for k, v in list(payload["props"].items()):
                if isinstance(v, (int, float)):
                    try:
                        payload["props"][k] = float(v) + _laplace_noise(scale)
                    except Exception:
                        continue
        try:
            r = requests.post(self.endpoint, json=payload, timeout=2)
            return r.status_code in (200, 201, 202)
        except Exception:
            return False


_default: Optional[Telemetry] = None


def get_telemetry() -> Telemetry:
    global _default
    if _default is None:
        _default = Telemetry()
    return _default


def get_status() -> Dict[str, object]:
    t = get_telemetry()
    return {
        "enabled": t.enabled,
        "endpoint": t.endpoint,
        "dp": t.dp_enabled,
        "epsilon": t.dp_epsilon,
    }
