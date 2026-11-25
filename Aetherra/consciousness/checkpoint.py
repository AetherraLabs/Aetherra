"""Bounded, versioned aggregate state for the governed runtime observer.

This codec grants no authority and performs no I/O. Lifecycle, events, narratives,
intentions and chat content are deliberately absent from its closed schema.
"""

from __future__ import annotations

# Standard library imports
import json
import math
import re
from dataclasses import dataclass

OWNER = "consciousness:observer"
SCOPE = "observer_continuity:v1"
MAX_BYTES = 65536
QUALIA_NAMES = ("valence", "arousal", "certainty", "curiosity", "care", "fatigue")
_HANDLE = re.compile(r"[0-9a-f]{32}\Z")
_NAME = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")


@dataclass(frozen=True)
class TrustRecord:
    name: str
    score: float
    last_event_ts: float
    history: tuple[float, ...]


@dataclass(frozen=True)
class TrustCheckpoint:
    half_life_s: float
    subsystems: tuple[TrustRecord, ...]


@dataclass(frozen=True)
class ObserverCheckpoint:
    checkpoint_id: str
    captured_at: float
    qualia: tuple[tuple[str, float], ...]
    trust: TrustCheckpoint
    schema: int = 1
    owner: str = OWNER
    scope: str = SCOPE


def _invalid() -> ValueError:
    return ValueError("checkpoint_invalid")


def _keys(value, expected) -> None:
    if (
        type(value) is not dict
        or len(value) != len(expected)
        or set(value) != set(expected)
    ):
        raise _invalid()


def _number(value, low=0.0, high=None) -> float:
    if type(value) not in (int, float):
        raise _invalid()
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise _invalid() from exc
    if (
        not math.isfinite(result)
        or result < low
        or (high is not None and result > high)
    ):
        raise _invalid()
    return result


def _decode_trust(value: dict) -> TrustCheckpoint:
    _keys(value, ("half_life_s", "subsystems"))
    half_life = _number(value["half_life_s"])
    entries = value["subsystems"]
    if half_life <= 0 or type(entries) is not list or len(entries) > 64:
        raise _invalid()
    names = set()
    records = []
    for entry in entries:
        _keys(entry, ("name", "score", "last_event_ts", "history"))
        name, history = entry["name"], entry["history"]
        if (
            type(name) is not str
            or not _NAME.fullmatch(name)
            or name in names
            or type(history) is not list
            or len(history) > 64
        ):
            raise _invalid()
        names.add(name)
        records.append(
            TrustRecord(
                name,
                _number(entry["score"], high=100),
                _number(entry["last_event_ts"]),
                tuple(_number(score, high=100) for score in history),
            )
        )
    return TrustCheckpoint(half_life, tuple(records))


def _trust_payload(state: TrustCheckpoint) -> dict:
    if (
        type(state) is not TrustCheckpoint
        or type(state.subsystems) is not tuple
        or len(state.subsystems) > 64
    ):
        raise _invalid()
    records = []
    for entry in state.subsystems:
        if (
            type(entry) is not TrustRecord
            or type(entry.history) is not tuple
            or len(entry.history) > 64
        ):
            raise _invalid()
        records.append(
            {
                "name": entry.name,
                "score": entry.score,
                "last_event_ts": entry.last_event_ts,
                "history": list(entry.history),
            }
        )
    return {"half_life_s": state.half_life_s, "subsystems": records}


def validate_trust_checkpoint(state: TrustCheckpoint) -> TrustCheckpoint:
    """Detach and validate before applying any trust state."""
    return _decode_trust(_trust_payload(state))


def decode_checkpoint(payload: dict) -> ObserverCheckpoint:
    """Validate the closed schema before constructing immutable detached state."""
    _keys(
        payload,
        ("schema", "checkpoint_id", "owner", "scope", "captured_at", "qualia", "trust"),
    )
    handle = payload["checkpoint_id"]
    if (
        type(payload["schema"]) is not int
        or payload["schema"] != 1
        or type(handle) is not str
        or not _HANDLE.fullmatch(handle)
        or payload["owner"] != OWNER
        or payload["scope"] != SCOPE
    ):
        raise _invalid()
    _keys(payload["qualia"], QUALIA_NAMES)
    qualia = tuple(
        (name, _number(payload["qualia"][name], -1 if name == "valence" else 0, 1))
        for name in QUALIA_NAMES
    )
    state = ObserverCheckpoint(
        handle, _number(payload["captured_at"]), qualia, _decode_trust(payload["trust"])
    )
    # The schema bounds the object before serialization, including arrays/text.
    if len(_serialize(_payload(state))) > MAX_BYTES:
        raise _invalid()
    return state


def _payload(state: ObserverCheckpoint) -> dict:
    if (
        type(state) is not ObserverCheckpoint
        or type(state.qualia) is not tuple
        or len(state.qualia) != 6
        or any(type(pair) is not tuple or len(pair) != 2 for pair in state.qualia)
    ):
        raise _invalid()
    try:
        qualia = dict(state.qualia)
    except (ValueError, TypeError) as exc:
        raise _invalid() from exc
    return {
        "schema": state.schema,
        "checkpoint_id": state.checkpoint_id,
        "owner": state.owner,
        "scope": state.scope,
        "captured_at": state.captured_at,
        "qualia": qualia,
        "trust": _trust_payload(state.trust),
    }


def encode_checkpoint(state: ObserverCheckpoint) -> dict:
    """Return detached, validated JSON-compatible data."""
    return _payload(decode_checkpoint(_payload(state)))


def _serialize(payload: dict) -> bytes:
    try:
        return json.dumps(
            payload, allow_nan=False, ensure_ascii=True, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise _invalid() from exc


def dump_checkpoint_json(state: ObserverCheckpoint) -> bytes:
    return _serialize(encode_checkpoint(state))


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _invalid()
        result[key] = value
    return result


def load_checkpoint_json(data: bytes | str) -> ObserverCheckpoint:
    """Reject oversized/deep/duplicate JSON before it can become trusted state."""
    if type(data) not in (bytes, str) or len(data) > MAX_BYTES:
        raise _invalid()
    try:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        if len(raw) > MAX_BYTES:
            raise _invalid()
        text = raw.decode("utf-8")
        depth, quoted, escaped = 0, False, False
        for char in text:
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in "[{":
                depth += 1
                if depth > 8:
                    raise _invalid()
            elif char in "]}":
                depth -= 1
        return decode_checkpoint(
            json.loads(
                text,
                object_pairs_hook=_unique_keys,
                parse_constant=lambda _: (_ for _ in ()).throw(_invalid()),
            )
        )
    except (UnicodeError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise _invalid() from exc
