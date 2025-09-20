#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[COSMOS] Phase 6: Layout Memory System (extracted)
Manages persistent GUI state and learned user preferences.
"""

# Standard library imports
import json
import logging
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Third party imports
from PySide6.QtCore import QMutex

# Local imports
from .phase6_types import GUIState

logger = logging.getLogger(__name__)


class LayoutMemorySystem:
    """Manages persistent GUI state and user preferences"""

    def __init__(self, db_path: str = "gui_memory.db"):
        self.db_path = Path(db_path)
        self.mutex = QMutex()
        self._init_database()

    def _init_database(self):
        """Initialize the GUI memory database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS gui_states (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        state_data TEXT,
                        timestamp DATETIME,
                        user_context TEXT
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        last_updated DATETIME,
                        usage_count INTEGER DEFAULT 1
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS layout_patterns (
                        pattern_id TEXT PRIMARY KEY,
                        pattern_data TEXT,
                        frequency INTEGER DEFAULT 1,
                        last_used DATETIME,
                        effectiveness_score FLOAT DEFAULT 0.5
                    )
                """
                )

                conn.commit()

        except Exception as e:
            logger.error(f"[PHASE6] Database initialization failed: {e}")

    def save_gui_state(self, state: GUIState, session_id: str):
        """Save current GUI state to memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                state_json = json.dumps(asdict(state), default=str)
                conn.execute(
                    """
                    INSERT INTO gui_states (session_id, state_data, timestamp, user_context)
                    VALUES (?, ?, ?, ?)
                """,
                    (session_id, state_json, datetime.now(), ""),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"[PHASE6] Failed to save GUI state: {e}")

    def load_last_gui_state(
        self, session_id: Optional[str] = None
    ) -> Optional[GUIState]:
        """Load the most recent GUI state"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if session_id:
                    cursor = conn.execute(
                        """
                        SELECT state_data FROM gui_states
                        WHERE session_id = ?
                        ORDER BY timestamp DESC LIMIT 1
                    """,
                        (session_id,),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT state_data FROM gui_states
                        ORDER BY timestamp DESC LIMIT 1
                    """
                    )

                row = cursor.fetchone()
                if row:
                    state_data = json.loads(row[0])
                    # Convert datetime strings back to datetime objects
                    if "last_accessed" in state_data:
                        state_data["last_accessed"] = datetime.fromisoformat(
                            state_data["last_accessed"]
                        )
                    return GUIState(**state_data)

        except Exception as e:
            logger.error(f"[PHASE6] Failed to load GUI state: {e}")

        return None

    def learn_user_preference(self, key: str, value: Any):
        """Learn and store user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                value_json = json.dumps(value) if not isinstance(value, str) else value

                # Update or insert preference
                conn.execute(
                    """
                    INSERT OR REPLACE INTO user_preferences (key, value, last_updated, usage_count)
                    VALUES (?, ?, ?, COALESCE((SELECT usage_count + 1 FROM user_preferences WHERE key = ?), 1))
                """,
                    (key, value_json, datetime.now(), key),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"[PHASE6] Failed to learn preference: {e}")

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get all learned user preferences"""
        preferences = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT key, value FROM user_preferences")
                for key, value in cursor.fetchall():
                    try:
                        preferences[key] = json.loads(value)
                    except Exception:
                        preferences[key] = value

        except Exception as e:
            logger.error(f"[PHASE6] Failed to get preferences: {e}")

        return preferences


__all__ = ["LayoutMemorySystem"]
