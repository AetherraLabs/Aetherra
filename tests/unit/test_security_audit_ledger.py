"""Tests for the signed, hash-chained Security JSONL ledger."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from Aetherra.security.audit_ledger import (
    AuditIntegrityError,
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
                lambda index: ledger.append(
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
