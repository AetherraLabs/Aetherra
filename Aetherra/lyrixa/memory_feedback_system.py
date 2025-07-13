# memory_feedback_system.py
# 🧠 Memory Feedback + Versioning System for Lyrixa
# Tracks development history, reasons for changes, and performance impact

import json
import logging
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class PluginSnapshot:
    """Snapshot of a plugin at a specific point in time"""
    plugin_id: str
    version: str
    code_content: str
    metadata: Dict[str, Any]
    metrics: Dict[str, float]
    timestamp: float
    reason_for_change: str
    change_type: str  # "improvement", "fix", "feature", "refactor"
    confidence_score: float

@dataclass
class PerformanceMetrics:
    """Performance metrics for a plugin"""
    execution_time: float
    memory_usage: float
    error_rate: float
    success_rate: float
    user_satisfaction: float
    code_quality_score: float
    timestamp: Optional[float] = None

@dataclass
class DevelopmentReflection:
    """Reflection on a development action and its outcomes"""
    change_id: str
    before_snapshot: PluginSnapshot
    after_snapshot: PluginSnapshot
    performance_before: PerformanceMetrics
    performance_after: PerformanceMetrics
    improvement_achieved: bool
    lessons_learned: List[str]
    confidence_accuracy: float  # How accurate was the original confidence score
    timestamp: float

class MemoryFeedbackSystem:
    """
    🧠 Memory Feedback + Versioning System

    Records and analyzes development history to learn from outcomes:
    - Why changes were made
    - Before/after snapshots
    - Performance impact analysis
    - Reflection on decision quality
    """

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.memory_dir = self.workspace_path / "lyrixa_memory"
        self.memory_dir.mkdir(exist_ok=True)

        # Initialize storage
        self.snapshots_file = self.memory_dir / "plugin_snapshots.json"
        self.reflections_file = self.memory_dir / "development_reflections.json"
        self.performance_file = self.memory_dir / "performance_history.json"

        # Load existing data
        self.plugin_snapshots: Dict[str, List[PluginSnapshot]] = self._load_snapshots()
        self.reflections: List[DevelopmentReflection] = self._load_reflections()
        self.performance_history: Dict[str, List[PerformanceMetrics]] = self._load_performance_history()

    def _load_snapshots(self) -> Dict[str, List[PluginSnapshot]]:
        """Load plugin snapshots from disk"""
        if self.snapshots_file.exists():
            try:
                with open(self.snapshots_file, 'r') as f:
                    data = json.load(f)
                    snapshots = {}
                    for plugin_id, snapshot_list in data.items():
                        snapshots[plugin_id] = [
                            PluginSnapshot(**snapshot) for snapshot in snapshot_list
                        ]
                    return snapshots
            except Exception as e:
                logger.warning(f"⚠️ Failed to load snapshots: {e}")
        return {}

    def _load_reflections(self) -> List[DevelopmentReflection]:
        """Load development reflections from disk"""
        if self.reflections_file.exists():
            try:
                with open(self.reflections_file, 'r') as f:
                    data = json.load(f)
                    # Note: This would need custom deserialization for nested dataclasses
                    # For now, return empty list
                    return []
            except Exception as e:
                logger.warning(f"⚠️ Failed to load reflections: {e}")
        return []

    def _load_performance_history(self) -> Dict[str, List[PerformanceMetrics]]:
        """Load performance history from disk"""
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                    history = {}
                    for plugin_id, metrics_list in data.items():
                        history[plugin_id] = [
                            PerformanceMetrics(**metrics) for metrics in metrics_list
                        ]
                    return history
            except Exception as e:
                logger.warning(f"⚠️ Failed to load performance history: {e}")
        return {}

    def create_plugin_snapshot(self, plugin_id: str, plugin_path: str,
                             reason: str, change_type: str, confidence: float) -> PluginSnapshot:
        """
        📸 Create a snapshot of a plugin before changes
        """
        try:
            # Read plugin code
            with open(plugin_path, 'r', encoding='utf-8') as f:
                code_content = f.read()

            # Extract metadata (basic version)
            metadata = self._extract_metadata(code_content)

            # Calculate basic metrics
            metrics = self._calculate_basic_metrics(code_content)

            # Generate version string
            current_snapshots = self.plugin_snapshots.get(plugin_id, [])
            version = f"v{len(current_snapshots) + 1}.0"

            snapshot = PluginSnapshot(
                plugin_id=plugin_id,
                version=version,
                code_content=code_content,
                metadata=metadata,
                metrics=metrics,
                timestamp=time.time(),
                reason_for_change=reason,
                change_type=change_type,
                confidence_score=confidence
            )

            # Store snapshot
            if plugin_id not in self.plugin_snapshots:
                self.plugin_snapshots[plugin_id] = []
            self.plugin_snapshots[plugin_id].append(snapshot)

            self._save_snapshots()

            logger.info(f"📸 Created snapshot {version} for {plugin_id}: {reason}")
            return snapshot

        except Exception as e:
            logger.error(f"❌ Failed to create snapshot for {plugin_id}: {e}")
            raise

    def _extract_metadata(self, code: str) -> Dict[str, Any]:
        """Extract metadata from plugin code"""
        metadata: Dict[str, Any] = {
            "lines_of_code": len(code.split('\n')),
            "function_count": code.count('def '),
            "class_count": code.count('class '),
            "import_count": code.count('import '),
            "comment_lines": len([line for line in code.split('\n') if line.strip().startswith('#')])
        }

        # Extract version from comments if available
        for line in code.split('\n')[:20]:
            if '# @version:' in line:
                metadata['declared_version'] = line.split(':', 1)[1].strip()
                break

        return metadata

    def _calculate_basic_metrics(self, code: str) -> Dict[str, float]:
        """Calculate basic code metrics"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        return {
            "complexity_score": min(100.0, len(non_empty_lines) / 10),  # Simple complexity metric
            "documentation_ratio": len([line for line in lines if line.strip().startswith('#')]) / max(1, len(non_empty_lines)),
            "code_density": len(code) / max(1, len(lines))
        }

    def record_performance_metrics(self, plugin_id: str, metrics: PerformanceMetrics):
        """Record performance metrics for a plugin"""
        if plugin_id not in self.performance_history:
            self.performance_history[plugin_id] = []

        self.performance_history[plugin_id].append(metrics)

        # Keep only last 50 entries per plugin
        if len(self.performance_history[plugin_id]) > 50:
            self.performance_history[plugin_id] = self.performance_history[plugin_id][-50:]

        self._save_performance_history()

    def create_development_reflection(self, change_id: str, before_snapshot: PluginSnapshot,
                                   after_snapshot: PluginSnapshot) -> DevelopmentReflection:
        """
        🤔 Create a reflection on a development action
        """
        # Get performance metrics before and after
        performance_before = self._get_latest_performance(before_snapshot.plugin_id, before_snapshot.timestamp)
        performance_after = self._get_latest_performance(after_snapshot.plugin_id, after_snapshot.timestamp)

        # Analyze if improvement was achieved
        improvement_achieved = self._analyze_improvement(performance_before, performance_after,
                                                      before_snapshot, after_snapshot)

        # Extract lessons learned
        lessons = self._extract_lessons_from_change(before_snapshot, after_snapshot,
                                                  performance_before, performance_after)

        # Calculate confidence accuracy
        confidence_accuracy = self._calculate_confidence_accuracy(after_snapshot.confidence_score,
                                                               improvement_achieved)

        reflection = DevelopmentReflection(
            change_id=change_id,
            before_snapshot=before_snapshot,
            after_snapshot=after_snapshot,
            performance_before=performance_before,
            performance_after=performance_after,
            improvement_achieved=improvement_achieved,
            lessons_learned=lessons,
            confidence_accuracy=confidence_accuracy,
            timestamp=time.time()
        )

        self.reflections.append(reflection)
        self._save_reflections()

        logger.info(f"🤔 Created reflection for change {change_id}: improvement={improvement_achieved}")
        return reflection

    def _get_latest_performance(self, plugin_id: str, before_timestamp: float) -> PerformanceMetrics:
        """Get the latest performance metrics for a plugin before a timestamp"""
        history = self.performance_history.get(plugin_id, [])

        # Find metrics recorded before the timestamp
        relevant_metrics = [m for m in history if m.timestamp is not None and m.timestamp < before_timestamp]

        if relevant_metrics:
            return relevant_metrics[-1]  # Most recent

        # Return default metrics if none found
        return PerformanceMetrics(
            execution_time=1.0,
            memory_usage=10.0,
            error_rate=0.0,
            success_rate=1.0,
            user_satisfaction=0.8,
            code_quality_score=0.7,
            timestamp=time.time()
        )

    def _analyze_improvement(self, before: PerformanceMetrics, after: PerformanceMetrics,
                           before_snapshot: PluginSnapshot, after_snapshot: PluginSnapshot) -> bool:
        """Analyze if the change resulted in improvement"""
        # Performance improvements
        performance_improved = (
            after.execution_time <= before.execution_time and
            after.memory_usage <= before.memory_usage and
            after.error_rate <= before.error_rate and
            after.success_rate >= before.success_rate
        )

        # Code quality improvements
        code_quality_improved = (
            after_snapshot.metrics.get("documentation_ratio", 0) >=
            before_snapshot.metrics.get("documentation_ratio", 0)
        )

        return performance_improved or code_quality_improved

    def _extract_lessons_from_change(self, before: PluginSnapshot, after: PluginSnapshot,
                                   perf_before: PerformanceMetrics, perf_after: PerformanceMetrics) -> List[str]:
        """Extract lessons learned from a change"""
        lessons = []

        # Confidence-related lessons
        if after.confidence_score > 0.8 and perf_after.success_rate > perf_before.success_rate:
            lessons.append("High confidence changes tend to improve success rates")

        # Change type lessons
        if after.change_type == "refactor" and perf_after.code_quality_score > 0.8:
            lessons.append("Refactoring changes improve code quality")

        # Size-related lessons
        code_size_change = len(after.code_content) - len(before.code_content)
        if code_size_change > 0 and perf_after.execution_time > perf_before.execution_time:
            lessons.append("Larger code changes may impact performance")

        return lessons

    def _calculate_confidence_accuracy(self, original_confidence: float, success: bool) -> float:
        """Calculate how accurate the original confidence score was"""
        if success:
            # If change was successful, higher confidence was more accurate
            return original_confidence
        else:
            # If change failed, lower confidence would have been more accurate
            return 1.0 - original_confidence

    def get_plugin_history(self, plugin_id: str) -> List[PluginSnapshot]:
        """Get the complete history of a plugin"""
        return self.plugin_snapshots.get(plugin_id, [])

    def get_development_insights(self) -> Dict[str, Any]:
        """Get insights from development history"""
        if not self.reflections:
            return {"message": "No development reflections available"}

        total_changes = len(self.reflections)
        successful_changes = sum(1 for r in self.reflections if r.improvement_achieved)

        # Calculate average confidence accuracy
        avg_confidence_accuracy = sum(r.confidence_accuracy for r in self.reflections) / total_changes

        # Aggregate lessons learned
        all_lessons = []
        for reflection in self.reflections:
            all_lessons.extend(reflection.lessons_learned)

        # Count lesson frequency
        lesson_counts = {}
        for lesson in all_lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1

        top_lessons = sorted(lesson_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_changes": total_changes,
            "improvement_rate": successful_changes / total_changes if total_changes > 0 else 0,
            "average_confidence_accuracy": avg_confidence_accuracy,
            "top_lessons": [lesson for lesson, count in top_lessons],
            "recent_reflections": self.reflections[-5:] if self.reflections else []
        }

    def compare_snapshots(self, plugin_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two snapshots of a plugin"""
        snapshots = self.plugin_snapshots.get(plugin_id, [])

        snap1 = next((s for s in snapshots if s.version == version1), None)
        snap2 = next((s for s in snapshots if s.version == version2), None)

        if not snap1 or not snap2:
            return {"error": "One or both snapshots not found"}

        # Calculate differences
        code_diff_lines = len(snap2.code_content.split('\n')) - len(snap1.code_content.split('\n'))

        metric_changes = {}
        for key in snap1.metrics:
            if key in snap2.metrics:
                metric_changes[key] = snap2.metrics[key] - snap1.metrics[key]

        return {
            "version_comparison": f"{version1} → {version2}",
            "time_difference": snap2.timestamp - snap1.timestamp,
            "code_line_difference": code_diff_lines,
            "metric_changes": metric_changes,
            "reason_for_change": snap2.reason_for_change,
            "change_type": snap2.change_type
        }

    def _save_snapshots(self):
        """Save snapshots to disk"""
        try:
            data = {}
            for plugin_id, snapshots in self.plugin_snapshots.items():
                data[plugin_id] = [asdict(snapshot) for snapshot in snapshots]

            with open(self.snapshots_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save snapshots: {e}")

    def _save_reflections(self):
        """Save reflections to disk"""
        try:
            # Note: This would need custom serialization for nested dataclasses
            # For now, just save basic info
            basic_reflections = []
            for reflection in self.reflections:
                basic_reflections.append({
                    "change_id": reflection.change_id,
                    "improvement_achieved": reflection.improvement_achieved,
                    "lessons_learned": reflection.lessons_learned,
                    "confidence_accuracy": reflection.confidence_accuracy,
                    "timestamp": reflection.timestamp
                })

            with open(self.reflections_file, 'w') as f:
                json.dump(basic_reflections, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save reflections: {e}")

    def _save_performance_history(self):
        """Save performance history to disk"""
        try:
            data = {}
            for plugin_id, metrics_list in self.performance_history.items():
                data[plugin_id] = [asdict(metrics) for metrics in metrics_list]

            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save performance history: {e}")


# Example usage
if __name__ == "__main__":
    def test_memory_feedback_system():
        """Test the memory feedback system"""
        print("🧠 Testing Memory Feedback System")
        print("=" * 40)

        memory_system = MemoryFeedbackSystem(".")

        # Test snapshot creation
        # This would normally be called with actual plugin files
        print("Testing snapshot creation...")

        # Test insights
        insights = memory_system.get_development_insights()
        print(f"Development insights: {insights}")

        print("✅ Memory feedback system test completed")

    test_memory_feedback_system()
