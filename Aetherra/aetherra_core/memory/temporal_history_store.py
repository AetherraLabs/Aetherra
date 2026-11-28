"""Bounded Temporal history operations on an already-open Memory transaction.

The owning worker chooses BEGIN mode and handles commit, rollback and cancellation.
All archive access is by indexed history/ordinal, operation, record or session ID.
"""

from __future__ import annotations

# Standard library imports
import sqlite3
from functools import wraps

# Local imports
from . import temporal_history as h
from .lifecycle_checkpoint import CheckpointError

_HEADS = "temporal_history_heads"
_RECORDS = "temporal_history_records"
_RECEIPTS = "temporal_history_receipts"
_SCHEMA = {
    _HEADS: f"""CREATE TABLE {_HEADS} (
        history_id TEXT PRIMARY KEY, writer_epoch INTEGER NOT NULL CHECK(writer_epoch>0),
        ordinal INTEGER NOT NULL CHECK(ordinal>=0), record_id TEXT, digest TEXT,
        seal TEXT NOT NULL) STRICT, WITHOUT ROWID""",
    _RECORDS: f"""CREATE TABLE {_RECORDS} (
        history_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal>0),
        record_id TEXT NOT NULL, operation_id TEXT NOT NULL, session_id TEXT NOT NULL,
        envelope BLOB NOT NULL, PRIMARY KEY(history_id,ordinal),
        UNIQUE(history_id,record_id)) STRICT, WITHOUT ROWID""",
    _RECEIPTS: f"""CREATE TABLE {_RECEIPTS} (
        history_id TEXT NOT NULL, operation_id TEXT NOT NULL,
        last_ordinal INTEGER NOT NULL CHECK(last_ordinal>0), receipt BLOB NOT NULL,
        seal TEXT NOT NULL, PRIMARY KEY(history_id,operation_id),
        UNIQUE(history_id,last_ordinal)) STRICT, WITHOUT ROWID""",
    "temporal_history_records_op": f"CREATE INDEX temporal_history_records_op ON {_RECORDS}(history_id,operation_id,ordinal)",
    "temporal_history_records_session": f"CREATE INDEX temporal_history_records_session ON {_RECORDS}(history_id,session_id,ordinal)",
}


# A legal row (including a complete three-record receipt) fits within this limit.
# SQLite can locate a STRICT BLOB's byte length from its header. TEXT byte-length
# conversions, index comparisons and result-row construction also need an engine
# limit so independently damaged storage can't trigger unbounded allocations.
_SQLITE_VALUE_LIMIT = 64 * 1024


def _bounded_sqlite(operation):
    @wraps(operation)
    def guarded(db, *args, **kwargs):
        category = sqlite3.SQLITE_LIMIT_LENGTH
        prior = db.getlimit(category)
        db.setlimit(category, min(prior, _SQLITE_VALUE_LIMIT))
        try:
            return operation(db, *args, **kwargs)
        except sqlite3.DataError:
            raise CheckpointError("corrupt") from None
        finally:
            db.setlimit(category, prior)

    return guarded


def _check(condition):
    h.require(condition, "corrupt")


def _stored(constructor, *args):
    try:
        return constructor(*args)
    except CheckpointError:
        raise CheckpointError("corrupt") from None


def _schema(db, *, create=False):
    h.require(db.in_transaction, "invalid")
    rows = db.execute(
        """SELECT CASE WHEN length(CAST(name AS BLOB)) <= 64 THEN name END,
                  CASE WHEN length(CAST(sql AS BLOB)) <= 2048 THEN sql END
             FROM main.sqlite_schema
             WHERE (tbl_name IN (?,?,?) OR name IN (?,?,?,?,?)) AND sql IS NOT NULL LIMIT 6""",
        (_HEADS, _RECORDS, _RECEIPTS, *_SCHEMA),
    ).fetchall()
    if not rows:
        h.require(create, "missing")
        for ddl in _SCHEMA.values():
            db.execute(ddl)
    else:
        _check(len(rows) == len(_SCHEMA) and dict(rows) == _SCHEMA)


def _head_seal(history_id, epoch, head):
    return h.sha256(
        h.canonical([history_id, epoch, head.ordinal, head.record_id, head.digest])
    )


def _transition(db, request, previous):
    """Validate a proposed or restored batch against its immediately preceding record."""
    events = request.events
    kinds = tuple((e.kind, e.reason) for e in events)
    source = events[-1].source
    h.require(all(e.source.to_bytes() == source.to_bytes() for e in events[:-1]))
    epoch = request.token.writer_epoch
    observation = ("observation", None)
    if previous is None:
        reason = "created" if epoch == 1 else "resumed"
        h.require(kinds == (("session_start", reason), observation))
        return
    h.require(epoch >= previous.writer_epoch)
    prior_source = previous.event.source
    same_source = source.session_id == prior_source.session_id
    if epoch > previous.writer_epoch:
        h.require(
            kinds == (("session_start", "resumed"), ("gap", "restart"), observation)
        )
    else:
        h.require(previous.event.kind != "session_end")
        if kinds == (("session_end", "orderly_stop"),):
            h.require(source.to_bytes() == prior_source.to_bytes())
            return
        gap_reason = "source_unavailable" if same_source else "source_changed"
        if kinds == (observation,):
            h.require(same_source)
        else:
            h.require(kinds == (("gap", gap_reason), observation))
    if same_source:
        h.require(
            source.session_started_at_unix_s == prior_source.session_started_at_unix_s
        )
        h.require(source.sequence > prior_source.sequence)
        h.require(source.observed_uptime_s >= prior_source.observed_uptime_s)
    else:
        used = db.execute(
            "SELECT 1 FROM main.temporal_history_records WHERE history_id=? AND session_id=? AND ordinal<=? LIMIT 1",
            (request.token.key.history_id, source.session_id, previous.ordinal),
        ).fetchone()
        h.require(used is None)
    if kinds == (observation,):
        h.require(source.counts != prior_source.counts, "unchanged")


_RECEIPT_LIMIT = 3 * h.MAX_RECORD_BYTES + 2048


class _History:
    """One transaction's verified head and memoized bounded point reads."""

    def __init__(self, db, key, epoch, head):
        self.db = db
        self.key = key
        self.history_id = key.history_id
        self.epoch = epoch
        self.head = head
        self.records = {}
        self.receipts = {}

    def record(self, ordinal):
        if ordinal not in self.records:
            row = self.db.execute(
                """SELECT ordinal,
                       CASE WHEN length(CAST(record_id AS BLOB)) <= 32 THEN record_id END,
                       CASE WHEN length(CAST(operation_id AS BLOB)) <= 32 THEN operation_id END,
                       CASE WHEN length(CAST(session_id AS BLOB)) <= 32 THEN session_id END,
                       CASE WHEN length(envelope) <= ? THEN envelope END
                   FROM main.temporal_history_records WHERE history_id=? AND ordinal=?""",
                (h.MAX_RECORD_BYTES, self.history_id, ordinal),
            ).fetchone()
            _check(row is not None and 1 <= ordinal <= self.head.ordinal)
            record = _stored(h.HistoryRecord.from_bytes, row[4])
            _check(
                record.ordinal == ordinal
                and record.history_id == self.history_id
                and record.writer_epoch <= self.epoch
                and (
                    record.ordinal,
                    record.event.record_id,
                    record.operation_id,
                    record.event.source.session_id,
                )
                == tuple(row[:4])
            )
            self.records[ordinal] = record
        return self.records[ordinal]

    def receipt(self, op):
        if op in self.receipts:
            return self.receipts[op]
        row = self.db.execute(
            """SELECT last_ordinal, CASE WHEN length(receipt) <= ? THEN receipt END,
                      CASE WHEN length(CAST(seal AS BLOB)) <= 64 THEN seal END
               FROM main.temporal_history_receipts WHERE history_id=? AND operation_id=?""",
            (_RECEIPT_LIMIT, self.history_id, op),
        ).fetchone()
        members = self.db.execute(
            "SELECT ordinal FROM main.temporal_history_records WHERE history_id=? AND operation_id=? ORDER BY ordinal LIMIT 4",
            (self.history_id, op),
        ).fetchall()
        if row is None:
            _check(not members)
            return None
        end, raw, seal = row
        _check(type(raw) is bytes and h.sha256(raw) == seal)
        receipt = _stored(h.AppendReceipt.from_bytes, raw)
        _check(receipt.head.ordinal == end <= self.head.ordinal)
        _check(
            [member[0] for member in members] == [r.ordinal for r in receipt.records]
        )
        for entry in receipt.records:
            _check(entry.to_bytes() == self.record(entry.ordinal).to_bytes())
        first = receipt.records[0]
        _check(first.operation_id == op)
        previous = self.record(first.ordinal - 1) if first.ordinal > 1 else None
        prior = previous.head if previous else h.EMPTY
        _check(first.prior_digest == prior.digest)
        token = h.HistoryToken(self.key, first.writer_epoch)
        request = _stored(
            h.AppendRequest, token, prior, op, tuple(r.event for r in receipt.records)
        )
        _check(request.digest() == receipt.request_digest)
        _stored(_transition, self.db, request, previous)
        self.receipts[op] = receipt
        return receipt

    def select(self, head, *, missing_code="conflict"):
        if head.ordinal == 0:
            return None
        h.require(head.ordinal <= self.head.ordinal, missing_code)
        record = self.record(head.ordinal)
        receipt = self.receipt(record.operation_id)
        _check(receipt is not None)
        h.require(record.head == head and receipt.head == head, "conflict")
        return record

    def evidence(self, request, *, appending=False):
        """Classify all indexed evidence; never infer rollback from a missing receipt."""
        original = self.receipt(request.operation_id)
        if original is not None:
            h.require(original.request_digest == request.digest(), "conflict")
            status = (
                "committed_current"
                if original.head == self.head
                else "committed_superseded"
            )
            return h.AppendInspection(status, original)

        if appending:
            h.require(request.expected_head == self.head, "conflict")
        else:
            # Even a negative recovery needs an exact, durable predecessor.
            self.select(request.expected_head, missing_code="corrupt")

        start = request.expected_head.ordinal + 1
        occupied = set(
            range(start, min(start + len(request.events), self.head.ordinal + 1))
        )
        for event in request.events:
            row = self.db.execute(
                "SELECT ordinal FROM main.temporal_history_records WHERE history_id=? AND record_id=?",
                (self.history_id, event.record_id),
            ).fetchone()
            if row is not None:
                occupied.add(row[0])
        for ordinal in occupied:
            record = self.record(ordinal)
            _check(self.receipt(record.operation_id) is not None)
        h.require(not occupied, "conflict")
        return h.AppendInspection("not_committed")


def _load(db, key, expected_epoch=None):
    history_id = key.history_id
    row = db.execute(
        """SELECT writer_epoch, ordinal,
                  CASE WHEN length(CAST(record_id AS BLOB)) <= 32 THEN record_id END,
                  CASE WHEN length(CAST(digest AS BLOB)) <= 64 THEN digest END,
                  CASE WHEN length(CAST(seal AS BLOB)) <= 64 THEN seal END,
                  record_id IS NULL, digest IS NULL
           FROM main.temporal_history_heads WHERE history_id=?""",
        (history_id,),
    ).fetchone()
    record_tip, receipt_tip = db.execute(
        """SELECT COALESCE((SELECT ordinal FROM main.temporal_history_records
                             WHERE history_id=? ORDER BY ordinal DESC LIMIT 1), 0),
                  COALESCE((SELECT last_ordinal FROM main.temporal_history_receipts
                             WHERE history_id=? ORDER BY last_ordinal DESC LIMIT 1), 0)""",
        (history_id, history_id),
    ).fetchone()
    if row is None:
        _check(record_tip == receipt_tip == 0)
        return None
    epoch, ordinal, record_id, digest, seal, id_null, digest_null = row
    _check(h.integer(epoch, 1) and ordinal == record_tip == receipt_tip)
    _check(
        (record_id is None) == bool(id_null) and (digest is None) == bool(digest_null)
    )
    head = _stored(h.HistoryHead, ordinal, record_id, digest)
    _check(_head_seal(history_id, epoch, head) == seal)
    if expected_epoch is not None:
        h.require(expected_epoch == epoch, "writer_fenced")
    history = _History(db, key, epoch, head)
    _stored(history.select, head)
    return history


@_bounded_sqlite
def acquire(db, key, start_mode):
    h.require(
        type(key) is h.HistoryKey
        and type(start_mode) is str
        and start_mode in ("create", "resume")
    )
    _schema(db, create=start_mode == "create")
    history = _load(db, key)
    if start_mode == "create":
        h.require(history is None, "conflict")
        epoch, head = 1, h.EMPTY
        db.execute(
            "INSERT INTO main.temporal_history_heads VALUES(?,?,0,NULL,NULL,?)",
            (key.history_id, epoch, _head_seal(key.history_id, epoch, head)),
        )
    else:
        h.require(history is not None, "missing")
        h.require(history.epoch < h.MAX_INT, "conflict")
        epoch, head = history.epoch + 1, history.head
        db.execute(
            "UPDATE main.temporal_history_heads SET writer_epoch=?,seal=? WHERE history_id=?",
            (epoch, _head_seal(key.history_id, epoch, head), key.history_id),
        )
    return h.HistorySelection(h.HistoryToken(key, epoch), head)


def _current(db, token):
    _schema(db)
    history = _load(db, token.key, token.writer_epoch)
    h.require(history is not None, "missing")
    return history


@_bounded_sqlite
def append(db, request, audit_id):
    h.require(type(request) is h.AppendRequest and h.valid_audit_id(audit_id))
    history = _current(db, request.token)
    outcome = history.evidence(request, appending=True)
    if outcome.receipt is not None:
        return outcome.receipt
    prior = history.head
    _transition(db, request, history.record(prior.ordinal) if prior.ordinal else None)
    records = []
    for event in request.events:
        record = h.HistoryRecord.build(request, prior, event)
        db.execute(
            "INSERT INTO main.temporal_history_records VALUES(?,?,?,?,?,?)",
            (
                history.history_id,
                record.ordinal,
                event.record_id,
                request.operation_id,
                event.source.session_id,
                record.to_bytes(),
            ),
        )
        records.append(record)
        prior = record.head
    receipt = h.AppendReceipt(request.digest(), tuple(records), prior, audit_id)
    raw = receipt.to_bytes()
    db.execute(
        "INSERT INTO main.temporal_history_receipts VALUES(?,?,?,?,?)",
        (history.history_id, request.operation_id, prior.ordinal, raw, h.sha256(raw)),
    )
    db.execute(
        "UPDATE main.temporal_history_heads SET ordinal=?,record_id=?,digest=?,seal=? WHERE history_id=?",
        (
            prior.ordinal,
            prior.record_id,
            prior.digest,
            _head_seal(history.history_id, history.epoch, prior),
            history.history_id,
        ),
    )
    return receipt


@_bounded_sqlite
def read(db, token, selected_head, after_ordinal, limit):
    h.validate_read(after_ordinal, limit, selected_head)
    history = _current(db, token)
    history.select(selected_head)
    end = min(selected_head.ordinal, after_ordinal + limit)
    prior_digest = history.record(after_ordinal).digest if after_ordinal else None
    records = []
    for ordinal in range(after_ordinal + 1, end + 1):
        record = history.record(ordinal)
        _check(
            history.receipt(record.operation_id) is not None
            and prior_digest == record.prior_digest
        )
        records.append(record)
        prior_digest = record.digest
    if end < history.head.ordinal:
        _check(history.record(end + 1).prior_digest == prior_digest)
    return h.HistoryPage(selected_head, tuple(records), end)


@_bounded_sqlite
def inspect(db, token, request):
    h.require(type(request) is h.AppendRequest and type(token) is h.HistoryToken)
    history = _current(db, token)
    h.require(
        request.token.key == token.key
        and request.token.writer_epoch < token.writer_epoch
    )
    return history.evidence(request)
