"""Owned, bounded observe-only lifecycle for the normal runtime's ConsciousnessCore."""

from __future__ import annotations

# Standard library imports
import asyncio
import copy
import math
import os
import re
import threading
import time
import uuid
from collections.abc import Callable
from typing import Any


def observer_settings(config: dict[str, Any]) -> float | None:
    """Return the requested interval, or None when this optional loop is disabled."""
    enabled = config.get("consciousness_enabled")
    if "consciousness_enabled" not in config:
        value = os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0")
        if value not in {"0", "1"}:
            raise ValueError("consciousness_config_invalid")
        enabled = value == "1"
    if type(enabled) is not bool:
        raise ValueError("consciousness_config_invalid")
    if not enabled:
        return None
    mode = config.get(
        "consciousness_mode", os.getenv("AETHERRA_AUTONOMY_MODE", "observe")
    )
    hz = config.get(
        "consciousness_tick_hz", os.getenv("AETHERRA_CONSCIOUSNESS_HZ", "1")
    )
    try:
        if isinstance(hz, bool) or mode != "observe":
            raise ValueError
        hz = float(hz)
        if not math.isfinite(hz) or not 0.1 <= hz <= 5:
            raise ValueError
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("consciousness_config_invalid") from exc
    return 1 / hz


def continuity_settings(config: dict[str, Any]) -> dict[str, Any]:
    """Persistence is an independent explicit opt-in with an exact selected handle."""
    settings = config.get("consciousness_continuity", {})
    if not isinstance(settings, dict) or set(settings) - {
        "enabled",
        "restore_checkpoint_id",
    }:
        raise ValueError("consciousness_config_invalid")
    enabled = settings.get("enabled", False)
    handle = settings.get("restore_checkpoint_id")
    if type(enabled) is not bool or (
        handle is not None
        and (
            not isinstance(handle, str) or re.fullmatch(r"[0-9a-f]{32}", handle) is None
        )
    ):
        raise ValueError("consciousness_config_invalid")
    if enabled and observer_settings(config) is None:
        raise ValueError("consciousness_config_invalid")
    return {"enabled": enabled, "restore_checkpoint_id": handle}


def observer_policy_ready() -> bool:
    """Observe mode is not permission to bypass the existing strict policy stack."""
    # Aetherra imports
    from Aetherra.guardian import guardian_enabled, guardian_mode, load_guardian_policy

    try:
        if not guardian_enabled() or guardian_mode().value != "enforcing":
            return False
        if any(
            os.getenv(name) != "1"
            for name in (
                "AETHERRA_REQUIRE_CAPABILITIES",
                "AETHERRA_GUARDIAN_REQUIRE_POLICY",
                "AETHERRA_SIGNING_STRICT",
                "AETHERRA_SCRIPT_VERIFY_STRICT",
                "AETHERRA_AUDIT",
            )
        ):
            return False
        load_guardian_policy(require_valid_policy=True)
        return True
    except Exception:
        return False


class ConsciousnessObserver:
    """One daemon worker; blocked work cannot delay the core asyncio executor.

    Stopping is bounded and reports a still-running worker honestly. A stopped or
    failed instance is never restarted implicitly. No chat, actuator, consolidator,
    host adapter or shared ThinkStream is attached. Checkpoints use owned Memory only.
    """

    def __init__(
        self,
        *,
        readiness: Callable[[], str | None],
        observations: Callable[[], list],
        tick_interval: float = 1.0,
        checkpoint_store: Any = None,
        continuity_enabled: bool = False,
        restore_checkpoint_id: str | None = None,
    ):
        if not math.isfinite(tick_interval) or not 0.2 <= tick_interval <= 10:
            raise ValueError("consciousness_config_invalid")
        if type(continuity_enabled) is not bool or (
            restore_checkpoint_id is not None
            and (
                not isinstance(restore_checkpoint_id, str)
                or re.fullmatch(r"[0-9a-f]{32}", restore_checkpoint_id) is None
            )
        ):
            raise ValueError("consciousness_config_invalid")
        self._checkpoint_store = checkpoint_store
        self._continuity_enabled = continuity_enabled
        self._continuity = {
            "enabled": continuity_enabled,
            "state": "fresh" if continuity_enabled else "disabled",
            "selected_checkpoint_id": restore_checkpoint_id,
            "restored_record_id": None,
            "saved_checkpoint_id": None,
            "saved_record_id": None,
            "outstanding": False,
            "last_error_code": None,
        }
        self._checkpoint_control = None
        self._checkpoint_failed = False
        self._last_completed_checkpoint = None
        self._save_requested = False
        self._save_deadline = 0.0
        self._stop_requested = False
        self._readiness = readiness
        self._observations = observations
        self._interval = tick_interval
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._state = "starting"
        self._error: str | None = None
        self._attempted = 0
        self._completed = 0
        self._events = 0
        self._last_tick: float | None = None
        self._snapshot: dict[str, Any] = {}
        self._pending_snapshot: dict[str, Any] = {}

    def block(self, reason: str) -> None:
        """Report a launcher configuration/dependency refusal without starting work."""
        with self._lock:
            if self._thread is not None:
                raise RuntimeError("observer_already_started")
            self._state = "blocked"
            self._error = (
                reason
                if reason in {"config_invalid", "core_not_ready", "policy_not_ready"}
                else "core_not_ready"
            )
            if self._continuity_enabled:
                self._checkpoint_failed = True
                self._continuity.update(state="blocked", last_error_code=self._error)

    def start(self) -> bool:
        with self._lock:
            if self._thread is not None or self._state != "starting":
                return False
            self._thread = threading.Thread(
                target=self._run, name="consciousness-observer", daemon=True
            )
            self._thread.start()
        return True

    def _ready_reason(self) -> str | None:
        if not observer_policy_ready():
            return "policy_not_ready"
        try:
            return "core_not_ready" if self._readiness() is not None else None
        except Exception:
            return "core_not_ready"

    def _capture(self, snapshot: dict[str, Any]) -> None:
        # The worker publishes only after the whole tick succeeds.
        self._pending_snapshot = copy.deepcopy(snapshot)

    def _checkpoint_owned(self) -> bool:
        # This predicate can refuse only. Memory performs actual capability/audit checks.
        return not self._checkpoint_failed and self._ready_reason() is None

    def _checkpoint_failure(self, code: str, *, uncertain=False, blocked=False) -> None:
        allowed = {
            "busy",
            "denied",
            "audit_failed",
            "missing",
            "ambiguous",
            "invalid",
            "unavailable",
            "cancelled",
            "uncertain",
            "policy_not_ready",
            "core_not_ready",
            "tick_failed",
            "reflection_denied",
            "config_invalid",
            "stale",
        }
        with self._lock:
            self._checkpoint_failed = True
            if self._continuity["state"] == "uncertain":
                return
            self._continuity.update(
                state=(
                    "uncertain" if uncertain else ("blocked" if blocked else "failed")
                ),
                last_error_code=(
                    code if isinstance(code, str) and code in allowed else "unavailable"
                ),
            )

    def _checkpoint_exchange(self, *, save: bool, payload=None):
        """Wait only on this worker; abandonment latches even if I/O later commits."""
        # Aetherra imports
        from Aetherra.aetherra_core.memory.lifecycle_checkpoint import (
            CheckpointJobControl,
        )

        deadline = time.monotonic() + 1.0
        if save:
            deadline = min(deadline, self._save_deadline)
        control = CheckpointJobControl(
            cancelled=threading.Event(),
            deadline=deadline,
            still_owned=self._checkpoint_owned,
        )
        with self._lock:
            self._checkpoint_control = control
            self._continuity.update(
                state="saving" if save else "restoring", outstanding=True
            )
        future = None
        abandoned = False
        try:
            if not self._checkpoint_owned() or time.monotonic() >= deadline:
                raise RuntimeError("checkpoint_unavailable")
            common = {
                "owner": "consciousness:observer",
                "scope": "observer_continuity:v1",
                "checkpoint_id": (
                    payload["checkpoint_id"]
                    if save
                    else self._continuity["selected_checkpoint_id"]
                ),
                "control": control,
            }
            if save:
                future = self._checkpoint_store.submit_store_lifecycle_checkpoint(
                    payload=payload, **common
                )
            else:
                future = self._checkpoint_store.submit_load_lifecycle_checkpoint(
                    **common
                )
            while not future.done():
                if (
                    time.monotonic() >= deadline
                    or control.cancelled.is_set()
                    or (not save and self._stop.is_set())
                    or not self._checkpoint_owned()
                ):
                    control.cancelled.set()
                    abandoned = True
                    self._checkpoint_failure("uncertain", uncertain=True)
                # Memory treats result(timeout) as abandonment, not polling.
                time.sleep(0.01)
            if (
                abandoned
                or control.cancelled.is_set()
                or time.monotonic() >= deadline
                or (not save and self._stop.is_set())
                or not self._checkpoint_owned()
            ):
                control.cancelled.set()
                self._checkpoint_failure("uncertain", uncertain=True)
                return None
            receipt = future.result()
            if receipt.checkpoint_id != common["checkpoint_id"]:
                raise ValueError("invalid_checkpoint_receipt")
            if (
                not isinstance(receipt.record_id, str)
                or not receipt.record_id
                or len(receipt.record_id) > 128
            ):
                raise ValueError("invalid_checkpoint_receipt")
            return receipt, control, future
        except Exception as exc:
            code = getattr(
                exc, "code", "invalid" if isinstance(exc, ValueError) else "unavailable"
            )
            self._checkpoint_failure(
                code, uncertain=code == "uncertain", blocked=not save
            )
            return None

    def _finish_checkpoint(self) -> None:
        with self._lock:
            self._continuity["outstanding"] = False
            self._checkpoint_control = None

    def _restore_checkpoint(self, core) -> bool:
        if not self._continuity_enabled:
            return True
        if self._checkpoint_store is None:
            self._checkpoint_failure("unavailable", blocked=True)
            return False
        if self._continuity["selected_checkpoint_id"] is None:
            return True
        result = self._checkpoint_exchange(save=False)
        if result is None:
            self._finish_checkpoint()
            return False
        receipt, control, future = result
        try:
            # Aetherra imports
            from Aetherra.consciousness.checkpoint import decode_checkpoint

            state = decode_checkpoint(receipt.payload)
            if state.checkpoint_id != self._continuity["selected_checkpoint_id"]:
                raise ValueError("invalid_checkpoint_receipt")
            # Policy may perform filesystem reads; keep it off the cached-status
            # lock. Recheck deadline/cancellation after all external validation.
            accepted = control.active()
            if accepted:
                future.result()
            with self._lock:
                accepted = (
                    accepted
                    and not self._stop.is_set()
                    and not self._checkpoint_failed
                    and not control.cancelled.is_set()
                    and time.monotonic() < control.deadline
                )
                if accepted:
                    # Core does bounded pure validation and an owner-thread swap;
                    # no policy, audit, dependency callbacks or disk I/O occur here.
                    core.restore_observer_checkpoint(state)
                    self._continuity.update(
                        state="restored", restored_record_id=receipt.record_id
                    )
            if not accepted:
                control.cancelled.set()
                self._checkpoint_failure("uncertain", uncertain=True)
            return accepted
        except Exception as exc:
            self._checkpoint_failure(getattr(exc, "code", "invalid"), blocked=True)
            return False
        finally:
            self._finish_checkpoint()

    def _save_checkpoint(self) -> None:
        if (
            not self._continuity_enabled
            or not self._save_requested
            or self._checkpoint_failed
            or self._last_completed_checkpoint is None
        ):
            return
        reason = self._ready_reason()
        age = None if self._last_tick is None else time.time() - self._last_tick
        if age is None or not 0 <= age <= max(3 * self._interval, 3):
            reason = reason or "stale"
        if reason:
            self._checkpoint_failure(reason, blocked=True)
            return
        # Standard library imports
        from dataclasses import replace

        # Aetherra imports
        from Aetherra.consciousness.checkpoint import encode_checkpoint

        state = replace(self._last_completed_checkpoint, checkpoint_id=uuid.uuid4().hex)
        result = self._checkpoint_exchange(save=True, payload=encode_checkpoint(state))
        if result is None:
            self._finish_checkpoint()
            return
        receipt, control, future = result
        try:
            accepted = control.active()
            if accepted:
                future.result()
            with self._lock:
                accepted = (
                    accepted
                    and not self._checkpoint_failed
                    and not control.cancelled.is_set()
                    and time.monotonic() < control.deadline
                )
                if accepted:
                    self._continuity.update(
                        state="saved",
                        saved_checkpoint_id=receipt.checkpoint_id,
                        saved_record_id=receipt.record_id,
                        last_error_code=None,
                    )
            if not accepted:
                control.cancelled.set()
                self._checkpoint_failure("uncertain", uncertain=True)
        except Exception as exc:
            self._checkpoint_failure(getattr(exc, "code", "uncertain"), uncertain=True)
        finally:
            self._finish_checkpoint()

    def _run(self) -> None:
        try:
            reason = self._ready_reason()
            if reason:
                with self._lock:
                    self._state, self._error = "blocked", reason
                if self._continuity_enabled:
                    self._checkpoint_failure(reason, blocked=True)
                return
            # Aetherra imports
            from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
            from Aetherra.perception_bus.bus import PerceptionBus

            bus = PerceptionBus(maxlen=64)
            core = ConsciousnessCore(bus, observer_only=True)
            core.ui.register_ui_callback(self._capture)
            if not self._restore_checkpoint(core):
                with self._lock:
                    self._state, self._error = "blocked", "continuity_restore_failed"
                return
            while not self._stop.is_set():
                reason = self._ready_reason()
                if reason:
                    with self._lock:
                        self._state, self._error = "blocked", reason
                    if self._continuity_enabled:
                        self._checkpoint_failure(reason, blocked=True)
                    return
                started = time.monotonic()
                for event in self._observations()[:16]:
                    bus.publish(event)
                with self._lock:
                    self._attempted += 1
                self._pending_snapshot = {}
                core.tick()
                if self._stop.is_set():
                    # The in-flight tick is discarded. Only an earlier frozen,
                    # fully completed tick may be saved after a normal return.
                    break
                reason = self._ready_reason()
                if reason:
                    with self._lock:
                        self._state, self._error = "blocked", reason
                    if self._continuity_enabled:
                        self._checkpoint_failure(reason, blocked=True)
                    return
                frozen = (
                    core.export_observer_checkpoint("0" * 32)
                    if self._continuity_enabled
                    else None
                )
                with self._lock:
                    if self._stop.is_set():
                        break
                    self._last_completed_checkpoint = frozen
                    self._completed += 1
                    self._events = core.total_events_perceived
                    self._last_tick = time.time()
                    self._snapshot = self._pending_snapshot
                    self._state, self._error = "running", None
                self._stop.wait(
                    max(0.001, self._interval - (time.monotonic() - started))
                )
            self._save_checkpoint()
        except PermissionError:
            with self._lock:
                self._state, self._error = "blocked", "reflection_denied"
            if self._continuity_enabled:
                self._checkpoint_failure("reflection_denied", blocked=True)
        except Exception:
            with self._lock:
                self._state, self._error = "failed", "tick_failed"
            if self._continuity_enabled:
                self._checkpoint_failure("tick_failed")
        finally:
            if self._stop.is_set():
                with self._lock:
                    if self._state not in {"blocked", "failed"}:
                        self._state, self._error = "stopped", None

    async def stop(
        self, *, timeout: float = 2.0, save_checkpoint: bool = False
    ) -> None:
        deadline = time.monotonic() + max(0, min(float(timeout), 5))
        with self._lock:
            if not self._stop_requested:
                self._stop_requested = True
                self._save_requested = save_checkpoint is True
                self._save_deadline = deadline
            self._stop.set()
            if (
                self._checkpoint_control is not None
                and self._continuity["state"] != "saving"
            ):
                self._checkpoint_control.cancelled.set()
            thread = self._thread
            if thread is not None and thread.is_alive():
                self._state, self._error = "stopping", "stop_pending"
            elif self._state not in {"blocked", "failed"}:
                self._state, self._error = "stopped", None
        while thread is not None and thread.is_alive() and time.monotonic() < deadline:
            await asyncio.sleep(0.01)
        with self._lock:
            control = self._checkpoint_control
            outstanding = self._continuity["outstanding"]
        if (
            thread is not None
            and thread.is_alive()
            and control is not None
            and outstanding
        ):
            control.cancelled.set()
            self._checkpoint_failure("uncertain", uncertain=True)

    def get_runtime_status(self) -> dict[str, Any]:
        """Read only cached bounded evidence; never run core or Guardian status work."""
        with self._lock:
            alive = self._thread is not None and self._thread.is_alive()
            age = None if self._last_tick is None else time.time() - self._last_tick
            state = self._state
            if state == "running" and (
                not alive or age is None or age < 0 or age > max(3 * self._interval, 3)
            ):
                state = "stale" if alive else "failed"
            return {
                "runtime_state": state,
                "running": state == "running",
                "thread_alive": alive,
                "ticks_attempted": self._attempted,
                "ticks_completed": self._completed,
                "last_tick_at": self._last_tick,
                "last_tick_age_seconds": age,
                "tick_interval_seconds": self._interval,
                "events_processed": self._events,
                "autonomy_mode": "observe",
                "persistence_enabled": self._continuity_enabled
                and self._checkpoint_store is not None,
                "legacy_file_persistence_enabled": False,
                "continuity": dict(self._continuity),
                "qfac_persistence_enabled": False,
                "action_execution_enabled": False,
                "last_error_code": self._error,
                "think_stream_available": state == "running" and bool(self._snapshot),
            }

    def get_think_stream(self) -> dict[str, Any]:
        status = self.get_runtime_status()
        state = status["runtime_state"]
        with self._lock:
            snapshot = (
                copy.deepcopy(self._snapshot)
                if status["think_stream_available"] and not self._stop.is_set()
                else {}
            )
        return {**snapshot, "status": state, "runtime_state": state}
