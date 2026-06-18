"""Guardian operating-mode state and controls."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from .models import GuardianMode
from .paths import guardian_state_dir
from .state import append_jsonl, read_jsonl


def _mode_log_path():
    return guardian_state_dir() / "mode.jsonl"


def current_guardian_mode() -> GuardianMode:
    """Return the active Guardian mode, with environment config taking precedence."""

    env_mode = _parse_mode(os.getenv("AETHERRA_GUARDIAN_MODE"))
    if env_mode is not None:
        return env_mode

    persisted = guardian_mode_status()
    persisted_mode = _parse_mode(persisted.get("mode"))
    return persisted_mode or GuardianMode.ENFORCING


def set_guardian_mode(
    mode: GuardianMode | str,
    *,
    reason: str,
    changed_by: str = "guardian",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist and audit a Guardian operating-mode change."""

    target_mode = _coerce_mode(mode)
    clean_reason = str(reason or "").strip()
    if not clean_reason:
        raise ValueError("mode changes require a non-empty reason")
    clean_actor = str(changed_by or "guardian").strip() or "guardian"

    previous_mode = current_guardian_mode()
    record = {
        "event": "mode_changed",
        "previous_mode": previous_mode.value,
        "mode": target_mode.value,
        "reason": clean_reason,
        "changed_by": clean_actor,
        "changed_at": _now(),
        "metadata": metadata or {},
        "env_override_active": _parse_mode(os.getenv("AETHERRA_GUARDIAN_MODE")) is not None,
    }
    append_jsonl(_mode_log_path(), record)

    from .audit import append_guardian_mode_change

    record["audit_id"] = append_guardian_mode_change(record)
    return record


def guardian_mode_events() -> list[dict[str, Any]]:
    """Return Guardian mode-control event history."""

    return read_jsonl(_mode_log_path())


def guardian_mode_status() -> dict[str, Any]:
    """Return the latest persisted Guardian mode state."""

    events = [event for event in guardian_mode_events() if event.get("event") == "mode_changed"]
    env_mode = _parse_mode(os.getenv("AETHERRA_GUARDIAN_MODE"))
    if not events:
        return {
            "mode": env_mode.value if env_mode is not None else GuardianMode.ENFORCING.value,
            "state": "env_override" if env_mode is not None else "default",
            "env_override_active": env_mode is not None,
        }
    latest = events[-1]
    active_mode = env_mode.value if env_mode is not None else latest.get("mode")
    return {
        **latest,
        "mode": active_mode,
        "persisted_mode": latest.get("mode"),
        "state": "env_override" if env_mode is not None else "persisted",
        "env_override_active": env_mode is not None,
    }


def _coerce_mode(mode: GuardianMode | str) -> GuardianMode:
    parsed = _parse_mode(mode.value if isinstance(mode, GuardianMode) else mode)
    if parsed is None:
        allowed = ", ".join(member.value for member in GuardianMode)
        raise ValueError(f"invalid Guardian mode: expected one of {allowed}")
    return parsed


def _parse_mode(raw: str | None) -> GuardianMode | None:
    value = str(raw or "").strip().lower()
    if not value:
        return None
    try:
        return GuardianMode(value)
    except ValueError:
        return None


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
