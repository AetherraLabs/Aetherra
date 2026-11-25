"""Bounded values and SQLite transactions for Memory-owned recovery streams."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from dataclasses import asdict, astuple, dataclass, field
from threading import RLock
from typing import Generic, TypeVar

from Aetherra.consciousness.checkpoint import OWNER, SCOPE, load_checkpoint_json

from .lifecycle_checkpoint import (
    CheckpointError,
    CheckpointJobControl,
    LifecycleCheckpoint,
    LifecycleCheckpointWorker,
    _insert_checkpoint,
)

_ID = re.compile(r"[0-9a-f]{32}")
_SHA = re.compile(r"[0-9a-f]{64}")
_MAX_INT = 2**63 - 1
T = TypeVar("T")


def _require(condition, code="invalid"):
    if not condition:
        raise CheckpointError(code)


def _number(value, low=0, high=_MAX_INT):
    return type(value) is int and low <= value <= high


def _hex(value, pattern=_ID):
    return type(value) is str and pattern.fullmatch(value) is not None


def _canonical(value):
    return json.dumps(
        asdict(value), sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("ascii")


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class StreamKey:
    owner: str
    scope: str
    stream_id: str

    def __post_init__(self):
        _require(type(self.owner) is str and self.owner == OWNER)
        _require(
            type(self.scope) is str and self.scope == SCOPE and _hex(self.stream_id)
        )


@dataclass(frozen=True, slots=True)
class StreamHead:
    generation: int
    checkpoint_id: str | None
    record_id: str | None
    payload_digest: str | None
    metadata_digest: str | None

    def __post_init__(self):
        _require(_number(self.generation))
        if self.generation == 0:
            _require(all(v is None for v in astuple(self)[1:]))
        else:
            _require(
                _hex(self.checkpoint_id)
                and _hex(self.record_id)
                and self.checkpoint_id != self.record_id
            )
            _require(
                _hex(self.payload_digest, _SHA) and _hex(self.metadata_digest, _SHA)
            )

    def digest(self):
        return _digest(_canonical(self))


_EMPTY = StreamHead(0, None, None, None, None)


@dataclass(frozen=True, slots=True)
class StreamToken:
    key: StreamKey
    writer_epoch: int

    def __post_init__(self):
        _require(type(self.key) is StreamKey and _number(self.writer_epoch, 1))


@dataclass(frozen=True, slots=True)
class SnapshotMetadata:
    schema: int
    session_id: str
    session_started_at_unix_s: float
    last_verified_observation_at_unix_s: float
    captured_at_unix_s: float
    observation_uptime_s: float
    capture_uptime_s: float
    save_trigger: str

    def __post_init__(self):
        _require(_number(self.schema, 1, 1) and _hex(self.session_id))
        for t in (
            self.session_started_at_unix_s,
            self.last_verified_observation_at_unix_s,
            self.captured_at_unix_s,
            self.observation_uptime_s,
            self.capture_uptime_s,
        ):
            _require(type(t) in (int, float) and 0 <= t <= sys.float_info.max)
        _require(self.observation_uptime_s <= self.capture_uptime_s)
        _require(
            type(self.save_trigger) is str
            and self.save_trigger in ("periodic", "orderly_stop")
        )

    def to_bytes(self) -> bytes:
        return _canonical(self)

    @classmethod
    def from_bytes(cls, raw: bytes):
        _require(type(raw) is bytes and len(raw) <= 4096)
        try:
            value = cls(**json.loads(raw))
            # The stored form is canonical; this also excludes duplicate keys.
            _require(value.to_bytes() == raw)
            return value
        except (TypeError, ValueError, RecursionError):
            raise CheckpointError("invalid") from None


@dataclass(frozen=True, slots=True)
class AttemptDescriptor:
    token: StreamToken
    expected_head: StreamHead
    operation_id: str
    checkpoint_id: str
    payload_digest: str
    metadata_digest: str

    def __post_init__(self):
        _require(
            type(self.token) is StreamToken and type(self.expected_head) is StreamHead
        )
        _require(
            self.expected_head.generation < _MAX_INT
            and _hex(self.operation_id)
            and _hex(self.checkpoint_id)
        )
        _require(_hex(self.payload_digest, _SHA) and _hex(self.metadata_digest, _SHA))

    @property
    def proposed_generation(self):
        return self.expected_head.generation + 1


@dataclass(frozen=True, slots=True)
class AdvanceRequest:
    attempt: AttemptDescriptor
    payload_bytes: bytes
    metadata_bytes: bytes

    def __post_init__(self):
        _require(type(self.attempt) is AttemptDescriptor)
        for name, limit in (("payload_bytes", 65536), ("metadata_bytes", 4096)):
            data = getattr(self, name)
            _require(type(data) in (bytes, bytearray) and len(data) <= limit)
            object.__setattr__(self, name, bytes(data))
        _require(_digest(self.payload_bytes) == self.attempt.payload_digest)
        _require(_digest(self.metadata_bytes) == self.attempt.metadata_digest)
        meta = SnapshotMetadata.from_bytes(self.metadata_bytes)
        try:
            payload = load_checkpoint_json(self.payload_bytes)
        except ValueError:
            raise CheckpointError("invalid") from None
        _require(
            payload.checkpoint_id == self.attempt.checkpoint_id
            and json.loads(self.payload_bytes)["captured_at"] == meta.captured_at_unix_s
        )


@dataclass(frozen=True, init=False)
class _SelectedCheckpoint(LifecycleCheckpoint):
    """Keep sealed bytes immutable while preserving the v1 detached dict interface."""

    _content: bytes = field(repr=False)

    def __init__(self, record_id, checkpoint_id, content):
        object.__setattr__(self, "record_id", record_id)
        object.__setattr__(self, "checkpoint_id", checkpoint_id)
        object.__setattr__(self, "_content", content)

    @property
    def payload(self):
        return json.loads(self._content)


@dataclass(frozen=True, slots=True)
class AcquiredStream:
    token: StreamToken
    head: StreamHead
    checkpoint: LifecycleCheckpoint | None
    metadata: SnapshotMetadata | None
    retention_needed: bool


@dataclass(frozen=True, slots=True)
class AdvanceReceipt:
    attempt: AttemptDescriptor
    head: StreamHead
    audit_id: str


@dataclass(frozen=True, slots=True)
class StreamCompletion(Generic[T]):
    value: T | None
    error_code: str | None

    def __post_init__(self):
        _require((self.value is None) != (self.error_code is None))


class StreamJob(Generic[T]):
    """Worker seals after its last policy observation. Only local state is polled."""

    def __init__(self, control: CheckpointJobControl | None, *, refusal=None):
        self._control = control
        self._lock = control._lock if control is not None else RLock()
        self._admitted = refusal is None
        self._outstanding = self._admitted
        self._sealed = None
        self._closed = None if refusal is None else StreamCompletion(None, refusal)

    @classmethod
    def refused(cls, code):
        # Refused jobs never run policy or consume the caller's control.
        return cls(None, refusal=code)

    @property
    def admitted(self):
        return self._admitted

    @property
    def outstanding(self):
        with self._lock:
            return self._outstanding

    @property
    def acceptance_closed(self):
        with self._lock:
            if self._closed is None and not self._control._open_locked():
                self.cancel()
            return self._closed is not None

    def cancel(self):
        with self._lock:
            if self._closed is None:
                self._control.cancel()
                self._closed = StreamCompletion(None, "uncertain")

    def poll(self, *, local_owned: bool) -> StreamCompletion[T] | None:
        with self._lock:
            if self._closed is None:
                if local_owned is not True or not self._control._open_locked():
                    self.cancel()
                elif self._sealed is not None:
                    self._closed = self._sealed
            return self._closed

    def _seal(self, value, error):
        # Called inside the worker admission condition, after all external I/O.
        with self._lock:
            if self._closed is None:
                if not self._control._open_locked():
                    self._closed = StreamCompletion(None, "uncertain")
                elif error is not None:
                    self._closed = StreamCompletion(None, error)
                else:
                    self._sealed = StreamCompletion(value, None)
            self._outstanding = False


_KEY = "owner=? AND scope=? AND stream_id=?"
_HEAD = "generation, checkpoint_id, record_id, payload_digest, metadata_digest"
_HEADS = "checkpoint_stream_heads"
_COMMITS = "checkpoint_stream_commits"
_SCHEMA = {
    _HEADS: f"""CREATE TABLE {_HEADS} (
        owner TEXT NOT NULL, scope TEXT NOT NULL, stream_id TEXT NOT NULL,
        schema INTEGER NOT NULL CHECK(schema=1), writer_epoch INTEGER NOT NULL CHECK(writer_epoch>0),
        generation INTEGER NOT NULL CHECK(generation>=0), checkpoint_id TEXT, record_id TEXT,
        payload_digest TEXT, metadata_digest TEXT, restore_pin_generation INTEGER NOT NULL,
        retain_checkpoints INTEGER NOT NULL CHECK(retain_checkpoints BETWEEN 2 AND 100),
        pruned_through INTEGER NOT NULL, PRIMARY KEY(owner,scope,stream_id))""",
    _COMMITS: f"""CREATE TABLE {_COMMITS} (
        owner TEXT NOT NULL, scope TEXT NOT NULL, stream_id TEXT NOT NULL,
        generation INTEGER NOT NULL CHECK(generation>0), checkpoint_id TEXT NOT NULL UNIQUE,
        record_id TEXT NOT NULL UNIQUE, payload_digest TEXT NOT NULL, metadata_digest TEXT NOT NULL,
        operation_id TEXT NOT NULL UNIQUE, writer_epoch INTEGER NOT NULL,
        predecessor_generation INTEGER NOT NULL, predecessor_head_digest TEXT NOT NULL,
        metadata_bytes BLOB NOT NULL, audit_id TEXT NOT NULL, PRIMARY KEY(owner,scope,stream_id,generation))""",
}


@contextmanager
def _bounded_rows(db):
    # A valid v1 row can have up to 64 KiB each of content and context.
    # Also bound SQLite values in damaged ID/digest columns before materialization.
    old = db.getlimit(sqlite3.SQLITE_LIMIT_LENGTH)
    db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, min(old, 256 * 1024))
    try:
        yield
    except sqlite3.DataError:
        raise CheckpointError("corrupt") from None
    finally:
        db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, old)


def _schema(db, *, create):
    actual = dict(
        db.execute(
            "SELECT name, sql FROM sqlite_master WHERE name IN (?,?)", tuple(_SCHEMA)
        )
    )
    if not actual and create:
        for ddl in _SCHEMA.values():
            db.execute(ddl)
    elif not actual:
        raise CheckpointError("missing")
    else:
        # Fail closed on unknown constraints, uniqueness, version or partial DDL.
        _require(actual == _SCHEMA, "corrupt")


def _catalog_head(db, key, generation):
    row = db.execute(
        f"SELECT {_HEAD} FROM {_COMMITS} WHERE {_KEY} AND generation=?",
        (*astuple(key), generation),
    ).fetchone()
    _require(row is not None, "corrupt")
    return StreamHead(*row)


def _selected(db, key, head, epoch):
    if head.generation == 0:
        return None, None
    row = db.execute(
        f"""SELECT {_HEAD}, operation_id, writer_epoch, predecessor_generation,
        predecessor_head_digest, CASE WHEN length(metadata_bytes)<=4096 THEN metadata_bytes END,
        CASE WHEN length(CAST(audit_id AS BLOB))<=256 THEN audit_id END FROM {_COMMITS}
        WHERE {_KEY} AND generation=?""",
        (*astuple(key), head.generation),
    ).fetchone()
    _require(row is not None and StreamHead(*row[:5]) == head, "corrupt")
    op, writer, prev, prev_digest, raw_meta, audit = row[5:]
    _require(
        _hex(op)
        and _number(writer, 1, epoch)
        and _number(prev)
        and prev == head.generation - 1
        and _hex(prev_digest, _SHA),
        "corrupt",
    )
    _require(type(audit) is str and audit.strip(), "corrupt")
    # The latest predecessor is protected by retention (N >= 2).
    predecessor = _EMPTY if prev == 0 else _catalog_head(db, key, prev)
    _require(predecessor.digest() == prev_digest, "corrupt")
    meta = SnapshotMetadata.from_bytes(raw_meta)
    _require(_digest(raw_meta) == head.metadata_digest, "corrupt")
    record, text = LifecycleCheckpointWorker._read_checkpoint(db, head.checkpoint_id)
    _require(
        record.record_id == head.record_id
        and json.loads(text)["captured_at"] == meta.captured_at_unix_s,
        "corrupt",
    )
    content = text.encode("utf-8")
    _require(_digest(content) == head.payload_digest, "corrupt")
    return _SelectedCheckpoint(record.record_id, record.checkpoint_id, content), meta


def _current(db, key, *, expected_epoch=None):
    params = astuple(key)
    row = db.execute(
        f"""SELECT {_HEAD}, schema,writer_epoch,restore_pin_generation,retain_checkpoints,pruned_through
                         FROM {_HEADS} WHERE {_KEY}""",
        params,
    ).fetchone()
    if row is not None and expected_epoch is not None:
        epoch = row[6]
        _require(_number(epoch, 1), "corrupt")
        _require(epoch == expected_epoch, "writer_fenced")
    generations = [
        r[0]
        for r in db.execute(
            f"SELECT generation FROM {_COMMITS} WHERE {_KEY} ORDER BY generation LIMIT 103",
            params,
        )
    ]
    if row is None:
        _require(not generations, "corrupt")
        return None
    try:
        head = StreamHead(*row[:5])
        schema, epoch, pin, retain, watermark = row[5:]
        _require(
            _number(schema, 1, 1) and _number(epoch, 1) and _number(retain, 2, 100)
        )
        _require(
            _number(pin, 0, head.generation)
            and _number(watermark, 0, max(0, head.generation - 2))
        )
        _require(len(generations) <= 102 and (not pin or pin in generations))
        # A protected entry from a previous acquisition may survive below the watermark.
        unpruned = [
            g for g in generations if _number(g, watermark + 1, head.generation)
        ]
        _require(all(_number(g, 1, head.generation) for g in generations))
        _require(len(unpruned) == head.generation - watermark)
        record, meta = _selected(db, key, head, epoch)
    except CheckpointError:
        raise CheckpointError("corrupt") from None
    return head, epoch, pin, retain, len(generations), record, meta


def _acquire(db, key, start_mode, retain):
    _schema(db, create=start_mode == "create")
    params = astuple(key)
    current = _current(db, key)
    if start_mode == "create":
        _require(current is None, "conflict")
        inserted = db.execute(
            f"""INSERT INTO {_HEADS} (owner,scope,stream_id,schema,writer_epoch,generation,restore_pin_generation,
                    retain_checkpoints,pruned_through) VALUES (?,?,?,1,1,0,0,?,0)""",
            (*params, retain),
        )
        _require(inserted.rowcount == 1, "conflict")
        return AcquiredStream(StreamToken(key, 1), _EMPTY, None, None, False)
    _require(current is not None, "missing")
    head, epoch, _, _, count, record, meta = current
    token = StreamToken(key, epoch + 1)
    changed = db.execute(
        f"""UPDATE {_HEADS} SET writer_epoch=?,restore_pin_generation=?,retain_checkpoints=?
                              WHERE {_KEY} AND writer_epoch=?""",
        (token.writer_epoch, head.generation, retain, *params, epoch),
    )
    _require(changed.rowcount == 1, "conflict")
    return AcquiredStream(token, head, record, meta, count > retain)


def _advance(db, request, audit):
    _schema(db, create=False)
    attempt = request.attempt
    key = attempt.token.key
    params = astuple(key)
    current = _current(db, key, expected_epoch=attempt.token.writer_epoch)
    _require(current is not None, "missing")
    head, epoch, pin, retain, count, _, _ = current
    _require(head == attempt.expected_head, "conflict")
    older_pin = 0 < pin <= head.generation - retain
    _require(count <= retain + int(older_pin), "capacity")
    kind = "consciousness_observer_checkpoint:" + attempt.checkpoint_id
    _require(
        db.execute(
            "SELECT 1 FROM memories WHERE memory_type=? LIMIT 1", (kind,)
        ).fetchone()
        is None,
        "conflict",
    )
    record_id = uuid.uuid4().hex
    next_head = StreamHead(
        attempt.proposed_generation,
        attempt.checkpoint_id,
        record_id,
        attempt.payload_digest,
        attempt.metadata_digest,
    )
    try:
        inserted = _insert_checkpoint(
            db, record_id, attempt.checkpoint_id, request.payload_bytes
        )
        _require(inserted == 1, "conflict")
        catalog = db.execute(
            f"""INSERT INTO {_COMMITS} (owner,scope,stream_id,{_HEAD},operation_id,writer_epoch,
                   predecessor_generation,predecessor_head_digest,metadata_bytes,audit_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                *params,
                *astuple(next_head),
                attempt.operation_id,
                epoch,
                head.generation,
                head.digest(),
                request.metadata_bytes,
                audit,
            ),
        )
        _require(catalog.rowcount == 1, "conflict")
    except sqlite3.IntegrityError:
        raise CheckpointError("conflict") from None
    changed = db.execute(
        f"""UPDATE {_HEADS} SET generation=?,checkpoint_id=?,record_id=?,payload_digest=?,metadata_digest=?
                              WHERE {_KEY} AND writer_epoch=? AND generation=? AND checkpoint_id IS ? AND record_id IS ?
                              AND payload_digest IS ? AND metadata_digest IS ?""",
        (*astuple(next_head), *params, epoch, *astuple(head)),
    )
    _require(changed.rowcount == 1, "conflict")
    return AdvanceReceipt(attempt, next_head, audit)
