"""Small JSONL state helpers for Guardian approval and containment queues."""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Mapping
from pathlib import Path
from typing import Any

_LOCKS_GUARD = threading.Lock()
_LOCKS: dict[Path, threading.RLock] = {}


def _path_lock(path: Path) -> threading.RLock:
    resolved = path.resolve()
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(resolved, threading.RLock())


def append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    """Append one JSON record to a state log with per-path locking."""

    path = path.expanduser().resolve()
    encoded = json.dumps(
        dict(record),
        default=str,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    with _path_lock(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "ab") as handle:
            handle.write(encoded + b"\n")
            handle.flush()
            os.fsync(handle.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read all valid JSON object records from a state log."""

    path = path.expanduser().resolve()
    if not path.exists():
        return []
    with _path_lock(path):
        records: list[dict[str, Any]] = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            data = json.loads(raw_line)
            if isinstance(data, dict):
                records.append(data)
        return records
