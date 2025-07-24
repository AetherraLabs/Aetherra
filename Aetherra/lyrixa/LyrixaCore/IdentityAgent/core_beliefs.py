"""
Core Beliefs Module - Fundamental Guiding Values System
Part of LyrixaCore IdentityAgent for Phase 6: Unified Cognitive Stack

This module manages Lyrixa's fundamental value system that guides all decisions
and ensures consistency across different cognitive subsystems.
"""

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class BeliefUpdate:
    """Record of belief value changes over time"""

    timestamp: float
    belief: str
    old_value: float
    new_value: float
    reason: str
    confidence: float


class CoreBeliefs:
    """
    Fundamental value system that guides all cognitive processes.

    These beliefs form the ethical and operational foundation for Lyrixa's
    decision-making across memory, ethics, curiosity, and reflection systems.
    """

    def __init__(self, db_path: str = "identity_core.db"):
        """Initialize core beliefs system with persistent storage"""
        self.db_path = db_path
        self.values = {
            "helpfulness": 1.0,  # Drive to assist and provide value
            "truthfulness": 1.0,  # Commitment to accuracy and honesty
            "harmlessness": 1.0,  # Avoid causing harm or negative outcomes
            "fairness": 0.9,  # Equitable treatment and justice
            "privacy": 0.9,  # Respect for user privacy and boundaries
            "autonomy": 0.95,  # Respect for user agency and choice
            "growth": 1.0,  # Commitment to learning and improvement
            "transparency": 0.85,  # Openness about capabilities and limitations
            "reliability": 1.0,  # Consistency and dependability
            "respect": 0.95,  # Dignity and consideration for all users
        }

        self.update_history: List[BeliefUpdate] = []
        self.belief_weights = {
            "helpfulness": 1.0,
            "truthfulness": 1.2,  # Slightly higher weight for truth
            "harmlessness": 1.3,  # Highest weight for safety
            "fairness": 1.0,
            "privacy": 1.1,
            "autonomy": 1.0,
            "growth": 0.9,
            "transparency": 0.8,
            "reliability": 1.1,
            "respect": 1.0,
        }

        # Initialize database
        self._init_database()
        self._load_from_database()

    def _init_database(self):
        """Initialize SQLite database for persistent belief storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS core_beliefs (
                        belief TEXT PRIMARY KEY,
                        value REAL NOT NULL,
                        last_updated REAL NOT NULL,
                        update_count INTEGER DEFAULT 0
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS belief_updates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        belief TEXT NOT NULL,
                        old_value REAL NOT NULL,
                        new_value REAL NOT NULL,
                        reason TEXT NOT NULL,
                        confidence REAL NOT NULL
                    )
                """)

                conn.commit()
        except Exception as e:
            print(f"[CoreBeliefs] Database initialization error: {e}")

    def _load_from_database(self):
        """Load beliefs from persistent storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT belief, value FROM core_beliefs")
                stored_beliefs = dict(cursor.fetchall())

                # Update values with stored data
                for belief, value in stored_beliefs.items():
                    if belief in self.values:
                        self.values[belief] = value

                # Load update history
                cursor = conn.execute("""
                    SELECT timestamp, belief, old_value, new_value, reason, confidence
                    FROM belief_updates
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)

                self.update_history = [
                    BeliefUpdate(
                        timestamp, belief, old_value, new_value, reason, confidence
                    )
                    for timestamp, belief, old_value, new_value, reason, confidence in cursor.fetchall()
                ]

        except Exception as e:
            print(f"[CoreBeliefs] Database loading error: {e}")

    def _save_to_database(self):
        """Save current beliefs to persistent storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                current_time = time.time()

                for belief, value in self.values.items():
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO core_beliefs (belief, value, last_updated, update_count)
                        VALUES (?, ?, ?, COALESCE((SELECT update_count FROM core_beliefs WHERE belief = ?) + 1, 1))
                    """,
                        (belief, value, current_time, belief),
                    )

                conn.commit()
        except Exception as e:
            print(f"[CoreBeliefs] Database saving error: {e}")

    def get_score(self, belief: str) -> float:
        """Get the current value for a specific belief"""
        return self.values.get(belief, 0.0)

    def get_weighted_score(self, belief: str) -> float:
        """Get belief score adjusted by importance weight"""
        base_score = self.get_score(belief)
        weight = self.belief_weights.get(belief, 1.0)
        return base_score * weight

    def update_belief(
        self,
        belief: str,
        delta: float,
        reason: str = "manual_adjustment",
        confidence: float = 1.0,
    ):
        """
        Update a belief value with change tracking

        Args:
            belief: Name of the belief to update
            delta: Change in value (-1.0 to +1.0)
            reason: Explanation for the change
            confidence: Confidence in this update (0.0 to 1.0)
        """
        if belief not in self.values:
            print(f"[CoreBeliefs] Unknown belief: {belief}")
            return False

        old_value = self.values[belief]
        new_value = max(0.0, min(1.0, old_value + delta))

        # Only update if there's an actual change
        if abs(new_value - old_value) > 0.001:
            self.values[belief] = new_value

            # Record the update
            update = BeliefUpdate(
                timestamp=time.time(),
                belief=belief,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
                confidence=confidence,
            )
            self.update_history.append(update)

            # Save to database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO belief_updates (timestamp, belief, old_value, new_value, reason, confidence)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            update.timestamp,
                            update.belief,
                            update.old_value,
                            update.new_value,
                            update.reason,
                            update.confidence,
                        ),
                    )
                    conn.commit()
            except Exception as e:
                print(f"[CoreBeliefs] Update recording error: {e}")

            self._save_to_database()

            print(
                f"[CoreBeliefs] Updated {belief}: {old_value:.3f} → {new_value:.3f} ({reason})"
            )
            return True

        return False

    def evaluate_decision_alignment(self, decision_context: Dict) -> float:
        """
        Evaluate how well a decision aligns with core beliefs

        Args:
            decision_context: Dictionary containing decision details and affected values

        Returns:
            Alignment score (0.0 to 1.0)
        """
        total_alignment = 0.0
        total_weight = 0.0

        for belief, impact in decision_context.get("belief_impacts", {}).items():
            if belief in self.values:
                belief_strength = self.get_weighted_score(belief)
                alignment_contribution = belief_strength * max(
                    0, impact
                )  # Only positive impacts count
                total_alignment += alignment_contribution
                total_weight += self.belief_weights.get(belief, 1.0)

        return total_alignment / max(total_weight, 1.0) if total_weight > 0 else 0.5

    def detect_belief_conflicts(
        self, threshold: float = 0.3
    ) -> List[Tuple[str, str, float]]:
        """
        Detect potential conflicts between beliefs based on recent updates

        Returns:
            List of (belief1, belief2, conflict_score) tuples
        """
        conflicts = []

        # Check for opposing trends in recent updates
        recent_updates = [
            u for u in self.update_history if time.time() - u.timestamp < 86400 * 7
        ]  # Last week

        belief_trends = {}
        for update in recent_updates:
            if update.belief not in belief_trends:
                belief_trends[update.belief] = []
            belief_trends[update.belief].append(update.new_value - update.old_value)

        # Calculate average trends
        for belief in belief_trends:
            belief_trends[belief] = sum(belief_trends[belief]) / len(
                belief_trends[belief]
            )

        # Check for conflicting pairs
        conflict_pairs = [
            ("privacy", "transparency"),
            ("autonomy", "helpfulness"),
            ("fairness", "efficiency"),
            ("harmlessness", "truthfulness"),
        ]

        for belief1, belief2 in conflict_pairs:
            if belief1 in belief_trends and belief2 in belief_trends:
                trend1 = belief_trends[belief1]
                trend2 = belief_trends[belief2]

                # Conflict if trends are strongly opposite
                if abs(trend1 + trend2) > threshold and trend1 * trend2 < 0:
                    conflict_score = abs(trend1 + trend2)
                    conflicts.append((belief1, belief2, conflict_score))

        return conflicts

    def get_belief_summary(self) -> Dict:
        """Get comprehensive summary of current belief state"""
        return {
            "values": self.values.copy(),
            "weighted_scores": {k: self.get_weighted_score(k) for k in self.values},
            "recent_updates": len(
                [u for u in self.update_history if time.time() - u.timestamp < 86400]
            ),
            "stability_score": self._calculate_stability_score(),
            "conflicts": self.detect_belief_conflicts(),
            "last_updated": max([u.timestamp for u in self.update_history])
            if self.update_history
            else time.time(),
        }

    def _calculate_stability_score(self) -> float:
        """Calculate how stable beliefs have been recently"""
        if not self.update_history:
            return 1.0

        recent_updates = [
            u for u in self.update_history if time.time() - u.timestamp < 86400 * 7
        ]

        if not recent_updates:
            return 1.0

        # Calculate variance in updates
        total_change = sum(abs(u.new_value - u.old_value) for u in recent_updates)
        stability = 1.0 - min(total_change / len(recent_updates), 1.0)

        return stability

    def suggest_belief_adjustments(self) -> List[Dict]:
        """Suggest potential belief adjustments based on recent patterns"""
        suggestions = []

        # Check for beliefs that haven't been updated recently
        current_time = time.time()
        belief_last_updated = {}

        for update in self.update_history:
            if update.belief not in belief_last_updated:
                belief_last_updated[update.belief] = update.timestamp

        for belief in self.values:
            if (
                belief not in belief_last_updated
                or current_time - belief_last_updated[belief] > 86400 * 30
            ):
                suggestions.append(
                    {
                        "type": "stale_belief",
                        "belief": belief,
                        "current_value": self.values[belief],
                        "suggestion": "Consider reviewing this belief - it hasn't been updated recently",
                        "priority": "low",
                    }
                )

        # Check for extreme values
        for belief, value in self.values.items():
            if value < 0.3:
                suggestions.append(
                    {
                        "type": "low_value",
                        "belief": belief,
                        "current_value": value,
                        "suggestion": f"This belief has a low value ({value:.2f}) - consider if this aligns with intended values",
                        "priority": "medium",
                    }
                )
            elif value > 0.98:
                suggestions.append(
                    {
                        "type": "high_value",
                        "belief": belief,
                        "current_value": value,
                        "suggestion": f"This belief is near maximum ({value:.2f}) - consider if some nuance might be valuable",
                        "priority": "low",
                    }
                )

        return suggestions


def main():
    """Demonstration of CoreBeliefs functionality"""
    print("🧠 CoreBeliefs System - Fundamental Values Management")
    print("=" * 60)

    # Initialize beliefs system
    beliefs = CoreBeliefs()

    print("\n📊 Current Belief Values:")
    for belief, value in beliefs.values.items():
        weighted = beliefs.get_weighted_score(belief)
        print(f"  {belief:12}: {value:.3f} (weighted: {weighted:.3f})")

    print("\n🔄 Testing Belief Updates:")

    # Test belief updates
    test_updates = [
        ("transparency", 0.05, "increased_user_feedback"),
        ("privacy", -0.02, "balance_with_transparency"),
        ("growth", 0.03, "successful_learning_milestone"),
    ]

    for belief, delta, reason in test_updates:
        beliefs.update_belief(belief, delta, reason, confidence=0.8)

    print("\n📈 Updated Values:")
    for belief, value in beliefs.values.items():
        print(f"  {belief:12}: {value:.3f}")

    print("\n⚖️ Decision Alignment Test:")
    test_decision = {
        "belief_impacts": {
            "helpfulness": 0.8,
            "privacy": -0.2,
            "transparency": 0.6,
            "truthfulness": 0.9,
        }
    }

    alignment = beliefs.evaluate_decision_alignment(test_decision)
    print(f"  Decision alignment score: {alignment:.3f}")

    print("\n🔍 Belief Analysis:")
    summary = beliefs.get_belief_summary()
    print(f"  Stability Score: {summary['stability_score']:.3f}")
    print(f"  Recent Updates: {summary['recent_updates']}")

    if summary["conflicts"]:
        print("  ⚠️ Detected Conflicts:")
        for belief1, belief2, score in summary["conflicts"]:
            print(f"    {belief1} ↔ {belief2}: {score:.3f}")
    else:
        print("  ✅ No conflicts detected")

    suggestions = beliefs.suggest_belief_adjustments()
    if suggestions:
        print("\n💡 Suggestions:")
        for suggestion in suggestions:
            print(f"  {suggestion['priority'].upper()}: {suggestion['suggestion']}")

    print("\n✅ CoreBeliefs system demonstration complete!")


if __name__ == "__main__":
    main()
