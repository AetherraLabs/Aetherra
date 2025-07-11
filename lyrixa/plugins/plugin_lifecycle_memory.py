"""
Plugin Lifecycle Memory System
==============================

Memory-aware plugin lifecycle management that tracks plugin usage patterns,
creation context, and intelligent loading/unloading based on historical data.
"""

import json
import os
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class PluginMemoryEntry:
    """Represents a memory entry for plugin lifecycle events."""
    # Required plugin metadata
    name = "plugin_lifecycle_memory"
    description = "PluginMemoryEntry - Auto-generated description"
    input_schema = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input data"}
        },
        "required": ["input"]
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Processing result"},
            "status": {"type": "string", "description": "Operation status"}
        }
    }
    created_by = "Plugin System Auto-Fixer"


    def __init__(
        self, plugin_name: str, event_type: str, context: Optional[Dict] = None
    ):
        self.plugin_name = plugin_name
        self.event_type = (
            event_type  # 'loaded', 'unloaded', 'executed', 'created', 'modified'
        )
        self.timestamp = datetime.now()
        self.context = context or {}
        self.session_id = None
        self.user_intent = ""
        self.related_files = []
        self.success = True
        self.performance_metrics = {}


class PluginUsagePattern:
    """Tracks usage patterns for intelligent loading decisions."""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.total_uses = 0
        self.recent_uses = deque(maxlen=50)  # Last 50 usage events
        self.time_patterns = defaultdict(int)  # Hour -> usage count
        self.day_patterns = defaultdict(int)  # Day of week -> usage count
        self.context_patterns = defaultdict(int)  # Context -> usage count
        self.file_type_patterns = defaultdict(int)  # File extension -> usage count
        self.co_occurrence = defaultdict(int)  # Other plugins used together
        self.average_session_length = 0.0
        self.success_rate = 1.0
        self.last_used: Optional[datetime] = None
        self.creation_reason = ""
        self.lifecycle_stage = "active"  # active, idle, deprecated, retired


class PluginLifecycleMemory:
    """Memory-aware plugin lifecycle management system."""

    def __init__(self, memory_dir: Optional[str] = None):
        self.memory_dir = memory_dir or os.path.join(
            os.path.dirname(__file__), ".memory"
        )
        self.memory_entries = deque(maxlen=1000)  # Last 1000 memory entries
        self.usage_patterns = {}  # plugin_name -> PluginUsagePattern
        self.session_context = {}
        self.auto_load_rules = {}
        self.learning_data = {}
        self.lifecycle_predictions = {}

        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)

        self._load_memory_data()
        self._setup_default_rules()

    def _load_memory_data(self):
        """Load memory data from persistent storage."""
        try:
            memory_file = os.path.join(self.memory_dir, "plugin_lifecycle_memory.json")
            if os.path.exists(memory_file):
                with open(memory_file, "r") as f:
                    data = json.load(f)
                    self._deserialize_memory_data(data)
        except Exception as e:
            print(f"Could not load plugin lifecycle memory: {e}")

    def _save_memory_data(self):
        """Save memory data to persistent storage."""
        try:
            memory_file = os.path.join(self.memory_dir, "plugin_lifecycle_memory.json")
            data = self._serialize_memory_data()
            with open(memory_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save plugin lifecycle memory: {e}")

    def _serialize_memory_data(self) -> Dict:
        """Serialize memory data to JSON format."""
        return {
            "usage_patterns": {
                name: {
                    "plugin_name": pattern.plugin_name,
                    "total_uses": pattern.total_uses,
                    "recent_uses": [
                        {
                            "timestamp": entry["timestamp"],
                            "context": entry["context"],
                            "success": entry["success"],
                        }
                        for entry in list(pattern.recent_uses)
                    ],
                    "time_patterns": dict(pattern.time_patterns),
                    "day_patterns": dict(pattern.day_patterns),
                    "context_patterns": dict(pattern.context_patterns),
                    "file_type_patterns": dict(pattern.file_type_patterns),
                    "co_occurrence": dict(pattern.co_occurrence),
                    "average_session_length": pattern.average_session_length,
                    "success_rate": pattern.success_rate,
                    "last_used": pattern.last_used.isoformat()
                    if pattern.last_used
                    else None,
                    "creation_reason": pattern.creation_reason,
                    "lifecycle_stage": pattern.lifecycle_stage,
                }
                for name, pattern in self.usage_patterns.items()
            },
            "auto_load_rules": self.auto_load_rules,
            "learning_data": self.learning_data,
            "last_update": datetime.now().isoformat(),
        }

    def _deserialize_memory_data(self, data: Dict):
        """Deserialize memory data from JSON format."""
        for name, pattern_data in data.get("usage_patterns", {}).items():
            pattern = PluginUsagePattern(pattern_data["plugin_name"])
            pattern.total_uses = pattern_data.get("total_uses", 0)
            pattern.time_patterns = defaultdict(
                int, pattern_data.get("time_patterns", {})
            )
            pattern.day_patterns = defaultdict(
                int, pattern_data.get("day_patterns", {})
            )
            pattern.context_patterns = defaultdict(
                int, pattern_data.get("context_patterns", {})
            )
            pattern.file_type_patterns = defaultdict(
                int, pattern_data.get("file_type_patterns", {})
            )
            pattern.co_occurrence = defaultdict(
                int, pattern_data.get("co_occurrence", {})
            )
            pattern.average_session_length = pattern_data.get(
                "average_session_length", 0.0
            )
            pattern.success_rate = pattern_data.get("success_rate", 1.0)
            pattern.creation_reason = pattern_data.get("creation_reason", "")
            pattern.lifecycle_stage = pattern_data.get("lifecycle_stage", "active")

            if pattern_data.get("last_used"):
                pattern.last_used = datetime.fromisoformat(pattern_data["last_used"])

            # Reconstruct recent uses
            for use_data in pattern_data.get("recent_uses", []):
                pattern.recent_uses.append(use_data)

            self.usage_patterns[name] = pattern

        self.auto_load_rules = data.get("auto_load_rules", {})
        self.learning_data = data.get("learning_data", {})

    def _setup_default_rules(self):
        """Setup default auto-load rules."""
        if not self.auto_load_rules:
            self.auto_load_rules = {
                "time_based": {
                    "enabled": True,
                    "threshold": 0.7,  # Load if 70% likely to be used at this time
                    "lookback_days": 14,
                },
                "context_based": {
                    "enabled": True,
                    "threshold": 0.6,  # Load if 60% likely based on context
                    "file_type_weight": 0.4,
                    "task_weight": 0.6,
                },
                "co_occurrence": {
                    "enabled": True,
                    "threshold": 0.5,  # Load if 50% likely based on other loaded plugins
                    "max_suggestions": 3,
                },
                "frequency": {
                    "enabled": True,
                    "daily_threshold": 3,  # Auto-load if used 3+ times daily
                    "weekly_threshold": 10,  # Auto-load if used 10+ times weekly
                },
            }

    def record_plugin_event(
        self,
        plugin_name: str,
        event_type: str,
        context: Optional[Dict] = None,
        success: bool = True,
    ):
        """Record a plugin lifecycle event."""
        entry = PluginMemoryEntry(plugin_name, event_type, context)
        entry.success = success
        entry.session_id = self.session_context.get("session_id", "unknown")
        entry.user_intent = self.session_context.get("user_intent", "")
        entry.related_files = self.session_context.get("active_files", [])

        # Add to memory
        self.memory_entries.append(entry)

        # Update usage patterns
        if plugin_name not in self.usage_patterns:
            self.usage_patterns[plugin_name] = PluginUsagePattern(plugin_name)

        pattern = self.usage_patterns[plugin_name]

        if event_type in ["executed", "loaded"]:
            pattern.total_uses += 1
            pattern.last_used = datetime.now()

            # Record usage event
            use_entry = {
                "timestamp": entry.timestamp.isoformat(),
                "context": context or {},
                "success": success,
            }
            pattern.recent_uses.append(use_entry)

            # Update patterns
            current_hour = entry.timestamp.hour
            current_day = entry.timestamp.weekday()

            pattern.time_patterns[current_hour] += 1
            pattern.day_patterns[current_day] += 1

            # Context patterns
            if context:
                for key, value in context.items():
                    pattern.context_patterns[f"{key}:{value}"] += 1

            # File type patterns
            for file_path in entry.related_files:
                if "." in file_path:
                    ext = "." + file_path.split(".")[-1].lower()
                    pattern.file_type_patterns[ext] += 1

            # Update success rate
            recent_successes = sum(1 for use in pattern.recent_uses if use["success"])
            pattern.success_rate = (
                recent_successes / len(pattern.recent_uses)
                if pattern.recent_uses
                else 1.0
            )

        elif event_type == "created":
            pattern.creation_reason = context.get("reason", "") if context else ""
            pattern.lifecycle_stage = "active"

        # Save memory periodically
        if len(self.memory_entries) % 10 == 0:
            self._save_memory_data()

    def update_session_context(self, context: Dict):
        """Update current session context."""
        self.session_context.update(context)

    def get_load_recommendations(
        self, current_context: Optional[Dict] = None
    ) -> List[Dict]:
        """Get plugin load recommendations based on memory and patterns."""
        recommendations = []
        current_time = datetime.now()
        current_hour = current_time.hour
        current_day = current_time.weekday()

        current_context = current_context or self.session_context

        for plugin_name, pattern in self.usage_patterns.items():
            if pattern.lifecycle_stage in ["deprecated", "retired"]:
                continue

            score = 0.0
            reasons = []

            # Time-based scoring
            if self.auto_load_rules["time_based"]["enabled"]:
                time_score = pattern.time_patterns[current_hour] / max(
                    sum(pattern.time_patterns.values()), 1
                )
                day_score = pattern.day_patterns[current_day] / max(
                    sum(pattern.day_patterns.values()), 1
                )
                combined_time_score = (time_score + day_score) / 2

                if (
                    combined_time_score
                    >= self.auto_load_rules["time_based"]["threshold"]
                ):
                    score += combined_time_score * 30
                    reasons.append(
                        f"Frequently used at this time ({combined_time_score:.1%})"
                    )

            # Context-based scoring
            if self.auto_load_rules["context_based"]["enabled"]:
                context_score = 0.0

                # File type matching
                active_files = current_context.get("active_files", [])
                for file_path in active_files:
                    if "." in file_path:
                        ext = "." + file_path.split(".")[-1].lower()
                        if ext in pattern.file_type_patterns:
                            file_score = pattern.file_type_patterns[ext] / max(
                                sum(pattern.file_type_patterns.values()), 1
                            )
                            context_score += (
                                file_score
                                * self.auto_load_rules["context_based"][
                                    "file_type_weight"
                                ]
                            )

                # Task matching
                current_task = current_context.get("current_task", "")
                if current_task:
                    for context_key, count in pattern.context_patterns.items():
                        if current_task.lower() in context_key.lower():
                            task_score = count / max(
                                sum(pattern.context_patterns.values()), 1
                            )
                            context_score += (
                                task_score
                                * self.auto_load_rules["context_based"]["task_weight"]
                            )

                if context_score >= self.auto_load_rules["context_based"]["threshold"]:
                    score += context_score * 25
                    reasons.append(f"Relevant to current context ({context_score:.1%})")

            # Frequency-based scoring
            if self.auto_load_rules["frequency"]["enabled"]:
                # Recent usage frequency
                recent_uses = [
                    use
                    for use in pattern.recent_uses
                    if datetime.fromisoformat(use["timestamp"]).date()
                    >= (current_time - timedelta(days=7)).date()
                ]

                weekly_frequency = len(recent_uses)
                daily_frequency = len(
                    [
                        use
                        for use in recent_uses
                        if datetime.fromisoformat(use["timestamp"]).date()
                        == current_time.date()
                    ]
                )

                if (
                    weekly_frequency
                    >= self.auto_load_rules["frequency"]["weekly_threshold"]
                    or daily_frequency
                    >= self.auto_load_rules["frequency"]["daily_threshold"]
                ):
                    score += 20
                    reasons.append(
                        f"High usage frequency ({weekly_frequency} uses this week)"
                    )

            # Success rate bonus
            if pattern.success_rate > 0.8:
                score += pattern.success_rate * 10
                reasons.append(f"High success rate ({pattern.success_rate:.1%})")

            # Recency penalty
            if pattern.last_used:
                days_since_last_use = (current_time - pattern.last_used).days
                if days_since_last_use > 30:
                    score *= 0.5  # Reduce score for old plugins
                    reasons.append(f"Last used {days_since_last_use} days ago")

            if score > 0:
                recommendations.append(
                    {
                        "plugin_name": plugin_name,
                        "score": score,
                        "confidence": min(100, score),
                        "reasons": reasons,
                        "lifecycle_stage": pattern.lifecycle_stage,
                        "last_used": pattern.last_used.isoformat()
                        if pattern.last_used
                        else None,
                        "total_uses": pattern.total_uses,
                        "success_rate": pattern.success_rate,
                    }
                )

        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:10]

    def get_unload_suggestions(self) -> List[Dict]:
        """Get suggestions for plugins that should be unloaded."""
        suggestions = []
        current_time = datetime.now()

        for plugin_name, pattern in self.usage_patterns.items():
            if pattern.lifecycle_stage == "retired":
                continue

            suggestion_score = 0.0
            reasons = []

            # Long time since last use
            if pattern.last_used:
                days_since_last_use = (current_time - pattern.last_used).days
                if days_since_last_use > 14:
                    suggestion_score += min(50, days_since_last_use * 2)
                    reasons.append(f"Not used for {days_since_last_use} days")

            # Low success rate
            if pattern.success_rate < 0.6:
                suggestion_score += (1 - pattern.success_rate) * 30
                reasons.append(f"Low success rate ({pattern.success_rate:.1%})")

            # Infrequent usage
            recent_uses = [
                use
                for use in pattern.recent_uses
                if datetime.fromisoformat(use["timestamp"]).date()
                >= (current_time - timedelta(days=30)).date()
            ]

            if len(recent_uses) < 3:  # Less than 3 uses in 30 days
                suggestion_score += 25
                reasons.append(
                    f"Low usage frequency ({len(recent_uses)} uses in 30 days)"
                )

            if suggestion_score > 30:  # Threshold for unload suggestion
                suggestions.append(
                    {
                        "plugin_name": plugin_name,
                        "suggestion_score": suggestion_score,
                        "reasons": reasons,
                        "last_used": pattern.last_used.isoformat()
                        if pattern.last_used
                        else None,
                        "success_rate": pattern.success_rate,
                        "recent_usage_count": len(recent_uses),
                        "recommended_action": "unload"
                        if suggestion_score > 50
                        else "consider_unloading",
                    }
                )

        suggestions.sort(key=lambda x: x["suggestion_score"], reverse=True)
        return suggestions

    def analyze_plugin_lifecycle(self, plugin_name: str) -> Dict:
        """Analyze the complete lifecycle of a plugin."""
        if plugin_name not in self.usage_patterns:
            return {"error": f"No lifecycle data for plugin {plugin_name}"}

        pattern = self.usage_patterns[plugin_name]

        # Get all events for this plugin
        plugin_events = [
            entry for entry in self.memory_entries if entry.plugin_name == plugin_name
        ]

        # Analyze lifecycle stages
        lifecycle_events = defaultdict(list)
        for event in plugin_events:
            lifecycle_events[event.event_type].append(event)

        # Calculate lifecycle metrics
        creation_event = next(
            (e for e in plugin_events if e.event_type == "created"), None
        )
        first_use = min(
            (
                e.timestamp
                for e in plugin_events
                if e.event_type in ["executed", "loaded"]
            ),
            default=None,
        )
        last_use = max(
            (
                e.timestamp
                for e in plugin_events
                if e.event_type in ["executed", "loaded"]
            ),
            default=None,
        )

        analysis = {
            "plugin_name": plugin_name,
            "lifecycle_stage": pattern.lifecycle_stage,
            "creation_date": creation_event.timestamp.isoformat()
            if creation_event
            else None,
            "creation_reason": pattern.creation_reason,
            "first_use": first_use.isoformat() if first_use else None,
            "last_use": last_use.isoformat() if last_use else None,
            "total_uses": pattern.total_uses,
            "success_rate": pattern.success_rate,
            "average_session_length": pattern.average_session_length,
            "usage_trends": self._analyze_usage_trends(pattern),
            "context_preferences": dict(pattern.context_patterns),
            "time_preferences": {
                "best_hours": sorted(
                    pattern.time_patterns.items(), key=lambda x: x[1], reverse=True
                )[:3],
                "best_days": sorted(
                    pattern.day_patterns.items(), key=lambda x: x[1], reverse=True
                )[:3],
            },
            "file_type_associations": dict(pattern.file_type_patterns),
            "co_occurrence_patterns": dict(pattern.co_occurrence),
            "lifecycle_events_count": {
                event_type: len(events)
                for event_type, events in lifecycle_events.items()
            },
            "recommendation": self._generate_lifecycle_recommendation(pattern),
        }

        return analysis

    def _analyze_usage_trends(self, pattern: PluginUsagePattern) -> Dict:
        """Analyze usage trends for a plugin."""
        if not pattern.recent_uses:
            return {"trend": "no_data"}

        # Group by weeks
        weekly_usage = defaultdict(int)
        for use in pattern.recent_uses:
            use_date = datetime.fromisoformat(use["timestamp"])
            week_key = use_date.strftime("%Y-W%U")
            weekly_usage[week_key] += 1

        weeks = sorted(weekly_usage.keys())
        if len(weeks) < 2:
            return {"trend": "insufficient_data"}

        # Calculate trend
        recent_weeks = list(weekly_usage.values())[-4:]  # Last 4 weeks
        if len(recent_weeks) >= 2:
            trend_direction = (
                "increasing" if recent_weeks[-1] > recent_weeks[0] else "decreasing"
            )
            trend_strength = abs(recent_weeks[-1] - recent_weeks[0]) / max(
                recent_weeks[0], 1
            )
        else:
            trend_direction = "stable"
            trend_strength = 0

        return {
            "trend": trend_direction,
            "strength": trend_strength,
            "weekly_usage": dict(weekly_usage),
            "recent_weeks_usage": recent_weeks,
        }

    def _generate_lifecycle_recommendation(self, pattern: PluginUsagePattern) -> Dict:
        """Generate lifecycle management recommendation."""
        current_time = datetime.now()

        # Calculate metrics
        days_since_last_use = (
            (current_time - pattern.last_used).days if pattern.last_used else 999
        )
        recent_usage_count = len(
            [
                use
                for use in pattern.recent_uses
                if datetime.fromisoformat(use["timestamp"]).date()
                >= (current_time - timedelta(days=30)).date()
            ]
        )

        # Decision logic
        if pattern.success_rate < 0.5:
            return {
                "action": "investigate",
                "priority": "high",
                "reason": "Low success rate indicates potential issues",
                "details": f"Success rate: {pattern.success_rate:.1%}",
            }
        elif days_since_last_use > 60:
            return {
                "action": "retire",
                "priority": "medium",
                "reason": "Plugin unused for extended period",
                "details": f"Last used {days_since_last_use} days ago",
            }
        elif recent_usage_count < 2:
            return {
                "action": "consider_unloading",
                "priority": "low",
                "reason": "Low recent usage",
                "details": f"Only {recent_usage_count} uses in last 30 days",
            }
        elif pattern.total_uses > 50 and pattern.success_rate > 0.8:
            return {
                "action": "promote",
                "priority": "low",
                "reason": "High-performing plugin",
                "details": f"{pattern.total_uses} uses with {pattern.success_rate:.1%} success rate",
            }
        else:
            return {
                "action": "maintain",
                "priority": "low",
                "reason": "Plugin performing within normal parameters",
                "details": f"{pattern.total_uses} total uses, {pattern.success_rate:.1%} success rate",
            }

    def get_memory_insights(self) -> Dict:
        """Get comprehensive insights from plugin lifecycle memory."""
        total_plugins = len(self.usage_patterns)
        active_plugins = len(
            [p for p in self.usage_patterns.values() if p.lifecycle_stage == "active"]
        )

        # Most successful plugins
        most_successful = sorted(
            [
                (name, pattern.success_rate, pattern.total_uses)
                for name, pattern in self.usage_patterns.items()
            ],
            key=lambda x: (x[1], x[2]),
            reverse=True,
        )[:5]

        # Usage trends
        current_time = datetime.now()
        recent_activity = len(
            [
                entry
                for entry in self.memory_entries
                if entry.timestamp >= current_time - timedelta(days=7)
            ]
        )

        return {
            "total_plugins_tracked": total_plugins,
            "active_plugins": active_plugins,
            "total_memory_entries": len(self.memory_entries),
            "recent_activity_count": recent_activity,
            "most_successful_plugins": [
                {"name": name, "success_rate": rate, "total_uses": uses}
                for name, rate, uses in most_successful
            ],
            "lifecycle_distribution": {
                stage: len(
                    [
                        p
                        for p in self.usage_patterns.values()
                        if p.lifecycle_stage == stage
                    ]
                )
                for stage in ["active", "idle", "deprecated", "retired"]
            },
            "auto_load_rules": self.auto_load_rules,
            "memory_health": "good" if recent_activity > 10 else "low_activity",
        }

    def export_memory_data(self) -> Dict:
        """Export all memory data for backup or analysis."""
        return self._serialize_memory_data()

    def import_memory_data(self, data: Dict):
        """Import memory data from backup."""
        self._deserialize_memory_data(data)
        self._save_memory_data()

    def cleanup_old_entries(self, days: int = 90):
        """Clean up old memory entries to maintain performance."""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Remove old memory entries
        self.memory_entries = deque(
            [entry for entry in self.memory_entries if entry.timestamp >= cutoff_date],
            maxlen=1000,
        )

        # Clean up old usage data
        for pattern in self.usage_patterns.values():
            pattern.recent_uses = deque(
                [
                    use
                    for use in pattern.recent_uses
                    if datetime.fromisoformat(use["timestamp"]) >= cutoff_date
                ],
                maxlen=50,
            )

        self._save_memory_data()


# Global lifecycle memory instance
lifecycle_memory = PluginLifecycleMemory()


def record_plugin_event(
    plugin_name: str,
    event_type: str,
    context: Optional[Dict] = None,
    success: bool = True,
):
    """Convenience function for recording plugin events."""
    return lifecycle_memory.record_plugin_event(
        plugin_name, event_type, context, success
    )


def get_load_recommendations(current_context: Optional[Dict] = None) -> List[Dict]:
    """Convenience function for getting load recommendations."""
    return lifecycle_memory.get_load_recommendations(current_context)
