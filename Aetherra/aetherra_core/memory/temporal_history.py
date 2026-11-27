"""Closed, canonical values for Memory's append-only Temporal observation history."""

from __future__ import annotations

# Standard library imports
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, fields

# Local imports
from .lifecycle_checkpoint import CheckpointError

OWNER = "consciousness:temporal"
SCOPE = "temporal_history:v1"
MAX_INT = 2**63 - 1
MAX_COUNT = 2**31 - 1
MAX_EVENT_BYTES = 4096
MAX_RECORD_BYTES = MAX_EVENT_BYTES + 1024
MAX_REQUEST_BYTES = 3 * MAX_EVENT_BYTES + 1024
_ID = re.compile(r"[0-9a-f]{32}")
_SHA = re.compile(r"[0-9a-f]{64}")


def require(condition, code="invalid"):
    if not condition:
        raise CheckpointError(code)


def integer(value, low=0, high=MAX_INT):
    return type(value) is int and low <= value <= high


def _hex(value, pattern=_ID):
    return type(value) is str and pattern.fullmatch(value) is not None


def _time(value):
    return type(value) in (int, float) and 0 <= value <= sys.float_info.max


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


class _Value:
    __slots__ = ()

    def to_bytes(self):
        return canonical(asdict(self))

    @classmethod
    def from_bytes(cls, raw):
        require(type(raw) is bytes and len(raw) <= _LIMITS.get(cls, 4096))
        try:
            value = _build(cls, json.loads(raw), wire=True)
            # Includes duplicate keys, extra whitespace and alternate numeric spellings.
            require(value.to_bytes() == raw)
            return value
        except (UnicodeError, ValueError, TypeError, RecursionError, OverflowError):
            raise CheckpointError("invalid") from None


@dataclass(frozen=True, slots=True)
class HistoryKey(_Value):
    owner: str
    scope: str
    history_id: str

    def __post_init__(self):
        require(type(self.owner) is str and self.owner == OWNER)
        require(type(self.scope) is str and self.scope == SCOPE)
        require(_hex(self.history_id))


@dataclass(frozen=True, slots=True)
class HistoryToken(_Value):
    key: HistoryKey
    writer_epoch: int

    def __post_init__(self):
        require(type(self.key) is HistoryKey and integer(self.writer_epoch, 1))


@dataclass(frozen=True, slots=True)
class HistoryHead(_Value):
    ordinal: int
    record_id: str | None
    digest: str | None

    def __post_init__(self):
        require(integer(self.ordinal))
        if self.ordinal == 0:
            require(self.record_id is None and self.digest is None)
        else:
            require(_hex(self.record_id) and _hex(self.digest, _SHA))


EMPTY = HistoryHead(0, None, None)


@dataclass(frozen=True, slots=True)
class TemporalSource(_Value):
    session_id: str
    session_started_at_unix_s: float
    sequence: int
    observed_at_unix_s: float
    observed_uptime_s: float
    working_memory_count: int
    active_intention_count: int
    focus_count: int

    def __post_init__(self):
        require(_hex(self.session_id) and integer(self.sequence, 1))
        require(
            all(
                _time(v)
                for v in (
                    self.session_started_at_unix_s,
                    self.observed_at_unix_s,
                    self.observed_uptime_s,
                )
            )
        )
        require(all(integer(v, 0, MAX_COUNT) for v in self.counts))

    @property
    def counts(self):
        return self.working_memory_count, self.active_intention_count, self.focus_count


_REASONS = {
    "session_start": ("created", "resumed"),
    "observation": (None,),
    "gap": ("restart", "source_unavailable", "source_changed"),
    "session_end": ("orderly_stop",),
}


@dataclass(frozen=True, slots=True)
class TemporalEvent(_Value):
    record_id: str
    kind: str
    source: TemporalSource
    captured_at_unix_s: float
    reason: str | None = None

    def __post_init__(self):
        require(_hex(self.record_id) and type(self.source) is TemporalSource)
        require(
            type(self.kind) is str and len(self.kind) <= 16 and self.kind in _REASONS
        )
        require(self.reason is None or type(self.reason) is str)
        require(self.reason in _REASONS[self.kind] and _time(self.captured_at_unix_s))
        require(len(self.to_bytes()) <= MAX_EVENT_BYTES)


@dataclass(frozen=True, slots=True)
class AppendRequest(_Value):
    token: HistoryToken
    expected_head: HistoryHead
    operation_id: str
    events: tuple[TemporalEvent, ...]

    def __post_init__(self):
        require(
            type(self.token) is HistoryToken and type(self.expected_head) is HistoryHead
        )
        require(_hex(self.operation_id))
        require(type(self.events) is tuple and 1 <= len(self.events) <= 3)
        require(all(type(event) is TemporalEvent for event in self.events))
        require(len({event.record_id for event in self.events}) == len(self.events))
        require(self.expected_head.ordinal <= MAX_INT - len(self.events))

    def digest(self):
        return sha256(self.to_bytes())


@dataclass(frozen=True, slots=True)
class HistoryRecord(_Value):
    schema: int
    history_id: str
    ordinal: int
    writer_epoch: int
    operation_id: str
    prior_digest: str | None
    event: TemporalEvent
    digest: str

    def __post_init__(self):
        require(integer(self.schema, 1, 1) and _hex(self.history_id))
        require(integer(self.ordinal, 1) and integer(self.writer_epoch, 1))
        require(_hex(self.operation_id) and type(self.event) is TemporalEvent)
        require(
            self.prior_digest is None
            if self.ordinal == 1
            else _hex(self.prior_digest, _SHA)
        )
        require(_hex(self.digest, _SHA))
        content = asdict(self)
        del content["digest"]
        require(sha256(canonical(content)) == self.digest)

    @classmethod
    def build(cls, request, prior, event):
        content = {
            "schema": 1,
            "history_id": request.token.key.history_id,
            "ordinal": prior.ordinal + 1,
            "writer_epoch": request.token.writer_epoch,
            "operation_id": request.operation_id,
            "prior_digest": prior.digest,
            "event": event,
        }
        digest = sha256(canonical({**content, "event": asdict(event)}))
        return cls(**content, digest=digest)

    @property
    def head(self):
        return HistoryHead(self.ordinal, self.event.record_id, self.digest)


@dataclass(frozen=True, slots=True)
class HistorySelection(_Value):
    token: HistoryToken
    head: HistoryHead

    def __post_init__(self):
        require(type(self.token) is HistoryToken and type(self.head) is HistoryHead)


def _records(value, minimum, maximum):
    require(type(value) is tuple and minimum <= len(value) <= maximum)
    require(all(type(record) is HistoryRecord for record in value))
    for left, right in zip(value, value[1:], strict=False):
        require(
            left.ordinal + 1 == right.ordinal
            and left.digest == right.prior_digest
            and left.history_id == right.history_id
        )


def valid_audit_id(value):
    return (
        type(value) is str
        and 0 < len(value) <= 256
        and bool(value.strip())
        and len(value.encode("utf-8", errors="surrogatepass")) <= 256
        and all(ord(ch) < 0xD800 or ord(ch) > 0xDFFF for ch in value)
    )


@dataclass(frozen=True, slots=True)
class AppendReceipt(_Value):
    request_digest: str
    records: tuple[HistoryRecord, ...]
    head: HistoryHead
    audit_id: str

    def __post_init__(self):
        require(_hex(self.request_digest, _SHA) and valid_audit_id(self.audit_id))
        _records(self.records, 1, 3)
        require(type(self.head) is HistoryHead and self.head == self.records[-1].head)
        first = self.records[0]
        require(
            all(
                r.writer_epoch == first.writer_epoch
                and r.operation_id == first.operation_id
                for r in self.records
            )
        )


@dataclass(frozen=True, slots=True)
class HistoryPage(_Value):
    selected_head: HistoryHead
    records: tuple[HistoryRecord, ...]
    next_ordinal: int

    def __post_init__(self):
        require(type(self.selected_head) is HistoryHead)
        require(integer(self.next_ordinal, 0, self.selected_head.ordinal))
        _records(self.records, 0, 64)
        if self.records:
            require(self.records[-1].ordinal == self.next_ordinal)
            if self.next_ordinal == self.selected_head.ordinal:
                require(self.records[-1].head == self.selected_head)


@dataclass(frozen=True, slots=True)
class AppendInspection(_Value):
    status: str
    receipt: AppendReceipt | None = None

    def __post_init__(self):
        require(type(self.status) is str)
        if self.status == "not_committed":
            require(self.receipt is None)
        else:
            require(self.status in ("committed_current", "committed_superseded"))
            require(type(self.receipt) is AppendReceipt)


def validate_read(after_ordinal, limit, selected_head):
    require(type(selected_head) is HistoryHead)
    require(integer(after_ordinal, 0, selected_head.ordinal) and integer(limit, 1, 64))


# Decode only the declared nested objects and bounded arrays. Scalar constructors
# check sizes and types before the admitted copy is serialized or handed off.
_CHILDREN = {
    HistoryKey: {},
    HistoryHead: {},
    TemporalSource: {},
    HistoryToken: {"key": HistoryKey},
    TemporalEvent: {"source": TemporalSource},
    AppendRequest: {
        "token": HistoryToken,
        "expected_head": HistoryHead,
        "events": (TemporalEvent, 3),
    },
    HistoryRecord: {"event": TemporalEvent},
    HistorySelection: {"token": HistoryToken, "head": HistoryHead},
    AppendReceipt: {"records": (HistoryRecord, 3), "head": HistoryHead},
    HistoryPage: {"records": (HistoryRecord, 64), "selected_head": HistoryHead},
    AppendInspection: {"receipt": AppendReceipt},
}
_LIMITS = {
    TemporalEvent: MAX_EVENT_BYTES,
    AppendRequest: MAX_REQUEST_BYTES,
    HistoryRecord: MAX_RECORD_BYTES,
    AppendReceipt: MAX_RECORD_BYTES * 3 + 2048,
    AppendInspection: MAX_RECORD_BYTES * 3 + 3072,
    HistoryPage: MAX_RECORD_BYTES * 64 + 1024,
}


def _build(cls, value, *, wire):
    names = fields(cls)
    if wire:
        require(type(value) is dict and len(value) == len(names))
        require(all(f.name in value for f in names))
        args = value.copy()
    else:
        require(type(value) is cls)
        args = {f.name: getattr(value, f.name) for f in names}
    for field, child in _CHILDREN[cls].items():
        item = args[field]
        if type(child) is tuple:
            element, limit = child
            require(type(item) is (list if wire else tuple) and len(item) <= limit)
            args[field] = tuple(_build(element, entry, wire=wire) for entry in item)
        elif not (cls is AppendInspection and item is None):
            args[field] = _build(child, item, wire=wire)
    return cls(**args)


def freeze(value, expected_type):
    """Detach and revalidate every admitted field, including already-frozen values."""
    require(expected_type in _CHILDREN)
    try:
        return _build(expected_type, value, wire=False)
    except (AttributeError, TypeError, ValueError, OverflowError):
        raise CheckpointError("invalid") from None
