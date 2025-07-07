"""
Context-Aware Plugin Surfacing System
====================================

Intelligent plugin recommendation and surfacing based on current context,
user behavior, task patterns, and environmental factors.
"""

import json
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class ContextSnapshot:
    """Represents a snapshot of current context."""

    def __init__(self):
        self.timestamp = datetime.now()
        self.active_files = []
        self.current_task = ""
        self.user_input = ""
        self.environment_vars = {}
        self.recent_plugins = []
        self.success_metrics = {}
        self.error_context = {}


class ContextAwareSurfacing:
    """Context-aware plugin surfacing system."""

    def __init__(self):
        self.context_history = deque(maxlen=100)
        self.plugin_usage_patterns = defaultdict(list)
        self.task_plugin_mapping = defaultdict(set)
        self.context_triggers = {}
        self.learning_data = {}
        self.recommendation_cache = {}
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the context-aware surfacing system."""
        self._load_learning_data()
        self._setup_default_triggers()

    def _load_learning_data(self):
        """Load learning data from storage."""
        try:
            import os

            data_file = os.path.join(os.path.dirname(__file__), "surfacing_data.json")
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                    self._deserialize_learning_data(data)
        except Exception as e:
            print(f"Could not load surfacing data: {e}")

    def _save_learning_data(self):
        """Save learning data to storage."""
        try:
            import os

            data_file = os.path.join(os.path.dirname(__file__), "surfacing_data.json")
            data = self._serialize_learning_data()
            with open(data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save surfacing data: {e}")

    def _serialize_learning_data(self) -> Dict:
        """Serialize learning data to JSON format."""
        return {
            "plugin_usage_patterns": dict(self.plugin_usage_patterns),
            "task_plugin_mapping": {
                k: list(v) for k, v in self.task_plugin_mapping.items()
            },
            "context_triggers": self.context_triggers,
            "learning_data": self.learning_data,
            "last_update": datetime.now().isoformat(),
        }

    def _deserialize_learning_data(self, data: Dict):
        """Deserialize learning data from JSON format."""
        self.plugin_usage_patterns = defaultdict(
            list, data.get("plugin_usage_patterns", {})
        )
        self.task_plugin_mapping = defaultdict(
            set, {k: set(v) for k, v in data.get("task_plugin_mapping", {}).items()}
        )
        self.context_triggers = data.get("context_triggers", {})
        self.learning_data = data.get("learning_data", {})

    def _setup_default_triggers(self):
        """Setup default context triggers for plugin recommendations."""
        self.context_triggers = {
            "file_extensions": {
                ".json": ["json_processor", "data_analyzer"],
                ".csv": ["csv_processor", "data_analyzer", "chart_generator"],
                ".txt": ["text_processor", "content_analyzer"],
                ".py": ["code_analyzer", "syntax_checker", "doc_generator"],
                ".md": ["markdown_processor", "doc_converter"],
                ".xml": ["xml_processor", "data_transformer"],
                ".html": ["html_processor", "web_analyzer"],
            },
            "keywords": {
                "api": ["api_client", "rest_processor", "http_helper"],
                "data": ["data_processor", "analyzer", "transformer"],
                "text": ["text_processor", "nlp_tools", "content_generator"],
                "file": ["file_manager", "batch_processor", "file_analyzer"],
                "database": ["db_connector", "query_builder", "data_migrator"],
                "chart": ["chart_generator", "visualization", "graph_maker"],
                "web": ["web_scraper", "html_parser", "url_processor"],
                "email": ["email_sender", "mail_processor", "notification"],
                "image": [
                    "image_processor",
                    "thumbnail_generator",
                    "metadata_extractor",
                ],
            },
            "task_patterns": {
                "processing": ["batch_processor", "data_transformer", "file_converter"],
                "analysis": ["data_analyzer", "content_analyzer", "pattern_detector"],
                "generation": [
                    "content_generator",
                    "report_generator",
                    "template_engine",
                ],
                "validation": ["data_validator", "format_checker", "quality_control"],
                "integration": ["api_client", "webhook_handler", "sync_manager"],
                "automation": ["workflow_manager", "task_scheduler", "auto_responder"],
            },
        }

    def capture_context(self, **kwargs) -> ContextSnapshot:
        """Capture current context snapshot."""
        snapshot = ContextSnapshot()

        # Update snapshot with provided data
        for key, value in kwargs.items():
            if hasattr(snapshot, key):
                setattr(snapshot, key, value)

        # Add to context history
        self.context_history.append(snapshot)

        return snapshot

    def get_context_recommendations(
        self, context: ContextSnapshot = None, limit: int = 10
    ) -> List[Dict]:
        """Get plugin recommendations based on current context."""
        if not context:
            context = self.capture_context()

        # Check cache first
        cache_key = self._generate_cache_key(context)
        if cache_key in self.recommendation_cache:
            cached_result = self.recommendation_cache[cache_key]
            if datetime.now() - cached_result["timestamp"] < timedelta(minutes=5):
                return cached_result["recommendations"][:limit]

        recommendations = []
        plugin_scores = defaultdict(float)

        # Score plugins based on different context factors
        self._score_by_file_context(context, plugin_scores)
        self._score_by_task_context(context, plugin_scores)
        self._score_by_usage_patterns(context, plugin_scores)
        self._score_by_recent_activity(context, plugin_scores)
        self._score_by_success_metrics(context, plugin_scores)

        # Convert scores to recommendations
        for plugin_name, score in plugin_scores.items():
            if score > 0:
                recommendations.append(
                    {
                        "plugin": plugin_name,
                        "score": score,
                        "confidence": min(100, score * 10),
                        "reason": self._generate_recommendation_reason(
                            plugin_name, context
                        ),
                        "category": self._get_plugin_category(plugin_name),
                    }
                )

        # Sort by score and limit results
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        final_recommendations = recommendations[:limit]

        # Cache results
        self.recommendation_cache[cache_key] = {
            "recommendations": final_recommendations,
            "timestamp": datetime.now(),
        }

        return final_recommendations

    def _generate_cache_key(self, context: ContextSnapshot) -> str:
        """Generate cache key for context."""
        key_parts = [
            str(len(context.active_files)),
            context.current_task[:20] if context.current_task else "",
            context.user_input[:20] if context.user_input else "",
            str(len(context.recent_plugins)),
        ]
        return "|".join(key_parts)

    def _score_by_file_context(
        self, context: ContextSnapshot, plugin_scores: Dict[str, float]
    ):
        """Score plugins based on file context."""
        for file_path in context.active_files:
            # Extract file extension
            if "." in file_path:
                ext = "." + file_path.split(".")[-1].lower()
                if ext in self.context_triggers["file_extensions"]:
                    for plugin in self.context_triggers["file_extensions"][ext]:
                        plugin_scores[plugin] += 3.0

            # Check filename patterns
            filename = file_path.split("/")[-1].lower()
            for keyword, plugins in self.context_triggers["keywords"].items():
                if keyword in filename:
                    for plugin in plugins:
                        plugin_scores[plugin] += 2.0

    def _score_by_task_context(
        self, context: ContextSnapshot, plugin_scores: Dict[str, float]
    ):
        """Score plugins based on current task context."""
        task_lower = context.current_task.lower()

        # Check task keywords
        for keyword, plugins in self.context_triggers["keywords"].items():
            if keyword in task_lower:
                for plugin in plugins:
                    plugin_scores[plugin] += 2.5

        # Check task patterns
        for pattern, plugins in self.context_triggers["task_patterns"].items():
            if pattern in task_lower:
                for plugin in plugins:
                    plugin_scores[plugin] += 3.0

        # Check mapped plugins for similar tasks
        if context.current_task in self.task_plugin_mapping:
            for plugin in self.task_plugin_mapping[context.current_task]:
                plugin_scores[plugin] += 4.0

    def _score_by_usage_patterns(
        self, context: ContextSnapshot, plugin_scores: Dict[str, float]
    ):
        """Score plugins based on historical usage patterns."""
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()

        for plugin, usage_history in self.plugin_usage_patterns.items():
            # Time-based scoring
            recent_usage = [
                usage
                for usage in usage_history[-20:]  # Last 20 uses
                if datetime.fromisoformat(usage["timestamp"]).date()
                >= (datetime.now() - timedelta(days=7)).date()
            ]

            if recent_usage:
                plugin_scores[plugin] += len(recent_usage) * 0.5

                # Same hour preference
                same_hour_usage = [
                    usage
                    for usage in recent_usage
                    if datetime.fromisoformat(usage["timestamp"]).hour == current_hour
                ]
                if same_hour_usage:
                    plugin_scores[plugin] += len(same_hour_usage) * 0.3

                # Same day of week preference
                same_day_usage = [
                    usage
                    for usage in recent_usage
                    if datetime.fromisoformat(usage["timestamp"]).weekday()
                    == current_day
                ]
                if same_day_usage:
                    plugin_scores[plugin] += len(same_day_usage) * 0.2

    def _score_by_recent_activity(
        self, context: ContextSnapshot, plugin_scores: Dict[str, float]
    ):
        """Score plugins based on recent activity."""
        # Boost plugins used recently
        for plugin_name in context.recent_plugins:
            plugin_scores[plugin_name] += 1.5

        # Check recent context history
        recent_contexts = list(self.context_history)[-5:]  # Last 5 contexts
        for recent_context in recent_contexts:
            for plugin_name in recent_context.recent_plugins:
                plugin_scores[plugin_name] += 0.5

    def _score_by_success_metrics(
        self, context: ContextSnapshot, plugin_scores: Dict[str, float]
    ):
        """Score plugins based on success metrics."""
        for plugin_name, metrics in context.success_metrics.items():
            success_rate = metrics.get("success_rate", 0.5)
            execution_time = metrics.get("avg_execution_time", 1.0)

            # Boost highly successful plugins
            plugin_scores[plugin_name] += success_rate * 2.0

            # Slight penalty for slow plugins
            if execution_time > 5.0:
                plugin_scores[plugin_name] -= 0.5

    def _generate_recommendation_reason(
        self, plugin_name: str, context: ContextSnapshot
    ) -> str:
        """Generate human-readable reason for recommendation."""
        reasons = []

        # File-based reasons
        for file_path in context.active_files:
            if "." in file_path:
                ext = "." + file_path.split(".")[-1].lower()
                if ext in self.context_triggers["file_extensions"]:
                    if plugin_name in self.context_triggers["file_extensions"][ext]:
                        reasons.append(f"Works with {ext} files")

        # Task-based reasons
        task_lower = context.current_task.lower()
        for keyword, plugins in self.context_triggers["keywords"].items():
            if keyword in task_lower and plugin_name in plugins:
                reasons.append(f"Relevant for {keyword} tasks")

        # Usage-based reasons
        if plugin_name in self.plugin_usage_patterns:
            recent_count = len(
                [
                    usage
                    for usage in self.plugin_usage_patterns[plugin_name][-10:]
                    if datetime.fromisoformat(usage["timestamp"]).date()
                    >= (datetime.now() - timedelta(days=7)).date()
                ]
            )
            if recent_count > 0:
                reasons.append(f"Used {recent_count} times recently")

        return "; ".join(reasons) if reasons else "General recommendation"

    def _get_plugin_category(self, plugin_name: str) -> str:
        """Get plugin category (placeholder - would integrate with plugin discovery)."""
        # This would integrate with the plugin discovery system
        category_mapping = {
            "data": ["data_processor", "analyzer", "transformer", "csv_processor"],
            "text": ["text_processor", "nlp_tools", "content_generator"],
            "file": ["file_manager", "batch_processor", "file_analyzer"],
            "web": ["web_scraper", "html_parser", "url_processor", "api_client"],
            "utility": ["json_processor", "format_checker", "validator"],
        }

        for category, plugins in category_mapping.items():
            if plugin_name in plugins:
                return category

        return "general"

    def record_plugin_usage(
        self,
        plugin_name: str,
        context: ContextSnapshot,
        success: bool = True,
        execution_time: float = None,
    ):
        """Record plugin usage for learning."""
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "plugin": plugin_name,
            "context_task": context.current_task,
            "success": success,
            "execution_time": execution_time,
            "file_count": len(context.active_files),
            "file_types": list(
                set(
                    "." + f.split(".")[-1].lower()
                    for f in context.active_files
                    if "." in f
                )
            ),
        }

        # Add to usage patterns
        self.plugin_usage_patterns[plugin_name].append(usage_record)

        # Limit history size
        if len(self.plugin_usage_patterns[plugin_name]) > 100:
            self.plugin_usage_patterns[plugin_name] = self.plugin_usage_patterns[
                plugin_name
            ][-100:]

        # Map task to plugin
        if context.current_task:
            self.task_plugin_mapping[context.current_task].add(plugin_name)

        # Update learning data
        self._update_learning_data(plugin_name, usage_record)

        # Save data periodically
        if len(self.plugin_usage_patterns[plugin_name]) % 10 == 0:
            self._save_learning_data()

    def _update_learning_data(self, plugin_name: str, usage_record: Dict):
        """Update learning data based on usage."""
        if plugin_name not in self.learning_data:
            self.learning_data[plugin_name] = {
                "total_uses": 0,
                "success_count": 0,
                "avg_execution_time": 0.0,
                "preferred_contexts": defaultdict(int),
                "file_type_associations": defaultdict(int),
            }

        data = self.learning_data[plugin_name]
        data["total_uses"] += 1

        if usage_record["success"]:
            data["success_count"] += 1

        if usage_record["execution_time"]:
            # Update running average
            current_avg = data["avg_execution_time"]
            total_uses = data["total_uses"]
            data["avg_execution_time"] = (
                current_avg * (total_uses - 1) + usage_record["execution_time"]
            ) / total_uses

        # Track context preferences
        if usage_record["context_task"]:
            data["preferred_contexts"][usage_record["context_task"]] += 1

        # Track file type associations
        for file_type in usage_record["file_types"]:
            data["file_type_associations"][file_type] += 1

    def get_contextual_insights(self) -> Dict:
        """Get insights about contextual usage patterns."""
        insights = {
            "total_contexts": len(self.context_history),
            "tracked_plugins": len(self.plugin_usage_patterns),
            "task_mappings": len(self.task_plugin_mapping),
            "most_used_plugins": [],
            "common_file_types": defaultdict(int),
            "peak_usage_hours": defaultdict(int),
            "success_rates": {},
        }

        # Most used plugins
        plugin_usage_counts = {
            plugin: len(usage_history)
            for plugin, usage_history in self.plugin_usage_patterns.items()
        }
        insights["most_used_plugins"] = sorted(
            plugin_usage_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Common file types and peak hours
        for plugin, usage_history in self.plugin_usage_patterns.items():
            for usage in usage_history:
                # File types
                for file_type in usage.get("file_types", []):
                    insights["common_file_types"][file_type] += 1

                # Peak hours
                hour = datetime.fromisoformat(usage["timestamp"]).hour
                insights["peak_usage_hours"][hour] += 1

        # Success rates
        for plugin, data in self.learning_data.items():
            if data["total_uses"] > 0:
                insights["success_rates"][plugin] = (
                    data["success_count"] / data["total_uses"]
                )

        return insights

    def clear_cache(self):
        """Clear recommendation cache."""
        self.recommendation_cache.clear()

    def export_surfacing_data(self) -> Dict:
        """Export all surfacing data."""
        return self._serialize_learning_data()

    def import_surfacing_data(self, data: Dict):
        """Import surfacing data."""
        self._deserialize_learning_data(data)
        self._save_learning_data()


# Global surfacing instance
context_surfacing = ContextAwareSurfacing()


def get_recommendations(context: ContextSnapshot = None, limit: int = 10) -> List[Dict]:
    """Convenience function for getting context-aware recommendations."""
    return context_surfacing.get_context_recommendations(context, limit)


def capture_context(**kwargs) -> ContextSnapshot:
    """Convenience function for capturing context."""
    return context_surfacing.capture_context(**kwargs)
