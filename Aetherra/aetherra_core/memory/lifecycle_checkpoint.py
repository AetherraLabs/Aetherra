"""Governed exact checkpoint I/O owned by one existing Memory instance.

The daemon owns its SQLite connection and one outstanding slot, including audit.
A timeout closes result acceptance; it does not assert that a commit rolled back.
"""

from __future__ import annotations

# Standard library imports
import json
import math
import os
import re
import sqlite3
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import Future, TimeoutError
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Local imports
    from .checkpoint_stream import (
        AdvanceRequest,
        AttemptDescriptor,
        StreamJob,
        StreamKey,
        StreamToken,
    )

_OWNER = "consciousness:observer"
_SCOPE = "observer_continuity:v1"
_HANDLE = re.compile(r"[0-9a-f]{32}\Z")
_MAX_BYTES = 65536


class CheckpointError(Exception):
    """Sanitized checkpoint failure; never includes payloads or paths."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class LifecycleCheckpoint:
    record_id: str
    checkpoint_id: str
    payload: dict


@dataclass(frozen=True)
class CheckpointJobControl:
    cancelled: threading.Event
    deadline: float
    still_owned: Callable[[], bool]
    wake_event: threading.Event | None = None
    _lock: threading.RLock = field(
        default_factory=threading.RLock, init=False, repr=False
    )
    _closed: bool = field(default=False, init=False, repr=False)
    _bound_deadline: float | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        if (
            not isinstance(self.cancelled, threading.Event)
            or isinstance(self.deadline, bool)
            or not isinstance(self.deadline, (int, float))
            or not math.isfinite(self.deadline)
            or not callable(self.still_owned)
            or (
                self.wake_event is not None
                and type(self.wake_event) is not threading.Event
            )
        ):
            raise CheckpointError("invalid")

    def cancel(self):
        with self._lock:
            object.__setattr__(self, "_closed", True)
            self.cancelled.set()

    def _bind(self):
        with self._lock:
            # A token is never refreshed or extended by resubmission.
            deadline = min(self.deadline, time.monotonic() + 1.0)
            if self._bound_deadline is not None:
                deadline = min(deadline, self._bound_deadline)
            object.__setattr__(self, "_bound_deadline", deadline)

    def _open_locked(self) -> bool:
        deadline = self._bound_deadline
        if deadline is None:
            deadline = self.deadline
        return (
            not self._closed
            and not self.cancelled.is_set()
            and time.monotonic() < min(self.deadline, deadline)
        )

    def active(self) -> bool:
        return self._active_if_owned(self.still_owned)

    def _active_if_owned(self, owned_check: Callable[[], bool]) -> bool:
        with self._lock:
            if not self._open_locked():
                object.__setattr__(self, "_closed", True)
                return False
        # This callback can perform policy/ownership I/O. Never hold a lock
        # needed by cancellation, admission, status or shutdown while calling it.
        try:
            owned = owned_check() is True
        except Exception:
            owned = False
        with self._lock:
            active = owned and self._open_locked()
            if not active:
                object.__setattr__(self, "_closed", True)
            return active

    def check(self):
        if not self.active():
            raise CheckpointError("cancelled")


class _CheckpointFuture(Future):
    def __init__(self, control: CheckpointJobControl, *, writing: bool):
        super().__init__()
        self.control = control
        self._writing = writing
        self._intent = None
        self.set_running_or_notify_cancel()

    def cancel(self):
        self.control.cancel()
        # Running audit/I/O remains owned until actual completion.
        return super().cancel()

    def result(self, timeout=None):
        try:
            result = super().result(timeout)
        except TimeoutError:
            self.control.cancel()
            raise
        try:
            _recheck_policy(self._intent)
        except CheckpointError as exc:
            self.control.cancel()
            raise CheckpointError("uncertain" if self._writing else exc.code) from None
        if not self.control.active():
            raise CheckpointError("uncertain" if self._writing else "cancelled")
        with self.control._lock:
            if not self.control._open_locked():
                raise CheckpointError("uncertain" if self._writing else "cancelled")
            return result


def failed_checkpoint_future(code: str) -> Future:
    future = Future()
    future.set_exception(CheckpointError(code))
    return future


def _identity(owner, scope, checkpoint_id):
    if (
        owner != _OWNER
        or scope != _SCOPE
        or not isinstance(checkpoint_id, str)
        or not _HANDLE.fullmatch(checkpoint_id)
    ):
        raise CheckpointError("invalid")


def _decode(data: bytes | str, checkpoint_id: str):
    # Aetherra imports
    from Aetherra.consciousness.checkpoint import (
        encode_checkpoint,
        load_checkpoint_json,
    )

    try:
        payload = encode_checkpoint(load_checkpoint_json(data))
        _identity(payload["owner"], payload["scope"], payload["checkpoint_id"])
        if payload["checkpoint_id"] != checkpoint_id:
            raise ValueError
        return payload
    except Exception:
        raise CheckpointError("invalid") from None


def _freeze(payload: dict, checkpoint_id: str) -> bytes:
    # Aetherra imports
    from Aetherra.consciousness.checkpoint import (
        decode_checkpoint,
        dump_checkpoint_json,
    )

    try:
        # The codec validates structure before serialization can traverse it.
        frozen = dump_checkpoint_json(decode_checkpoint(payload))
        _decode(frozen, checkpoint_id)
        return frozen
    except Exception:
        raise CheckpointError("invalid") from None


def _insert_checkpoint(connection, record_id, checkpoint_id, data):
    context = {
        "owner": _OWNER,
        "scope": _SCOPE,
        "schema": 1,
        "checkpoint_id": checkpoint_id,
        "record_id": record_id,
    }
    now = datetime.now(UTC).isoformat()
    inserted = connection.execute(
        "INSERT INTO memories (id,content,context,tags,importance,created_at,last_accessed,access_count,memory_type) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            record_id,
            data.decode("utf-8"),
            json.dumps(context),
            "[]",
            0.0,
            now,
            now,
            0,
            "consciousness_observer_checkpoint:" + checkpoint_id,
        ),
    )
    return inserted.rowcount


def _strict_policy():
    # Aetherra imports
    from Aetherra.guardian import guardian_enabled, guardian_mode, load_guardian_policy
    from Aetherra.security.capabilities import _load_policy_full

    try:
        if (
            not guardian_enabled()
            or guardian_mode().value != "enforcing"
            or os.getenv("AETHERRA_PROD_UNSAFE_ALLOW", "0") == "1"
            or any(
                os.getenv(key) != "1"
                for key in (
                    "AETHERRA_REQUIRE_CAPABILITIES",
                    "AETHERRA_GUARDIAN_REQUIRE_POLICY",
                    "AETHERRA_SIGNING_STRICT",
                    "AETHERRA_SCRIPT_VERIFY_STRICT",
                    "AETHERRA_AUDIT",
                )
            )
        ):
            raise ValueError
        load_guardian_policy(require_valid_policy=True)
        _load_policy_full(require_valid_policy=True)
    except Exception:
        raise CheckpointError("denied") from None


def _recheck_policy(intent):
    # Aetherra imports
    from Aetherra.guardian.policy import evaluate_guardian_policy
    from Aetherra.security.capabilities import has_capability

    _strict_policy()
    if (
        (os.getenv("AETHERRA_PRINCIPAL", "").strip() or "consciousness:core")
        != intent.requester
        or not evaluate_guardian_policy(intent, require_valid_policy=True).allowed
        or not all(has_capability(intent.requester, cap) for cap in intent.capabilities)
    ):
        raise CheckpointError("denied")


def _authorize(operation: str, checkpoint_id: str):
    caps = ("consciousness:write", "memory:read", "fs:read")
    if operation == "save":
        caps = ("consciousness:write", "memory:write", "fs:read", "fs:write")
    intent, _ = _authorize_intent(operation, caps, {"checkpoint_id": checkpoint_id})
    return intent


def _authorize_stream(job):
    if job.operation == "acquire":
        key, mode, retain = job.data
        metadata = {
            "stream_id": key.stream_id,
            "start_mode": mode,
            "retain_checkpoints": retain,
        }
    else:
        attempt = job.data[1] if job.operation == "inspect" else job.data.attempt
        metadata = {
            "stream_id": attempt.token.key.stream_id,
            "writer_epoch": attempt.token.writer_epoch,
            "generation": attempt.proposed_generation,
            "operation_id": attempt.operation_id,
            "checkpoint_id": attempt.checkpoint_id,
            "payload_digest": attempt.payload_digest,
            "metadata_digest": attempt.metadata_digest,
            "predecessor_head_digest": attempt.expected_head.digest(),
        }
    caps = ("consciousness:write", "memory:read", "memory:write", "fs:read", "fs:write")
    if job.operation == "inspect":
        caps = ("consciousness:write", "memory:read", "fs:read")
        metadata["inspecting_epoch"] = job.data[0].writer_epoch
    intent, audit = _authorize_intent(job.operation, caps, metadata)
    if len(audit.encode("utf-8")) > 256:
        raise CheckpointError("audit_failed")
    return intent, audit


def _authorize_intent(operation, caps, metadata):
    # Aetherra imports
    from Aetherra.guardian import IntentDeclaration, evaluate_intent
    from Aetherra.security.capabilities import has_capability

    _strict_policy()
    intent = IntentDeclaration(
        requester=os.getenv("AETHERRA_PRINCIPAL", "").strip() or "consciousness:core",
        subsystem="consciousness",
        action=f"consciousness.continuity_{operation}",
        target="memory:core",
        purpose="Bounded exact observer continuity checkpoint",
        capabilities=caps,
        reversible=True,
        rollback_plan="Rollback uncommitted transaction; preserve immutable committed rows on uncertainty.",
        evidence=("observer_continuity:v1",),
        metadata={**metadata, "operation": operation, "schema": 1},
    )
    try:
        decision = evaluate_intent(
            intent,
            capability_checker=has_capability,
            require_valid_policy=True,
        )
    except Exception:
        raise CheckpointError("audit_failed") from None
    if not decision.allowed:
        raise CheckpointError("denied")
    if not isinstance(decision.audit_id, str) or not decision.audit_id.strip():
        raise CheckpointError("audit_failed")
    return intent, decision.audit_id


@dataclass(frozen=True)
class _Job:
    operation: str
    checkpoint_id: str
    data: (
        bytes
        | tuple[StreamKey, str, int]
        | tuple[StreamToken, AttemptDescriptor]
        | AdvanceRequest
        | None
    )
    control: CheckpointJobControl
    future: _CheckpointFuture | StreamJob
    backend_owned: Callable[[], bool] | None = None

    def backend_active(self):
        return self.backend_owned is None or self.control._active_if_owned(
            self.backend_owned
        )

    def check(self):
        self.control.check()
        if not self.backend_active():
            raise CheckpointError("cancelled")


class LifecycleCheckpointWorker:
    """One lazy daemon and one slot; no checkpoint job queue or shared connection."""

    def __init__(self, database_path: str):
        self._database_path = database_path
        if (
            isinstance(database_path, (str, os.PathLike))
            and str(database_path)
            and str(database_path) != ":memory:"
            and not str(database_path).lower().startswith("file:")
        ):
            # Bind relative paths at Core construction, not on a later worker tick.
            self._database_path = os.path.abspath(database_path)
        self._condition = threading.Condition()
        self._job: _Job | None = None
        self._thread: threading.Thread | None = None
        self._closing = False

    def pending(self) -> bool:
        with self._condition:
            return self._job is not None

    def submit(self, *, operation, owner, scope, checkpoint_id, control, payload=None):
        try:
            _identity(owner, scope, checkpoint_id)
            if not isinstance(control, CheckpointJobControl):
                raise CheckpointError("invalid")
            control._bind()
            # Freeze before admission, never authorize a caller-owned dictionary.
            data = _freeze(payload, checkpoint_id) if operation == "save" else None
            future = _CheckpointFuture(control, writing=operation == "save")
            return self._admit(_Job(operation, checkpoint_id, data, control, future))
        except CheckpointError as exc:
            return failed_checkpoint_future(exc.code)
        except Exception:
            return failed_checkpoint_future("invalid")

    def submit_stream(
        self,
        *,
        operation,
        control,
        key=None,
        start_mode=None,
        retain_checkpoints=None,
        request=None,
        token=None,
        attempt=None,
        backend_owned=None,
    ):
        # Local imports
        from .checkpoint_stream import (
            AdvanceRequest,
            AttemptDescriptor,
            StreamJob,
            StreamKey,
            StreamToken,
        )

        try:
            if (
                type(control) is not CheckpointJobControl
                or type(control.cancelled) is not threading.Event
            ):
                raise CheckpointError("invalid")
            control._bind()
            if (
                operation == "acquire"
                and type(key) is StreamKey
                and type(start_mode) is str
                and start_mode in ("create", "resume")
                and type(retain_checkpoints) is int
                and 2 <= retain_checkpoints <= 100
            ):
                data = (key, start_mode, retain_checkpoints)
                handle = key.stream_id
            elif (
                operation == "inspect"
                and type(token) is StreamToken
                and type(attempt) is AttemptDescriptor
                and token.key == attempt.token.key
                and token.writer_epoch > attempt.token.writer_epoch
            ):
                data = (token, attempt)
                handle = attempt.checkpoint_id
            elif operation == "advance" and type(request) is AdvanceRequest:
                data = request
                handle = request.attempt.checkpoint_id
            else:
                raise CheckpointError("invalid")
            return self._admit(
                _Job(
                    operation, handle, data, control, StreamJob(control), backend_owned
                )
            )
        except CheckpointError as exc:
            return StreamJob.refused(exc.code)

    def _admit(self, job):
        control = job.control
        path = self._database_path
        if (
            not isinstance(path, (str, os.PathLike))
            or not str(path)
            or str(path) == ":memory:"
            or str(path).lower().startswith("file:")
        ):
            raise CheckpointError("unavailable")
        with self._condition:
            if self._closing:
                raise CheckpointError("unavailable")
            if self._job is not None:
                raise CheckpointError("busy")
            # Admission checks only internal cancellation/deadline state.
            # External readiness and policy run on the owned worker.
            with control._lock:
                if not control._open_locked():
                    raise CheckpointError("cancelled")
            self._job = job
            if self._thread is None:
                self._thread = threading.Thread(
                    target=self._run,
                    name="memory-lifecycle-checkpoint",
                    daemon=True,
                )
                try:
                    self._thread.start()
                except Exception:
                    self._job = None
                    self._closing = True
                    raise CheckpointError("unavailable") from None
            self._condition.notify_all()
            return job.future

    def shutdown(self, timeout: float = 1.0) -> bool:
        with self._condition:
            self._closing = True
            thread = self._thread
            self._condition.notify_all()
        if thread is None:
            return True
        if thread is threading.current_thread():
            return False
        thread.join(max(0.0, timeout))
        return not thread.is_alive()

    def _run(self):
        connection = None
        try:
            while True:
                with self._condition:
                    self._condition.wait_for(
                        lambda: self._job is not None or self._closing
                    )
                    job = self._job
                    if job is None:
                        return
                result = None
                failure = None
                committing = False
                intent = None
                stream = job.operation in ("acquire", "advance", "inspect")
                try:
                    job.check()
                    if stream:
                        intent, audit = _authorize_stream(job)
                    else:
                        intent = _authorize(job.operation, job.checkpoint_id)
                        job.future._intent = intent
                    job.check()
                    _recheck_policy(intent)
                    job.check()
                    if connection is None:
                        uri = Path(self._database_path).resolve().as_uri() + "?mode=rw"
                        connection = sqlite3.connect(uri, uri=True, timeout=0.25)
                        connection.execute("PRAGMA busy_timeout=250")
                    job.check()
                    _recheck_policy(intent)
                    job.check()
                    if stream:
                        # Local imports
                        from . import checkpoint_stream

                        connection.execute(
                            "BEGIN" if job.operation == "inspect" else "BEGIN IMMEDIATE"
                        )
                        job.check()
                        _recheck_policy(intent)
                        job.check()
                        with checkpoint_stream._bounded_rows(connection):
                            if job.operation == "acquire":
                                result = checkpoint_stream._acquire(
                                    connection, *job.data
                                )
                            elif job.operation == "inspect":
                                result = checkpoint_stream._inspect(
                                    connection, *job.data
                                )
                            else:
                                result = checkpoint_stream._advance(
                                    connection, job.data, audit
                                )
                        job.check()
                        _recheck_policy(intent)
                        job.check()
                        committing = job.operation != "inspect"
                        connection.commit()
                        _recheck_policy(intent)
                    elif job.operation == "save":
                        payload = _decode(job.data, job.checkpoint_id)
                        connection.execute("BEGIN IMMEDIATE")
                        job.check()
                        _recheck_policy(intent)
                        existing = connection.execute(
                            "SELECT id FROM memories WHERE memory_type=? LIMIT 1",
                            ("consciousness_observer_checkpoint:" + job.checkpoint_id,),
                        ).fetchone()
                        if existing is not None:
                            raise CheckpointError("ambiguous")
                        record_id = uuid.uuid4().hex
                        while record_id == job.checkpoint_id:
                            record_id = uuid.uuid4().hex
                        inserted = _insert_checkpoint(
                            connection, record_id, job.checkpoint_id, job.data
                        )
                        if inserted != 1:
                            raise CheckpointError("unavailable")
                        job.check()
                        _recheck_policy(intent)
                        job.check()
                        committing = True
                        connection.commit()
                        result = LifecycleCheckpoint(
                            record_id, job.checkpoint_id, payload
                        )
                    else:
                        result = self._load(connection, job.checkpoint_id)
                except CheckpointError as exc:
                    failure = CheckpointError("uncertain" if committing else exc.code)
                except Exception:
                    failure = CheckpointError(
                        "uncertain" if committing else "unavailable"
                    )
                finally:
                    if connection is not None and connection.in_transaction:
                        try:
                            connection.rollback()
                        except Exception:
                            connection.close()
                            connection = None
                # Policy/ownership callbacks and Future callbacks may block.
                # Keep them outside the admission condition and cancellation lock.
                active = job.control.active() and job.backend_active()
                with job.control._lock:
                    if not active or not job.control._open_locked():
                        failure = CheckpointError(
                            "uncertain" if committing else "cancelled"
                        )
                with self._condition:
                    self._job = None
                    if stream:
                        restore_authority = None
                        if job.operation in ("acquire", "inspect"):
                            restore_authority = intent, job.backend_owned
                        job.future._seal(
                            result,
                            failure.code if failure else None,
                            restore_authority=restore_authority,
                        )
                    self._condition.notify_all()
                if stream:
                    if job.control.wake_event is not None:
                        job.control.wake_event.set()
                    continue
                # I/O is complete and the slot is released; result() still rechecks
                # policy/deadline/cancellation before a receipt can be accepted.
                if failure is None:
                    job.future.set_result(result)
                else:
                    job.future.set_exception(failure)
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def _load(connection, checkpoint_id):
        checkpoint, _ = LifecycleCheckpointWorker._read_checkpoint(
            connection, checkpoint_id
        )
        return checkpoint

    @staticmethod
    def _read_checkpoint(connection, checkpoint_id):
        # CASE prevents materializing oversized content/context in Python.
        records = connection.execute(
            "SELECT id, length(CAST(content AS BLOB)), "
            "CASE WHEN length(CAST(content AS BLOB))<=? THEN content END, "
            "length(CAST(context AS BLOB)), "
            "CASE WHEN length(CAST(context AS BLOB))<=? THEN context END "
            "FROM memories WHERE memory_type=? LIMIT 2",
            (
                _MAX_BYTES,
                _MAX_BYTES,
                "consciousness_observer_checkpoint:" + checkpoint_id,
            ),
        ).fetchall()
        if not records:
            raise CheckpointError("missing")
        if len(records) != 1:
            raise CheckpointError("ambiguous")
        record_id, content_size, content, context_size, raw_context = records[0]
        if (
            not isinstance(record_id, str)
            or not _HANDLE.fullmatch(record_id)
            or record_id == checkpoint_id
            or content_size is None
            or content_size > _MAX_BYTES
            or context_size is None
            or context_size > _MAX_BYTES
            or not isinstance(content, str)
            or not isinstance(raw_context, str)
        ):
            raise CheckpointError("invalid")
        expected = {
            "owner": _OWNER,
            "scope": _SCOPE,
            "schema": 1,
            "checkpoint_id": checkpoint_id,
            "record_id": record_id,
        }
        try:

            def unique(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError
                    result[key] = value
                return result

            context = json.loads(raw_context, object_pairs_hook=unique)
            if context != expected or type(context["schema"]) is not int:
                raise ValueError
        except Exception:
            raise CheckpointError("invalid") from None
        return (
            LifecycleCheckpoint(
                record_id, checkpoint_id, _decode(content, checkpoint_id)
            ),
            content,
        )
