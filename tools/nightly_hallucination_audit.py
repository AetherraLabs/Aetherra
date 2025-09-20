#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Nightly Hallucination Audit
===========================

Scans persistent memory for Lyrixa chat responses with low confidence or
unverified critical claims and writes a timestamped audit report.

Usage: python tools/nightly_hallucination_audit.py

Environment:
  AETHERRA_AUDIT_MIN_CONF   Minimal confidence threshold (default 0.55)
  AETHERRA_AUDIT_WINDOW_H   Lookback window hours (default 24)
  AETHERRA_AUDIT_OUT        Output path (default audits/hallucination_audit_<date>.md)
"""

# Standard library imports
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_DIR = Path(os.environ.get("AETHERRA_MEMORY_DIR", "aetherra_memory"))
DB_PATH = DB_DIR / "cognitive_memory.db"

MIN_CONF = float(os.environ.get("AETHERRA_AUDIT_MIN_CONF", "0.55"))
WINDOW_H = int(os.environ.get("AETHERRA_AUDIT_WINDOW_H", "24"))
OUT_DIR = Path("audits")
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = Path(
    os.environ.get(
        "AETHERRA_AUDIT_OUT",
        str(OUT_DIR / f"hallucination_audit_{datetime.now().strftime('%Y%m%d')}.md"),
    )
)

CRITICAL_CATEGORIES = {"ownership", "identity", "safety", "policy"}


def main() -> int:
    if not DB_PATH.exists():
        print(f"[AUDIT] No persistent memory DB at {DB_PATH}")
        return 0

    since = datetime.now() - timedelta(hours=WINDOW_H)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Fetch chat responses and facts in window
    cur.execute(
        """
        SELECT id, content, memory_type, context, importance, created_at,
               confidence, verified
        FROM memories
        WHERE datetime(created_at) >= ?
          AND memory_type IN ('chat_response','fact')
        ORDER BY created_at DESC
        """,
        (since.isoformat(),),
    )
    rows = cur.fetchall()
    conn.close()

    low_conf = []
    crit_unverified = []

    for (
        rid,
        content,
        mtype,
        context_json,
        importance,
        created_at,
        conf,
        verified,
    ) in rows:
        try:
            # Simple parse for category
            category = None
            if context_json:
                # Standard library imports
                import json

                ctx = json.loads(context_json)
                category = ctx.get("category")
        except Exception:
            category = None

        if mtype == "chat_response":
            if conf is None or (isinstance(conf, (int, float)) and conf < MIN_CONF):
                low_conf.append((created_at, conf or 0.0, content[:240]))
        elif mtype == "fact":
            if category in CRITICAL_CATEGORIES and not verified:
                crit_unverified.append((created_at, content[:240]))

    # Write report
    lines = []
    lines.append(f"# Nightly Hallucination Audit — {datetime.now().isoformat()}\n")
    lines.append(f"Lookback window: last {WINDOW_H} hours; threshold: {MIN_CONF}\n")

    lines.append("## Low-confidence chat responses\n")
    if not low_conf:
        lines.append("- None found\n")
    else:
        for ts, conf, snippet in low_conf:
            lines.append(f"- [{ts}] conf={conf:.2f}: {snippet}\n")

    lines.append("\n## Critical facts not verified\n")
    if not crit_unverified:
        lines.append("- None found\n")
    else:
        for ts, snippet in crit_unverified:
            lines.append(f"- [{ts}] {snippet}\n")

    OUT_PATH.write_text("".join(lines), encoding="utf-8")
    print(f"[AUDIT] Wrote report to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
