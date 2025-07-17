# plugin_ai_feedback.py
# 🧠 AI Feedback System for Plugin Output Analysis
# "Enable AI feedback from plugin output"

import json
import re
import ast
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, deque


@dataclass
class PluginOutput:
    """Represents plugin execution output"""
    plugin_name: str
    input_data: Any
    output_data: Any
    execution_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None


@dataclass
class FeedbackInsight:
    """AI-generated insight about plugin performance"""
    category: str  # 'performance', 'reliability', 'output_quality', 'efficiency'
    severity: str  # 'info', 'warning', 'error', 'critical'
    message: str
    confidence: float  # 0.0 to 1.0
    suggested_action: Optional[str] = None
    code_reference: Optional[str] = None


@dataclass
class PluginAnalysis:
    """Comprehensive plugin analysis"""
    plugin_name: str
    total_executions: int
    success_rate: float
    avg_execution_time: float
    performance_trend: str  # 'improving', 'stable', 'degrading'
    reliability_score: float
    efficiency_score: float
    output_quality_score: float
    insights: List[FeedbackInsight]
    recommendations: List[str]


class PluginOutputAnalyzer:
    """Analyzes plugin output and provides AI-powered feedback"""

    def __init__(self, max_history_size: int = 1000):
        self.execution_history: deque = deque(maxlen=max_history_size)
        self.plugin_stats: Dict[str, List[PluginOutput]] = defaultdict(list)
        self.feedback_cache: Dict[str, FeedbackInsight] = {}
        self.learning_patterns: Dict[str, Any] = {}

    def record_execution(self, output: PluginOutput):
        """Record a plugin execution for analysis"""
        self.execution_history.append(output)
        self.plugin_stats[output.plugin_name].append(output)

        # Keep only recent executions per plugin
        if len(self.plugin_stats[output.plugin_name]) > 100:
            self.plugin_stats[output.plugin_name] = self.plugin_stats[output.plugin_name][-100:]

    def analyze_plugin_output(self, output: PluginOutput) -> List[FeedbackInsight]:
        """Analyze a single plugin output and generate insights"""
        insights = []

        # Performance analysis
        perf_insights = self._analyze_performance(output)
        insights.extend(perf_insights)

        # Output quality analysis
        quality_insights = self._analyze_output_quality(output)
        insights.extend(quality_insights)

        # Reliability analysis
        reliability_insights = self._analyze_reliability(output)
        insights.extend(reliability_insights)

        # Pattern recognition
        pattern_insights = self._analyze_patterns(output)
        insights.extend(pattern_insights)

        return insights

    def _analyze_performance(self, output: PluginOutput) -> List[FeedbackInsight]:
        """Analyze performance aspects of plugin output"""
        insights = []

        # Execution time analysis
        if output.execution_time > 2.0:
            insights.append(FeedbackInsight(
                category='performance',
                severity='warning',
                message=f'Slow execution time: {output.execution_time:.2f}s',
                confidence=0.9,
                suggested_action='Consider optimizing plugin logic or adding caching',
                code_reference='fn execute()'
            ))
        elif output.execution_time > 5.0:
            insights.append(FeedbackInsight(
                category='performance',
                severity='error',
                message=f'Very slow execution: {output.execution_time:.2f}s',
                confidence=0.95,
                suggested_action='Urgent optimization needed - consider async processing',
                code_reference='fn execute()'
            ))

        # Memory usage analysis
        if output.memory_usage and output.memory_usage > 50 * 1024 * 1024:  # 50MB
            insights.append(FeedbackInsight(
                category='performance',
                severity='warning',
                message=f'High memory usage: {output.memory_usage / 1024 / 1024:.1f}MB',
                confidence=0.8,
                suggested_action='Review memory allocation and consider cleanup',
                code_reference='Memory optimization needed'
            ))

        # Historical performance comparison
        if output.plugin_name in self.plugin_stats:
            recent_times = [exec.execution_time for exec in self.plugin_stats[output.plugin_name][-10:]]
            if len(recent_times) >= 5:
                avg_time = sum(recent_times) / len(recent_times)
                if output.execution_time > avg_time * 1.5:
                    insights.append(FeedbackInsight(
                        category='performance',
                        severity='info',
                        message=f'Slower than recent average ({avg_time:.2f}s)',
                        confidence=0.7,
                        suggested_action='Check for input complexity or system load',
                        code_reference='Performance regression'
                    ))

        return insights

    def _analyze_output_quality(self, output: PluginOutput) -> List[FeedbackInsight]:
        """Analyze the quality of plugin output"""
        insights = []

        if not output.success:
            insights.append(FeedbackInsight(
                category='output_quality',
                severity='error',
                message=f'Plugin execution failed: {output.error_message}',
                confidence=1.0,
                suggested_action='Fix the error and add proper error handling',
                code_reference='Error handling'
            ))
            return insights

        # Analyze output structure
        if output.output_data is None:
            insights.append(FeedbackInsight(
                category='output_quality',
                severity='warning',
                message='Plugin returned null/undefined output',
                confidence=0.8,
                suggested_action='Ensure plugin returns meaningful data',
                code_reference='return statement'
            ))

        # Check for empty outputs
        if isinstance(output.output_data, (str, list, dict)):
            if not output.output_data:
                insights.append(FeedbackInsight(
                    category='output_quality',
                    severity='info',
                    message='Plugin returned empty output',
                    confidence=0.7,
                    suggested_action='Verify if empty output is expected',
                    code_reference='Output validation'
                ))

        # Check for error indicators in output
        if isinstance(output.output_data, str):
            error_indicators = ['error', 'failed', 'exception', 'undefined', 'null']
            output_lower = output.output_data.lower()
            for indicator in error_indicators:
                if indicator in output_lower:
                    insights.append(FeedbackInsight(
                        category='output_quality',
                        severity='warning',
                        message=f'Output contains error indicator: "{indicator}"',
                        confidence=0.6,
                        suggested_action='Review output for potential issues',
                        code_reference='Output content'
                    ))
                    break

        # Check for structured output
        if isinstance(output.output_data, dict):
            if 'success' in output.output_data or 'status' in output.output_data:
                insights.append(FeedbackInsight(
                    category='output_quality',
                    severity='info',
                    message='Good: Plugin uses structured output format',
                    confidence=0.9,
                    suggested_action='Continue using structured output patterns',
                    code_reference='Output structure'
                ))

        return insights

    def _analyze_reliability(self, output: PluginOutput) -> List[FeedbackInsight]:
        """Analyze reliability aspects"""
        insights = []

        if output.plugin_name not in self.plugin_stats:
            return insights

        # Calculate success rate
        recent_executions = self.plugin_stats[output.plugin_name][-20:]  # Last 20 executions
        if len(recent_executions) >= 5:
            success_count = sum(1 for exec in recent_executions if exec.success)
            success_rate = success_count / len(recent_executions)

            if success_rate < 0.8:
                insights.append(FeedbackInsight(
                    category='reliability',
                    severity='warning',
                    message=f'Low success rate: {success_rate:.1%}',
                    confidence=0.9,
                    suggested_action='Investigate common failure patterns',
                    code_reference='Error handling and validation'
                ))
            elif success_rate < 0.5:
                insights.append(FeedbackInsight(
                    category='reliability',
                    severity='error',
                    message=f'Very low success rate: {success_rate:.1%}',
                    confidence=0.95,
                    suggested_action='Urgent: Review plugin implementation',
                    code_reference='Core plugin logic'
                ))

        # Check for consistency in execution times
        if len(recent_executions) >= 10:
            times = [exec.execution_time for exec in recent_executions if exec.success]
            if times:
                avg_time = sum(times) / len(times)
                variance = sum((t - avg_time) ** 2 for t in times) / len(times)
                if variance > avg_time:  # High variance
                    insights.append(FeedbackInsight(
                        category='reliability',
                        severity='info',
                        message='Inconsistent execution times detected',
                        confidence=0.7,
                        suggested_action='Check for input-dependent performance',
                        code_reference='Performance optimization'
                    ))

        return insights

    def _analyze_patterns(self, output: PluginOutput) -> List[FeedbackInsight]:
        """Analyze patterns in plugin behavior"""
        insights = []

        # Time-based patterns
        current_hour = output.timestamp.hour
        if current_hour in [2, 3, 4]:  # Early morning
            insights.append(FeedbackInsight(
                category='efficiency',
                severity='info',
                message='Plugin execution during low-activity hours',
                confidence=0.5,
                suggested_action='Consider scheduling heavy operations during this time',
                code_reference='Scheduling optimization'
            ))

        # Input pattern analysis
        if hasattr(output.input_data, '__len__'):
            input_size = len(str(output.input_data))
            if input_size > 10000:  # Large input
                insights.append(FeedbackInsight(
                    category='efficiency',
                    severity='info',
                    message=f'Large input data: {input_size} characters',
                    confidence=0.8,
                    suggested_action='Consider input chunking or streaming',
                    code_reference='Input processing'
                ))

        return insights

    def get_plugin_analysis(self, plugin_name: str) -> PluginAnalysis:
        """Get comprehensive analysis for a specific plugin"""
        if plugin_name not in self.plugin_stats:
            return PluginAnalysis(
                plugin_name=plugin_name,
                total_executions=0,
                success_rate=0.0,
                avg_execution_time=0.0,
                performance_trend='unknown',
                reliability_score=0.0,
                efficiency_score=0.0,
                output_quality_score=0.0,
                insights=[],
                recommendations=[]
            )

        executions = self.plugin_stats[plugin_name]
        total_executions = len(executions)

        # Calculate success rate
        successful_executions = [exec for exec in executions if exec.success]
        success_rate = len(successful_executions) / total_executions if total_executions > 0 else 0.0

        # Calculate average execution time
        if successful_executions:
            avg_execution_time = sum(exec.execution_time for exec in successful_executions) / len(successful_executions)
        else:
            avg_execution_time = 0.0

        # Calculate performance trend
        performance_trend = self._calculate_performance_trend(executions)

        # Calculate scores
        reliability_score = self._calculate_reliability_score(executions)
        efficiency_score = self._calculate_efficiency_score(executions)
        output_quality_score = self._calculate_output_quality_score(executions)

        # Generate insights from recent executions
        insights = []
        for exec in executions[-5:]:  # Last 5 executions
            insights.extend(self.analyze_plugin_output(exec))

        # Generate recommendations
        recommendations = self._generate_recommendations(executions, insights)

        return PluginAnalysis(
            plugin_name=plugin_name,
            total_executions=total_executions,
            success_rate=success_rate,
            avg_execution_time=avg_execution_time,
            performance_trend=performance_trend,
            reliability_score=reliability_score,
            efficiency_score=efficiency_score,
            output_quality_score=output_quality_score,
            insights=insights,
            recommendations=recommendations
        )

    def _calculate_performance_trend(self, executions: List[PluginOutput]) -> str:
        """Calculate performance trend"""
        if len(executions) < 10:
            return 'insufficient_data'

        # Compare recent vs older executions
        recent_times = [exec.execution_time for exec in executions[-5:] if exec.success]
        older_times = [exec.execution_time for exec in executions[-15:-5] if exec.success]

        if not recent_times or not older_times:
            return 'insufficient_data'

        recent_avg = sum(recent_times) / len(recent_times)
        older_avg = sum(older_times) / len(older_times)

        if recent_avg < older_avg * 0.9:
            return 'improving'
        elif recent_avg > older_avg * 1.1:
            return 'degrading'
        else:
            return 'stable'

    def _calculate_reliability_score(self, executions: List[PluginOutput]) -> float:
        """Calculate reliability score (0.0 to 1.0)"""
        if not executions:
            return 0.0

        # Base score on success rate
        success_rate = sum(1 for exec in executions if exec.success) / len(executions)

        # Adjust for consistency
        if len(executions) >= 10:
            recent_success_rate = sum(1 for exec in executions[-10:] if exec.success) / 10
            consistency_factor = 1.0 - abs(success_rate - recent_success_rate)
        else:
            consistency_factor = 1.0

        return success_rate * consistency_factor

    def _calculate_efficiency_score(self, executions: List[PluginOutput]) -> float:
        """Calculate efficiency score (0.0 to 1.0)"""
        successful_executions = [exec for exec in executions if exec.success]
        if not successful_executions:
            return 0.0

        # Base score on execution time
        avg_time = sum(exec.execution_time for exec in successful_executions) / len(successful_executions)

        # Score decreases with execution time
        if avg_time <= 0.1:
            time_score = 1.0
        elif avg_time <= 0.5:
            time_score = 0.9
        elif avg_time <= 1.0:
            time_score = 0.8
        elif avg_time <= 2.0:
            time_score = 0.6
        else:
            time_score = 0.4

        # Factor in memory usage if available
        memory_scores = []
        for exec in successful_executions:
            if exec.memory_usage:
                if exec.memory_usage < 10 * 1024 * 1024:  # < 10MB
                    memory_scores.append(1.0)
                elif exec.memory_usage < 50 * 1024 * 1024:  # < 50MB
                    memory_scores.append(0.8)
                else:
                    memory_scores.append(0.6)

        if memory_scores:
            memory_score = sum(memory_scores) / len(memory_scores)
            return (time_score + memory_score) / 2

        return time_score

    def _calculate_output_quality_score(self, executions: List[PluginOutput]) -> float:
        """Calculate output quality score (0.0 to 1.0)"""
        successful_executions = [exec for exec in executions if exec.success]
        if not successful_executions:
            return 0.0

        quality_scores = []
        for exec in successful_executions:
            score = 1.0

            # Penalize for null/empty outputs
            if exec.output_data is None:
                score -= 0.3
            elif isinstance(exec.output_data, (str, list, dict)) and not exec.output_data:
                score -= 0.2

            # Reward for structured output
            if isinstance(exec.output_data, dict) and ('success' in exec.output_data or 'status' in exec.output_data):
                score += 0.1

            # Penalize for error indicators in output
            if isinstance(exec.output_data, str):
                error_indicators = ['error', 'failed', 'exception']
                if any(indicator in exec.output_data.lower() for indicator in error_indicators):
                    score -= 0.2

            quality_scores.append(max(0.0, min(1.0, score)))

        return sum(quality_scores) / len(quality_scores)

    def _generate_recommendations(self, executions: List[PluginOutput], insights: List[FeedbackInsight]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Performance recommendations
        perf_insights = [insight for insight in insights if insight.category == 'performance']
        if perf_insights:
            recommendations.append("⚡ Optimize plugin performance - multiple performance issues detected")

        # Reliability recommendations
        reliability_insights = [insight for insight in insights if insight.category == 'reliability']
        if reliability_insights:
            recommendations.append("🔧 Improve error handling and input validation")

        # Output quality recommendations
        quality_insights = [insight for insight in insights if insight.category == 'output_quality']
        if quality_insights:
            recommendations.append("📊 Standardize output format with success/error indicators")

        # General recommendations based on execution patterns
        if len(executions) >= 10:
            avg_time = sum(exec.execution_time for exec in executions[-10:] if exec.success) / 10
            if avg_time > 1.0:
                recommendations.append("🚀 Consider async processing for long-running operations")

        return recommendations

    def get_real_time_feedback(self, plugin_name: str) -> Dict[str, Any]:
        """Get real-time feedback for a plugin"""
        if plugin_name not in self.plugin_stats:
            return {"status": "no_data", "message": "No execution data available"}

        recent_executions = self.plugin_stats[plugin_name][-5:]

        # Quick health check
        success_count = sum(1 for exec in recent_executions if exec.success)
        success_rate = success_count / len(recent_executions)

        if success_rate < 0.5:
            status = "critical"
            message = f"Plugin failing frequently ({success_rate:.1%} success rate)"
        elif success_rate < 0.8:
            status = "warning"
            message = f"Plugin showing reliability issues ({success_rate:.1%} success rate)"
        else:
            status = "healthy"
            message = f"Plugin performing well ({success_rate:.1%} success rate)"

        # Performance check
        avg_time = 0.0
        if recent_executions:
            avg_time = sum(exec.execution_time for exec in recent_executions if exec.success) / max(1, success_count)
            if avg_time > 2.0:
                status = max(status, "warning")
                message += f" - Slow execution ({avg_time:.2f}s average)"

        return {
            "status": status,
            "message": message,
            "recent_executions": len(recent_executions),
            "success_rate": success_rate,
            "avg_execution_time": avg_time
        }

    def export_analysis(self, plugin_name: Optional[str] = None) -> Dict[str, Any]:
        """Export analysis data for external use"""
        if plugin_name:
            analysis = self.get_plugin_analysis(plugin_name)
            return {
                "plugin_name": plugin_name,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Export all plugins
            all_analyses = {}
            for plugin_name in self.plugin_stats:
                all_analyses[plugin_name] = self.get_plugin_analysis(plugin_name)

            return {
                "all_plugins": all_analyses,
                "total_executions": len(self.execution_history),
                "timestamp": datetime.now().isoformat()
            }


# Example usage and testing
if __name__ == "__main__":
    # Create analyzer
    analyzer = PluginOutputAnalyzer()

    # Simulate plugin executions
    test_outputs = [
        PluginOutput(
            plugin_name="weather_plugin",
            input_data="New York",
            output_data={"temperature": 22, "condition": "sunny"},
            execution_time=0.5,
            timestamp=datetime.now(),
            success=True
        ),
        PluginOutput(
            plugin_name="weather_plugin",
            input_data="London",
            output_data=None,
            execution_time=2.5,
            timestamp=datetime.now(),
            success=False,
            error_message="API timeout"
        ),
        PluginOutput(
            plugin_name="calculator_plugin",
            input_data="2 + 2",
            output_data=4,
            execution_time=0.1,
            timestamp=datetime.now(),
            success=True
        )
    ]

    # Record and analyze
    for output in test_outputs:
        analyzer.record_execution(output)
        insights = analyzer.analyze_plugin_output(output)

        print(f"\n🔍 Analysis for {output.plugin_name}:")
        for insight in insights:
            print(f"  {insight.severity.upper()}: {insight.message}")
            if insight.suggested_action:
                print(f"    💡 Suggestion: {insight.suggested_action}")

    # Get comprehensive analysis
    weather_analysis = analyzer.get_plugin_analysis("weather_plugin")
    print(f"\n📊 Weather Plugin Analysis:")
    print(f"  Success Rate: {weather_analysis.success_rate:.1%}")
    print(f"  Reliability Score: {weather_analysis.reliability_score:.2f}")
    print(f"  Performance Trend: {weather_analysis.performance_trend}")

    for rec in weather_analysis.recommendations:
        print(f"  📝 {rec}")
