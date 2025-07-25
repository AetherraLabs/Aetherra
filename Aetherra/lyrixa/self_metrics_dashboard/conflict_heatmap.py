#!/usr/bin/env python3
"""
📈 Conflict Heatmap Generator
============================

Analyzes and visualizes conflicts in decision-making processes.
Provides insights into cognitive conflicts and resolution patterns.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class ConflictEvent:
    """Represents a cognitive conflict event"""

    timestamp: str
    conflict_type: str
    intensity: float
    resolution_time: float
    resolved: bool


class ConflictHeatmapGenerator:
    """Generates conflict analysis and visualization data"""

    def __init__(self, data_dir: str = "conflict_data"):
        self.data_dir = data_dir
        self.conflicts: List[ConflictEvent] = []

    def log_conflict(self, conflict_type: str, intensity: float) -> str:
        """Log a new conflict event"""
        conflict = ConflictEvent(
            timestamp=datetime.now().isoformat(),
            conflict_type=conflict_type,
            intensity=intensity,
            resolution_time=0.0,
            resolved=False,
        )
        self.conflicts.append(conflict)
        return conflict.timestamp

    def resolve_conflict(self, conflict_id: str, resolution_time: float):
        """Mark a conflict as resolved"""
        for conflict in self.conflicts:
            if conflict.timestamp == conflict_id:
                conflict.resolved = True
                conflict.resolution_time = resolution_time
                break

    def get_conflict_heatmap_data(self) -> Dict[str, Any]:
        """Generate heatmap visualization data"""
        return {
            "total_conflicts": len(self.conflicts),
            "resolved_conflicts": sum(1 for c in self.conflicts if c.resolved),
            "average_intensity": sum(c.intensity for c in self.conflicts)
            / max(len(self.conflicts), 1),
            "average_resolution_time": sum(
                c.resolution_time for c in self.conflicts if c.resolved
            )
            / max(sum(1 for c in self.conflicts if c.resolved), 1),
            "conflict_types": list(set(c.conflict_type for c in self.conflicts)),
        }

    def get_recent_conflicts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent conflicts for analysis"""
        return [
            {
                "timestamp": c.timestamp,
                "type": c.conflict_type,
                "intensity": c.intensity,
                "resolved": c.resolved,
                "resolution_time": c.resolution_time,
            }
            for c in self.conflicts[-10:]  # Return last 10 conflicts as placeholder
        ]
