"""Owned, bounded observe-only lifecycle for the normal runtime's ConsciousnessCore."""

from __future__ import annotations

# Standard library imports
import asyncio
import copy
import math
import os
import threading
import time
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
    host adapter, shared ThinkStream, or persistent continuity store is attached.
    """

    def __init__(
        self,
        *,
        readiness: Callable[[], str | None],
        observations: Callable[[], list],
        tick_interval: float = 1.0,
    ):
        if not math.isfinite(tick_interval) or not 0.2 <= tick_interval <= 10:
            raise ValueError("consciousness_config_invalid")
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

    def _run(self) -> None:
        try:
            reason = self._ready_reason()
            if reason:
                with self._lock:
                    self._state, self._error = "blocked", reason
                return
            # Aetherra imports
            from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
            from Aetherra.perception_bus.bus import PerceptionBus

            bus = PerceptionBus(maxlen=64)
            core = ConsciousnessCore(bus, observer_only=True)
            core.ui.register_ui_callback(self._capture)
            while not self._stop.is_set():
                reason = self._ready_reason()
                if reason:
                    with self._lock:
                        self._state, self._error = "blocked", reason
                    return
                started = time.monotonic()
                for event in self._observations()[:16]:
                    bus.publish(event)
                with self._lock:
                    self._attempted += 1
                self._pending_snapshot = {}
                core.tick()
                if self._stop.is_set():
                    return
                reason = self._ready_reason()
                if reason:
                    with self._lock:
                        self._state, self._error = "blocked", reason
                    return
                with self._lock:
                    if self._stop.is_set():
                        return
                    self._completed += 1
                    self._events = core.total_events_perceived
                    self._last_tick = time.time()
                    self._snapshot = self._pending_snapshot
                    self._state, self._error = "running", None
                self._stop.wait(
                    max(0.001, self._interval - (time.monotonic() - started))
                )
        except PermissionError:
            with self._lock:
                self._state, self._error = "blocked", "reflection_denied"
        except Exception:
            with self._lock:
                self._state, self._error = "failed", "tick_failed"
        finally:
            if self._stop.is_set():
                with self._lock:
                    self._state, self._error = "stopped", None

    async def stop(self, *, timeout: float = 2.0) -> None:
        self._stop.set()
        with self._lock:
            thread = self._thread
            if thread is not None and thread.is_alive():
                self._state, self._error = "stopping", "stop_pending"
            elif self._state not in {"blocked", "failed"}:
                self._state, self._error = "stopped", None
        deadline = time.monotonic() + max(0, min(float(timeout), 5))
        while thread is not None and thread.is_alive() and time.monotonic() < deadline:
            await asyncio.sleep(0.01)

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
                "persistence_enabled": False,
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
