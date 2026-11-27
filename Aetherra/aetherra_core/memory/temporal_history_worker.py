"""Governed Temporal history on a dedicated connection to the profile Memory DB."""

from __future__ import annotations

# Standard library imports
import asyncio
import os
import sqlite3
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# Local imports
from .checkpoint_stream import StreamJob
from .lifecycle_checkpoint import (
    CheckpointError,
    CheckpointJobControl,
    _authorize_intent,
    _recheck_policy,
)

_WRITE_OPERATIONS = ("acquire", "append")
_READ_CAPABILITIES = ("consciousness:write", "memory:read", "fs:read")
_WRITE_CAPABILITIES = (*_READ_CAPABILITIES, "memory:write", "fs:write")
_MAX_BUSY_MS = 250


@dataclass(frozen=True)
class _Job:
    operation: str
    args: tuple
    control: CheckpointJobControl
    result: StreamJob
    backend_owned: Callable[[], bool] | None


def _freeze_args(operation, key, start_mode, request, token, head, after, limit):
    # Local imports
    from .temporal_history import (
        AppendRequest,
        HistoryHead,
        HistoryKey,
        HistoryToken,
        freeze,
        validate_read,
    )

    if operation == "acquire":
        if type(start_mode) is not str or start_mode not in ("create", "resume"):
            raise CheckpointError("invalid")
        return freeze(key, HistoryKey), start_mode
    if operation == "append":
        return (freeze(request, AppendRequest),)
    if operation == "read":
        token = freeze(token, HistoryToken)
        head = freeze(head, HistoryHead)
        validate_read(after, limit, head)
        return token, head, after, limit
    if operation == "inspect":
        token = freeze(token, HistoryToken)
        request = freeze(request, AppendRequest)
        if (
            token.key != request.token.key
            or token.writer_epoch <= request.token.writer_epoch
        ):
            raise CheckpointError("invalid")
        return token, request
    raise CheckpointError("invalid")


def _authorize(job):
    # Aetherra imports
    from Aetherra.guardian import IntentDeclaration

    # Local imports
    from .temporal_history import SCOPE

    operation = job.operation
    if operation == "acquire":
        metadata = {"history_id": job.args[0].history_id}
    elif operation == "read":
        token, head, _, _ = job.args
        metadata = {"history_id": token.key.history_id}
        if head.digest is not None:
            metadata["selected_head_digest"] = head.digest
    else:
        request = job.args[-1]
        metadata = {
            "history_id": request.token.key.history_id,
            "operation_id": request.operation_id,
            "request_digest": request.digest(),
        }
    intent = IntentDeclaration(
        requester=os.getenv("AETHERRA_PRINCIPAL", "").strip() or "consciousness:core",
        subsystem="consciousness",
        action=f"consciousness.temporal_history_{operation}",
        target="memory:core",
        purpose="Govern bounded access to Temporal memory history",
        capabilities=(
            _WRITE_CAPABILITIES
            if operation in _WRITE_OPERATIONS
            else _READ_CAPABILITIES
        ),
        evidence=(SCOPE,),
        reversible=True,
        rollback_plan="Roll back uncommitted work and preserve committed history.",
        metadata=metadata,
    )
    audit_id = _authorize_intent(intent)
    if len(audit_id.encode("utf-8")) > 256:
        raise CheckpointError("audit_failed")
    return intent, audit_id


class TemporalHistoryWorker:
    """One lazy daemon owns the connection and slot through actual settlement."""

    def __init__(self, database_path: str):
        self._uri = None
        if (
            isinstance(database_path, (str, os.PathLike))
            and str(database_path)
            and str(database_path) != ":memory:"
            and not str(database_path).lower().startswith("file:")
        ):
            # Bind relative paths when the Core opens its selected database.
            self._uri = Path(os.path.abspath(database_path)).as_uri() + "?mode=rw"
        self._condition = threading.Condition()
        self._closing = threading.Event()
        self._thread: threading.Thread | None = None
        self._job: _Job | None = None
        # Only the daemon opens, uses and closes this connection.
        self._connection: sqlite3.Connection | None = None

    def submit(
        self,
        *,
        operation,
        control,
        key=None,
        start_mode=None,
        request=None,
        token=None,
        selected_head=None,
        after_ordinal=None,
        limit=None,
        backend_owned=None,
    ):
        try:
            if (
                type(control) is not CheckpointJobControl
                or type(control.cancelled) is not threading.Event
            ):
                raise CheckpointError("invalid")
            control._bind()
            args = _freeze_args(
                operation,
                key,
                start_mode,
                request,
                token,
                selected_head,
                after_ordinal,
                limit,
            )
            return self._admit(
                _Job(operation, args, control, StreamJob(control), backend_owned)
            )
        except CheckpointError as exc:
            return StreamJob.refused(exc.code)

    def _admit(self, job):
        with self._condition:
            if self._uri is None or self._closing.is_set():
                raise CheckpointError("unavailable")
            if self._job is not None:
                raise CheckpointError("busy")
            with job.control._lock:
                if job.control._admission_closed or not job.control._open_locked():
                    raise CheckpointError("cancelled")
                self._job = job
            if self._thread is None:
                self._thread = threading.Thread(
                    target=self._run, name="memory-temporal-history", daemon=True
                )
                try:
                    self._thread.start()
                except Exception:
                    self._job = None
                    self._closing.set()
                    raise CheckpointError("unavailable") from None
            self._condition.notify_all()
            return job.result

    def pending(self) -> bool:
        with self._condition:
            return self._job is not None

    def close_admission(self) -> None:
        with self._condition:
            self._closing.set()
            if self._job is not None:
                self._job.result.cancel()
            self._condition.notify_all()

    def shutdown(self, timeout: float = 1.0) -> bool:
        self.close_admission()
        thread = self._thread
        if thread is None:
            return True
        if thread is threading.current_thread():
            return False
        thread.join(min(1.0, max(0.0, timeout)))
        return not thread.is_alive()

    def _local_open(self, control) -> bool:
        with control._lock:
            return not self._closing.is_set() and control._open_locked()

    def _check_local(self, control):
        if not self._local_open(control):
            raise CheckpointError("cancelled")

    @staticmethod
    def _check_owner(job):
        control = job.control
        if not control.active() or (
            job.backend_owned is not None
            and not control._active_if_owned(job.backend_owned)
        ):
            raise CheckpointError("cancelled")

    @staticmethod
    def _set_busy_timeout(connection, control):
        with control._lock:
            # Admission always binds a local deadline no later than one second.
            seconds = control._bound_deadline - time.monotonic()
        busy_ms = max(0, min(_MAX_BUSY_MS, int(seconds * 1000)))
        connection.execute(f"PRAGMA busy_timeout={busy_ms}")

    def _execute(self, job):
        connection = self._connection
        result = None
        failure = None
        commit_started = False
        try:
            self._check_owner(job)
            intent, audit_id = _authorize(job)
            self._check_owner(job)
            if connection is None:
                self._connection = connection = sqlite3.connect(
                    self._uri,
                    uri=True,
                    isolation_level=None,
                    timeout=_MAX_BUSY_MS / 1000,
                )
            # Local imports
            from . import temporal_history_store

            store_operation = getattr(temporal_history_store, job.operation)
            args = (*job.args, audit_id) if job.operation == "append" else job.args
            # This is the permit boundary. The active transaction only reads
            # local cancellation state and calls bounded storage operations.
            _recheck_policy(intent)
            self._check_owner(job)
            self._check_local(job.control)
            self._set_busy_timeout(connection, job.control)
            connection.set_progress_handler(
                lambda: not self._local_open(job.control), 1000
            )
            try:
                connection.execute(
                    "BEGIN IMMEDIATE" if job.operation in _WRITE_OPERATIONS else "BEGIN"
                )
                self._check_local(job.control)
                result = store_operation(connection, *args)
                self._check_local(job.control)
                commit_started = True
                connection.commit()
            finally:
                connection.set_progress_handler(None, 0)
            _recheck_policy(intent)
            self._check_owner(job)
            self._check_local(job.control)
        except asyncio.CancelledError:
            job.control.cancel()
            failure = "cancelled"
        except CheckpointError as exc:
            failure = exc.code
        except sqlite3.Error as exc:
            primary = getattr(exc, "sqlite_errorcode", 0) & 0xFF
            if primary in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                failure = "busy"
            elif primary in (sqlite3.SQLITE_CORRUPT, sqlite3.SQLITE_NOTADB):
                failure = "corrupt"
            else:
                failure = "unavailable"
        except Exception:
            failure = "unavailable"
        finally:
            if connection is not None and connection.in_transaction:
                try:
                    connection.rollback()
                except sqlite3.Error:
                    connection.close()
                    self._connection = None
        if failure is not None and commit_started:
            failure = "uncertain"
        authority = (intent, job.backend_owned) if failure is None else None
        return result, failure, authority

    def _settle_locked(self, job, result, failure, authority):
        job.result._seal(result, failure, restore_authority=authority)
        self._job = None
        self._condition.notify_all()
        if job.control.wake_event is not None:
            job.control.wake_event.set()

    def _run(self):
        try:
            while True:
                with self._condition:
                    self._condition.wait_for(
                        lambda: self._job is not None or self._closing.is_set()
                    )
                    job = self._job
                    if job is None:
                        return
                result, failure, authority = self._execute(job)
                with self._condition:
                    self._settle_locked(job, result, failure, authority)
                # Ownership callbacks can keep the entire Core alive.
                del job, result, authority
        finally:
            try:
                if self._connection is not None:
                    self._connection.close()
                    self._connection = None
            finally:
                with self._condition:
                    self._closing.set()
                    if self._job is not None:
                        self._job.result.cancel()
                        self._settle_locked(self._job, None, "uncertain", None)
