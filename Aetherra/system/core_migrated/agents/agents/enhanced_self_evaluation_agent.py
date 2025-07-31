#!/usr/bin/env python3
"""
🤖 ENHANCED SELF-EVALUATION AGENT
=================================

Advanced autonomous agent that continuously monitors, evaluates, and improves
Lyrixa's performance and capabilities based on self-insights and patterns.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .enhanced_memory import LyrixaEnhancedMemorySystem


class EnhancedSelfEvaluationAgent:
    """Autonomous agent for continuous self-evaluation and improvement"""

    def __init__(
        self,
        memory_system: LyrixaEnhancedMemorySystem,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.memory_system = memory_system
        self.config = config or {}

        # Default configuration
        self.default_config = {
            "evaluation_interval_hours": 6,
            "insight_analysis_depth": "deep",
            "auto_remediation_threshold": 0.7,  # Confidence threshold for auto-remediation
            "pattern_detection_window_days": 7,
            "max_auto_actions_per_cycle": 3,
        }

        self.is_running = False
        self.evaluation_patterns = {
            "performance_degradation": [
                "slow",
                "timeout",
                "performance",
                "lag",
                "delay",
            ],
            "error_patterns": ["error", "exception", "failed", "crash", "bug"],
            "improvement_opportunities": [
                "todo",
                "fixme",
                "optimize",
                "refactor",
                "improve",
            ],
            "user_satisfaction_indicators": [
                "helpful",
                "thanks",
                "great",
                "perfect",
                "excellent",
                "frustrated",
                "confused",
            ],
        }

    async def start_continuous_evaluation(self):
        """Start continuous self-evaluation cycle"""
        if self.is_running:
            print("🤖 Self-evaluation agent already running")
            return

        self.is_running = True
        print("🤖 Starting continuous self-evaluation agent...")

        try:
            while self.is_running:
                await self._run_evaluation_cycle()

                # Wait for next evaluation
                interval_hours = self.config.get(
                    "evaluation_interval_hours",
                    self.default_config["evaluation_interval_hours"],
                )
                await asyncio.sleep(interval_hours * 3600)

        except Exception as e:
            print(f"❌ Self-evaluation agent error: {e}")
        finally:
            self.is_running = False

    async def stop_continuous_evaluation(self):
        """Stop continuous evaluation"""
        print("🛑 Stopping self-evaluation agent...")
        self.is_running = False

    async def run_immediate_evaluation(self) -> Dict[str, Any]:
        """Run immediate evaluation cycle"""
        print("🤖 Running immediate self-evaluation...")
        return await self._run_evaluation_cycle()

    async def _run_evaluation_cycle(self) -> Dict[str, Any]:
        """Run a complete evaluation cycle"""
        cycle_start = datetime.now()
        print(f"🔍 Starting evaluation cycle at {cycle_start.isoformat()}")

        # Step 1: Analyze recent self-insights
        insight_analysis = await self._analyze_recent_insights()

        # Step 2: Detect patterns and trends
        pattern_analysis = await self._detect_patterns()

        # Step 3: Evaluate system performance
        performance_analysis = await self._evaluate_system_performance()

        # Step 4: Generate improvement recommendations
        recommendations = await self._generate_improvement_recommendations(
            insight_analysis, pattern_analysis, performance_analysis
        )

        # Step 5: Execute safe auto-improvements
        auto_improvements = await self._execute_auto_improvements(recommendations)

        # Step 6: Store evaluation results
        evaluation_results = {
            "timestamp": cycle_start.isoformat(),
            "insight_analysis": insight_analysis,
            "pattern_analysis": pattern_analysis,
            "performance_analysis": performance_analysis,
            "recommendations": recommendations,
            "auto_improvements": auto_improvements,
            "cycle_duration": (datetime.now() - cycle_start).total_seconds(),
        }

        await self._store_evaluation_results(evaluation_results)

        print(
            f"✅ Evaluation cycle complete. Generated {len(recommendations)} recommendations"
        )

        return evaluation_results

    async def _analyze_recent_insights(self) -> Dict[str, Any]:
        """Analyze recent self-insights for actionable patterns"""
        try:
            # Get recent self-insights
            insights = await self.memory_system.get_memories_by_tags(
                ["self_insight", "introspection"], limit=100
            )

            # Filter recent insights (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_insights = []

            for insight in insights:
                created_at = insight.get("created_at", "")
                if created_at:
                    try:
                        insight_time = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                        if insight_time > cutoff_time:
                            recent_insights.append(insight)
                    except ValueError:
                        continue

            # Analyze insight patterns
            analysis = {
                "total_insights": len(recent_insights),
                "high_priority_count": 0,
                "medium_priority_count": 0,
                "low_priority_count": 0,
                "actionable_insights": [],
                "recurring_issues": [],
                "improvement_opportunities": [],
            }

            issue_tracker = {}

            for insight_memory in recent_insights:
                content = insight_memory.get("content", {})
                insights_data = content.get("insights", [])

                for insight in insights_data:
                    severity = insight.get("severity", "low")
                    issue_type = insight.get("type", "unknown")
                    issue_desc = insight.get("issue", "")

                    # Count by severity
                    if severity == "high":
                        analysis["high_priority_count"] += 1
                    elif severity == "medium":
                        analysis["medium_priority_count"] += 1
                    else:
                        analysis["low_priority_count"] += 1

                    # Track recurring issues
                    issue_key = f"{issue_type}:{issue_desc[:50]}"
                    if issue_key not in issue_tracker:
                        issue_tracker[issue_key] = 0
                    issue_tracker[issue_key] += 1

                    # Collect actionable insights
                    if insight.get("actionable", False) or severity == "high":
                        analysis["actionable_insights"].append(insight)

            # Identify recurring issues (appeared more than once)
            analysis["recurring_issues"] = [
                {"issue": issue, "count": count}
                for issue, count in issue_tracker.items()
                if count > 1
            ]

            return analysis

        except Exception as e:
            print(f"⚠️ Error analyzing recent insights: {e}")
            return {"error": str(e)}

    async def _detect_patterns(self) -> Dict[str, Any]:
        """Detect patterns in system behavior and user interactions"""
        try:
            # Get recent memories for pattern analysis

            # Analyze conversation patterns
            conversation_memories = await self.memory_system.get_memories_by_tags(
                ["conversation", "user_interaction"], limit=200
            )

            # Analyze error patterns
            error_memories = await self.memory_system.get_memories_by_tags(
                ["error", "exception", "failed"], limit=50
            )

            pattern_analysis = {
                "conversation_patterns": self._analyze_conversation_patterns(
                    conversation_memories
                ),
                "error_patterns": await self._analyze_error_patterns(error_memories),
                "performance_trends": await self._analyze_performance_trends(),
                "user_satisfaction_trend": await self._analyze_user_satisfaction(
                    conversation_memories
                ),
            }

            return pattern_analysis

        except Exception as e:
            print(f"⚠️ Error detecting patterns: {e}")
            return {"error": str(e)}

    def _analyze_conversation_patterns(self, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation patterns for insights, user experience, and context-aware help"""
        total_conversations = len(memories)
        if total_conversations == 0:
            return {"total_conversations": 0}

        # Track question types, follow-ups, user sentiment, and context
        complex_queries = 0
        successful_responses = 0
        follow_ups = 0
        positive_feedback = 0
        negative_feedback = 0
        context_requests = 0
        for memory in memories[-50:]:  # Last 50 conversations
            content = memory.get("content", {})
            user_input = content.get("user_input", "")
            response = content.get("lyrixa_response", "")

            # Detect complex queries
            if len(user_input.split()) > 20 or any(
                word in user_input.lower()
                for word in ["complex", "difficult", "help", "explain", "why", "how"]
            ):
                complex_queries += 1

            # Detect follow-up questions
            if any(
                q in user_input.lower() for q in ["again", "more", "clarify", "expand"]
            ):
                follow_ups += 1

            # Detect context-aware help requests
            if any(
                q in user_input.lower()
                for q in [
                    "context",
                    "remind",
                    "what was",
                    "previous",
                    "history",
                    "summarize",
                ]
            ):
                context_requests += 1

            # Detect successful responses (improved heuristic)
            if len(response) > 50 and not any(
                err in response.lower() for err in ["error", "failed", "sorry"]
            ):
                successful_responses += 1

            # User sentiment (simple keyword-based)
            if any(
                word in user_input.lower()
                for word in ["thanks", "great", "awesome", "perfect", "helpful"]
            ):
                positive_feedback += 1
            if any(
                word in user_input.lower()
                for word in ["frustrated", "confused", "bad", "useless"]
            ):
                negative_feedback += 1

        return {
            "total_conversations": total_conversations,
            "complex_queries": complex_queries,
            "follow_ups": follow_ups,
            "context_requests": context_requests,
            "successful_responses": successful_responses,
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "success_rate": successful_responses / min(50, total_conversations)
            if total_conversations > 0
            else 0,
        }

    async def _analyze_error_patterns(self, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns to identify systemic issues"""
        error_types = {}
        error_frequency = []

        for memory in memories:
            content = memory.get("content", {})
            error_info = str(content)

            # Extract error types (simplified)
            for error_pattern in self.evaluation_patterns["error_patterns"]:
                if error_pattern in error_info.lower():
                    if error_pattern not in error_types:
                        error_types[error_pattern] = 0
                    error_types[error_pattern] += 1

            # Track error timing
            created_at = memory.get("created_at", "")
            if created_at:
                error_frequency.append(created_at)

        return {
            "total_errors": len(memories),
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0]
            if error_types
            else None,
            "error_frequency_trend": "stable",  # Simplified - could calculate actual trend
        }

    async def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze system performance trends"""
        # Get recent performance data
        performance_memories = await self.memory_system.get_memories_by_tags(
            ["performance", "metrics"], limit=20
        )

        if not performance_memories:
            return {"status": "no_performance_data"}

        # Simplified performance analysis
        return {
            "performance_samples": len(performance_memories),
            "trend": "stable",  # Could implement actual trend calculation
            "status": "operational",
        }

    async def _analyze_user_satisfaction(
        self, conversation_memories: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze user satisfaction indicators"""
        positive_indicators = 0
        negative_indicators = 0

        for memory in conversation_memories[-20:]:  # Last 20 conversations
            content = memory.get("content", {})
            user_input = content.get("user_input", "").lower()

            # Check for satisfaction indicators
            for indicator in self.evaluation_patterns["user_satisfaction_indicators"]:
                if indicator in user_input:
                    if indicator in [
                        "helpful",
                        "thanks",
                        "great",
                        "perfect",
                        "excellent",
                    ]:
                        positive_indicators += 1
                    elif indicator in ["frustrated", "confused"]:
                        negative_indicators += 1

        total_indicators = positive_indicators + negative_indicators
        satisfaction_score = (
            positive_indicators / total_indicators if total_indicators > 0 else 0.5
        )

        return {
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators,
            "satisfaction_score": satisfaction_score,
            "trend": "positive"
            if satisfaction_score > 0.6
            else "neutral"
            if satisfaction_score > 0.4
            else "needs_attention",
        }

    async def _evaluate_system_performance(self) -> Dict[str, Any]:
        """Evaluate overall system performance"""
        try:
            # Get system metrics (simplified)
            return {
                "memory_system_health": "operational",
                "plugin_system_health": "operational",
                "conversation_engine_health": "operational",
                "overall_health": "good",
                "uptime_estimate": "stable",
                "resource_usage": "normal",
            }

        except Exception as e:
            return {"error": str(e)}

    async def _generate_improvement_recommendations(
        self, insight_analysis: Dict, pattern_analysis: Dict, performance_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """Generate specific improvement recommendations (more powerful and user-centric)"""
        recommendations = []

        # Analyze high priority insights
        high_priority_count = insight_analysis.get("high_priority_count", 0)
        if high_priority_count > 0:
            recommendations.append(
                {
                    "type": "urgent_attention",
                    "priority": "high",
                    "description": f"Address {high_priority_count} high-priority issues",
                    "auto_executable": False,
                    "confidence": 0.9,
                }
            )

        # Analyze recurring issues
        recurring_issues = insight_analysis.get("recurring_issues", [])
        if len(recurring_issues) > 2:
            recommendations.append(
                {
                    "type": "pattern_resolution",
                    "priority": "medium",
                    "description": f"Resolve {len(recurring_issues)} recurring issues",
                    "auto_executable": True,
                    "confidence": 0.8,
                }
            )

        # Analyze error patterns
        error_patterns = pattern_analysis.get("error_patterns", {})
        total_errors = error_patterns.get("total_errors", 0)
        if total_errors > 5:
            recommendations.append(
                {
                    "type": "error_reduction",
                    "priority": "medium",
                    "description": f"Investigate and reduce error frequency ({total_errors} recent errors)",
                    "auto_executable": False,
                    "confidence": 0.7,
                }
            )

        # Analyze user satisfaction and feedback
        user_satisfaction = pattern_analysis.get("user_satisfaction_trend", {})
        satisfaction_score = user_satisfaction.get("satisfaction_score", 0.5)
        if satisfaction_score < 0.6:
            recommendations.append(
                {
                    "type": "user_experience_improvement",
                    "priority": "medium",
                    "description": "Improve user satisfaction based on interaction patterns and feedback",
                    "auto_executable": True,
                    "confidence": 0.7,
                }
            )

        # Recommend smarter help/context if many follow-ups, negative feedback, or context requests
        conversation_patterns = pattern_analysis.get("conversation_patterns", {})
        if (
            conversation_patterns.get("follow_ups", 0) > 5
            or conversation_patterns.get("negative_feedback", 0) > 2
            or conversation_patterns.get("context_requests", 0) > 2
        ):
            recommendations.append(
                {
                    "type": "smarter_help",
                    "priority": "medium",
                    "description": "Add smarter help, clarifications, or context-aware suggestions for users (e.g., auto-summarize, context reminders, or history-aware answers).",
                    "auto_executable": True,
                    "confidence": 0.8,
                }
            )

        # Performance recommendations
        if performance_analysis.get("overall_health") != "good":
            recommendations.append(
                {
                    "type": "performance_optimization",
                    "priority": "medium",
                    "description": "Optimize system performance",
                    "auto_executable": True,
                    "confidence": 0.7,
                }
            )

        return recommendations

    async def _execute_auto_improvements(
        self, recommendations: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Execute safe automatic improvements"""
        auto_threshold = self.config.get(
            "auto_remediation_threshold",
            self.default_config["auto_remediation_threshold"],
        )
        max_actions = self.config.get(
            "max_auto_actions_per_cycle",
            self.default_config["max_auto_actions_per_cycle"],
        )

        auto_improvements = []
        executed_count = 0

        for recommendation in recommendations:
            if executed_count >= max_actions:
                break

            if (
                recommendation.get("auto_executable", False)
                and recommendation.get("confidence", 0) >= auto_threshold
            ):
                try:
                    improvement_result = await self._execute_improvement_action(
                        recommendation
                    )
                    auto_improvements.append(improvement_result)
                    executed_count += 1

                except Exception as e:
                    auto_improvements.append(
                        {
                            "recommendation": recommendation,
                            "success": False,
                            "error": str(e),
                        }
                    )

        if auto_improvements:
            print(f"🤖 Executed {len(auto_improvements)} automatic improvements")

        return auto_improvements

    async def _execute_improvement_action(
        self, recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific improvement action"""
        action_type = recommendation.get("type")

        if action_type == "pattern_resolution":
            return await self._resolve_pattern_issues(recommendation)
        elif action_type == "user_experience_improvement":
            return await self._improve_user_experience(recommendation)
        elif action_type == "performance_optimization":
            return await self._optimize_performance(recommendation)
        else:
            return {
                "recommendation": recommendation,
                "success": False,
                "reason": "No auto-improvement handler available",
            }

    async def _resolve_pattern_issues(self, recommendation: Dict) -> Dict[str, Any]:
        """Resolve recurring pattern issues"""
        # Store pattern resolution intent in memory for manual review
        await self.memory_system.store_enhanced_memory(
            content={
                "improvement_action": "pattern_resolution",
                "recommendation": recommendation,
                "status": "flagged_for_review",
                "timestamp": datetime.now().isoformat(),
            },
            context={"type": "auto_improvement", "source": "self_evaluation_agent"},
            tags=["auto_improvement", "pattern_resolution", "flagged"],
            importance=0.7,
        )

        return {
            "recommendation": recommendation,
            "success": True,
            "action": "flagged_for_manual_review",
            "message": "Pattern issues flagged for developer attention",
        }

    async def _improve_user_experience(self, recommendation: Dict) -> Dict[str, Any]:
        """Implement user experience improvements"""
        # Store UX improvement suggestion
        await self.memory_system.store_enhanced_memory(
            content={
                "improvement_action": "user_experience",
                "recommendation": recommendation,
                "suggested_actions": [
                    "Review conversation patterns",
                    "Enhance response quality",
                    "Improve error handling",
                ],
                "timestamp": datetime.now().isoformat(),
            },
            context={"type": "auto_improvement", "source": "self_evaluation_agent"},
            tags=["auto_improvement", "user_experience", "enhancement"],
            importance=0.8,
        )

        return {
            "recommendation": recommendation,
            "success": True,
            "action": "ux_enhancement_planned",
            "message": "User experience improvements scheduled",
        }

    async def _optimize_performance(self, recommendation: Dict) -> Dict[str, Any]:
        """Implement performance optimizations"""
        # Store performance optimization plan
        await self.memory_system.store_enhanced_memory(
            content={
                "improvement_action": "performance_optimization",
                "recommendation": recommendation,
                "optimization_areas": [
                    "Memory usage optimization",
                    "Plugin loading efficiency",
                    "Response time improvement",
                ],
                "timestamp": datetime.now().isoformat(),
            },
            context={"type": "auto_improvement", "source": "self_evaluation_agent"},
            tags=["auto_improvement", "performance", "optimization"],
            importance=0.8,
        )

        return {
            "recommendation": recommendation,
            "success": True,
            "action": "performance_optimization_scheduled",
            "message": "Performance optimizations planned",
        }

    async def _store_evaluation_results(self, results: Dict[str, Any]):
        """Store evaluation results in memory"""
        try:
            await self.memory_system.store_enhanced_memory(
                content=results,
                context={
                    "type": "self_evaluation_cycle",
                    "source": "enhanced_self_evaluation_agent",
                },
                tags=["self_evaluation", "autonomous", "cycle_results"],
                importance=0.9,
            )
            print("📝 Stored evaluation results in memory")

        except Exception as e:
            print(f"⚠️ Failed to store evaluation results: {e}")

    async def get_evaluation_metrics(self, days_back: int = 7) -> Dict[str, Any]:
        """Get metrics on self-evaluation activities"""
        try:
            memories = await self.memory_system.get_memories_by_tags(
                ["self_evaluation", "autonomous"], limit=50
            )

            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_evaluations = []

            for memory in memories:
                created_at = memory.get("created_at", "")
                if created_at:
                    try:
                        memory_date = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                        if memory_date > cutoff_date:
                            recent_evaluations.append(memory)
                    except ValueError:
                        continue

            total_recommendations = sum(
                len(memory.get("content", {}).get("recommendations", []))
                for memory in recent_evaluations
            )

            total_auto_improvements = sum(
                len(memory.get("content", {}).get("auto_improvements", []))
                for memory in recent_evaluations
            )

            return {
                "period_days": days_back,
                "total_evaluation_cycles": len(recent_evaluations),
                "total_recommendations": total_recommendations,
                "total_auto_improvements": total_auto_improvements,
                "avg_recommendations_per_cycle": total_recommendations
                / max(len(recent_evaluations), 1),
                "improvement_rate": total_auto_improvements
                / max(total_recommendations, 1),
                "last_evaluation": recent_evaluations[0].get("created_at")
                if recent_evaluations
                else None,
            }

        except Exception as e:
            return {"error": str(e)}

    async def propose_changes(self) -> dict:
        """
        Analyze recent insights and propose actionable changes, storing them as 'proposed_change' memories.
        Returns a summary of proposed changes.
        """
        try:
            insights = await self._analyze_recent_insights()
            recommendations = insights.get("recommendations", [])
            proposed_changes = []
            for rec in recommendations:
                change = {
                    "type": "proposed_change",
                    "created_at": datetime.utcnow().isoformat(),
                    "content": rec,
                }
                # Store in memory system (async)
                await self.memory_system.store_enhanced_memory(content=change)
                proposed_changes.append(change)
            return {
                "proposed_changes": proposed_changes,
                "count": len(proposed_changes),
                "status": "success",
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}


# Main function for plugin interface
async def main(input_data: Any, **kwargs) -> Dict[str, Any]:
    """Main entry point for self-evaluation agent"""
    memory_system = kwargs.get("memory_system")

    if not memory_system:
        return {"error": "Memory system required for self-evaluation"}

    agent = EnhancedSelfEvaluationAgent(memory_system)

    # Handle different commands
    if isinstance(input_data, dict):
        command = input_data.get("command", "evaluate")
    else:
        command = str(input_data) if input_data else "evaluate"

    if command == "start_continuous":
        asyncio.create_task(agent.start_continuous_evaluation())
        return {"success": True, "message": "Continuous evaluation started"}
    elif command == "stop_continuous":
        await agent.stop_continuous_evaluation()
        return {"success": True, "message": "Continuous evaluation stopped"}
    elif command == "metrics":
        metrics = await agent.get_evaluation_metrics()
        return {"success": True, "metrics": metrics}
    else:
        # Default: run immediate evaluation
        results = await agent.run_immediate_evaluation()
        return {"success": True, "results": results}
