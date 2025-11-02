# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Approvals API (Phase 5)
=======================

Lightweight, in-memory approval registry for actions requiring consent.
Integrates with the safety envelope's policy engine queue.
"""

from __future__ import annotations

import contextlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class ApprovalRecord:
    id: str
    intent_goal: str
    risk: str
    requested_by: str
    reason: str
    status: str = "pending"  # pending|approved|denied|revoked
    created_ts: float = field(default_factory=lambda: time.time())
    decided_ts: float | None = None
    approver: str | None = None
    decision_reason: str | None = None
    diff_preview: dict | None = None


class ApprovalStore:
    """In-memory store for approval records."""

    def __init__(self) -> None:
        self._records: Dict[str, ApprovalRecord] = {}
        self._persist_enabled = os.getenv("AETHERRA_APPROVALS_PERSIST", "1") == "1"
        self._log_path = Path(os.getenv("AETHERRA_APPROVALS_LOG_PATH", "data/approvals_log.jsonl"))
        # Rotation settings
        self._max_bytes = int(os.getenv("AETHERRA_APPROVALS_LOG_MAX_BYTES", str(2 * 1024 * 1024)))
        self._max_backups = int(os.getenv("AETHERRA_APPROVALS_LOG_BACKUPS", "3"))
        if self._persist_enabled:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)

    def request(
        self,
        intent_goal: str,
        risk: str,
        requested_by: str,
        reason: str,
        diff_preview: dict | None = None,
    ) -> ApprovalRecord:
        rec = ApprovalRecord(
            id=str(uuid.uuid4()),
            intent_goal=intent_goal,
            risk=risk,
            requested_by=requested_by,
            reason=reason,
            diff_preview=diff_preview,
        )
        self._records[rec.id] = rec
        self._append_log({"event": "requested", **rec.__dict__})
        return rec

    def approve(self, rec_id: str, approver: str, reason: str = "") -> bool:
        rec = self._records.get(rec_id)
        if not rec or rec.status != "pending":
            return False
        rec.status = "approved"
        rec.approver = approver
        rec.decided_ts = time.time()
        rec.decision_reason = reason
        self._append_log({"event": "approved", **rec.__dict__})
        return True

    def deny(self, rec_id: str, approver: str, reason: str = "") -> bool:
        rec = self._records.get(rec_id)
        if not rec or rec.status != "pending":
            return False
        rec.status = "denied"
        rec.approver = approver
        rec.decided_ts = time.time()
        rec.decision_reason = reason
        self._append_log({"event": "denied", **rec.__dict__})
        return True

    def revoke(self, rec_id: str, reason: str = "") -> bool:
        rec = self._records.get(rec_id)
        if not rec or rec.status not in ("pending", "approved"):
            return False
        rec.status = "revoked"
        rec.decided_ts = time.time()
        rec.decision_reason = reason
        self._append_log({"event": "revoked", **rec.__dict__})
        return True

    def get(self, rec_id: str) -> ApprovalRecord | None:
        return self._records.get(rec_id)

    def list(self, status: str | None = None) -> List[ApprovalRecord]:
        if status is None:
            return list(self._records.values())
        return [r for r in self._records.values() if r.status == status]

    def _append_log(self, payload: dict) -> None:
        if not self._persist_enabled:
            return
        try:
            self._maybe_rotate()
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            # Non-fatal
            pass

    def _maybe_rotate(self) -> None:
        try:
            if not self._log_path.exists():
                return
            if self._log_path.stat().st_size < self._max_bytes:
                return
            # Rotate backups: .{n} -> .{n+1}
            for idx in range(self._max_backups, 0, -1):
                src = self._log_path.with_suffix(self._log_path.suffix + f".{idx}")
                dst = self._log_path.with_suffix(self._log_path.suffix + f".{idx + 1}")
                if src.exists():
                    if idx == self._max_backups:
                        with contextlib.suppress(Exception):
                            src.unlink()
                    else:
                        with contextlib.suppress(Exception):
                            src.rename(dst)
            # Move current to .1 and create new empty file
            backup1 = self._log_path.with_suffix(self._log_path.suffix + ".1")
            with contextlib.suppress(Exception):
                self._log_path.rename(backup1)
        except Exception:
            pass
