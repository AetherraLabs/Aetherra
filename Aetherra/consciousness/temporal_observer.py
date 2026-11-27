"""Optional five-second observer of committed Temporal history."""

from __future__ import annotations

# Standard library imports
import asyncio
import re
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime

# Local imports
from .runtime_observer import observer_settings


def temporal_settings(config: dict) -> dict | None:
    if "temporal_observer" not in config:
        return None
    value = config["temporal_observer"]
    if type(value) is dict and type(value.get("enabled")) is bool:
        if not value["enabled"] and set(value) == {"enabled"}:
            return None
        if (
            value["enabled"]
            and set(value) == {"enabled", "history_id", "start_mode"}
            and type(value["history_id"]) is str
            and re.fullmatch("[0-9a-f]{32}", value["history_id"])
            and value["start_mode"] in ("create", "resume")
            and observer_settings(config) is not None
        ):
            return dict(value)
    raise ValueError("temporal_config_invalid")


def _engine():
    # Local imports
    from .quantum.temporal_consciousness_system import TemporalConsciousnessEngine

    return TemporalConsciousnessEngine()


def _utc(value):
    try:
        datetime.fromtimestamp(value, UTC)
    except (ValueError, OSError, OverflowError, TypeError):
        raise _TemporalError("invalid") from None
    return value


_ERROR_CODES = frozenset(
    {
        "invalid",
        "missing",
        "unchanged",
        "conflict",
        "corrupt",
        "busy",
        "denied",
        "audit_failed",
        "unavailable",
        "cancelled",
        "uncertain",
        "writer_fenced",
        "ownership_lost",
        "temporal_config_invalid",
        "config_invalid",
        "core_not_ready",
        "memory_not_ready",
        "policy_not_ready",
        "service_conflict",
    }
)


class _TemporalError(Exception):
    pass


class TemporalObserver:
    def __init__(
        self, source, memory, *, settings, local_owned, readiness, engine_factory=None
    ):
        self._source = source
        self._memory = memory
        self._settings = dict(settings) if settings else None
        self._owned = local_owned
        self._readiness = readiness
        self._factory = engine_factory or _engine
        self._engine = None
        self._lock = threading.RLock()
        self._wake = threading.Event()
        self._cancel = threading.Event()
        self._thread = None
        self._job = None
        self._control = None
        self._attempt_deadline = None
        self._observation_control = False
        self._closed = False
        self._stop_deadline = None
        self._save_end = False
        self._fresh_until = 0.0
        self._records = ()
        self._last = self._seen = None
        self._gap = self._saved = False
        self._status = {
            "enabled": bool(settings),
            "runtime_state": "starting" if settings else "disabled",
            "thread_alive": False,
            "source_fresh": False,
            "accepted_observations": 0,
            "skipped_observations": 0,
            "selected_head_record_id": None,
            "restored_record_id": None,
            "saved_record_id": None,
            "writer_epoch": None,
            "ownership_state": "unverified",
            "persistence_state": "idle",
            "outstanding": False,
            "last_error_code": None,
            "last_verified_observation_at_unix_s": None,
            "observation_gap_seconds": None,
            "observation_gap_state": "unknown",
            "offline_duration_state": "unknown",
        }

    def get_runtime_status(self):
        with self._lock:
            status = dict(self._status)
            now = time.monotonic()
            if status["runtime_state"] != "blocked" and self._attempt_expired():
                status.update(
                    runtime_state="blocked",
                    ownership_state="uncertain",
                    persistence_state="uncertain",
                    last_error_code="uncertain",
                    source_fresh=False,
                )
            if now >= self._fresh_until:
                status["source_fresh"] = False
            return status

    get_status = get_runtime_status

    def start(self):
        with self._lock:
            if (
                not self._settings
                or self._closed
                or self._thread
                or self._cancel.is_set()
            ):
                return False
            thread = threading.Thread(
                target=self._run, name="temporal-observer", daemon=True
            )
            thread.start()
            self._thread = thread
            self._status["thread_alive"] = True
            return True

    def block(self, code):
        if type(code) is not str or code not in _ERROR_CODES:
            code = "unavailable"
        with self._lock:
            if self._cancel.is_set():
                return
            if self._attempt_expired():
                code = "uncertain"
            self._closed = True
            self._cancel.set()
            self._wake.set()
            ownership = {
                "writer_fenced": "fenced",
                "ownership_lost": "lost",
                "uncertain": "uncertain",
            }.get(code, "unverified")
            self._status.update(
                runtime_state="blocked",
                ownership_state=ownership,
                source_fresh=False,
                last_error_code=code,
                persistence_state="uncertain" if code == "uncertain" else "blocked",
            )
            if self._control:
                self._control.cancel()
            if self._job:
                self._job.cancel()

    def close_observation_admission(self):
        with self._lock:
            self._closed = True
            self._status["source_fresh"] = False
            if self._observation_control and self._control:
                self._control.close_admission()
            if self._status["runtime_state"] in ("starting", "running"):
                self._status["runtime_state"] = "stopping"
            self._wake.set()

    async def stop(self, *, save_history=False, deadline=None):
        with self._lock:
            self.close_observation_admission()
            now = time.monotonic()
            if self._stop_deadline is None:
                self._stop_deadline = min(
                    now + 1, deadline if deadline is not None else now + 1
                )
                self._save_end = save_history is True
                if self._control:
                    self._control.limit_deadline(self._stop_deadline)
                    self._attempt_deadline = min(
                        self._attempt_deadline, self._stop_deadline
                    )
            if not self._thread and self._status["runtime_state"] == "stopping":
                self._status["runtime_state"] = "stopped"
            self._wake.set()
        while True:
            with self._lock:
                if not self._status["thread_alive"]:
                    return True
                remaining = self._stop_deadline - time.monotonic()
                if remaining <= 0:
                    self.block("uncertain")
                    return False
            await asyncio.sleep(min(0.01, remaining))

    def _attempt_expired(self):
        return (
            self._status["outstanding"]
            and self._attempt_deadline is not None
            and time.monotonic() >= self._attempt_deadline
        )

    def _check_local(self, job=None):
        if (
            self._cancel.is_set()
            or self._attempt_expired()
            or (
                self._stop_deadline is not None
                and time.monotonic() >= self._stop_deadline
            )
        ):
            raise _TemporalError("uncertain")
        if job is not None and not job.restore_window_open():
            raise _TemporalError("uncertain")

    @contextmanager
    def _publication(self, job):
        with self._lock:
            self._check_local(job)
            yield
            self._status["outstanding"] = False

    def _begin_attempt(self, *, observation=False):
        # Aetherra imports
        from Aetherra.aetherra_core.memory.lifecycle_checkpoint import (
            CheckpointJobControl,
        )

        with self._lock:
            self._check_local()
            if observation and self._closed:
                return None
            deadline = time.monotonic() + 1
            if self._stop_deadline is not None:
                deadline = min(deadline, self._stop_deadline)
            self._control = CheckpointJobControl(
                threading.Event(), deadline, self._owned
            )
            self._attempt_deadline = deadline
            self._observation_control = observation
            self._status["outstanding"] = True
            return self._control

    def _attempt(self, method, *, observation=False, control=None, **kwargs):
        if control is None:
            control = self._begin_attempt(observation=observation)
        if control is None:
            return None, None
        if self._owned() is not True:
            raise _TemporalError("ownership_lost")
        with self._lock:
            self._check_local()
        ready = not observation or self._readiness() is None
        with self._lock:
            self._check_local()
            if self._observation_control and self._closed:
                self._status["outstanding"] = False
                return None, None
        if not ready:
            self._gap = True
            with self._lock:
                self._status["source_fresh"] = False
            self._probe(control)
            return None, None
        # Admission on the worker can call adapter/backend code. Never hold the
        # status lock across it. The control's window includes admission time.
        job = method(control=control, **kwargs)
        with self._lock:
            self._job = job
            if self._cancel.is_set() or time.monotonic() >= self._attempt_deadline:
                job.cancel()
                raise _TemporalError("uncertain")
        while True:
            completion = job.poll(local_owned=not self._cancel.is_set())
            if completion is not None:
                if completion.error_code:
                    if (
                        self._observation_control
                        and self._closed
                        and not job.admitted
                        and completion.error_code == "cancelled"
                    ):
                        with self._lock:
                            self._check_local()
                            self._status["outstanding"] = False
                        return None, None
                    raise _TemporalError(completion.error_code)
                return job, completion.value
            time.sleep(0.002)

    def _publish(self, job, head, records):
        self._engine.import_history_window(
            records,
            history_id=self._settings["history_id"],
            selected_head=head,
            authorize=job.check_restore_policy,
            publication_guard=self._publication(job),
        )
        self._records, self._head = records, head

    def _restore(self):
        # Aetherra imports
        from Aetherra.aetherra_core.memory import temporal_history as h

        self._engine = self._factory()
        key = h.HistoryKey(h.OWNER, h.SCOPE, self._settings["history_id"])
        job, selection = self._attempt(
            self._memory.submit_acquire_temporal_history,
            key=key,
            start_mode=self._settings["start_mode"],
        )
        self._token, head = selection.token, selection.head
        if self._token.key != key:
            raise _TemporalError("corrupt")
        after = max(0, head.ordinal - 256)
        records = ()
        while after < head.ordinal:
            job, page = self._attempt(
                self._memory.submit_read_temporal_history,
                token=self._token,
                selected_head=head,
                after_ordinal=after,
                limit=64,
            )
            if (
                page.selected_head != head
                or not page.records
                or page.records[0].ordinal != after + 1
            ):
                raise _TemporalError("corrupt")
            records += page.records
            after = page.next_ordinal
        self._publish(job, head, records)
        if records:
            self._last = self._seen = records[-1].event.source
        with self._lock:
            self._check_local()
            self._status.update(
                runtime_state="stopping" if self._closed else "running",
                persistence_state="ready",
                ownership_state="last_verified",
                writer_epoch=self._token.writer_epoch,
                selected_head_record_id=head.record_id,
                restored_record_id=head.record_id,
                outstanding=False,
                last_verified_observation_at_unix_s=(
                    self._last.observed_at_unix_s if self._last else None
                ),
            )

    def _probe(self, control=None) -> bool:
        job, _ = self._attempt(
            self._memory.submit_read_temporal_history,
            token=self._token,
            selected_head=self._head,
            after_ordinal=self._head.ordinal,
            limit=1,
            control=control,
        )
        if job is None:
            return False
        job.check_restore_policy()
        with self._publication(job):
            self._status["outstanding"] = False
        return True

    def _append(self, source, kinds, *, observation, control=None):
        # Aetherra imports
        from Aetherra.aetherra_core.memory import temporal_history as h

        captured = _utc(time.time())
        events = tuple(
            h.TemporalEvent(uuid.uuid4().hex, kind, source, captured, reason)
            for kind, reason in kinds
        )
        request = h.AppendRequest(self._token, self._head, uuid.uuid4().hex, events)
        job, receipt = self._attempt(
            self._memory.submit_append_temporal_history,
            request=request,
            observation=observation,
            control=control,
        )
        if job is None:
            return False
        records = receipt.records
        if (
            receipt.request_digest != request.digest()
            or tuple(r.event for r in records) != events
            or records[0].ordinal != self._head.ordinal + 1
            or records[0].prior_digest != self._head.digest
        ):
            raise _TemporalError("uncertain")
        self._publish(job, receipt.head, (self._records + records)[-256:])
        with self._lock:
            self._check_local()
            self._status.update(
                saved_record_id=receipt.head.record_id,
                selected_head_record_id=receipt.head.record_id,
                persistence_state="saved",
                outstanding=False,
            )
            if observation:
                if self._last:
                    gap = source.observed_at_unix_s - self._last.observed_at_unix_s
                    self._status.update(
                        observation_gap_seconds=gap if gap >= 0 else None,
                        observation_gap_state=(
                            "estimated" if gap >= 0 else "inconsistent"
                        ),
                    )
                self._status["accepted_observations"] += 1
                self._status["last_verified_observation_at_unix_s"] = (
                    source.observed_at_unix_s
                )
                self._last, self._saved, self._gap = source, True, False

        return True

    def _sample(self):
        # Aetherra imports
        from Aetherra.aetherra_core.memory.temporal_history import TemporalSource

        control = self._begin_attempt(observation=True)
        if control is None:
            return
        ready = self._readiness() is None
        with self._lock:
            self._check_local()
        raw = self._source.get_temporal_observation() if ready else None
        with self._lock:
            self._check_local()
        if raw is None:
            self._gap = True
            with self._lock:
                self._status["source_fresh"] = False
            self._probe(control)
            return
        source = TemporalSource(**raw)
        _utc(source.session_started_at_unix_s)
        _utc(source.observed_at_unix_s)
        seen = self._seen
        same = seen and seen.session_id == source.session_id
        with self._lock:
            self._check_local()
            if self._closed:
                self._status["outstanding"] = False
                return
            self._status["source_fresh"] = True
            self._fresh_until = time.monotonic() + 5
        if same and source.sequence <= seen.sequence:
            self._probe(control)
            return
        kinds = []
        if not self._saved:
            kinds.append(
                (
                    "session_start",
                    "created" if self._token.writer_epoch == 1 else "resumed",
                )
            )
            if self._last:
                kinds.append(("gap", "restart"))
        elif self._last.session_id != source.session_id:
            kinds.append(("gap", "source_changed"))
        elif self._gap:
            kinds.append(("gap", "source_unavailable"))
        if not kinds and source.counts == self._last.counts:
            if not self._probe(control):
                return
        elif not self._append(
            source, [*kinds, ("observation", None)], observation=True, control=control
        ):
            return
        self._seen = source
        if same:
            with self._lock:
                self._status["skipped_observations"] += max(
                    0, source.sequence - seen.sequence - 1
                )

    def _wait_for_sample(self, deadline):
        self._wake.wait(max(0, deadline - time.monotonic()))

    def _run(self):
        # Aetherra imports
        from Aetherra.aetherra_core.memory.lifecycle_checkpoint import CheckpointError

        try:
            with self._lock:
                self._status["persistence_state"] = "restoring"
            self._restore()
            while not self._closed:
                next_sample = time.monotonic() + 5
                self._sample()
                self._wait_for_sample(next_sample)
            while self._stop_deadline is None and not self._cancel.is_set():
                self._wake.clear()
                if self._stop_deadline is None and not self._cancel.is_set():
                    self._wake.wait()
            if self._save_end and self._saved and not self._cancel.is_set():
                self._append(
                    self._last, [("session_end", "orderly_stop")], observation=False
                )
            with self._lock:
                self._check_local()
                self._status.update(runtime_state="stopped", persistence_state="closed")
        except (CheckpointError, _TemporalError) as exc:
            self.block(exc.code if isinstance(exc, CheckpointError) else str(exc))
        except asyncio.CancelledError:
            self.block("cancelled")
        except Exception:
            self.block("unavailable")
        finally:
            with self._lock:
                if self._status["runtime_state"] not in ("blocked", "stopped"):
                    self.block("unavailable")
            while self._job is not None and self._job.outstanding:
                time.sleep(0.01)
            with self._lock:
                self._status.update(
                    outstanding=False, thread_alive=False, source_fresh=False
                )
