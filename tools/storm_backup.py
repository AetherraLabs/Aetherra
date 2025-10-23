#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
STORM backup/restore helper (SQLite)

Usage:
  python tools/storm_backup.py backup --db configs/storm_sheaf.db --out backups/storm_backup.json
  python tools/storm_backup.py restore --db configs/storm_sheaf.db --in backups/storm_backup.json

Notes:
- Only backs up STORM tables (storm_cells, storm_overlaps, storm_meta, storm_schema_version)
- JSON format for portability
- No destructive ops on restore unless --force is provided
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

STORM_TABLES = [
    "storm_cells",
    "storm_overlaps",
    "storm_meta",
    "storm_schema_version",
]

SELECT_ALL = {
    "storm_cells": "SELECT * FROM storm_cells",
    "storm_overlaps": "SELECT * FROM storm_overlaps",
    "storm_meta": "SELECT * FROM storm_meta",
    "storm_schema_version": "SELECT * FROM storm_schema_version",
}

DELETE_ALL = {
    "storm_cells": "DELETE FROM storm_cells",
    "storm_overlaps": "DELETE FROM storm_overlaps",
    "storm_meta": "DELETE FROM storm_meta",
    "storm_schema_version": "DELETE FROM storm_schema_version",
}

INSERT_PREFIX = {
    "storm_cells": "INSERT INTO storm_cells",
    "storm_overlaps": "INSERT INTO storm_overlaps",
    "storm_meta": "INSERT INTO storm_meta",
    "storm_schema_version": "INSERT INTO storm_schema_version",
}


def _safe_table(name: str) -> str:
    if name not in STORM_TABLES:
        raise ValueError(f"Invalid table: {name}")
    return name


def backup(db_path: str, out_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    data: dict[str, Any] = {
        "_meta": {"generated_at": datetime.utcnow().isoformat() + "Z"}
    }
    try:
        for table in STORM_TABLES:
            t = _safe_table(table)
            rows = conn.execute(SELECT_ALL[t]).fetchall()
            data[table] = [dict(r) for r in rows]
    finally:
        conn.close()

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[STORM] Backup written: {out_path}")


def restore(db_path: str, in_path: str, force: bool = False) -> None:
    if not os.path.exists(in_path):
        raise FileNotFoundError(in_path)
    with open(in_path, encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        conn.commit()

        if not force:
            print("[STORM] Dry run: use --force to write changes.")
            for table in STORM_TABLES:
                count = len(data.get(table, []))
                print(f"  would restore {count} rows into {table}")
            return

        for table in STORM_TABLES:
            rows = data.get(table, [])
            if not rows:
                continue
            cols = list(rows[0].keys())
            placeholders = ",".join([":" + c for c in cols])
            t = _safe_table(table)
            # Validate columns exist
            schema_cols = [
                r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()
            ]
            if not set(cols).issubset(schema_cols):
                raise ValueError(f"Invalid columns for table {t}: {cols}")
            cur.execute(DELETE_ALL[t])
            insert_sql = (
                INSERT_PREFIX[t] + f" ({','.join(cols)}) VALUES ({placeholders})"
            )
            cur.executemany(insert_sql, rows)
        conn.commit()
    finally:
        conn.close()
    print(f"[STORM] Restore completed from: {in_path}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("backup")
    pb.add_argument("--db", required=True)
    pb.add_argument("--out", required=True)

    pr = sub.add_parser("restore")
    pr.add_argument("--db", required=True)
    pr.add_argument("--in", dest="in_", required=True)
    pr.add_argument("--force", action="store_true")

    args = p.parse_args()

    if args.cmd == "backup":
        backup(args.db, args.out)
    elif args.cmd == "restore":
        restore(args.db, args.in_, args.force)


if __name__ == "__main__":
    main()
