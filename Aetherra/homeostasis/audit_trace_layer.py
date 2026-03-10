#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔍 Aetherra Homeostasis Audit & Trace Layer
============================================

Advanced audit and tracing system for homeostasis actions with deep diagnostics
and correlation tracking. Provides comprehensive logging of action → effect →
steady-state return cycles for system transparency and debugging.

This module:
- Persists all homeostasis controller actions to SQLite WAL database
- Tracks correlation IDs between actions, effects, and outcomes
- Provides deep diagnostic capabilities for control loop analysis
- Integrates with Lyrixa's introspection layer for unified observability
- Supports action replay and impact analysis

Author: Aetherra Labs
"""

import json
import logging
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ActionTrace:
    """Complete trace record for a homeostasis action."""

    # Core identifiers
    trace_id: str
    correlation_id: str
    session_id: str

    # Action details
    action_type: str
    target_service: str
    parameters: Dict[str, Any]
    priority: str
    controller_name: str
    reason: str

    # Execution context
    timestamp: str
    execution_start: float
    execution_end: Optional[float]
    execution_duration: Optional[float]

    # Results and effects
    success: bool
    message: str
    rollback_data: Optional[Dict[str, Any]]
    immediate_effects: Dict[str, Any]

    # Stability metrics context
    pre_action_metrics: Dict[str, Any]
    post_action_metrics: Optional[Dict[str, Any]]
    steady_state_metrics: Optional[Dict[str, Any]]
    steady_state_achieved: Optional[bool]
    steady_state_timestamp: Optional[str]

    # Diagnostic data
    controller_state: Dict[str, Any]
    system_health_impact: Optional[float]
    effectiveness_score: Optional[float]
    unintended_consequences: List[str]

    # Correlation tracking
    triggered_by: Optional[str]  # trace_id of action that caused this one
    triggers: List[str]  # trace_ids of actions this one triggered
    cluster_id: Optional[str]  # for grouping related actions


@dataclass
class CorrelationChain:
    """Tracks correlation chains for action → effect → steady-state analysis."""

    chain_id: str
    root_trace_id: str
    actions: List[str]  # trace_ids in chronological order
    start_timestamp: str
    end_timestamp: Optional[str]
    chain_status: str  # "active", "stabilized", "failed", "timeout"
    final_effectiveness: Optional[float]
    lessons_learned: List[str]


class HomeostasisAuditLayer:
    """
    Advanced audit and trace system for homeostasis actions.

    Provides comprehensive logging, correlation tracking, and deep diagnostics
    for all homeostasis controller actions and their effects.
    """

    def __init__(
        self,
        db_path: str = "homeostasis_audit.db",
        introspection_db_path: str = "introspection.db",
        enable_wal: bool = True,
    ):
        self.db_path = Path(db_path)
        self.introspection_db_path = Path(introspection_db_path)
        self.enable_wal = enable_wal

        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.active_traces: Dict[str, ActionTrace] = {}
        self.correlation_chains: Dict[str, CorrelationChain] = {}

        # Performance tracking
        self.traces_written = 0
        self.correlation_updates = 0
        self.effectiveness_calculations = 0

        # Thread safety
        self._lock = threading.RLock()

        self._init_database()

        logger.info(f"🔍 Homeostasis Audit Layer initialized (session: {self.session_id[:8]})")

    def _init_database(self):
        """Initialize the audit database with comprehensive schema."""
        with sqlite3.connect(self.db_path) as conn:
            if self.enable_wal:
                try:
                    conn.execute("PRAGMA journal_mode=WAL;")
                    conn.execute("PRAGMA synchronous=NORMAL;")
                    conn.execute("PRAGMA busy_timeout=5000;")
                    logger.debug("✅ WAL mode enabled for audit database")
                except Exception as e:
                    logger.warning(f"⚠️ Could not enable WAL mode: {e}")

            # Action traces table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT UNIQUE NOT NULL,
                    correlation_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    target_service TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    controller_name TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    execution_start REAL NOT NULL,
                    execution_end REAL,
                    execution_duration REAL,
                    success BOOLEAN NOT NULL,
                    message TEXT NOT NULL,
                    rollback_data_json TEXT,
                    immediate_effects_json TEXT NOT NULL,
                    pre_action_metrics_json TEXT NOT NULL,
                    post_action_metrics_json TEXT,
                    steady_state_metrics_json TEXT,
                    steady_state_achieved BOOLEAN,
                    steady_state_timestamp TEXT,
                    controller_state_json TEXT NOT NULL,
                    system_health_impact REAL,
                    effectiveness_score REAL,
                    unintended_consequences_json TEXT NOT NULL,
                    triggered_by TEXT,
                    triggers_json TEXT NOT NULL,
                    cluster_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Correlation chains table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS correlation_chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chain_id TEXT UNIQUE NOT NULL,
                    root_trace_id TEXT NOT NULL,
                    actions_json TEXT NOT NULL,
                    start_timestamp TEXT NOT NULL,
                    end_timestamp TEXT,
                    chain_status TEXT NOT NULL,
                    final_effectiveness REAL,
                    lessons_learned_json TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Effectiveness metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS effectiveness_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    pre_value REAL NOT NULL,
                    target_value REAL NOT NULL,
                    post_value REAL,
                    final_value REAL,
                    improvement_ratio REAL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (trace_id) REFERENCES action_traces (trace_id)
                )
            """)

            # Create indexes for performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_correlation ON action_traces (correlation_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_timestamp ON action_traces (timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_session ON action_traces (session_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_traces_action_type ON action_traces (action_type)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chains_status ON correlation_chains (chain_status)"
            )

            conn.commit()

    async def start_action_trace(
        self,
        action_type: str,
        target_service: str,
        parameters: Dict[str, Any],
        priority: str,
        controller_name: str,
        reason: str,
        controller_state: Dict[str, Any],
        pre_action_metrics: Dict[str, Any],
        triggered_by: Optional[str] = None,
    ) -> str:
        """
        Start tracing a new homeostasis action.

        Returns the trace_id for correlation tracking.
        """
        trace_id = str(uuid.uuid4())
        correlation_id = triggered_by or str(uuid.uuid4())

        trace = ActionTrace(
            trace_id=trace_id,
            correlation_id=correlation_id,
            session_id=self.session_id,
            action_type=action_type,
            target_service=target_service,
            parameters=parameters,
            priority=priority,
            controller_name=controller_name,
            reason=reason,
            timestamp=datetime.now().isoformat(),
            execution_start=time.time(),
            execution_end=None,
            execution_duration=None,
            success=False,  # Will be updated on completion
            message="Action in progress",
            rollback_data=None,
            immediate_effects={},
            pre_action_metrics=pre_action_metrics,
            post_action_metrics=None,
            steady_state_metrics=None,
            steady_state_achieved=None,
            steady_state_timestamp=None,
            controller_state=controller_state,
            system_health_impact=None,
            effectiveness_score=None,
            unintended_consequences=[],
            triggered_by=triggered_by,
            triggers=[],
            cluster_id=None,
        )

        with self._lock:
            self.active_traces[trace_id] = trace

            # Start or extend correlation chain
            if triggered_by:
                await self._extend_correlation_chain(triggered_by, trace_id)
            else:
                await self._start_correlation_chain(trace_id)

        logger.debug(f"🔍 Started action trace {trace_id[:8]} for {action_type}")
        return trace_id

    async def complete_action_trace(
        self,
        trace_id: str,
        success: bool,
        message: str,
        rollback_data: Optional[Dict[str, Any]] = None,
        immediate_effects: Optional[Dict[str, Any]] = None,
        post_action_metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Complete an action trace with results."""
        with self._lock:
            if trace_id not in self.active_traces:
                logger.error(f"❌ Trace {trace_id[:8]} not found in active traces")
                return False

            trace = self.active_traces[trace_id]

            # Update trace with completion data
            trace.execution_end = time.time()
            trace.execution_duration = trace.execution_end - trace.execution_start
            trace.success = success
            trace.message = message
            trace.rollback_data = rollback_data or {}
            trace.immediate_effects = immediate_effects or {}
            trace.post_action_metrics = post_action_metrics or {}

            # Calculate immediate effectiveness if we have post metrics
            if post_action_metrics:
                trace.effectiveness_score = await self._calculate_immediate_effectiveness(trace)

            # Persist to database
            await self._persist_trace(trace)

            # Move from active to completed
            del self.active_traces[trace_id]

            self.traces_written += 1

            logger.debug(f"🔍 Completed action trace {trace_id[:8]} - {'✅' if success else '❌'}")
            return True

    async def update_steady_state_metrics(
        self, trace_id: str, steady_state_metrics: Dict[str, Any], steady_state_achieved: bool
    ) -> bool:
        """Update trace with steady-state analysis results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE action_traces
                    SET steady_state_metrics_json = ?,
                        steady_state_achieved = ?,
                        steady_state_timestamp = ?
                    WHERE trace_id = ?
                """,
                    (
                        json.dumps(steady_state_metrics),
                        steady_state_achieved,
                        datetime.now().isoformat(),
                        trace_id,
                    ),
                )

                # Recalculate final effectiveness
                final_effectiveness = await self._calculate_final_effectiveness(trace_id)
                if final_effectiveness is not None:
                    conn.execute(
                        """
                        UPDATE action_traces
                        SET effectiveness_score = ?
                        WHERE trace_id = ?
                    """,
                        (final_effectiveness, trace_id),
                    )

                conn.commit()

                # Update correlation chain if this completes it
                await self._check_correlation_chain_completion(trace_id)

                logger.debug(f"🔍 Updated steady state for trace {trace_id[:8]}")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to update steady state for trace {trace_id[:8]}: {e}")
            return False

    async def add_correlation(self, parent_trace_id: str, child_trace_id: str) -> bool:
        """Add correlation between actions (parent triggered child)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Update parent's triggers list
                cursor = conn.execute(
                    """
                    SELECT triggers_json FROM action_traces WHERE trace_id = ?
                """,
                    (parent_trace_id,),
                )

                row = cursor.fetchone()
                if not row:
                    logger.error(f"❌ Parent trace {parent_trace_id[:8]} not found")
                    return False

                triggers = json.loads(row[0])
                if child_trace_id not in triggers:
                    triggers.append(child_trace_id)

                    conn.execute(
                        """
                        UPDATE action_traces
                        SET triggers_json = ?
                        WHERE trace_id = ?
                    """,
                        (json.dumps(triggers), parent_trace_id),
                    )

                # Update child's triggered_by
                conn.execute(
                    """
                    UPDATE action_traces
                    SET triggered_by = ?
                    WHERE trace_id = ?
                """,
                    (parent_trace_id, child_trace_id),
                )

                conn.commit()

                self.correlation_updates += 1
                logger.debug(f"🔍 Added correlation: {parent_trace_id[:8]} → {child_trace_id[:8]}")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to add correlation: {e}")
            return False

    async def get_action_history(
        self, limit: int = 100, action_type: Optional[str] = None, success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get action history with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM action_traces
                    WHERE 1=1
                """
                params: List[Any] = []

                if action_type:
                    query += " AND action_type = ?"
                    params.append(action_type)

                if success_only:
                    query += " AND success = 1"

                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                # Convert to dictionaries
                columns = [desc[0] for desc in cursor.description]
                history = []

                for row in rows:
                    record = dict(zip(columns, row, strict=True))
                    # Parse JSON fields
                    for json_field in [
                        "parameters_json",
                        "immediate_effects_json",
                        "pre_action_metrics_json",
                        "post_action_metrics_json",
                        "steady_state_metrics_json",
                        "rollback_data_json",
                        "controller_state_json",
                        "unintended_consequences_json",
                        "triggers_json",
                    ]:
                        if record.get(json_field):
                            try:
                                record[json_field[:-5]] = json.loads(record[json_field])
                            except Exception:
                                record[json_field[:-5]] = {}

                    history.append(record)

                return history

        except Exception as e:
            logger.error(f"❌ Failed to get action history: {e}")
            return []

    async def get_correlation_chain(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get the complete correlation chain for a trace."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Find the correlation chain
                cursor = conn.execute(
                    """
                    SELECT chain_id FROM action_traces WHERE trace_id = ?
                """,
                    (trace_id,),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                correlation_id = row[0]

                # Get all actions in the chain
                cursor = conn.execute(
                    """
                    SELECT * FROM action_traces
                    WHERE correlation_id = ?
                    ORDER BY timestamp ASC
                """,
                    (correlation_id,),
                )

                actions = []
                columns = [desc[0] for desc in cursor.description]

                for row in cursor.fetchall():
                    action = dict(zip(columns, row, strict=True))
                    actions.append(action)

                # Get chain metadata
                cursor = conn.execute(
                    """
                    SELECT * FROM correlation_chains WHERE chain_id = ?
                """,
                    (correlation_id,),
                )

                chain_row = cursor.fetchone()
                chain_data = {}

                if chain_row:
                    chain_columns = [desc[0] for desc in cursor.description]
                    chain_data = dict(zip(chain_columns, chain_row, strict=True))

                return {
                    "chain_id": correlation_id,
                    "chain_metadata": chain_data,
                    "actions": actions,
                    "total_actions": len(actions),
                    "chain_duration": self._calculate_chain_duration(actions),
                }

        except Exception as e:
            logger.error(f"❌ Failed to get correlation chain: {e}")
            return None

    async def get_effectiveness_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get effectiveness analytics for the specified period."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                # Overall statistics
                cursor = conn.execute(
                    """
                    SELECT
                        COUNT(*) as total_actions,
                        AVG(effectiveness_score) as avg_effectiveness,
                        COUNT(CASE WHEN success = 1 THEN 1 END) as successful_actions,
                        COUNT(CASE WHEN steady_state_achieved = 1 THEN 1 END) as steady_state_achieved,
                        AVG(execution_duration) as avg_execution_time
                    FROM action_traces
                    WHERE timestamp > ?
                """,
                    (cutoff_date,),
                )

                stats = dict(
                    zip([desc[0] for desc in cursor.description], cursor.fetchone(), strict=True)
                )

                # Per-action-type breakdown
                cursor = conn.execute(
                    """
                    SELECT
                        action_type,
                        COUNT(*) as count,
                        AVG(effectiveness_score) as avg_effectiveness,
                        COUNT(CASE WHEN success = 1 THEN 1 END) / CAST(COUNT(*) AS FLOAT) as success_rate
                    FROM action_traces
                    WHERE timestamp > ?
                    GROUP BY action_type
                    ORDER BY count DESC
                """,
                    (cutoff_date,),
                )

                action_breakdown = []
                for row in cursor.fetchall():
                    action_breakdown.append(
                        dict(zip([desc[0] for desc in cursor.description], row, strict=True))
                    )

                # Correlation chain effectiveness
                cursor = conn.execute(
                    """
                    SELECT
                        chain_status,
                        COUNT(*) as count,
                        AVG(final_effectiveness) as avg_final_effectiveness
                    FROM correlation_chains
                    WHERE start_timestamp > ?
                    GROUP BY chain_status
                """,
                    (cutoff_date,),
                )

                chain_stats = []
                for row in cursor.fetchall():
                    chain_stats.append(
                        dict(zip([desc[0] for desc in cursor.description], row, strict=True))
                    )

                return {
                    "period_days": days,
                    "overall_statistics": stats,
                    "action_type_breakdown": action_breakdown,
                    "correlation_chain_statistics": chain_stats,
                    "total_traces_written": self.traces_written,
                    "total_correlation_updates": self.correlation_updates,
                    "effectiveness_calculations": self.effectiveness_calculations,
                }

        except Exception as e:
            logger.error(f"❌ Failed to get effectiveness analytics: {e}")
            return {"error": str(e)}

    # Private helper methods

    async def _persist_trace(self, trace: ActionTrace):
        """Persist action trace to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO action_traces (
                        trace_id, correlation_id, session_id, action_type, target_service,
                        parameters_json, priority, controller_name, reason, timestamp,
                        execution_start, execution_end, execution_duration, success, message,
                        rollback_data_json, immediate_effects_json, pre_action_metrics_json,
                        post_action_metrics_json, steady_state_metrics_json, steady_state_achieved,
                        steady_state_timestamp, controller_state_json, system_health_impact,
                        effectiveness_score, unintended_consequences_json, triggered_by,
                        triggers_json, cluster_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        trace.trace_id,
                        trace.correlation_id,
                        trace.session_id,
                        trace.action_type,
                        trace.target_service,
                        json.dumps(trace.parameters),
                        trace.priority,
                        trace.controller_name,
                        trace.reason,
                        trace.timestamp,
                        trace.execution_start,
                        trace.execution_end,
                        trace.execution_duration,
                        trace.success,
                        trace.message,
                        json.dumps(trace.rollback_data or {}),
                        json.dumps(trace.immediate_effects),
                        json.dumps(trace.pre_action_metrics),
                        json.dumps(trace.post_action_metrics or {}),
                        json.dumps(trace.steady_state_metrics or {}),
                        trace.steady_state_achieved,
                        trace.steady_state_timestamp,
                        json.dumps(trace.controller_state),
                        trace.system_health_impact,
                        trace.effectiveness_score,
                        json.dumps(trace.unintended_consequences),
                        trace.triggered_by,
                        json.dumps(trace.triggers),
                        trace.cluster_id,
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to persist trace {trace.trace_id[:8]}: {e}")

    async def _start_correlation_chain(self, root_trace_id: str):
        """Start a new correlation chain."""
        chain_id = str(uuid.uuid4())

        chain = CorrelationChain(
            chain_id=chain_id,
            root_trace_id=root_trace_id,
            actions=[root_trace_id],
            start_timestamp=datetime.now().isoformat(),
            end_timestamp=None,
            chain_status="active",
            final_effectiveness=None,
            lessons_learned=[],
        )

        self.correlation_chains[chain_id] = chain

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO correlation_chains (
                        chain_id, root_trace_id, actions_json, start_timestamp,
                        chain_status, lessons_learned_json
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        chain_id,
                        root_trace_id,
                        json.dumps([root_trace_id]),
                        chain.start_timestamp,
                        "active",
                        json.dumps([]),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to start correlation chain: {e}")

    async def _extend_correlation_chain(self, parent_trace_id: str, child_trace_id: str):
        """Extend an existing correlation chain."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT correlation_id FROM action_traces WHERE trace_id = ?
                """,
                    (parent_trace_id,),
                )

                row = cursor.fetchone()
                if not row:
                    return

                correlation_id = row[0]

                # Update chain with new action
                cursor = conn.execute(
                    """
                    SELECT actions_json FROM correlation_chains WHERE chain_id = ?
                """,
                    (correlation_id,),
                )

                chain_row = cursor.fetchone()
                if chain_row:
                    actions = json.loads(chain_row[0])
                    actions.append(child_trace_id)

                    conn.execute(
                        """
                        UPDATE correlation_chains
                        SET actions_json = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE chain_id = ?
                    """,
                        (json.dumps(actions), correlation_id),
                    )

                    conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to extend correlation chain: {e}")

    async def _calculate_immediate_effectiveness(self, trace: ActionTrace) -> Optional[float]:
        """Calculate immediate effectiveness score based on metric improvements."""
        try:
            if not trace.post_action_metrics or not trace.pre_action_metrics:
                return None

            # Extract key stability metrics
            pre_metrics = trace.pre_action_metrics
            post_metrics = trace.post_action_metrics

            improvements = []

            # Check common stability metrics
            metric_keys = [
                "stability_score",
                "health_score",
                "error_rate",
                "response_time",
                "memory_usage",
            ]

            for key in metric_keys:
                if key in pre_metrics and key in post_metrics:
                    pre_val = pre_metrics[key]
                    post_val = post_metrics[key]

                    # For metrics where lower is better (error_rate, memory_usage)
                    if key in ["error_rate", "memory_usage", "response_time"]:
                        improvement = (pre_val - post_val) / pre_val if pre_val > 0 else 0.0
                    else:
                        # For metrics where higher is better
                        improvement = (post_val - pre_val) / pre_val if pre_val > 0 else 0.0

                    improvements.append(max(-1.0, min(1.0, improvement)))  # Clamp to [-1, 1]

            if improvements:
                self.effectiveness_calculations += 1
                return float(sum(improvements) / len(improvements))

            return None

        except Exception as e:
            logger.error(f"❌ Failed to calculate effectiveness: {e}")
            return None

    async def _calculate_final_effectiveness(self, trace_id: str) -> Optional[float]:
        """Calculate final effectiveness including steady-state analysis."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT pre_action_metrics_json, post_action_metrics_json,
                           steady_state_metrics_json, steady_state_achieved
                    FROM action_traces WHERE trace_id = ?
                """,
                    (trace_id,),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                pre_metrics = json.loads(row[0])
                post_metrics = json.loads(row[1] or "{}")
                steady_achieved = row[3]

                # Base effectiveness on immediate results
                immediate_score = 0.0
                if post_metrics:
                    # Similar calculation to immediate effectiveness
                    improvements = []
                    metric_keys = ["stability_score", "health_score", "error_rate", "response_time"]

                    for key in metric_keys:
                        if key in pre_metrics and key in post_metrics:
                            pre_val = pre_metrics[key]
                            post_val = post_metrics[key]

                            if key in ["error_rate", "response_time"]:
                                improvement = (pre_val - post_val) / pre_val if pre_val > 0 else 0.0
                            else:
                                improvement = (post_val - pre_val) / pre_val if pre_val > 0 else 0.0

                            improvements.append(max(-1.0, min(1.0, improvement)))

                    if improvements:
                        immediate_score = sum(improvements) / len(improvements)

                # Apply steady state multiplier
                final_score = immediate_score
                if steady_achieved:
                    # Bonus for achieving steady state
                    final_score *= 1.2
                elif steady_achieved is False:
                    # Penalty for not achieving steady state
                    final_score *= 0.8

                return max(-1.0, min(1.0, final_score))

        except Exception as e:
            logger.error(f"❌ Failed to calculate final effectiveness: {e}")
            return None

    async def _check_correlation_chain_completion(self, trace_id: str):
        """Check if a correlation chain should be marked as completed."""
        # This is a simplified version - in practice, you'd have more sophisticated
        # logic to determine when a chain is "complete"
        actions = self.correlation_chains.get(trace_id, [])
        if not actions:
            return False
        completion_threshold = 3
        return len(actions) >= completion_threshold

    def _calculate_chain_duration(self, actions: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate the duration of a correlation chain."""
        if len(actions) < 2:
            return None

        try:
            start_time = datetime.fromisoformat(actions[0]["timestamp"])
            end_time = datetime.fromisoformat(actions[-1]["timestamp"])
            return (end_time - start_time).total_seconds()
        except Exception:
            return None


# Global singleton for easy access
_audit_layer_instance: Optional[HomeostasisAuditLayer] = None
_audit_layer_lock = threading.Lock()


def get_audit_layer() -> HomeostasisAuditLayer:
    """Get the global audit layer instance."""
    global _audit_layer_instance

    if _audit_layer_instance is None:
        with _audit_layer_lock:
            if _audit_layer_instance is None:
                _audit_layer_instance = HomeostasisAuditLayer()

    return _audit_layer_instance


def initialize_audit_layer(
    db_path: str = "homeostasis_audit.db", introspection_db_path: str = "introspection.db"
) -> HomeostasisAuditLayer:
    """Initialize the global audit layer with custom paths."""
    global _audit_layer_instance

    with _audit_layer_lock:
        _audit_layer_instance = HomeostasisAuditLayer(
            db_path=db_path, introspection_db_path=introspection_db_path
        )

    return _audit_layer_instance
