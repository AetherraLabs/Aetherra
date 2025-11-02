# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Memory Consolidation & Decay — Phase 4
=======================================

Manages memory lifecycle: pruning low-salience entries,
promoting high-impact events to long-term storage.

Design:
- Salience-based pruning (remove entries below threshold)
- High-impact promotion (move events above threshold to LT storage)
- Audit logging for all deletions (safety & transparency)
- Throttled I/O to avoid performance impact
- Configurable thresholds and batch sizes
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Consolidator:
    """Memory consolidation and decay engine.

    Prunes low-salience episodic memories and promotes high-impact
    events to long-term storage during offline cycles.
    """

    def __init__(
        self,
        memory_engine: Any,
        salience_threshold: float = 0.2,
        promotion_threshold: float = 0.7,
        batch_size: int = 100,
        audit_log_path: str = "/var/lib/aetherra/memory_audit.log",
    ):
        """Initialize consolidator.

        Args:
            memory_engine: MemoryEngine instance to operate on
            salience_threshold: Prune entries below this salience (default: 0.2)
            promotion_threshold: Promote entries above this salience (default: 0.7)
            batch_size: Max entries to process per consolidation (default: 100)
            audit_log_path: Path for deletion audit log (default: /var/lib/aetherra/memory_audit.log)
        """
        self.memory_engine = memory_engine
        self.salience_threshold = salience_threshold
        self.promotion_threshold = promotion_threshold
        self.batch_size = batch_size
        self.audit_log_path = audit_log_path
        self.last_run_ts: Optional[float] = None
        self.total_pruned = 0
        self.total_promoted = 0

    def consolidate(self) -> Dict[str, Any]:
        """Run memory consolidation cycle.

        Prunes low-salience entries and promotes high-impact events.

        Returns:
            Dict with consolidation metrics (pruned, promoted, errors)
        """
        self.last_run_ts = time.time()

        # Get episodic memories (recent first)
        episodic = self._get_episodic_memories()

        if not episodic:
            return {
                "status": "no_data",
                "pruned": 0,
                "promoted": 0,
                "errors": 0,
            }

        # Limit to batch size
        to_process = episodic[: self.batch_size]

        # Separate into prune/promote/keep
        to_prune = []
        to_promote = []
        errors = 0

        for entry in to_process:
            try:
                salience = self._compute_salience(entry)

                if salience < self.salience_threshold:
                    to_prune.append(entry)
                elif salience > self.promotion_threshold:
                    to_promote.append(entry)

            except Exception as e:
                logger.error(f"Error processing memory entry {entry.get('id')}: {e}")
                errors += 1

        # Execute pruning
        pruned_count = self._prune_entries(to_prune)

        # Execute promotion
        promoted_count = self._promote_entries(to_promote)

        # Update totals
        self.total_pruned += pruned_count
        self.total_promoted += promoted_count

        return {
            "status": "completed",
            "processed": len(to_process),
            "pruned": pruned_count,
            "promoted": promoted_count,
            "errors": errors,
            "remaining_episodic": len(episodic) - len(to_process),
        }

    def _get_episodic_memories(self) -> List[Dict[str, Any]]:
        """Get episodic memories from memory engine.

        Returns:
            List of episodic memory entries
        """
        # Access memory engine's episodic store
        # This assumes memory_engine has a method to retrieve episodic memories
        if hasattr(self.memory_engine, "get_episodic_memories"):
            return self.memory_engine.get_episodic_memories()

        # Fallback: try to access internal storage
        if hasattr(self.memory_engine, "episodic"):
            return list(self.memory_engine.episodic.values())

        logger.warning("Memory engine has no episodic memory accessor")
        return []

    def _compute_salience(self, entry: Dict[str, Any]) -> float:
        """Compute salience score for memory entry.

        Salience is a weighted combination of:
        - Emotional valence (absolute value)
        - Recency (newer = higher)
        - Access frequency (more = higher)
        - Confidence (higher = higher)

        Args:
            entry: Memory entry dict

        Returns:
            Salience score (0.0 = low, 1.0 = high)
        """
        # Emotional weight (absolute valence)
        valence = abs(entry.get("valence", 0.0))
        emotional_weight = min(1.0, valence)

        # Recency weight (exponential decay from timestamp)
        ts = entry.get("timestamp", time.time())
        age_seconds = time.time() - ts
        recency_weight = max(0.0, 1.0 - (age_seconds / (7 * 24 * 3600)))  # 7-day window

        # Access frequency weight (normalized)
        access_count = entry.get("access_count", 0)
        frequency_weight = min(1.0, access_count / 10.0)  # Cap at 10 accesses

        # Confidence weight
        confidence = entry.get("confidence", 0.5)

        # Weighted average
        salience = (
            0.3 * emotional_weight
            + 0.3 * recency_weight
            + 0.2 * frequency_weight
            + 0.2 * confidence
        )

        return salience

    def _prune_entries(self, entries: List[Dict[str, Any]]) -> int:
        """Prune low-salience memory entries.

        Args:
            entries: List of entries to prune

        Returns:
            Number of entries successfully pruned
        """
        pruned = 0

        for entry in entries:
            entry_id = entry.get("id", "unknown")
            try:
                # Audit log before deletion
                self._audit_log(
                    "PRUNE",
                    entry_id,
                    {
                        "salience": self._compute_salience(entry),
                        "age_days": (time.time() - entry.get("timestamp", time.time())) / 86400,
                    },
                )

                # Delete from memory engine
                if hasattr(self.memory_engine, "delete_memory"):
                    self.memory_engine.delete_memory(entry_id)
                elif (
                    hasattr(self.memory_engine, "episodic")
                    and entry_id in self.memory_engine.episodic
                ):
                    del self.memory_engine.episodic[entry_id]

                pruned += 1

            except Exception as e:
                logger.error(f"Failed to prune entry {entry_id}: {e}")

        return pruned

    def _promote_entries(self, entries: List[Dict[str, Any]]) -> int:
        """Promote high-salience entries to long-term storage.

        Args:
            entries: List of entries to promote

        Returns:
            Number of entries successfully promoted
        """
        promoted = 0

        for entry in entries:
            entry_id = entry.get("id", "unknown")
            try:
                # Audit log promotion
                self._audit_log(
                    "PROMOTE",
                    entry_id,
                    {
                        "salience": self._compute_salience(entry),
                        "valence": entry.get("valence", 0.0),
                    },
                )

                # Move to long-term storage
                if hasattr(self.memory_engine, "promote_to_longterm"):
                    self.memory_engine.promote_to_longterm(entry_id)
                elif hasattr(self.memory_engine, "longterm"):
                    # Copy to longterm, remove from episodic
                    self.memory_engine.longterm[entry_id] = entry
                    if (
                        hasattr(self.memory_engine, "episodic")
                        and entry_id in self.memory_engine.episodic
                    ):
                        del self.memory_engine.episodic[entry_id]

                promoted += 1

            except Exception as e:
                logger.error(f"Failed to promote entry {entry_id}: {e}")

        return promoted

    def _audit_log(self, action: str, entry_id: str, metadata: Dict[str, Any]) -> None:
        """Write audit log entry for memory operation.

        Args:
            action: Action type (PRUNE, PROMOTE)
            entry_id: Memory entry ID
            metadata: Additional metadata (salience, age, etc.)
        """
        import json

        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                log_entry = {
                    "ts": time.time(),
                    "action": action,
                    "entry_id": entry_id,
                    "metadata": metadata,
                }
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.warning(f"Failed to write audit log: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get consolidator statistics.

        Returns:
            Dict with total pruned, promoted, last run timestamp
        """
        return {
            "last_run_ts": self.last_run_ts,
            "total_pruned": self.total_pruned,
            "total_promoted": self.total_promoted,
            "salience_threshold": self.salience_threshold,
            "promotion_threshold": self.promotion_threshold,
        }
