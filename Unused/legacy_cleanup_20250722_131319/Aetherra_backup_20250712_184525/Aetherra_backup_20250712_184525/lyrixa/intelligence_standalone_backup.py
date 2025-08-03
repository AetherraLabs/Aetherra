#!/usr/bin/env python3
"""
Lyrixa Intelligence Stack - Advanced AI capabilities and insights
Provides real-time intelligence, system monitoring, and cognitive analysis
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.logging_utils import log


class LyrixaIntelligenceStack:
    """
    Advanced intelligence layer for Lyrixa providing:
    - Real-time system insights
    - Performance monitoring
    - Agent behavior analysis
    - Learning recommendations
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or str(Path.cwd())
        self.insights = []
        self.performance_metrics = {}
        self.agent_analytics = {}
        self.learning_patterns = []
        self.start_time = time.time()

        log("🧠 Lyrixa Intelligence Stack initialized", "success")

    async def get_system_intelligence(self) -> Dict[str, Any]:
        """Get comprehensive system intelligence report"""
        uptime = time.time() - self.start_time

        return {
            "status": "Active",
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "insights_count": len(self.insights),
            "learning_patterns": len(self.learning_patterns),
            "performance_score": self._calculate_performance_score(),
            "recommendations": await self._generate_recommendations(),
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_agent_performance(self, agent_name: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual agent performance"""
        if agent_name not in self.agent_analytics:
            self.agent_analytics[agent_name] = {
                "total_requests": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "error_count": 0,
                "improvement_suggestions": []
            }

        analytics = self.agent_analytics[agent_name]
        analytics["total_requests"] += 1
        analytics["last_update"] = datetime.now().isoformat()

        # Update metrics based on provided data
        if "success" in metrics:
            success_count = analytics.get("success_count", 0) + (1 if metrics["success"] else 0)
            analytics["success_count"] = success_count
            analytics["success_rate"] = success_count / analytics["total_requests"]

        if "response_time" in metrics:
            total_time = analytics.get("total_response_time", 0) + metrics["response_time"]
            analytics["total_response_time"] = total_time
            analytics["avg_response_time"] = total_time / analytics["total_requests"]

        if "error" in metrics:
            analytics["error_count"] += 1

        # Generate improvement suggestions
        analytics["improvement_suggestions"] = self._generate_agent_suggestions(agent_name, analytics)

        return analytics

    async def record_insight(self, insight_type: str, data: Dict[str, Any]):
        """Record a new intelligence insight"""
        insight = {
            "type": insight_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "id": len(self.insights)
        }

        self.insights.append(insight)

        # Keep only last 100 insights to prevent memory bloat
        if len(self.insights) > 100:
            self.insights = self.insights[-100:]

        log(f"📊 Intelligence insight recorded: {insight_type}", "info")

    async def get_learning_recommendations(self) -> List[str]:
        """Generate learning and improvement recommendations"""
        recommendations = []

        # Agent-based recommendations
        for agent_name, analytics in self.agent_analytics.items():
            if analytics.get("success_rate", 1.0) < 0.8:
                recommendations.append(f"[TOOL] {agent_name}: Success rate low ({analytics['success_rate']:.1%}), consider optimization")

            if analytics.get("avg_response_time", 0) > 2.0:
                recommendations.append(f"⚡ {agent_name}: Average response time high ({analytics['avg_response_time']:.2f}s), consider caching")

        # System-wide recommendations
        if len(self.insights) > 50:
            recommendations.append("🧠 Rich insight history available - consider implementing pattern analysis")

        uptime = time.time() - self.start_time
        if uptime > 3600:  # 1 hour
            recommendations.append("🕐 Extended session detected - consider periodic system optimization")

        # Add forward-looking suggestions
        recommendations.extend([
            "📈 Monitor agent conversation patterns for optimization opportunities",
            "🎯 Consider implementing predictive response caching",
            "🔄 Regular system health checks recommended"
        ])

        return recommendations[:10]  # Return top 10 recommendations

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        uptime = time.time() - self.start_time

        return {
            "uptime": self._format_uptime(uptime),
            "active_agents": len(self.agent_analytics),
            "total_insights": len(self.insights),
            "recent_activity": len([
                i for i in self.insights
                if self._parse_timestamp(i["timestamp"]) > datetime.now() - timedelta(minutes=5)
            ]),
            "performance_score": self._calculate_performance_score(),
            "status": "🟢 Optimal" if self._calculate_performance_score() > 0.8 else
                     "🟡 Good" if self._calculate_performance_score() > 0.6 else "🔴 Needs Attention"
        }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def _calculate_performance_score(self) -> float:
        """Calculate overall system performance score (0-1)"""
        if not self.agent_analytics:
            return 1.0

        total_score = 0.0
        agent_count = len(self.agent_analytics)

        for analytics in self.agent_analytics.values():
            success_rate = analytics.get("success_rate", 1.0)
            response_time = analytics.get("avg_response_time", 0.5)

            # Score based on success rate (0.7 weight) and response time (0.3 weight)
            time_score = max(0, 1 - (response_time - 0.5) / 2.0)  # Optimal at 0.5s, penalty after 2.5s
            agent_score = (success_rate * 0.7) + (time_score * 0.3)
            total_score += agent_score

        return total_score / agent_count if agent_count > 0 else 1.0

    async def _generate_recommendations(self) -> List[str]:
        """Generate intelligent system recommendations"""
        return await self.get_learning_recommendations()

    def _generate_agent_suggestions(self, agent_name: str, analytics: Dict[str, Any]) -> List[str]:
        """Generate specific suggestions for an agent"""
        suggestions = []

        success_rate = analytics.get("success_rate", 1.0)
        avg_time = analytics.get("avg_response_time", 0.5)
        error_count = analytics.get("error_count", 0)

        if success_rate < 0.9:
            suggestions.append("Consider implementing better error handling")

        if avg_time > 1.5:
            suggestions.append("Optimize response processing for faster interactions")

        if error_count > 5:
            suggestions.append("Review error patterns for systematic improvements")

        if analytics.get("total_requests", 0) > 100:
            suggestions.append("High usage detected - consider implementing caching")

        return suggestions

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse ISO timestamp string to datetime"""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            return datetime.now()

    async def shutdown(self):
        """Gracefully shutdown intelligence stack"""
        log("🧠 Intelligence stack shutting down...", "info")

        # Save final analytics if needed
        final_report = await self.get_system_intelligence()
        log(f"📊 Final performance score: {final_report['performance_score']:.2f}", "info")


# Intelligence utilities for system analysis
def analyze_conversation_patterns(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze conversation patterns for insights"""
    if not messages:
        return {"pattern": "no_data", "insights": []}

    total_messages = len(messages)
    user_messages = [m for m in messages if m.get("role") == "user"]
    assistant_messages = [m for m in messages if m.get("role") == "assistant"]

    return {
        "pattern": "active_conversation" if total_messages > 10 else "starting_conversation",
        "total_messages": total_messages,
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "avg_message_length": sum(len(str(m.get("content", ""))) for m in messages) / total_messages,
        "insights": [
            "Conversation is active and engaging" if total_messages > 20 else "Building conversation history",
            "Good interaction balance" if abs(len(user_messages) - len(assistant_messages)) < 3 else "Consider more balanced interaction",
            "Rich communication detected" if any(len(str(m.get("content", ""))) > 200 for m in messages) else "Concise communication style"
        ]
    }


def generate_intelligence_summary(intelligence_data: Dict[str, Any]) -> str:
    """Generate a human-readable intelligence summary"""
    uptime = intelligence_data.get("uptime_formatted", "0s")
    score = intelligence_data.get("performance_score", 1.0)
    insights = intelligence_data.get("insights_count", 0)

    status_emoji = "🟢" if score > 0.8 else "🟡" if score > 0.6 else "🔴"

    return f"""
{status_emoji} **Intelligence Summary**
⏱️ Uptime: {uptime}
📊 Performance: {score:.1%}
🧠 Insights: {insights} recorded
📈 Status: {'Excellent' if score > 0.8 else 'Good' if score > 0.6 else 'Needs Attention'}

💡 System is {'operating optimally' if score > 0.8 else 'performing well with room for improvement' if score > 0.6 else 'requiring attention for optimal performance'}
"""
