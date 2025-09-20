"""Audit logging for coding system (Phase 0)

Appends JSON records to ledger (default audit/aetherra_runs.jsonl) when AETHERRA_AUDIT != 0.

Environment:
  AETHERRA_AUDIT=0 -> disable
  AETHERRA_AUDIT_PATH -> override path
  AETHERRA_MODE -> stored for context

Record shape (example):
{"ts": 1234567890.1, "mode": "assist", "event": "plan", "data": {"intent": "..."}}
"""

from __future__ import annotations

# Standard library imports
import json
import os
import time
from pathlib import Path
from threading import Lock

_LEDGER_LOCK = Lock()


def _ledger_path() -> Path:
    path = os.getenv("AETHERRA_AUDIT_PATH", "audit/aetherra_runs.jsonl")
    return Path(path)


def record_event(event: str, data: dict | None = None) -> None:
    if os.getenv("AETHERRA_AUDIT", "1") == "0":
        return
    entry = {
        "ts": time.time(),
        "mode": os.getenv("AETHERRA_MODE", "assist"),
        "event": event,
        "data": data or {},
    }
    path = _ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False)
    with _LEDGER_LOCK:
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
