"""Tests for the signed, hash-chained Security JSONL ledger."""

from __future__ import annotations

# Standard library imports
import contextlib
import json
import multiprocessing
import os
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

# Third party imports
import pytest

# Aetherra imports
from Aetherra.security import audit_ledger
from Aetherra.security.audit_ledger import (
    AuditIntegrityError,
    AuditLedgerError,
    SecurityAuditLedger,
)


def _records(path):
    return [json.loads(line) for line in path.read_text("utf-8").splitlines()]


def test_signed_chain_detects_record_tampering(tmp_path):
    path = tmp_path / "audit.jsonl"
    ledger = SecurityAuditLedger(path)
    ledger.append(actor="security", event_type="first")
    ledger.append(actor="security", event_type="second")
    assert ledger.verify_integrity() is True

    records = _records(path)
    records[0]["event_type"] = "tampered"
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")

    assert ledger.verify_integrity() is False
    with pytest.raises(AuditIntegrityError):
        ledger.append(actor="security", event_type="third")


def test_chain_detects_deletion_and_reordering(tmp_path):
    path = tmp_path / "audit.jsonl"
    ledger = SecurityAuditLedger(path)
    for index in range(3):
        ledger.append(actor="security", event_type=f"event-{index}")
    records = _records(path)

    path.write_text("\n".join(json.dumps(record) for record in records[1:]) + "\n")
    assert ledger.verify_integrity() is False

    path.write_text(
        "\n".join(json.dumps(record) for record in reversed(records)) + "\n"
    )
    assert ledger.verify_integrity() is False


def test_legacy_prefix_is_anchored_when_new_record_is_appended(tmp_path):
    path = tmp_path / "audit.jsonl"
    path.write_text(json.dumps({"event_type": "legacy"}) + "\n", encoding="utf-8")
    ledger = SecurityAuditLedger(path)

    appended = ledger.append(actor="security", event_type="signed")

    assert appended["prev_hash"].startswith("legacy:")
    assert ledger.verify_integrity() is True


def test_concurrent_appends_produce_a_valid_sequence(tmp_path):
    path = tmp_path / "audit.jsonl"
    ledger = SecurityAuditLedger(path)

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(
            executor.map(
                lambda index: SecurityAuditLedger(path).append(
                    actor="worker", event_type="concurrent", details={"index": index}
                ),
                range(40),
            )
        )

    records = _records(path)
    assert [record["sequence"] for record in records] == list(range(1, 41))
    assert ledger.verify_integrity() is True


def test_signature_key_is_not_stored_inside_the_ledger(tmp_path):
    path = tmp_path / "audit.jsonl"
    ledger = SecurityAuditLedger(path)
    ledger.append(actor="security", event_type="created")

    assert ledger.key_path.exists()
    assert ledger.key_path.read_text("utf-8").strip()
    assert ledger.key_path.read_text("utf-8").strip() not in path.read_text("utf-8")


def _signatures(monkeypatch):
    seen = []
    sign = audit_ledger._signature

    def counted(secret, record_hash):
        seen.append(record_hash)
        return sign(secret, record_hash)

    monkeypatch.setattr(audit_ledger, "_signature", counted)
    return seen


def test_new_instance_validates_each_external_tail_record_only_once(
    tmp_path, monkeypatch
):
    ledger = SecurityAuditLedger(tmp_path / "audit.jsonl")
    for _ in range(12):
        ledger.append(actor="security", event_type="warm")
    # An independent writer extends identical history using the same key.
    other = SecurityAuditLedger(tmp_path / "other.jsonl", key_path=ledger.key_path)
    other.path.write_bytes(ledger.path.read_bytes())
    external = [other.append(actor="external", event_type="event") for _ in range(3)]
    other.path.replace(ledger.path)

    seen = _signatures(monkeypatch)
    current = SecurityAuditLedger(ledger.path)
    new = current.append(actor="security", event_type="next")
    assert new["sequence"] == 16
    assert all(seen.count(record["hash"]) == 1 for record in external)
    # At most one locally appended record can still await its first reread.
    assert len(seen) <= len(external) + 2

    seen.clear()
    assert current.verify_integrity(require_signed_records=True)
    assert seen == [record["hash"] for record in _records(current.path)]


def _signed_history(tmp_path, count=4):
    ledger = SecurityAuditLedger(tmp_path / "audit.jsonl")
    for _ in range(count):
        ledger.append(actor="security", event_type="known")
    return ledger


@pytest.mark.parametrize("replace", [False, True], ids=["in_place", "atomic"])
def test_same_size_prefix_edit_with_restored_timestamps_fails_closed(tmp_path, replace):
    ledger = _signed_history(tmp_path)
    path = ledger.path
    original = path.read_bytes()
    stat = path.stat()
    changed = original.replace(b'"known"', b'"other"', 1)
    target = tmp_path / "replacement" if replace else path
    target.write_bytes(changed)
    if replace:
        target.replace(path)
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert path.stat().st_size == len(original)
    assert not ledger.verify_integrity()
    with pytest.raises(AuditIntegrityError, match="invalid hash at audit line 1"):
        SecurityAuditLedger(path).append(actor="security", event_type="next")
    assert path.read_bytes() == changed


@pytest.mark.parametrize(
    ("damage", "reason"),
    [
        ("sequence", "invalid sequence at audit line 6"),
        ("prev_hash", "broken chain at audit line 6"),
        ("hash", "invalid hash at audit line 6"),
        ("signature", "invalid signature at audit line 6"),
        ("json", "invalid JSON at audit line 6"),
        ("array", "invalid record at audit line 6"),
        ("legacy", "legacy record found after signed records"),
    ],
)
def test_signed_suffix_preserves_cold_errors_and_line_numbers(tmp_path, damage, reason):
    ledger = SecurityAuditLedger(tmp_path / "audit.jsonl")
    ledger.path.write_bytes(b'\r\n {"legacy":true} \r\n')
    first = ledger.append(actor="security", event_type="first")
    assert first["prev_hash"].startswith("legacy:")
    with ledger.path.open("ab") as handle:
        handle.write(b"\r\n\t\r\n")
    last = ledger.append(actor="security", event_type="last")
    # Prior signed records, the legacy anchor, and both blank lines are warm.
    prefix = ledger.path.read_bytes().splitlines(keepends=True)[:-1]
    if damage in {"sequence", "prev_hash", "hash", "signature"}:
        last[damage] = 99 if damage == "sequence" else "invalid"
        suffix = json.dumps(last).encode()
    else:
        suffix = {"json": b'{"', "array": b"[]", "legacy": b"{}"}[damage]
    ledger.path.write_bytes(b"".join(prefix) + suffix + b"\r\n")
    assert not ledger.verify_integrity(require_signed_records=True)
    with pytest.raises(AuditIntegrityError, match=reason):
        ledger.append(actor="security", event_type="next")


@pytest.mark.parametrize(
    "source", ["audit_env", "state_env", "key_file", "invalid_file"]
)
def test_effective_signing_key_is_checked_even_with_no_uncached_tail(
    tmp_path, monkeypatch, source
):
    ledger = _signed_history(tmp_path)
    # Drop the freshly signed line, leaving exactly the last validated prefix.
    lines = ledger.path.read_bytes().splitlines(keepends=True)
    ledger.path.write_bytes(b"".join(lines[:-1]))
    if source == "audit_env":
        monkeypatch.setenv("AETHERRA_SECURITY_AUDIT_SECRET", "different")
    elif source == "state_env":
        monkeypatch.setenv("AETHERRA_SECURITY_STATE_SECRET", "different")
    else:
        ledger.key_path.write_bytes(b"x" * (1 if source == "invalid_file" else 48))
    expected = (
        "signing key is invalid"
        if source == "invalid_file"
        else "invalid signature at audit line 1"
    )
    assert not ledger.verify_integrity()
    with pytest.raises(AuditLedgerError, match=expected):
        SecurityAuditLedger(ledger.path).append(actor="security", event_type="next")


@pytest.mark.parametrize("change", ["shorter", "different", "empty", "partial"])
def test_replacement_is_decided_by_the_current_chain(tmp_path, change):
    ledger = _signed_history(tmp_path)
    other = SecurityAuditLedger(tmp_path / "replacement", key_path=ledger.key_path)
    expected_sequence = 1
    if change == "shorter":
        other.path.write_bytes(ledger.path.read_bytes().splitlines(keepends=True)[0])
        expected_sequence = 2
    elif change == "different":
        for _ in range(6):
            other.append(actor="other", event_type="independent")
        expected_sequence = 7
    elif change == "empty":
        other.path.write_bytes(b"")
    else:
        other.path.write_bytes(ledger.path.read_bytes()[:20])
    other.path.replace(ledger.path)

    if change == "partial":
        with pytest.raises(AuditIntegrityError, match="invalid JSON at audit line 1"):
            ledger.append(actor="security", event_type="next")
        assert not ledger.verify_integrity()
    else:
        new = ledger.append(actor="security", event_type="next")
        assert new["sequence"] == expected_sequence
        assert ledger.verify_integrity(require_signed_records=True)


@pytest.mark.parametrize("ending", [b"", b"\r"])
def test_append_after_unterminated_or_cr_only_record_preserves_framing(
    tmp_path, ending
):
    ledger = _signed_history(tmp_path)
    original = ledger.path.read_bytes().rstrip(b"\n") + ending
    ledger.path.write_bytes(original)
    assert ledger.verify_integrity(require_signed_records=True)
    assert ledger.append(actor="security", event_type="next")["sequence"] == 5
    assert ledger.path.read_bytes().startswith(original + b"{")
    if ending == b"\r":
        assert ledger.verify_integrity()
    else:
        assert not ledger.verify_integrity()
        with pytest.raises(AuditIntegrityError, match="invalid JSON at audit line 4"):
            ledger.append(actor="security", event_type="again")


@pytest.mark.parametrize("partial", [False, True])
def test_failed_write_discards_cached_validation(tmp_path, monkeypatch, partial):
    ledger = _signed_history(tmp_path)
    original = ledger.path.read_bytes()

    def fail(encoded):
        if partial:
            with ledger.path.open("ab") as handle:
                handle.write(encoded[:20])
        raise OSError("injected append failure")

    monkeypatch.setattr(ledger, "_append_bytes", fail)
    with pytest.raises(OSError, match="injected append failure"):
        ledger.append(actor="security", event_type="failed")
    if partial:
        assert not ledger.verify_integrity()
        with pytest.raises(AuditIntegrityError, match="invalid JSON at audit line 5"):
            SecurityAuditLedger(ledger.path).append(
                actor="security", event_type="blocked"
            )
        ledger.path.write_bytes(original)
    current = SecurityAuditLedger(ledger.path)
    seen = _signatures(monkeypatch)
    new = current.append(actor="security", event_type="retry")
    assert new["sequence"] == 5
    assert seen == [record["hash"] for record in _records(ledger.path)]


def test_prefix_reuse_expires_even_with_active_appends(tmp_path, monkeypatch):
    now = 100.0
    monkeypatch.setattr(audit_ledger, "monotonic", lambda: now)
    monkeypatch.setattr(audit_ledger, "_PREFIX_LIFETIME", 5.0)
    ledger = _signed_history(tmp_path)
    seen = _signatures(monkeypatch)
    now += 4
    ledger.append(actor="security", event_type="warm")
    assert len(seen) <= 2
    now += 1
    seen.clear()
    ledger.append(actor="security", event_type="expired")
    assert seen == [record["hash"] for record in _records(ledger.path)]


def test_bounded_cache_evicts_the_least_recently_used_path(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_ledger, "_PREFIXES", OrderedDict())
    monkeypatch.setattr(audit_ledger, "_PREFIX_LIMIT", 2)
    a = _signed_history(tmp_path / "a")
    b = _signed_history(tmp_path / "b")
    a.append(actor="security", event_type="touch")
    _signed_history(tmp_path / "c")
    seen = _signatures(monkeypatch)
    a.append(actor="security", event_type="retained")
    assert len(seen) <= 2
    seen.clear()
    b.append(actor="security", event_type="evicted")
    assert seen == [record["hash"] for record in _records(b.path)]


def _overlapping_append(path, ready, before_write, receipts):
    class OverlappingLedger(SecurityAuditLedger):
        def _append_bytes(self, encoded):
            # Give an independent writer a chance to sign against this same tail.
            with contextlib.suppress(threading.BrokenBarrierError):
                before_write.wait(timeout=0.12)
            super()._append_bytes(encoded)

    ledger = OverlappingLedger(path)
    ready.wait(timeout=10)
    record = ledger.append(actor=str(os.getpid()), event_type="overlap")
    receipts.put(record["hash"])


def test_process_appends_acknowledge_one_verifiable_chain(tmp_path):
    ledger = _signed_history(tmp_path, count=1)
    original_key = ledger.key_path.read_bytes()
    context = multiprocessing.get_context("spawn")
    receipts = context.Queue()
    args = (ledger.path, context.Barrier(2), context.Barrier(2), receipts)
    writers = [context.Process(target=_overlapping_append, args=args) for _ in range(2)]
    try:
        for writer in writers:
            writer.start()
        for writer in writers:
            writer.join(15)
            assert writer.exitcode == 0
        records = _records(ledger.path)
        assert {receipts.get(timeout=2) for _ in writers} == {
            record["hash"] for record in records[1:]
        }
        assert [record["sequence"] for record in records] == [1, 2, 3]
        assert ledger.verify_integrity(require_signed_records=True)
        assert ledger.key_path.read_bytes() == original_key
    finally:
        for writer in writers:
            if writer.is_alive():
                writer.terminate()
                writer.join(5)
        receipts.close()


def _pause_signed_write(path, entered, resume, split):
    class PausedLedger(SecurityAuditLedger):
        def _append_bytes(self, encoded):
            if split:
                super()._append_bytes(encoded[:20])
                encoded = encoded[20:]
            entered.set()
            if not split:
                os._exit(23)
            assert resume.wait(10)
            # Let the verifier encounter the in-progress write.
            time.sleep(0.08)
            super()._append_bytes(encoded)

    PausedLedger(path).append(actor="writer", event_type="change")


@pytest.mark.parametrize("crash", [False, True], ids=["verify_snapshot", "holder_exit"])
def test_process_lock_covers_verification_and_releases_on_exit(tmp_path, crash):
    ledger = _signed_history(tmp_path, count=1)
    context = multiprocessing.get_context("spawn")
    entered, resume = context.Event(), context.Event()
    writer = context.Process(
        target=_pause_signed_write, args=(ledger.path, entered, resume, not crash)
    )
    writer.start()
    try:
        assert entered.wait(10)
        if not crash:
            resume.set()
            assert ledger.verify_integrity(require_signed_records=True)
        writer.join(5)
        assert not writer.is_alive()
        assert writer.exitcode == (23 if crash else 0)
        appended = ledger.append(actor="parent", event_type="after")
        assert appended["sequence"] == (2 if crash else 3)
        assert ledger.verify_integrity(require_signed_records=True)
    finally:
        resume.set()
        if writer.is_alive():
            writer.terminate()
            writer.join(5)


@pytest.mark.parametrize("export", [False, True], ids=["active_profile", "export"])
def test_verifying_read_only_history_needs_no_write_access(
    tmp_path, monkeypatch, export
):
    ledger = _signed_history(tmp_path, count=1)
    lock_path = ledger.path.with_suffix(".jsonl.lock")
    if export:
        lock_path.unlink(missing_ok=True)
    original_open = os.open

    def read_only_open(path, flags, *args, **kwargs):
        if flags & (os.O_CREAT | os.O_RDWR | os.O_WRONLY):
            raise PermissionError("read-only export")
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", read_only_open)
    assert ledger.verify_integrity(require_signed_records=True)
    if export:
        assert not lock_path.exists()
    missing = SecurityAuditLedger(tmp_path / "absent" / "audit.jsonl")
    assert missing.verify_integrity()
    assert not missing.path.parent.exists()
