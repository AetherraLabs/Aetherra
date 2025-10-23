# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import hashlib
import os
import sqlite3
import time
from contextlib import suppress
from dataclasses import dataclass
from typing import Optional

import numpy as np

SCHEMA_VERSION = 1


@dataclass
class EmbeddingRecord:
    content_hash: str
    dim: int
    dtype: str
    embedding: bytes
    content_excerpt: str
    created_at: float


class StormStorage:
    """SQLite-backed persistence for STORM sheaf cells and overlaps.

    Minimal Phase 3 scope:
    - storm_cells: stores content-hash keyed deterministic embeddings for memory items
    - storm_meta: key/value store (schema_version, housekeeping)
    - Overlaps table reserved for later phases

    All operations are best-effort and must never break recall flows.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._initialize()

    def close(self) -> None:
        with suppress(Exception):
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def __del__(self):  # pragma: no cover - best-effort GC
        self.close()

    def _connect(self) -> None:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            # Speed-appropriate pragmas (safe defaults)
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA synchronous=NORMAL;")

    def _initialize(self) -> None:
        assert self._conn is not None
        cur = self._conn.cursor()
        # Cells table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS storm_cells (
                content_hash TEXT PRIMARY KEY,
                dim INTEGER NOT NULL,
                dtype TEXT NOT NULL,
                embedding BLOB NOT NULL,
                content_excerpt TEXT,
                created_at REAL NOT NULL
            )
            """
        )
        # Overlaps reserved (future)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS storm_overlaps (
                a_hash TEXT NOT NULL,
                b_hash TEXT NOT NULL,
                weight REAL NOT NULL,
                created_at REAL NOT NULL,
                PRIMARY KEY (a_hash, b_hash)
            )
            """
        )
        # Meta table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS storm_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        # Set schema version
        cur.execute(
            "INSERT OR REPLACE INTO storm_meta(key, value) VALUES(?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        self._conn.commit()

    # --- Utility serialization helpers ---
    @staticmethod
    def _hash_content(text: str) -> str:
        h = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
        return h

    @staticmethod
    def _to_blob(arr: np.ndarray) -> tuple[bytes, int, str]:
        arr = np.asarray(arr)
        return arr.tobytes(), int(arr.size), str(arr.dtype)

    @staticmethod
    def _from_blob(blob: bytes, size: int, dtype: str) -> np.ndarray:
        arr = np.frombuffer(blob, dtype=np.dtype(dtype))
        # Defensive: size field represents total elements; arr is 1-D
        return arr.reshape((size,))

    # --- Public API ---
    def get_embedding(self, content: str) -> Optional[np.ndarray]:
        """Fetch a persisted embedding for content if present.

        Returns None when not found or on any error.
        """
        try:
            assert self._conn is not None
            content_hash = self._hash_content(content)
            cur = self._conn.cursor()
            row = cur.execute(
                "SELECT embedding, dim, dtype FROM storm_cells WHERE content_hash=?",
                (content_hash,),
            ).fetchone()
            if not row:
                return None
            blob, dim, dtype = row
            arr = self._from_blob(blob, dim, dtype)
            return arr
        except Exception:
            return None

    def upsert_embedding(self, content: str, embedding: np.ndarray) -> str:
        """Persist embedding for content (insert or replace).

        Returns the content hash. Best-effort (swallows errors).
        """
        try:
            assert self._conn is not None
            content_hash = self._hash_content(content)
            blob, size, dtype = self._to_blob(embedding)
            excerpt = content[:200]
            now = time.time()
            cur = self._conn.cursor()
            cur.execute(
                """
                INSERT INTO storm_cells(content_hash, dim, dtype, embedding, content_excerpt, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(content_hash) DO UPDATE SET
                    dim=excluded.dim,
                    dtype=excluded.dtype,
                    embedding=excluded.embedding,
                    content_excerpt=excluded.content_excerpt
                """,
                (content_hash, size, dtype, blob, excerpt, now),
            )
            self._conn.commit()
            return content_hash
        except Exception:
            # Best-effort; do not propagate errors to callers
            return ""

    def get_all_embeddings(self) -> list[np.ndarray]:
        """Fetch all stored embeddings for maintenance operations.

        Returns list of all embedding vectors from storm_cells table.
        Used for inconsistency scanning during night-cycle maintenance.
        Returns empty list on error.
        """
        try:
            assert self._conn is not None
            cur = self._conn.cursor()
            rows = cur.execute("SELECT embedding, dim, dtype FROM storm_cells").fetchall()
            embeddings = []
            for blob, dim, dtype in rows:
                arr = self._from_blob(blob, dim, dtype)
                embeddings.append(arr)
            return embeddings
        except Exception:
            return []
