#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧬 AetherraCode Standard Library - Reflector Plugin
Built-in plugin for behavior analysis and self-reflection
"""

# Standard library imports
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class ReflectorPlugin:
    """Self-reflection and behavior analysis capabilities for AetherraCode"""

    def __init__(self):
        self.name = "reflector"
        self.description = "Behavior analysis and self-reflection tools"
        self.available_actions = [
            "analyze_behavior",
            "reflect_on_performance",
            "pattern_analysis",
            "usage_insights",
            "decision_tracking",
            "learning_assessment",
            "goal_effectiveness",
            "memory_patterns",
            "status",
        ]
        self.reflection_data = {}
        self.behavior_log = []

    def analyze_behavior(
        self, context: str, action_log: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Analyze recent behavior patterns and provide insights"""
        if action_log is None:
            action_log = self.behavior_log

        analysis = {
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "patterns": self._identify_patterns(action_log),
            "efficiency_metrics": self._calculate_efficiency(action_log),
            "recommendations": self._generate_recommendations(action_log),
            "learning_progress": self._assess_learning_progress(action_log),
        }

        # Store analysis for future reflection
        self.reflection_data[context] = analysis

        return analysis

    def reflect_on_performance(self, timeframe_hours: int = 24) -> Dict[str, Any]:
        """Reflect on performance over a specific timeframe"""
        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)

        recent_actions = [
            action
            for action in self.behavior_log
            if datetime.fromisoformat(action.get("timestamp", "1970-01-01")) > cutoff_time
        ]

        reflection = {
            "timeframe": f"Last {timeframe_hours} hours",
            "total_actions": len(recent_actions),
            "action_types": Counter([action.get("type", "unknown") for action in recent_actions]),
            "success_rate": self._calculate_success_rate(recent_actions),
            "goal_progress": self._evaluate_goal_progress(recent_actions),
            "inefficiencies": self._detect_inefficiencies(recent_actions),
            "growth_areas": self._identify_growth_areas(recent_actions),
        }

        return reflection

    def pattern_analysis(self, pattern_type: str = "all") -> Dict[str, Any]:
        """Analyze specific types of behavioral patterns"""
        patterns = {
            "temporal": self._analyze_temporal_patterns(),
            "contextual": self._analyze_contextual_patterns(),
            "decision": self._analyze_decision_patterns(),
            "error": self._analyze_error_patterns(),
            "learning": self._analyze_learning_patterns(),
        }

        if pattern_type != "all":
            return patterns.get(pattern_type, {})

        return patterns

    def usage_insights(self) -> Dict[str, Any]:
        """Generate insights about usage patterns and preferences"""
        insights = {
            "most_used_features": self._get_feature_usage(),
            "peak_activity_times": self._analyze_activity_times(),
            "preferred_workflows": self._identify_workflows(),
            "cognitive_load_patterns": self._analyze_cognitive_load(),
            "adaptation_speed": self._measure_adaptation_speed(),
        }

        return insights

    def decision_tracking(self, decision: Dict[str, Any]) -> str:
        """Track and analyze decision-making patterns"""
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": decision.get("context", "unknown"),
            "confidence": decision.get("confidence", 0.5),
            "outcome": decision.get("outcome", "pending"),
        }

        self.behavior_log.append(
            {
                "type": "decision",
                "timestamp": decision_entry["timestamp"],
                "data": decision_entry,
            }
        )

        # Analyze decision quality
        self._analyze_decision_quality(decision_entry)

        return f"Decision tracked: {decision.get('action', 'unknown')} (confidence: {decision.get('confidence', 0.5)})"

    def learning_assessment(self, topic: str, current_performance: float) -> Dict[str, Any]:
        """Assess learning progress on a specific topic"""
        assessment = {
            "topic": topic,
            "current_performance": current_performance,
            "improvement_rate": self._calculate_improvement_rate(topic, current_performance),
            "learning_curve": self._analyze_learning_curve(topic),
            "mastery_level": self._assess_mastery_level(topic, current_performance),
            "next_steps": self._suggest_learning_steps(topic, current_performance),
        }

        return assessment

    def goal_effectiveness(self, goal_id: str) -> Dict[str, Any]:
        """Analyze the effectiveness of a specific goal"""
        goal_actions = [
            action
            for action in self.behavior_log
            if action.get("data", {}).get("goal_id") == goal_id
        ]

        effectiveness = {
            "goal_id": goal_id,
            "total_actions": len(goal_actions),
            "completion_rate": self._calculate_goal_completion_rate(goal_actions),
            "time_efficiency": self._analyze_goal_time_efficiency(goal_actions),
            "resource_usage": self._analyze_goal_resource_usage(goal_actions),
            "side_effects": self._identify_goal_side_effects(goal_actions),
            "recommendations": self._generate_goal_recommendations(goal_actions),
        }

        return effectiveness

    def memory_patterns(self) -> Dict[str, Any]:
        """Analyze memory usage and retention patterns"""
        memory_data = [
            action
            for action in self.behavior_log
            if action.get("type") in ["remember", "recall", "forget"]
        ]

        patterns = {
            "retention_rates": self._analyze_retention_rates(memory_data),
            "recall_frequency": self._analyze_recall_frequency(memory_data),
            "memory_categories": self._categorize_memories(memory_data),
            "forgetting_patterns": self._analyze_forgetting_patterns(memory_data),
            "memory_efficiency": self._calculate_memory_efficiency(memory_data),
        }

        return patterns

    def log_action(self, action_type: str, context: Dict[str, Any]) -> None:
        """Log an action for future reflection"""
        log_entry = {
            "type": action_type,
            "timestamp": datetime.now().isoformat(),
            "data": context,
        }

        self.behavior_log.append(log_entry)

        # Keep log size manageable
        if len(self.behavior_log) > 10000:
            self.behavior_log = self.behavior_log[-5000:]  # Keep last 5000 entries

    def status(self) -> Dict[str, Any]:
        """Get current reflector status and statistics"""
        return {
            "name": self.name,
            "description": self.description,
            "available_actions": self.available_actions,
            "logged_actions": len(self.behavior_log),
            "reflection_contexts": len(self.reflection_data),
            "recent_activity": len(
                [
                    action
                    for action in self.behavior_log
                    if datetime.fromisoformat(action.get("timestamp", "1970-01-01"))
                    > datetime.now() - timedelta(hours=1)
                ]
            ),
        }

    # Private helper methods
    def _identify_patterns(self, action_log: List[Dict]) -> Dict[str, Any]:
        """Identify behavioral patterns in action log"""
        if not action_log:
            return {}

        action_types = [action.get("type", "unknown") for action in action_log]
        type_frequency = Counter(action_types)

        return {
            "most_common_actions": type_frequency.most_common(5),
            "action_diversity": len(set(action_types)),
            "repetitive_behaviors": [
                action_type
                for action_type, count in type_frequency.items()
                if count > len(action_log) * 0.3
            ],
        }

    def _calculate_efficiency(self, action_log: List[Dict]) -> Dict[str, Any]:
        """Calculate efficiency metrics from action log"""
        if not action_log:
            return {"efficiency_score": 0.0}

        # Mock efficiency calculation based on action patterns
        successful_actions = len(
            [action for action in action_log if action.get("data", {}).get("success", True)]
        )

        efficiency_score = successful_actions / len(action_log) if action_log else 0.0

        return {
            "efficiency_score": efficiency_score,
            "successful_actions": successful_actions,
            "total_actions": len(action_log),
            "waste_indicators": self._identify_waste_indicators(action_log),
        }

    def _generate_recommendations(self, action_log: List[Dict]) -> List[str]:
        """Generate behavioral recommendations based on analysis"""
        recommendations = []

        if not action_log:
            return ["Start logging actions for better self-reflection"]

        # Analyze patterns and suggest improvements
        type_frequency = Counter([action.get("type", "unknown") for action in action_log])

        if type_frequency.get("error", 0) > len(action_log) * 0.2:
            recommendations.append(
                "High error rate detected - consider implementing error prevention strategies"
            )

        if type_frequency.get("goal", 0) < len(action_log) * 0.1:
            recommendations.append(
                "Low goal-setting activity - consider setting more specific objectives"
            )

        if len(set(type_frequency.keys())) < 3:
            recommendations.append(
                "Limited behavioral diversity - explore new approaches and tools"
            )

        return recommendations

    def _assess_learning_progress(self, action_log: List[Dict]) -> Dict[str, Any]:
        """Assess learning progress from action patterns"""
        learning_actions = [
            action for action in action_log if action.get("type") in ["learn", "adapt", "analyze"]
        ]

        return {
            "learning_frequency": len(learning_actions) / len(action_log) if action_log else 0,
            "learning_domains": list(
                {action.get("data", {}).get("domain", "general") for action in learning_actions}
            ),
            "adaptation_rate": self._calculate_adaptation_rate(action_log),
        }

    def _calculate_adaptation_rate(self, action_log: List[Dict]) -> float:
        """Calculate how quickly the system adapts to new patterns"""
        # Mock calculation - in real implementation would analyze actual adaptation
        adapt_actions = [action for action in action_log if action.get("type") == "adapt"]
        return len(adapt_actions) / len(action_log) if action_log else 0.0

    def _calculate_success_rate(self, action_log: List[Dict]) -> float:
        """Calculate overall success rate of actions"""
        if not action_log:
            return 0.0

        successful = len(
            [action for action in action_log if action.get("data", {}).get("success", True)]
        )

        return successful / len(action_log)

    def _evaluate_goal_progress(self, action_log: List[Dict]) -> Dict[str, Any]:
        """Evaluate progress toward goals"""
        goal_actions = [action for action in action_log if action.get("type") == "goal"]

        return {
            "goals_set": len(goal_actions),
            "goal_completion_estimate": 0.7,  # Mock value
            "active_goals": len({action.get("data", {}).get("goal_id") for action in goal_actions}),
        }

    def _detect_inefficiencies(self, action_log: List[Dict]) -> List[str]:
        """Detect inefficient behavioral patterns"""
        inefficiencies = []

        # Look for repeated failed actions
        failed_actions = [
            action for action in action_log if not action.get("data", {}).get("success", True)
        ]

        if len(failed_actions) > len(action_log) * 0.3:
            inefficiencies.append("High failure rate - consider reviewing approach")

        return inefficiencies

    def _identify_growth_areas(self, action_log: List[Dict]) -> List[str]:
        """Identify areas for potential growth and improvement"""
        growth_areas = []

        # Analyze action diversity
        action_types = {action.get("type", "unknown") for action in action_log}

        if "optimize" not in action_types:
            growth_areas.append("Consider adding optimization activities")

        if "reflect" not in action_types:
            growth_areas.append("Increase self-reflection frequency")

        return growth_areas

    # Additional helper methods for comprehensive analysis
    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in behavior"""
        if not self.behavior_log:
            return {
                "total_actions": 0,
                "hourly_distribution": {},
                "peak_hour": None,
                "weekday_distribution": {},
            }

        hourly = Counter()
        weekday = Counter()
        for action in self.behavior_log:
            try:
                ts = datetime.fromisoformat(action.get("timestamp", "1970-01-01"))
                hourly[ts.hour] += 1
                weekday[ts.strftime("%A")] += 1
            except Exception:
                continue

        peak_hour = hourly.most_common(1)[0][0] if hourly else None
        return {
            "total_actions": len(self.behavior_log),
            "hourly_distribution": dict(sorted(hourly.items())),
            "peak_hour": peak_hour,
            "weekday_distribution": dict(weekday),
        }

    def _analyze_contextual_patterns(self) -> Dict[str, Any]:
        """Analyze contextual patterns in behavior"""
        if not self.behavior_log:
            return {"contexts": {}, "top_context": None}

        contexts = Counter()
        for action in self.behavior_log:
            ctx = action.get("data", {}).get("context") or "unknown"
            contexts[str(ctx)] += 1

        top_context = contexts.most_common(1)[0][0] if contexts else None
        return {"contexts": dict(contexts), "top_context": top_context}

    def _analyze_decision_patterns(self) -> Dict[str, Any]:
        """Analyze decision-making patterns"""
        decisions = [a for a in self.behavior_log if a.get("type") == "decision"]
        if not decisions:
            return {
                "decision_count": 0,
                "avg_confidence": 0.0,
                "outcomes": {},
            }

        confidences = []
        outcomes = Counter()
        for d in decisions:
            payload = d.get("data", {}).get("decision", {})
            conf = payload.get("confidence", d.get("data", {}).get("confidence", 0.5))
            try:
                confidences.append(float(conf))
            except Exception:
                pass
            outcomes[str(payload.get("outcome", d.get("data", {}).get("outcome", "pending")))] += 1

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return {
            "decision_count": len(decisions),
            "avg_confidence": round(avg_conf, 3),
            "outcomes": dict(outcomes),
        }

    def _analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze error patterns"""
        errors = [
            a
            for a in self.behavior_log
            if a.get("type") == "error" or not a.get("data", {}).get("success", True)
        ]
        total = len(self.behavior_log)
        rate = len(errors) / total if total else 0.0
        by_type = Counter(a.get("type", "unknown") for a in errors)
        return {
            "error_count": len(errors),
            "error_rate": round(rate, 3),
            "error_types": dict(by_type),
        }

    def _analyze_learning_patterns(self) -> Dict[str, Any]:
        """Analyze learning patterns"""
        learning = [
            a
            for a in self.behavior_log
            if a.get("type") in {"learn", "adapt", "analyze"}
        ]
        domains = Counter(a.get("data", {}).get("domain", "general") for a in learning)
        return {
            "learning_events": len(learning),
            "domains": dict(domains),
            "adaptation_rate": self._calculate_adaptation_rate(self.behavior_log),
        }

    def _get_feature_usage(self) -> Dict[str, int]:
        """Get feature usage statistics"""
        return {"feature_usage": 0}  # Return int instead of string

    def _analyze_activity_times(self) -> Dict[str, Any]:
        """Analyze peak activity times"""
        temporal = self._analyze_temporal_patterns()
        if temporal.get("total_actions", 0) == 0:
            return {
                "peak_hour": None,
                "hourly_distribution": {},
                "business_hours_ratio": 0.0,
            }

        hourly = temporal.get("hourly_distribution", {})
        total = sum(hourly.values()) if hourly else 0
        business = sum(count for hour, count in hourly.items() if 9 <= int(hour) <= 17)
        ratio = (business / total) if total else 0.0
        return {
            "peak_hour": temporal.get("peak_hour"),
            "hourly_distribution": hourly,
            "business_hours_ratio": round(ratio, 3),
        }

    def _identify_workflows(self) -> List[str]:
        """Identify preferred workflows"""
        if not self.behavior_log:
            return []

        seq = [a.get("type", "unknown") for a in self.behavior_log]
        pair_counts = Counter()
        for i in range(len(seq) - 1):
            pair_counts[f"{seq[i]}->{seq[i + 1]}"] += 1
        return [pair for pair, _ in pair_counts.most_common(5)]

    def _analyze_cognitive_load(self) -> Dict[str, Any]:
        """Analyze cognitive load patterns"""
        if not self.behavior_log:
            return {
                "cognitive_load": "low",
                "avg_actions_per_hour": 0.0,
                "high_complexity_ratio": 0.0,
            }

        now = datetime.now()
        cutoff = now - timedelta(hours=24)
        recent = []
        for action in self.behavior_log:
            try:
                ts = datetime.fromisoformat(action.get("timestamp", "1970-01-01"))
                if ts > cutoff:
                    recent.append(action)
            except Exception:
                continue

        avg_actions_per_hour = len(recent) / 24.0
        high_complexity = 0
        for action in recent:
            c = str(action.get("data", {}).get("complexity", "")).lower()
            if c in {"high", "critical", "complex"}:
                high_complexity += 1
        ratio = (high_complexity / len(recent)) if recent else 0.0

        label = "low"
        if avg_actions_per_hour > 8 or ratio > 0.4:
            label = "high"
        elif avg_actions_per_hour > 3 or ratio > 0.2:
            label = "medium"

        return {
            "cognitive_load": label,
            "avg_actions_per_hour": round(avg_actions_per_hour, 3),
            "high_complexity_ratio": round(ratio, 3),
        }

    def _measure_adaptation_speed(self) -> float:
        """Measure adaptation speed"""
        return 0.5  # Baseline estimate

    def _analyze_decision_quality(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze quality of a decision"""
        confidence = float(decision.get("confidence", 0.5))
        outcome = str(decision.get("outcome", "pending")).lower()
        outcome_bonus = 0.0
        if outcome in {"success", "completed", "ok"}:
            outcome_bonus = 0.2
        elif outcome in {"failed", "error"}:
            outcome_bonus = -0.2

        score = min(1.0, max(0.0, confidence + outcome_bonus))
        return {
            "quality_score": round(score, 3),
            "confidence": confidence,
            "outcome": outcome,
        }

    def _calculate_improvement_rate(self, topic: str, performance: float) -> float:
        """Calculate improvement rate for a topic"""
        relevant = [
            a
            for a in self.behavior_log
            if a.get("data", {}).get("topic") == topic
            and isinstance(a.get("data", {}).get("performance"), (int, float))
        ]
        historical = [float(a.get("data", {}).get("performance")) for a in relevant]
        if not historical:
            return 0.0
        avg_prev = sum(historical) / len(historical)
        return round(float(performance) - avg_prev, 3)

    def _analyze_learning_curve(self, topic: str) -> Dict[str, Any]:
        """Analyze learning curve for a topic"""
        points = []
        for a in self.behavior_log:
            data = a.get("data", {})
            if data.get("topic") != topic:
                continue
            perf = data.get("performance")
            if isinstance(perf, (int, float)):
                points.append(float(perf))

        if len(points) < 2:
            trend = "insufficient_data"
            slope = 0.0
        else:
            slope = (points[-1] - points[0]) / (len(points) - 1)
            trend = "improving" if slope > 0.01 else "declining" if slope < -0.01 else "stable"

        return {
            "curve": points,
            "trend": trend,
            "slope": round(slope, 3),
        }

    def _assess_mastery_level(self, topic: str, performance: float) -> str:
        """Assess mastery level"""
        if performance > 0.8:
            return "advanced"
        elif performance > 0.5:
            return "intermediate"
        else:
            return "beginner"

    def _suggest_learning_steps(self, topic: str, performance: float) -> List[str]:
        """Suggest next learning steps"""
        return ["Continue practicing", "Seek feedback", "Apply knowledge"]

    def _calculate_goal_completion_rate(self, goal_actions: List[Dict]) -> float:
        """Calculate goal completion rate"""
        return 0.7  # Baseline estimate

    def _analyze_goal_time_efficiency(self, goal_actions: List[Dict]) -> Dict[str, Any]:
        """Analyze time efficiency for goals"""
        if not goal_actions:
            return {"efficiency": 0.0, "avg_duration_sec": None}

        durations = [
            float(a.get("data", {}).get("duration_sec", 0.0))
            for a in goal_actions
            if isinstance(a.get("data", {}).get("duration_sec"), (int, float))
        ]
        if not durations:
            return {"efficiency": 0.0, "avg_duration_sec": None}

        avg_dur = sum(durations) / len(durations)
        efficiency = max(0.0, min(1.0, 1.0 / (1.0 + avg_dur / 300.0)))
        return {"efficiency": round(efficiency, 3), "avg_duration_sec": round(avg_dur, 3)}

    def _analyze_goal_resource_usage(self, goal_actions: List[Dict]) -> Dict[str, Any]:
        """Analyze resource usage for goals"""
        cpu_vals = []
        mem_vals = []
        for a in goal_actions:
            usage = a.get("data", {}).get("resource_usage", {})
            cpu = usage.get("cpu")
            mem = usage.get("memory")
            if isinstance(cpu, (int, float)):
                cpu_vals.append(float(cpu))
            if isinstance(mem, (int, float)):
                mem_vals.append(float(mem))

        return {
            "resources": {
                "avg_cpu": round(sum(cpu_vals) / len(cpu_vals), 3) if cpu_vals else None,
                "avg_memory": round(sum(mem_vals) / len(mem_vals), 3) if mem_vals else None,
                "samples": max(len(cpu_vals), len(mem_vals)),
            }
        }

    def _identify_goal_side_effects(self, goal_actions: List[Dict]) -> List[str]:
        """Identify side effects of goal pursuit"""
        effects = Counter()
        for a in goal_actions:
            for effect in a.get("data", {}).get("side_effects", []) or []:
                effects[str(effect)] += 1
        return [k for k, _ in effects.most_common(5)]

    def _generate_goal_recommendations(self, goal_actions: List[Dict]) -> List[str]:
        """Generate recommendations for goal improvement"""
        if not goal_actions:
            return ["No goal activity found; begin tracking goal-linked actions"]

        recommendations = []
        completion = self._calculate_goal_completion_rate(goal_actions)
        if completion < 0.5:
            recommendations.append("Increase milestone granularity and checkpoint frequency")

        eff = self._analyze_goal_time_efficiency(goal_actions).get("efficiency", 0.0)
        if isinstance(eff, (int, float)) and eff < 0.4:
            recommendations.append("Reduce task scope per session to improve time efficiency")

        resources = self._analyze_goal_resource_usage(goal_actions).get("resources", {})
        avg_cpu = resources.get("avg_cpu")
        if isinstance(avg_cpu, (int, float)) and avg_cpu > 0.85:
            recommendations.append("High CPU usage detected; consider batching heavy operations")

        return recommendations or ["Goal execution is stable; continue current strategy"]

    def _analyze_retention_rates(self, memory_data: List[Dict]) -> Dict[str, float]:
        """Analyze memory retention rates"""
        return {"retention": 0.8}

    def _analyze_recall_frequency(self, memory_data: List[Dict]) -> Dict[str, int]:
        """Analyze recall frequency"""
        return {"frequency": 5}

    def _categorize_memories(self, memory_data: List[Dict]) -> Dict[str, int]:
        """Categorize memories by type"""
        return {"general": 10}  # Return flat dict instead of nested

    def _analyze_forgetting_patterns(self, memory_data: List[Dict]) -> Dict[str, Any]:
        """Analyze forgetting patterns"""
        forget_events = [m for m in memory_data if m.get("type") == "forget"]
        recall_events = [m for m in memory_data if m.get("type") == "recall"]
        ratio = (len(forget_events) / len(recall_events)) if recall_events else 0.0
        return {
            "patterns": {
                "forget_count": len(forget_events),
                "recall_count": len(recall_events),
                "forget_to_recall_ratio": round(ratio, 3),
            }
        }

    def _calculate_memory_efficiency(self, memory_data: List[Dict]) -> float:
        """Calculate memory efficiency"""
        return 0.75

    def _identify_waste_indicators(self, action_log: List[Dict]) -> List[str]:
        """Identify indicators of waste or inefficiency"""
        waste_indicators = []

        # Look for repeated similar actions that might indicate inefficiency
        action_types = [action.get("type", "unknown") for action in action_log]
        type_counts = Counter(action_types)

        for action_type, count in type_counts.items():
            if count > len(action_log) * 0.5:  # If one action type is >50% of all actions
                waste_indicators.append(f"Excessive {action_type} actions detected")

        return waste_indicators

    def execute_action(self, action: str, memory_system=None, **kwargs) -> str:
        """Execute a reflector action with standardized interface"""
        try:
            if action == "analyze" or action == "analyze_behavior":
                context = kwargs.get("context", "default")
                action_log = kwargs.get("action_log", [])
                result = self.analyze_behavior(context, action_log)
                patterns_count = len(result.get("patterns", {}))
                return (
                    f"Behavior analysis complete for context '{context}'. Found "
                    f"{patterns_count} patterns."
                )

            elif action == "reflect" or action == "reflect_on_performance":
                timeframe = kwargs.get("timeframe_hours", 24)
                result = self.reflect_on_performance(timeframe)
                overall_eff = result.get("overall_efficiency", "unknown")
                return (
                    f"Performance reflection complete for {timeframe}h timeframe. "
                    f"Overall efficiency: {overall_eff}"
                )

            elif action == "patterns" or action == "pattern_analysis":
                action_log = kwargs.get("action_log", [])
                patterns = self.pattern_analysis(action_log)
                return f"Pattern analysis found {len(patterns.get('patterns', []))} behavioral patterns."

            elif action == "insights" or action == "usage_insights":
                timeframe = kwargs.get("timeframe_hours", 168)
                self.usage_insights()  # Call without parameters as method expects none
                return f"Usage insights generated for {timeframe}h period."

            elif action == "status":
                return (
                    f"Reflector plugin active. {len(self.behavior_log)} logged behaviors, "
                    f"{len(self.reflection_data)} reflection contexts."
                )

            else:
                available = ", ".join(self.available_actions)
                return f"Unknown action '{action}'. Available: {available}"

        except Exception as e:
            return f"Error in reflector.{action}: {str(e)}"


# Plugin registration
PLUGIN_CLASS = ReflectorPlugin
