"""
🔍 Introsfrom typing import Any, Dict, List, Optional, Set

# Use conditional import to avoid file permission issues during testing
try:
    from .memory.logger import MemoryLogger
    MEMORY_LOGGER_AVAILABLE = True
except (ImportError, PermissionError):
    MEMORY_LOGGER_AVAILABLE = False
    MemoryLogger = Nonetive Logging System
==============================

Self-aware AI execution tracking, reflection, and activity monitoring
for enhanced intelligence and user insight into system behavior.
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Use conditional import to avoid file permission issues during testing
try:
    from .memory.logger import MemoryLogger

    MEMORY_LOGGER_AVAILABLE = True
except (ImportError, PermissionError):
    MEMORY_LOGGER_AVAILABLE = False
    MemoryLogger = None


class ActivityType(Enum):
    """Types of activities the AI can perform"""

    EXECUTION = "execution"
    LEARNING = "learning"
    REFLECTION = "reflection"
    INTERACTION = "interaction"
    OPTIMIZATION = "optimization"
    ERROR_HANDLING = "error_handling"
    MEMORY_OPERATION = "memory_operation"
    PLUGIN_OPERATION = "plugin_operation"


class ExecutionStatus(Enum):
    """Status of executed operations"""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""

    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    lines_processed: Optional[int] = None
    tokens_generated: Optional[int] = None
    success_rate: Optional[float] = None


@dataclass
class ExecutionReflection:
    """Reflection on a single execution"""

    id: str
    timestamp: datetime
    activity_type: ActivityType
    operation: str
    code: Optional[str]
    result: Any
    status: ExecutionStatus
    performance: PerformanceMetrics
    context: Dict[str, Any]
    insights: List[str]
    lessons_learned: List[str]
    improvement_suggestions: List[str]
    user_feedback: Optional[str] = None
    error_details: Optional[str] = None


@dataclass
class ActivitySession:
    """Group of related activities in a session"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    activities: List[ExecutionReflection]
    session_insights: List[str]
    productivity_score: Optional[float] = None
    user_satisfaction: Optional[float] = None


class IntrospectiveLogger:
    """Main introspective logging system"""

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.current_session: Optional[ActivitySession] = None

        # Initialize memory logger conditionally
        if MEMORY_LOGGER_AVAILABLE:
            try:
                self.memory_logger = MemoryLogger()
            except (PermissionError, FileNotFoundError):
                self.memory_logger = None
        else:
            self.memory_logger = None

        self.reflection_history: List[ExecutionReflection] = []
        self.session_history: List[ActivitySession] = []

        self.activity_patterns: Dict[str, Any] = {}
        self.performance_trends: Dict[str, List[float]] = {}
        self.learning_insights: Set[str] = set()

        self._load_historical_data()
        self._start_new_session()

    def _load_historical_data(self):
        """Load historical reflection data"""
        reflection_file = self.data_dir / "execution_reflections.json"
        if reflection_file.exists():
            try:
                with open(reflection_file) as f:
                    data = json.load(f)
                    for item in data:
                        reflection = ExecutionReflection(
                            id=item["id"],
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            activity_type=ActivityType(item["activity_type"]),
                            operation=item["operation"],
                            code=item.get("code"),
                            result=item["result"],
                            status=ExecutionStatus(item["status"]),
                            performance=PerformanceMetrics(**item["performance"]),
                            context=item["context"],
                            insights=item["insights"],
                            lessons_learned=item["lessons_learned"],
                            improvement_suggestions=item["improvement_suggestions"],
                            user_feedback=item.get("user_feedback"),
                            error_details=item.get("error_details"),
                        )
                        self.reflection_history.append(reflection)
            except Exception as e:
                print(f"Error loading reflection history: {e}")

    def _save_reflections(self):
        """Save reflections to disk"""
        reflection_file = self.data_dir / "execution_reflections.json"
        try:
            data = []
            for reflection in self.reflection_history:
                item = asdict(reflection)
                item["timestamp"] = reflection.timestamp.isoformat()
                item["activity_type"] = reflection.activity_type.value
                item["status"] = reflection.status.value
                data.append(item)

            with open(reflection_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving reflections: {e}")

    def _start_new_session(self):
        """Start a new activity session"""
        session_id = f"session_{int(time.time())}"
        self.current_session = ActivitySession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            activities=[],
            session_insights=[],
        )

    def log_execution(
        self,
        operation: str,
        code: Optional[str],
        result: Any,
        activity_type: ActivityType = ActivityType.EXECUTION,
        performance: Optional[PerformanceMetrics] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an execution and generate reflection

        Args:
            operation: Description of the operation
            code: Code that was executed (if any)
            result: Result of the execution
            activity_type: Type of activity
            performance: Performance metrics
            context: Additional context

        Returns:
            Reflection ID
        """
        reflection_id = f"refl_{int(time.time() * 1000)}"

        # Determine status based on result
        if isinstance(result, Exception):
            status = ExecutionStatus.FAILURE
            error_details = str(result)
            result_str = f"Error: {str(result)}"
        else:
            status = ExecutionStatus.SUCCESS
            error_details = None
            result_str = str(result)

        # Create reflection
        reflection = ExecutionReflection(
            id=reflection_id,
            timestamp=datetime.now(),
            activity_type=activity_type,
            operation=operation,
            code=code,
            result=result_str,
            status=status,
            performance=performance or PerformanceMetrics(execution_time=0.0),
            context=context or {},
            insights=self._generate_insights(operation, result, context),
            lessons_learned=self._extract_lessons(operation, result, status),
            improvement_suggestions=self._suggest_improvements(operation, result, performance),
            error_details=error_details,
        )

        # Store reflection
        self.reflection_history.append(reflection)
        if self.current_session:
            self.current_session.activities.append(reflection)

        # Store in memory system
        if self.memory_logger:
            self.memory_logger.log_memory(
                content=f"Executed: {operation}",
                category="execution_reflection",
                importance=0.8,
                tags=["execution", "reflection", activity_type.value],
                metadata={
                    "reflection_id": reflection_id,
                    "status": status.value,
                    "operation": operation,
                },
            )

        # Update patterns and trends
        self._update_patterns(reflection)

        # Save to disk periodically
        if len(self.reflection_history) % 10 == 0:
            self._save_reflections()

        return reflection_id

    def _generate_insights(
        self, operation: str, result: Any, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights from an execution"""
        insights = []

        # Basic pattern recognition
        if "error" in str(result).lower():
            insights.append("Operation encountered errors - review error handling")

        if context and "retry_count" in context and context["retry_count"] > 0:
            insights.append(
                f"Operation required {context['retry_count']} retries - investigate reliability"
            )

        # Performance insights
        if context and "execution_time" in context:
            exec_time = context["execution_time"]
            if exec_time > 5.0:
                insights.append("Operation took longer than expected - optimize")
            elif exec_time < 0.1:
                insights.append("Operation was very fast - good performance")

        # Pattern-based insights
        recent_operations = [r.operation for r in self.reflection_history[-10:]]
        if recent_operations.count(operation) > 3:
            insights.append(
                "This operation has been repeated frequently - consider automation or optimization"
            )

        return insights

    def _extract_lessons(self, operation: str, result: Any, status: ExecutionStatus) -> List[str]:
        """Extract lessons learned from execution"""
        lessons = []

        if status == ExecutionStatus.FAILURE:
            lessons.append(f"Failure in {operation} - need better error handling")
        elif status == ExecutionStatus.SUCCESS:
            lessons.append(f"Successful execution of {operation} - pattern can be reused")

        # Learn from error patterns
        if "timeout" in str(result).lower():
            lessons.append("Implement timeout handling for long operations")

        if "memory" in str(result).lower():
            lessons.append("Monitor memory usage for resource-intensive operations")

        return lessons

    def _suggest_improvements(
        self, operation: str, result: Any, performance: Optional[PerformanceMetrics]
    ) -> List[str]:
        """Suggest improvements based on execution"""
        suggestions = []

        if performance:
            if performance.execution_time > 2.0:
                suggestions.append("Consider caching or optimization for better speed")

            if performance.memory_usage and performance.memory_usage > 100:
                suggestions.append("Optimize memory usage - consider streaming or chunking")

        # Suggest based on operation type
        if "parse" in operation.lower():
            suggestions.append("Consider implementing parser caching")

        if "load" in operation.lower():
            suggestions.append("Implement lazy loading for better performance")

        return suggestions

    def _update_patterns(self, reflection: ExecutionReflection):
        """Update activity patterns and trends"""
        operation = reflection.operation

        # Update performance trends
        if operation not in self.performance_trends:
            self.performance_trends[operation] = []

        self.performance_trends[operation].append(reflection.performance.execution_time)

        # Keep only recent trends
        if len(self.performance_trends[operation]) > 100:
            self.performance_trends[operation] = self.performance_trends[operation][-50:]

    def get_todays_activity(self) -> Dict[str, Any]:
        """Get today's activity summary"""
        today = datetime.now().date()
        todays_reflections = [r for r in self.reflection_history if r.timestamp.date() == today]

        if not todays_reflections:
            return {
                "date": today.isoformat(),
                "total_activities": 0,
                "summary": "No activities recorded today",
            }

        # Calculate statistics
        total_activities = len(todays_reflections)
        successful_activities = len(
            [r for r in todays_reflections if r.status == ExecutionStatus.SUCCESS]
        )
        failed_activities = len(
            [r for r in todays_reflections if r.status == ExecutionStatus.FAILURE]
        )

        success_rate = successful_activities / total_activities if total_activities > 0 else 0

        # Get activity types
        activity_types = {}
        for reflection in todays_reflections:
            activity_type = reflection.activity_type.value
            if activity_type not in activity_types:
                activity_types[activity_type] = 0
            activity_types[activity_type] += 1

        # Get top operations
        operations = {}
        for reflection in todays_reflections:
            operation = reflection.operation
            if operation not in operations:
                operations[operation] = 0
            operations[operation] += 1

        top_operations = sorted(operations.items(), key=lambda x: x[1], reverse=True)[:5]

        # Collect insights
        all_insights = []
        for reflection in todays_reflections:
            all_insights.extend(reflection.insights)

        unique_insights = list(set(all_insights))

        return {
            "date": today.isoformat(),
            "total_activities": total_activities,
            "successful_activities": successful_activities,
            "failed_activities": failed_activities,
            "success_rate": round(success_rate * 100, 1),
            "activity_types": activity_types,
            "top_operations": top_operations,
            "insights": unique_insights[:10],  # Top 10 insights
            "summary": self._generate_daily_summary(todays_reflections),
        }

    def _generate_daily_summary(self, reflections: List[ExecutionReflection]) -> str:
        """Generate a summary of the day's activities"""
        if not reflections:
            return "No activities today"

        total = len(reflections)
        successful = len([r for r in reflections if r.status == ExecutionStatus.SUCCESS])

        summary_parts = [
            f"Completed {total} activities today",
            f"Success rate: {round(successful / total * 100, 1)}%",
        ]

        # Most common activity type
        activity_counts = {}
        for r in reflections:
            activity_type = r.activity_type.value
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1

        if activity_counts:
            most_common = max(activity_counts.items(), key=lambda x: x[1])
            summary_parts.append(f"Primary focus: {most_common[0]} ({most_common[1]} times)")

        return ". ".join(summary_parts) + "."

    def auto_reflect(self) -> Dict[str, Any]:
        """Perform automatic reflection on recent activities"""
        recent_reflections = self.reflection_history[-20:] if self.reflection_history else []

        if not recent_reflections:
            return {"message": "No recent activities to reflect on"}

        # Analyze patterns
        patterns = self._analyze_patterns(recent_reflections)

        # Generate meta-insights
        meta_insights = self._generate_meta_insights(recent_reflections)

        # Suggest optimizations
        optimizations = self._suggest_optimizations(recent_reflections)

        reflection_summary = {
            "reflection_time": datetime.now().isoformat(),
            "activities_analyzed": len(recent_reflections),
            "patterns": patterns,
            "meta_insights": meta_insights,
            "optimization_suggestions": optimizations,
            "overall_assessment": self._assess_performance(recent_reflections),
        }

        # Store this meta-reflection
        self.log_execution(
            operation="auto_reflection",
            code=None,
            result=reflection_summary,
            activity_type=ActivityType.REFLECTION,
            context={"reflection_scope": "recent_activities"},
        )

        return reflection_summary

    def _analyze_patterns(self, reflections: List[ExecutionReflection]) -> Dict[str, Any]:
        """Analyze patterns in recent activities"""
        patterns = {}

        # Operation frequency
        operation_counts = {}
        for r in reflections:
            operation_counts[r.operation] = operation_counts.get(r.operation, 0) + 1

        patterns["frequent_operations"] = sorted(
            operation_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]

        # Error patterns
        error_patterns = []
        for r in reflections:
            if r.status == ExecutionStatus.FAILURE and r.error_details:
                error_patterns.append(r.error_details)

        patterns["common_errors"] = list(set(error_patterns))[:3]

        # Performance trends
        avg_execution_time = sum(r.performance.execution_time for r in reflections) / len(
            reflections
        )
        patterns["average_execution_time"] = round(avg_execution_time, 3)

        return patterns

    def _generate_meta_insights(self, reflections: List[ExecutionReflection]) -> List[str]:
        """Generate higher-level insights about behavior patterns"""
        insights = []

        success_rate = len([r for r in reflections if r.status == ExecutionStatus.SUCCESS]) / len(
            reflections
        )

        if success_rate > 0.9:
            insights.append("Excellent execution success rate - system is performing well")
        elif success_rate < 0.7:
            insights.append("Low success rate detected - investigate error causes")

        # Check for learning patterns
        learning_activities = [r for r in reflections if r.activity_type == ActivityType.LEARNING]
        if len(learning_activities) > len(reflections) * 0.3:
            insights.append("High learning activity - good knowledge acquisition pattern")

        return insights

    def _suggest_optimizations(self, reflections: List[ExecutionReflection]) -> List[str]:
        """Suggest system-wide optimizations"""
        suggestions = []

        # Analyze execution times
        slow_operations = [r for r in reflections if r.performance.execution_time > 2.0]
        if len(slow_operations) > len(reflections) * 0.2:
            suggestions.append("Consider implementing caching for frequently slow operations")

        # Analyze error frequency
        error_operations = [r for r in reflections if r.status == ExecutionStatus.FAILURE]
        if len(error_operations) > len(reflections) * 0.1:
            suggestions.append("Implement better error prevention and handling mechanisms")

        return suggestions

    def _assess_performance(self, reflections: List[ExecutionReflection]) -> str:
        """Assess overall performance"""
        if not reflections:
            return "No data to assess"

        success_rate = len([r for r in reflections if r.status == ExecutionStatus.SUCCESS]) / len(
            reflections
        )
        avg_time = sum(r.performance.execution_time for r in reflections) / len(reflections)

        if success_rate > 0.9 and avg_time < 1.0:
            return "Excellent - high success rate with good performance"
        elif success_rate > 0.8:
            return "Good - reliable execution with room for performance improvement"
        elif success_rate > 0.6:
            return "Fair - some reliability issues need attention"
        else:
            return "Poor - significant reliability and performance issues"


# Global introspective logger instance
introspective_logger = IntrospectiveLogger()


# Convenience functions
def log_neurocode_execution(
    code: str, result: Any, execution_time: float, context: Optional[Dict[str, Any]] = None
) -> str:
    """Log NeuroCode execution with reflection"""
    performance = PerformanceMetrics(execution_time=execution_time)
    return introspective_logger.log_execution(
        operation="neurocode_execution",
        code=code,
        result=result,
        activity_type=ActivityType.EXECUTION,
        performance=performance,
        context=context,
    )


def get_activity_dashboard() -> Dict[str, Any]:
    """Get comprehensive activity dashboard"""
    return {
        "todays_activity": introspective_logger.get_todays_activity(),
        "recent_reflection": introspective_logger.auto_reflect(),
        "system_status": "operational",
    }
