"""Small JSONL state helpers for Guardian approval and containment queues."""

from __future__ import annotations

# Standard library imports
import errno
import json
import os
import threading
import time
from collections.abc import Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

_LOCKS_GUARD = threading.Lock()
_LOCKS: dict[Path, threading.RLock] = {}


def _path_lock(path: Path) -> threading.RLock:
    resolved = path.resolve()
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(resolved, threading.RLock())


@contextmanager
def locked_jsonl(path: Path):
    """Serialize a state transition across independent callers sharing this log."""
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Keep the empty sidecar at a stable inode. Closing its descriptor releases
    # the OS lock, including when the holder exits unexpectedly.
    fd = os.open(path.with_suffix(path.suffix + ".lock"), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        deadline = time.monotonic() + 0.25
        while True:
            try:
                _lock_descriptor(fd)
                break
            except OSError as exc:
                if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError("Guardian state log is busy") from exc
                time.sleep(0.01)
        yield path
    finally:
        os.close(fd)


def _lock_descriptor(fd: int) -> None:
    if os.name == "nt":
        # Standard library imports
        import msvcrt

        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        # Standard library imports
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


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


def read_jsonl(path: Path, *, require_objects: bool = False) -> list[dict[str, Any]]:
    """Read all valid JSON object records from a state log."""

    path = path.expanduser().resolve()
    with _path_lock(path):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []
        records: list[dict[str, Any]] = []
        for raw_line in lines:
            if not raw_line.strip():
                continue
            data = json.loads(raw_line)
            if isinstance(data, dict):
                records.append(data)
            elif require_objects:
                raise ValueError("Guardian state record must be a JSON object")
        return records
