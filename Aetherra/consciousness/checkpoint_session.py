"""Owner-thread selection and nonblocking saves for an exact Memory checkpoint stream."""

from __future__ import annotations

# Standard library imports
import copy
import hashlib
import threading
import uuid
from collections.abc import Callable
from dataclasses import asdict, replace

# Aetherra imports
from Aetherra.aetherra_core.memory.checkpoint_stream import (
    AcquiredStream,
    AdvanceReceipt,
    AdvanceRequest,
    AttemptDescriptor,
    InspectionResult,
    SnapshotMetadata,
    StreamHead,
    StreamKey,
    StreamToken,
)
from Aetherra.aetherra_core.memory.lifecycle_checkpoint import (
    CheckpointError,
    CheckpointJobControl,
)
from Aetherra.consciousness.checkpoint import (
    OWNER,
    SCOPE,
    ObserverCheckpoint,
    dump_checkpoint_json,
)


def _invalid():
    raise ValueError("consciousness_config_invalid")


def automatic_settings(value):
    if type(value) is not dict or set(value) - {
        "enabled",
        "stream_id",
        "start_mode",
        "retain_checkpoints",
        "save_interval_seconds",
    }:
        _invalid()
    enabled = value.get("enabled")
    if type(enabled) is not bool:
        _invalid()
    retain = value.get("retain_checkpoints", 10)
    interval = value.get("save_interval_seconds", 300)
    if type(retain) is not int or not 2 <= retain <= 100:
        _invalid()
    if type(interval) is not int or not 30 <= interval <= 86400:
        _invalid()
    if (enabled or "start_mode" in value) and value.get("start_mode") not in (
        "create",
        "resume",
    ):
        _invalid()
    if enabled or "stream_id" in value:
        try:
            StreamKey(OWNER, SCOPE, value.get("stream_id"))
        except CheckpointError:
            _invalid()
    if not enabled:
        return None
    return {**value, "retain_checkpoints": retain, "save_interval_seconds": interval}


def _fields(value, names):
    if type(value) is not dict or len(value) != len(names) or value.keys() != names:
        _invalid()
    return value


def recovery_descriptor(value, automatic):
    """Accept the closed nested JSON representation of the frozen descriptor."""
    if type(value) is AttemptDescriptor:
        attempt = value
    else:
        root = _fields(
            value,
            {
                "token",
                "expected_head",
                "operation_id",
                "checkpoint_id",
                "payload_digest",
                "metadata_digest",
            },
        )
        token = _fields(root["token"], {"key", "writer_epoch"})
        key = _fields(token["key"], {"owner", "scope", "stream_id"})
        head = _fields(
            root["expected_head"],
            {
                "generation",
                "checkpoint_id",
                "record_id",
                "payload_digest",
                "metadata_digest",
            },
        )
        try:
            attempt = AttemptDescriptor(
                StreamToken(StreamKey(**key), token["writer_epoch"]),
                StreamHead(**head),
                root["operation_id"],
                root["checkpoint_id"],
                root["payload_digest"],
                root["metadata_digest"],
            )
        except CheckpointError:
            _invalid()
    if (
        automatic is None
        or automatic["start_mode"] != "resume"
        or automatic["stream_id"] != attempt.token.key.stream_id
    ):
        _invalid()
    return attempt


class ObserverCheckpointSession:
    """The owner schedules frozen ticks. Memory selects, fences and commits state."""

    def __init__(
        self,
        memory,
        automatic,
        *,
        wall_clock,
        monotonic_clock,
        still_owned,
        recovery_attempt=None,
        wake_event=None,
        tick_interval=1.0,
    ):
        self._memory = memory
        self._config = automatic_settings(automatic)
        if self._config is None:
            _invalid()
        self._attempt = (
            None
            if recovery_attempt is None
            else recovery_descriptor(recovery_attempt, self._config)
        )
        self._wall_clock = wall_clock
        self._monotonic_clock = monotonic_clock
        self._still_owned = still_owned
        self.startup_cancelled = threading.Event()
        self.wake_event = wake_event if wake_event is not None else threading.Event()
        self._freshness = max(3.0, 3 * tick_interval)
        self._stop_lock = threading.Lock()
        self._cancelled = threading.Event()
        self._stop_deadline = None
        self._final_attempted = False
        self._write_control = None
        self._write_job = None
        self._candidate = None
        self._completed = self._attempted_tick = 0
        self._started = False
        self._job = None
        self._acquire_job = None
        self._inspect_job = None
        self._acquired: AcquiredStream | None = None
        self._taken = False
        self._status = {
            "state": "restoring",
            "last_save_trigger": None,
            "last_save_acceptance": "none",
            "current_attempt": None,
            "saved_operation_id": None,
            "saved_generation": None,
            "saved_trigger": None,
            "saved_record_id": None,
            "saved_checkpoint_id": None,
            "stop_save_submitted": False,
            "ownership_checked_at_unix_s": None,
            "ownership_lost_at_unix_s": None,
            "outstanding": False,
            "last_error_code": None,
            "stream_id": self._config["stream_id"],
            "start_mode": self._config["start_mode"],
            "session_id": None,
            "session_started_at_unix_s": None,
            "session_uptime_seconds": 0.0,
            "last_verified_observation_at_unix_s": None,
            "captured_at_unix_s": None,
            "observation_gap_seconds": None,
            "observation_gap_state": "unknown",
            "offline_duration_seconds": None,
            "offline_duration_state": "unknown",
            "recovery_method": "none",
            "recovery_outcome": "not_attempted",
            "previous_save_acceptance": "unknown",
            "previous_shutdown_evidence": "unknown",
            "observed_writer_epoch": None,
            "observed_generation": None,
            "ownership_state": "not_acquired",
            "retention_needed": False,
            "matched_record_id": None,
        }

    def _control(self):
        self._startup_deadline = self._monotonic_clock() + 1.0
        return CheckpointJobControl(
            self.startup_cancelled,
            self._startup_deadline,
            self._still_owned,
            self.wake_event,
        )

    def begin_start(self) -> None:
        if self._started:
            return
        self._started = True
        self.started_monotonic = self._monotonic_clock()
        self._next_due = self.started_monotonic + self._config["save_interval_seconds"]
        self._status.update(
            session_id=uuid.uuid4().hex, session_started_at_unix_s=self._wall_clock()
        )
        key = StreamKey(OWNER, SCOPE, self._config["stream_id"])
        try:
            self._acquire_job = self._job = (
                self._memory.submit_acquire_checkpoint_stream(
                    key=key,
                    start_mode=self._config["start_mode"],
                    retain_checkpoints=self._config["retain_checkpoints"],
                    control=self._control(),
                )
            )
            self._status["outstanding"] = self._job.outstanding
        except Exception:
            self._block("unavailable")

    def _block(self, code):
        self._acquired = None
        if code not in {
            "invalid",
            "denied",
            "audit_failed",
            "corrupt",
            "missing",
            "busy",
            "cancelled",
            "conflict",
            "writer_fenced",
            "uncertain",
            "unavailable",
        }:
            code = "unavailable"
        self._status.update(
            state="uncertain" if code == "uncertain" else "blocked",
            last_error_code=code,
            recovery_outcome="blocked",
            ownership_state="lost" if code == "writer_fenced" else "uncertain",
        )

    def _poll_start(self, *, local_owned: bool) -> None:
        job = self._job
        if job is None:
            return
        result = job.poll(local_owned=local_owned)
        self._status["outstanding"] = job.outstanding
        if result is None:
            return
        if self._status["last_error_code"] is not None:
            return
        if result.error_code:
            self._block(result.error_code)
            return
        if local_owned is not True:
            self._block("uncertain")
            return
        try:
            if job is self._acquire_job:
                acquired = result.value
                if (
                    type(acquired) is not AcquiredStream
                    or acquired.token.key.stream_id != self._config["stream_id"]
                ):
                    raise CheckpointError("invalid")
                self._acquired = acquired
                self._head = acquired.head
                self._status["ownership_checked_at_unix_s"] = self._wall_clock()
                self._status.update(
                    observed_writer_epoch=acquired.token.writer_epoch,
                    observed_generation=acquired.head.generation,
                    retention_needed=acquired.retention_needed,
                    ownership_state="last_observed_owned",
                )
                if self._attempt is not None:
                    self._status["recovery_method"] = "exact_inspection"
                    self._inspect_job = self._job = (
                        self._memory.submit_inspect_checkpoint_stream(
                            token=acquired.token,
                            attempt=self._attempt,
                            control=self._control(),
                        )
                    )
                    self._status["outstanding"] = self._job.outstanding
                    return
            else:
                receipt = result.value
                if (
                    type(receipt) is not InspectionResult
                    or receipt.head != self._acquired.head
                ):
                    raise CheckpointError("corrupt")
                self._status.update(
                    recovery_outcome=receipt.outcome,
                    matched_record_id=receipt.matched_record_id,
                )
            self._select()
            self._job = None
        except CheckpointError as exc:
            self._block(exc.code)
        except Exception:
            self._block("unavailable")

    def _select(self):
        acquired = self._acquired
        if acquired.head.generation == 0:
            if acquired.metadata is not None or acquired.checkpoint is not None:
                raise CheckpointError("corrupt")
            if self._attempt is None:
                self._status.update(
                    recovery_method="new_stream", recovery_outcome="fresh"
                )
        else:
            metadata = acquired.metadata
            record = acquired.checkpoint
            if (
                metadata is None
                or record is None
                or record.record_id != acquired.head.record_id
                or record.checkpoint_id != acquired.head.checkpoint_id
            ):
                raise CheckpointError("corrupt")
            if self._attempt is None:
                self._status["recovery_method"] = "durable_head"
            gap = (
                self._status["session_started_at_unix_s"]
                - metadata.last_verified_observation_at_unix_s
            )
            gap_state = "host_wall_clock_estimate" if gap >= 0 else "clock_inconsistent"
            self._status.update(
                captured_at_unix_s=metadata.captured_at_unix_s,
                last_verified_observation_at_unix_s=metadata.last_verified_observation_at_unix_s,
                observation_gap_seconds=gap if gap >= 0 else None,
                observation_gap_state=gap_state,
            )
        self._status["state"] = "selected"

    def take_restore(self) -> AcquiredStream | None:
        if self._status["state"] != "selected" or self._taken:
            return None
        self._taken = True
        return self._acquired

    def check_before_apply(self):
        self._acquire_job.check_restore_policy()
        if self._attempt is not None:
            self._inspect_job.check_restore_policy()

    def apply_window_open(self):
        return self._acquire_job.restore_window_open() and (
            self._inspect_job is None or self._inspect_job.restore_window_open()
        )

    def mark_applied(self):
        state = "restored" if self._acquired.head.generation else "fresh"
        self._status["state"] = state
        if state == "restored" and self._attempt is None:
            self._status["recovery_outcome"] = "restored"

    def on_completed_tick(
        self,
        state: ObserverCheckpoint,
        *,
        observation_wall: float,
        observation_uptime: float,
        capture_uptime: float,
    ) -> None:
        self._candidate = (state, observation_wall, observation_uptime, capture_uptime)
        self._completed += 1
        self._status["session_uptime_seconds"] = capture_uptime

    def begin_stop(self, *, deadline: float, save_checkpoint: bool) -> None:
        # This may run off-owner. Only short local control operations belong here.
        with self._stop_lock:
            if self._stop_deadline is None or deadline < self._stop_deadline:
                self._stop_deadline = deadline
            self.startup_cancelled.set()
            if self._write_control is not None:
                self._write_control.limit_deadline(self._stop_deadline)
            if not save_checkpoint:
                self._cancel_writes()
        self.wake_event.set()

    def _cancel_writes(self):
        self._cancelled.set()
        if self._write_control is not None:
            self._write_control.cancel()

    def cancel(self) -> None:
        with self._stop_lock:
            self.startup_cancelled.set()
            self._cancel_writes()
        self.wake_event.set()

    def wait_timeout(self):
        """Time left to consume the active receipt. Closed work wakes on real drain."""
        job = self._job or self._write_job
        if job is None:
            return None
        if not job.outstanding:
            return 0
        if job.acceptance_closed:
            return None if self._status["last_error_code"] is not None else 0
        deadline = (
            self._startup_deadline
            if self._job is not None
            else self._write_control.deadline
        )
        if self._stop_deadline is not None:
            deadline = min(deadline, self._stop_deadline)
        return max(0.0, deadline - self._monotonic_clock())

    def poll(self, *, local_owned: bool | Callable[[], bool]) -> None:
        # A positive receipt is immutable once the worker releases the slot.
        # Observe that boundary before sampling the observer's local identities.
        write_pending = self._write_job is not None and self._write_job.outstanding
        if callable(local_owned):
            local_owned = local_owned()
        if self._job is not None:
            self._poll_start(local_owned=local_owned)
            return
        if self._write_job is not None:
            self._consume_write(local_owned, was_pending=write_pending)
        if (
            self._write_job is None
            and self._taken
            and self._acquired is not None
            and self._status["last_error_code"] is None
            and local_owned
            and not self._cancelled.is_set()
        ):
            self._schedule_write()

    def _schedule_write(self):
        now = self._monotonic_clock()
        stopping = self._stop_deadline is not None
        if stopping:
            if self._final_attempted or now >= self._stop_deadline:
                return
        elif now < self._next_due:
            return
        if self._candidate is None or self._completed == self._attempted_tick:
            return
        state, wall, observed, captured = self._candidate
        if not 0 <= now - self.started_monotonic - observed <= self._freshness:
            return
        trigger = "orderly_stop" if stopping else "periodic"
        deadline = now + 1.0
        if stopping:
            deadline = min(deadline, self._stop_deadline)
        try:
            handle = uuid.uuid4().hex
            payload = dump_checkpoint_json(replace(state, checkpoint_id=handle))
            metadata = SnapshotMetadata(
                1,
                self._status["session_id"],
                self._status["session_started_at_unix_s"],
                wall,
                state.captured_at,
                observed,
                captured,
                trigger,
            ).to_bytes()
            attempt = AttemptDescriptor(
                self._acquired.token,
                self._head,
                uuid.uuid4().hex,
                handle,
                hashlib.sha256(payload).hexdigest(),
                hashlib.sha256(metadata).hexdigest(),
            )
            request = AdvanceRequest(attempt, payload, metadata)
            with self._stop_lock:
                # Encoding is outside the stop lock. A stop during encoding wins.
                if self._cancelled.is_set() or stopping != (
                    self._stop_deadline is not None
                ):
                    return
                self._write_control = CheckpointJobControl(
                    self._cancelled, deadline, self._still_owned, self.wake_event
                )
                self._final_attempted = stopping
            self._attempted_tick = self._completed
            self._write_attempt = attempt
            self._write_job = self._memory.submit_advance_checkpoint_stream(
                request=request, control=self._write_control
            )
            if not self._write_job.admitted:
                refusal = self._write_job.poll(local_owned=True)
                self._write_job = None
                self._next_due = (
                    self._monotonic_clock() + self._config["save_interval_seconds"]
                )
                if refusal.error_code != "busy":
                    self._write_failure(refusal.error_code)
                return
            self._status.update(
                state="saving",
                outstanding=True,
                last_save_trigger=trigger,
                last_save_acceptance="pending",
                current_attempt=asdict(attempt),
                stop_save_submitted=stopping,
            )
        except (ValueError, CheckpointError) as exc:
            self._write_failure(getattr(exc, "code", "invalid"))
        except Exception:
            self._write_failure("unavailable")

    def _write_failure(self, code):
        if code not in {
            "busy",
            "cancelled",
            "uncertain",
            "unavailable",
            "denied",
            "audit_failed",
            "corrupt",
            "capacity",
            "invalid",
            "writer_fenced",
            "conflict",
        }:
            code = "unavailable"
        lost = code == "writer_fenced"
        self._status.update(
            state="uncertain" if code == "uncertain" else "blocked",
            last_error_code=code,
            ownership_state="lost" if lost else "uncertain",
        )
        # Only admission publishes pending. A refusal before admission belongs
        # to no new attempt and leaves the previous receipt history intact.
        if self._status["last_save_acceptance"] == "pending":
            self._status["last_save_acceptance"] = "unacknowledged"
        if lost:
            self._status["ownership_lost_at_unix_s"] = self._wall_clock()

    def _consume_write(self, local_owned, *, was_pending):
        job = self._write_job
        deadline = self._write_control.deadline
        if self._stop_deadline is not None:
            deadline = min(deadline, self._stop_deadline)
        eligible = local_owned is True and self._monotonic_clock() < deadline
        if was_pending and eligible and not job.acceptance_closed:
            # The worker may have sealed during the identity check. Its wake
            # causes a fresh post-seal check. Local refusal/expiry needs no wait.
            return
        result = job.poll(local_owned=eligible)
        if result is None:
            return
        outstanding = job.outstanding
        self._status["outstanding"] = outstanding
        if not outstanding:
            self._write_job = None
            self._next_due = (
                self._monotonic_clock() + self._config["save_interval_seconds"]
            )
        if self._status["last_save_acceptance"] != "pending":
            return
        if result.error_code is not None:
            self._write_failure(result.error_code)
            return
        receipt = result.value
        attempt = self._write_attempt
        if (
            type(receipt) is not AdvanceReceipt
            or receipt.attempt != attempt
            or type(receipt.head) is not StreamHead
            or type(receipt.audit_id) is not str
            or not receipt.audit_id.strip()
            or receipt.head.generation != attempt.proposed_generation
            or receipt.head.checkpoint_id != attempt.checkpoint_id
            or receipt.head.payload_digest != attempt.payload_digest
            or receipt.head.metadata_digest != attempt.metadata_digest
        ):
            self._write_failure("corrupt")
            return
        self._head = receipt.head
        self._status.update(
            state="saved",
            saved_record_id=receipt.head.record_id,
            saved_operation_id=attempt.operation_id,
            saved_generation=receipt.head.generation,
            saved_trigger=self._status["last_save_trigger"],
            saved_checkpoint_id=receipt.head.checkpoint_id,
            observed_generation=receipt.head.generation,
            last_save_acceptance="acknowledged",
            ownership_checked_at_unix_s=self._wall_clock(),
        )

    def get_cached_status(self) -> dict:
        return copy.deepcopy(self._status)
