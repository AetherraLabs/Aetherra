"""Owner-thread startup selection of an exact Memory checkpoint stream."""

from __future__ import annotations

# Standard library imports
import threading
import uuid

# Aetherra imports
from Aetherra.aetherra_core.memory.checkpoint_stream import (
    AcquiredStream,
    AttemptDescriptor,
    InspectionResult,
    StreamHead,
    StreamKey,
    StreamToken,
)
from Aetherra.aetherra_core.memory.lifecycle_checkpoint import (
    CheckpointError,
    CheckpointJobControl,
)
from Aetherra.consciousness.checkpoint import OWNER, SCOPE


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
    """The observer owner advances startup. Memory alone selects and fences state."""

    def __init__(
        self,
        memory,
        automatic,
        *,
        wall_clock,
        monotonic_clock,
        still_owned,
        recovery_attempt=None,
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
        self._started = False
        self._job = None
        self._acquire_job = None
        self._inspect_job = None
        self._acquired: AcquiredStream | None = None
        self._taken = False
        self._status = {
            "state": "restoring",
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
        return CheckpointJobControl(
            self.startup_cancelled, self._monotonic_clock() + 1.0, self._still_owned
        )

    def begin_start(self) -> None:
        if self._started:
            return
        self._started = True
        self.started_monotonic = self._monotonic_clock()
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

    def poll(self, *, local_owned: bool) -> None:
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

    def get_cached_status(self) -> dict:
        return dict(self._status)
