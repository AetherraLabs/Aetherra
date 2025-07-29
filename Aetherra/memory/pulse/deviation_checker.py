"""
💓 Memory Pulse - Drift Detection & Correction
===============================================

Periodic self-realignment system that detects memory drift, contradiction,
and degradation. Ensures memory system stays coherent and reliable.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from ..fractal_mesh.base import ConceptCluster, MemoryFragment


@dataclass
class DriftAlert:
    """Alert about detected memory drift"""

    alert_id: str
    drift_type: (
        str  # "concept_shift", "confidence_decay", "contradiction", "orphaned_memory"
    )
    affected_elements: List[str]  # Fragment IDs or concept names
    severity: str  # "low", "medium", "high", "critical"
    description: str
    recommended_action: str
    detected_at: datetime
    resolved: bool = False


@dataclass
class MemoryHealth:
    """Overall memory system health metrics"""

    total_fragments: int
    active_concepts: int
    average_confidence: float
    contradiction_count: int
    orphaned_fragments: int
    coherence_score: float  # 0.0 to 1.0
    last_maintenance: Optional[datetime]
    health_trend: str  # "improving", "stable", "declining"


class MemoryPulseMonitor:
    """
    Monitors memory system health and detects drift patterns

    Features:
    - Confidence decay detection
    - Concept drift analysis
    - Contradiction identification
    - Orphaned memory cleanup
    - Coherence scoring
    - Automated maintenance recommendations
    """

    def __init__(self, db_path: str = "memory_pulse.db"):
        self.db_path = db_path
        self.drift_alerts: List[DriftAlert] = []
        self.health_history: List[MemoryHealth] = []

        # Monitoring thresholds
        self.confidence_decay_threshold = 0.1  # 10% drop triggers alert
        self.contradiction_tolerance = 3  # Max contradictions before alert
        self.orphan_age_threshold = timedelta(days=30)  # Orphan after 30 days
        self.min_coherence_score = 0.7  # Minimum acceptable coherence

        self._init_database()
        self._load_existing_data()

    def _init_database(self):
        """Initialize memory pulse monitoring database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_alerts (
                    alert_id TEXT PRIMARY KEY,
                    drift_type TEXT NOT NULL,
                    affected_elements TEXT,
                    severity TEXT NOT NULL,
                    description TEXT,
                    recommended_action TEXT,
                    detected_at TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_health_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    total_fragments INTEGER,
                    active_concepts INTEGER,
                    average_confidence REAL,
                    contradiction_count INTEGER,
                    orphaned_fragments INTEGER,
                    coherence_score REAL,
                    last_maintenance TEXT,
                    health_trend TEXT,
                    recorded_at TEXT
                )
            """)

            conn.commit()
        finally:
            conn.close()

    def _load_existing_data(self):
        """Load existing monitoring data from database"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Load drift alerts
            cursor = conn.execute("SELECT * FROM drift_alerts WHERE resolved = FALSE")
            for row in cursor.fetchall():
                alert = self._row_to_alert(row)
                self.drift_alerts.append(alert)

            # Load recent health snapshots
            cursor = conn.execute("""
                SELECT * FROM memory_health_snapshots
                ORDER BY recorded_at DESC LIMIT 10
            """)
            for row in cursor.fetchall():
                health = self._row_to_health(row)
                self.health_history.append(health)

        finally:
            conn.close()

    def run_pulse_check(
        self, fragments: List[MemoryFragment], concept_clusters: List[ConceptCluster]
    ) -> MemoryHealth:
        """Run a comprehensive pulse check on memory system"""
        current_time = datetime.now()

        # Calculate basic metrics
        total_fragments = len(fragments)
        active_concepts = len(
            [c for c in concept_clusters if len(c.member_fragments) > 0]
        )
        average_confidence = self._calculate_average_confidence(fragments)

        # Detect specific issues
        contradictions = self._detect_contradictions(fragments)
        orphaned_fragments = self._detect_orphaned_fragments(
            fragments, concept_clusters
        )
        coherence_score = self._calculate_coherence_score(fragments, concept_clusters)

        # Create health snapshot
        health = MemoryHealth(
            total_fragments=total_fragments,
            active_concepts=active_concepts,
            average_confidence=average_confidence,
            contradiction_count=len(contradictions),
            orphaned_fragments=len(orphaned_fragments),
            coherence_score=coherence_score,
            last_maintenance=self._get_last_maintenance_time(),
            health_trend=self._determine_health_trend(),
        )

        # Store health snapshot
        self.health_history.append(health)
        self._persist_health_snapshot(health)

        # Generate alerts for issues
        self._generate_drift_alerts(fragments, concept_clusters, health)

        return health

    def _calculate_average_confidence(self, fragments: List[MemoryFragment]) -> float:
        """Calculate average confidence across all fragments"""
        if not fragments:
            return 0.0

        return sum(f.confidence_score for f in fragments) / len(fragments)

    def _detect_contradictions(
        self, fragments: List[MemoryFragment]
    ) -> List[Tuple[str, str]]:
        """Detect contradictory fragments"""
        contradictions = []

        # Group fragments by symbolic tags
        tag_groups = {}
        for fragment in fragments:
            for tag in fragment.symbolic_tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(fragment)

        # Look for contradictions within tag groups
        for tag, tag_fragments in tag_groups.items():
            if len(tag_fragments) < 2:
                continue

            # Simple contradiction detection based on confidence variance
            confidences = [f.confidence_score for f in tag_fragments]
            confidence_variance = self._calculate_variance(confidences)

            # High variance might indicate contradictions
            if confidence_variance > 0.3:  # Threshold for contradiction detection
                # Find the most divergent pairs
                for i, frag1 in enumerate(tag_fragments):
                    for frag2 in tag_fragments[i + 1 :]:
                        conf_diff = abs(frag1.confidence_score - frag2.confidence_score)
                        if conf_diff > 0.5:  # Significant confidence difference
                            contradictions.append(
                                (frag1.fragment_id, frag2.fragment_id)
                            )

        return contradictions

    def _detect_orphaned_fragments(
        self, fragments: List[MemoryFragment], concept_clusters: List[ConceptCluster]
    ) -> List[str]:
        """Detect fragments not connected to any concept cluster"""
        # Get all fragments that are in clusters
        clustered_fragment_ids = set()
        for cluster in concept_clusters:
            clustered_fragment_ids.update(cluster.member_fragments)

        # Find orphaned fragments (old and not clustered)
        orphaned = []
        cutoff_time = datetime.now() - self.orphan_age_threshold

        for fragment in fragments:
            if (
                fragment.fragment_id not in clustered_fragment_ids
                and fragment.created_at < cutoff_time
                and len(fragment.associative_links) == 0
            ):  # No associations either
                orphaned.append(fragment.fragment_id)

        return orphaned

    def _calculate_coherence_score(
        self, fragments: List[MemoryFragment], concept_clusters: List[ConceptCluster]
    ) -> float:
        """Calculate overall coherence score of memory system"""
        if not fragments:
            return 1.0

        # Factors for coherence:
        # 1. Clustering ratio (how many fragments are in clusters)
        # 2. Average cluster strength
        # 3. Confidence consistency
        # 4. Association density

        clustered_fragment_ids = set()
        total_cluster_strength = 0.0

        for cluster in concept_clusters:
            clustered_fragment_ids.update(cluster.member_fragments)
            total_cluster_strength += cluster.cluster_strength

        # Clustering ratio
        clustering_ratio = len(clustered_fragment_ids) / len(fragments)

        # Average cluster strength
        avg_cluster_strength = (
            total_cluster_strength / len(concept_clusters) if concept_clusters else 0.0
        )

        # Confidence consistency (lower variance = higher coherence)
        confidences = [f.confidence_score for f in fragments]
        confidence_variance = self._calculate_variance(confidences)
        confidence_consistency = max(0, 1.0 - confidence_variance)

        # Association density
        total_associations = sum(len(f.associative_links) for f in fragments)
        association_density = min(
            total_associations / (len(fragments) * 2), 1.0
        )  # Normalize

        # Weighted coherence score
        coherence = (
            clustering_ratio * 0.3
            + avg_cluster_strength * 0.25
            + confidence_consistency * 0.25
            + association_density * 0.2
        )

        return coherence

    def _determine_health_trend(self) -> str:
        """Determine if memory health is improving, stable, or declining"""
        if len(self.health_history) < 2:
            return "stable"

        # Compare last two health snapshots
        current = self.health_history[-1]
        previous = self.health_history[-2]

        # Key metrics to compare
        coherence_change = current.coherence_score - previous.coherence_score
        confidence_change = current.average_confidence - previous.average_confidence
        contradiction_change = (
            current.contradiction_count - previous.contradiction_count
        )

        # Weighted decision
        improvement_score = (
            coherence_change * 0.4
            + confidence_change * 0.4
            + (-contradiction_change * 0.1) * 0.2
        )  # Fewer contradictions = better

        if improvement_score > 0.05:
            return "improving"
        elif improvement_score < -0.05:
            return "declining"
        else:
            return "stable"

    def _generate_drift_alerts(
        self,
        fragments: List[MemoryFragment],
        concept_clusters: List[ConceptCluster],
        health: MemoryHealth,
    ):
        """Generate alerts based on detected issues"""
        current_time = datetime.now()

        # Confidence decay alert
        if health.average_confidence < 0.5:
            alert = DriftAlert(
                alert_id=str(uuid.uuid4()),
                drift_type="confidence_decay",
                affected_elements=["system_wide"],
                severity="medium" if health.average_confidence > 0.3 else "high",
                description=f"Average confidence has dropped to {health.average_confidence:.2f}",
                recommended_action="Review recent fragments and validate uncertain memories",
                detected_at=current_time,
            )
            self.drift_alerts.append(alert)
            self._persist_alert(alert)

        # Contradiction alert
        if health.contradiction_count > self.contradiction_tolerance:
            alert = DriftAlert(
                alert_id=str(uuid.uuid4()),
                drift_type="contradiction",
                affected_elements=["multiple_fragments"],
                severity="high",
                description=f"Detected {health.contradiction_count} contradictions",
                recommended_action="Reconcile contradictory memories and update confidence scores",
                detected_at=current_time,
            )
            self.drift_alerts.append(alert)
            self._persist_alert(alert)

        # Coherence alert
        if health.coherence_score < self.min_coherence_score:
            alert = DriftAlert(
                alert_id=str(uuid.uuid4()),
                drift_type="coherence_loss",
                affected_elements=["system_structure"],
                severity="critical" if health.coherence_score < 0.5 else "high",
                description=f"System coherence has dropped to {health.coherence_score:.2f}",
                recommended_action="Run memory consolidation and reorganization",
                detected_at=current_time,
            )
            self.drift_alerts.append(alert)
            self._persist_alert(alert)

        # Orphaned fragments alert
        if health.orphaned_fragments > 10:
            alert = DriftAlert(
                alert_id=str(uuid.uuid4()),
                drift_type="orphaned_memory",
                affected_elements=[f"{health.orphaned_fragments}_fragments"],
                severity="medium",
                description=f"Found {health.orphaned_fragments} orphaned memory fragments",
                recommended_action="Review and integrate orphaned memories or archive if obsolete",
                detected_at=current_time,
            )
            self.drift_alerts.append(alert)
            self._persist_alert(alert)

    def get_active_alerts(
        self, severity_filter: Optional[str] = None
    ) -> List[DriftAlert]:
        """Get active drift alerts, optionally filtered by severity"""
        active_alerts = [alert for alert in self.drift_alerts if not alert.resolved]

        if severity_filter:
            active_alerts = [
                alert for alert in active_alerts if alert.severity == severity_filter
            ]

        return sorted(active_alerts, key=lambda a: a.detected_at, reverse=True)

    def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """Mark an alert as resolved"""
        for alert in self.drift_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                self._update_alert_resolution(alert_id, resolution_note)
                return True
        return False

    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of current memory health"""
        if not self.health_history:
            return {"status": "no_data"}

        current_health = self.health_history[-1]
        active_alerts = self.get_active_alerts()

        return {
            "overall_status": self._determine_overall_status(
                current_health, active_alerts
            ),
            "coherence_score": current_health.coherence_score,
            "average_confidence": current_health.average_confidence,
            "total_fragments": current_health.total_fragments,
            "active_concepts": current_health.active_concepts,
            "health_trend": current_health.health_trend,
            "active_alerts": len(active_alerts),
            "critical_alerts": len(
                [a for a in active_alerts if a.severity == "critical"]
            ),
            "last_pulse_check": self.health_history[-1].__dict__
            if self.health_history
            else None,
        }

    def _determine_overall_status(
        self, health: MemoryHealth, alerts: List[DriftAlert]
    ) -> str:
        """Determine overall system status"""
        critical_alerts = [a for a in alerts if a.severity == "critical"]
        high_alerts = [a for a in alerts if a.severity == "high"]

        if critical_alerts:
            return "critical"
        elif high_alerts or health.coherence_score < 0.6:
            return "warning"
        elif health.coherence_score > 0.8 and health.average_confidence > 0.7:
            return "excellent"
        else:
            return "good"

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def _get_last_maintenance_time(self) -> Optional[datetime]:
        """Get timestamp of last maintenance operation"""
        # This would track when maintenance operations were performed
        # For now, return None (would be implemented with maintenance tracking)
        return None

    # Database persistence methods
    def _persist_alert(self, alert: DriftAlert):
        """Persist drift alert to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO drift_alerts
                (alert_id, drift_type, affected_elements, severity, description,
                 recommended_action, detected_at, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    alert.alert_id,
                    alert.drift_type,
                    json.dumps(alert.affected_elements),
                    alert.severity,
                    alert.description,
                    alert.recommended_action,
                    alert.detected_at.isoformat(),
                    alert.resolved,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _persist_health_snapshot(self, health: MemoryHealth):
        """Persist health snapshot to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            snapshot_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO memory_health_snapshots
                (snapshot_id, total_fragments, active_concepts, average_confidence,
                 contradiction_count, orphaned_fragments, coherence_score,
                 last_maintenance, health_trend, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot_id,
                    health.total_fragments,
                    health.active_concepts,
                    health.average_confidence,
                    health.contradiction_count,
                    health.orphaned_fragments,
                    health.coherence_score,
                    health.last_maintenance.isoformat()
                    if health.last_maintenance
                    else None,
                    health.health_trend,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _update_alert_resolution(self, alert_id: str, resolution_note: str):
        """Update alert resolution in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                UPDATE drift_alerts
                SET resolved = TRUE
                WHERE alert_id = ?
            """,
                (alert_id,),
            )
            conn.commit()
        finally:
            conn.close()

    def _row_to_alert(self, row) -> DriftAlert:
        """Convert database row to DriftAlert object"""
        return DriftAlert(
            alert_id=row[0],
            drift_type=row[1],
            affected_elements=json.loads(row[2]) if row[2] else [],
            severity=row[3],
            description=row[4] or "",
            recommended_action=row[5] or "",
            detected_at=datetime.fromisoformat(row[6]),
            resolved=bool(row[7]),
        )

    def _row_to_health(self, row) -> MemoryHealth:
        """Convert database row to MemoryHealth object"""
        return MemoryHealth(
            total_fragments=row[1],
            active_concepts=row[2],
            average_confidence=row[3],
            contradiction_count=row[4],
            orphaned_fragments=row[5],
            coherence_score=row[6],
            last_maintenance=datetime.fromisoformat(row[7]) if row[7] else None,
            health_trend=row[8] or "stable",
        )
