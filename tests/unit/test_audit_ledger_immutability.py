import os
import sqlite3
import tempfile
from pathlib import Path

from aetherra_self_incorporation import AuditLedger


def test_audit_ledger_hash_chain_detects_tamper():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "audit.db"
        ledger = AuditLedger(db_path)

        # Append two entries
        ledger.append(
            plan_id="p1",
            action="proposal:optimize",
            status="accepted",
            target={"a": 1},
            result={"ok": True},
            trace_id="t1",
            ethics_overall=None,
            risk_level="low",
        )
        ledger.append(
            plan_id="p2",
            action="proposal:optimize",
            status="accepted",
            target={"a": 2},
            result={"ok": True},
            trace_id="t2",
            ethics_overall=None,
            risk_level="low",
        )

        # Should verify successfully
        assert ledger.verify_integrity() is True

        # Tamper with the first row
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                "UPDATE audit_records SET action = 'proposal:hack' WHERE id = 1"
            )
            conn.commit()
        finally:
            conn.close()

        # Now integrity check should fail
        assert ledger.verify_integrity() is False
