"""
Telemetry opt-in manager and emitter with privacy guardrails.

- Respects env AETHERRA_TELEMETRY=0/1 and ~/.aetherra/telemetry.json opt-in file.
- Emits anonymized counters and timings; never sends content payloads.
- Sends to local hub /api/telemetry by default; no network if hub down.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

try:
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
        CONF_FILE.write_text(json.dumps({"opt_in": value}, indent=2), encoding="utf-8")
        self.enabled = value

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
