# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2025 Aetherra
"""Capability test: plugin execution analytics schema migrator.

Validates that an existing legacy (v1) database is migrated to the latest
version (v2) adding latency_ms column while preserving data and supporting
idempotent re-run.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from Aetherra.plugins.lifecycle.plugin_analytics import PluginMetricsCollector


def _create_legacy_v1_db(path: str):
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE plugin_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                execution_time REAL NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                memory_usage REAL,
                cpu_usage REAL,
                timestamp TEXT NOT NULL,
                context_hash TEXT,
                user_session TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE plugin_schema_version (version INTEGER NOT NULL)
            """
        )
        # Explicitly set legacy version 1
        conn.execute("INSERT INTO plugin_schema_version (version) VALUES (1)")
        conn.execute(
            """
            INSERT INTO plugin_executions (plugin_id, execution_time, success, error_message, memory_usage, cpu_usage, timestamp, context_hash, user_session)
            VALUES ('demo_plugin', 0.123, 1, NULL, 10.5, 5.2, '2025-01-01T00:00:00', 'hash123', 'sess1')
            """
        )


def test_migrator_upgrades_and_is_idempotent(tmp_path: Path):
    db_path = tmp_path / "plugin_analytics_legacy.db"
    _create_legacy_v1_db(str(db_path))

    # Sanity: legacy schema has no latency_ms
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("PRAGMA table_info(plugin_executions)")
        cols = {r[1] for r in cur.fetchall()}
        assert "latency_ms" not in cols
        version = conn.execute("SELECT version FROM plugin_schema_version").fetchone()[
            0
        ]
        assert version == 1

    # Instantiate collector -> triggers migration
    collector = PluginMetricsCollector(str(db_path))

    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("PRAGMA table_info(plugin_executions)")
        cols = {r[1] for r in cur.fetchall()}
        assert "latency_ms" in cols, "Expected migration to add latency_ms column"
        version = conn.execute("SELECT version FROM plugin_schema_version").fetchone()[
            0
        ]
        assert version >= 2
        # Original row preserved with NULL latency_ms
        row = conn.execute(
            "SELECT latency_ms FROM plugin_executions WHERE plugin_id='demo_plugin'"
        ).fetchone()
        assert row is not None and row[0] is None

    # Record a new execution and ensure latency_ms populated
    collector.record_execution(
        plugin_id="demo_plugin",
        execution_time=0.050,
        success=True,
    )
    with sqlite3.connect(db_path) as conn:
        # Newest row should now have latency_ms (non-null)
        cur = conn.execute(
            "SELECT latency_ms FROM plugin_executions ORDER BY id DESC LIMIT 1"
        )
        lat = cur.fetchone()[0]
        assert (
            lat is not None and lat >= 50 - 2 and lat <= 50 + 2
        )  # allow rounding jitter

    # Re-instantiate to assert idempotent (no error, version stable)
    _ = PluginMetricsCollector(str(db_path))
    with sqlite3.connect(db_path) as conn:
        version2 = conn.execute("SELECT version FROM plugin_schema_version").fetchone()[
            0
        ]
        assert version2 == version
