-- SPDX-License-Identifier: GPL-3.0-or-later
-- STORM SQLite schema v1

PRAGMA foreign_keys = ON;

-- Tracks the current schema version
CREATE TABLE IF NOT EXISTS storm_schema_version (
  version INTEGER NOT NULL,
  applied_at TEXT NOT NULL
);

-- Sheaf cells (cover over manifold x time x concept)
CREATE TABLE IF NOT EXISTS storm_cells (
  cell_id TEXT PRIMARY KEY,
  center_sem BLOB,           -- serialized vector/centroid
  window_time_start REAL,
  window_time_end REAL,
  concept_tokens TEXT,       -- JSON array of tokens
  measure_json TEXT,         -- serialized measure parameters
  tda_summary TEXT,          -- JSON (persistence diagram/summary)
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- Overlaps between cells (restriction maps)
CREATE TABLE IF NOT EXISTS storm_overlaps (
  overlap_id TEXT PRIMARY KEY,
  cell_a_id TEXT NOT NULL,
  cell_b_id TEXT NOT NULL,
  restriction_params TEXT,   -- JSON parameters for restrictions
  sheaf_inconsistency REAL DEFAULT 0.0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(cell_a_id) REFERENCES storm_cells(cell_id) ON DELETE CASCADE,
  FOREIGN KEY(cell_b_id) REFERENCES storm_cells(cell_id) ON DELETE CASCADE
);

-- Per-run metadata and status (optional)
CREATE TABLE IF NOT EXISTS storm_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- Useful indices
CREATE INDEX IF NOT EXISTS idx_storm_overlaps_cells ON storm_overlaps(cell_a_id, cell_b_id);

-- Initialize version if empty
INSERT INTO storm_schema_version(version, applied_at)
  SELECT 1, datetime('now')
  WHERE NOT EXISTS (SELECT 1 FROM storm_schema_version);
