#!/usr/bin/env python3
"""
💡 SUGGESTION GENERATOR - PHASE 2
=================================

Generates intelligent, contextual suggestions based on user
activity patterns, context analysis, and learned preferences.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class SuggestionCategory(Enum):
    """Categories of suggestions"""
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"
    WORKFLOW = "workflow"
    WELLBEING = "wellbeing"
    OPTIMIZATION = "optimization"
    COLLABORATION = "collaboration"


@dataclass
class SuggestionTemplate:
    """Template for generating suggestions"""
    category: SuggestionCategory
    title_template: str
    description_template: str
    actions: List[str]
    triggers: List[str]  # Context conditions that trigger this suggestion
    confidence_base: float
    

class SuggestionGenerator:
    """Generates contextual suggestions for users"""
    
    def __init__(self):
        self.suggestion_templates = self._initialize_templates()
        self.user_preferences: Dict[str, float] = {}
        self.suggestion_history: List[Dict[str, Any]] = []
        
    def _initialize_templates(self) -> List[SuggestionTemplate]:
        """Initialize suggestion templates"""
        
        return [
            # Productivity suggestions
            SuggestionTemplate(
                category=SuggestionCategory.PRODUCTIVITY,
                title_template="Use time blocking for {activity}",
                description_template="You've been working on {activity} for {duration}. Consider time blocking to maintain focus.",
                actions=["Set specific time blocks", "Use a timer", "Minimize distractions"],
                triggers=["long_session", "focus_needed"],
                confidence_base=0.7
            ),
            
            SuggestionTemplate(
                category=SuggestionCategory.PRODUCTIVITY,
                title_template="Take a strategic break",
                description_template="You've been highly focused for {duration}. A short break could boost your productivity.",
                actions=["Take a 5-10 minute walk", "Do some stretching", "Practice deep breathing"],
                triggers=["high_focus_extended", "productivity_plateau"],
                confidence_base=0.8
            ),
            
            SuggestionTemplate(
                category=SuggestionCategory.WORKFLOW,
                title_template="Continue your {activity} workflow",
                description_template="Based on your pattern, you typically {next_step} after {current_activity}.",
                actions=["Follow established workflow", "Review previous results", "Plan next steps"],
                triggers=["pattern_detected", "workflow_continuation"],
                confidence_base=0.75
            ),
            
            SuggestionTemplate(
                category=SuggestionCategory.OPTIMIZATION,
                title_template="Batch similar tasks",
                description_template="You're doing multiple short {activity} tasks. Batching them could be more efficient.",
                actions=["Group similar tasks", "Set dedicated time blocks", "Reduce context switching"],
                triggers=["repeated_short_tasks", "context_switching"],
                confidence_base=0.8
            ),
            
            SuggestionTemplate(
                category=SuggestionCategory.LEARNING,
                title_template="Explore related topics",
                description_template="While working on {activity}, you might benefit from learning about {related_topic}.",
                actions=["Research best practices", "Find tutorials or guides", "Connect with experts"],
                triggers=["knowledge_gap", "skill_development"],
                confidence_base=0.6
            ),
            
            SuggestionTemplate(
                category=SuggestionCategory.WELLBEING,
                title_template="Maintain work-life balance",
                description_template="You've been working intensively. Consider your wellbeing and work-life balance.",
                actions=["Schedule personal time", "Plan relaxing activities", "Connect with friends/family"],
                triggers=["overwork_detected", "extended_hours"],
                confidence_base=0.7
            ),
            
            SuggestionTemplate(
                category=SuggestionCategory.COLLABORATION,
                title_template="Share your progress",
                description_template="You've made good progress on {activity}. Consider sharing updates with your team.",
                actions=["Send progress update", "Schedule review meeting", "Document achievements"],
                triggers=["milestone_reached", "collaborative_project"],
                confidence_base=0.6
            )
        ]
        
    def generate_suggestions(
        self,
        context: Dict[str, Any],
        activity_history: List[Dict[str, Any]],
        max_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate contextual suggestions based on current situation"""
        
        suggestions = []
        
        # Analyze current context - variables will be used by sub-functions
        # current_activity = context.get("primary_activity", "unknown")
        # focus_level = context.get("focus_level", 0.5)
        # productivity_score = context.get("productivity_score", 0.5)
        # time_in_state = context.get("time_in_state", 0)
        
        # Generate suggestions for each applicable template
        for template in self.suggestion_templates:
            suggestion = self._generate_from_template(
                template, context, activity_history
            )
            if suggestion:
                suggestions.append(suggestion)
                
        # Add pattern-based suggestions
        pattern_suggestions = self._generate_pattern_suggestions(
            activity_history, context
        )
        suggestions.extend(pattern_suggestions)
        
        # Add time-based suggestions
        time_suggestions = self._generate_time_based_suggestions(
            context, activity_history
        )
        suggestions.extend(time_suggestions)
        
        # Score and rank suggestions
        scored_suggestions = self._score_suggestions(suggestions, context)
        
        # Return top suggestions
        return scored_suggestions[:max_suggestions]
        
    def _generate_from_template(
        self,
        template: SuggestionTemplate,
        context: Dict[str, Any],
        activity_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Generate a suggestion from a template"""
        
        # Check if template triggers match current context
        if not self._check_triggers(template.triggers, context, activity_history):
            return None
            
        # Extract context variables
        activity = context.get("primary_activity", "current task")
        duration = self._format_duration(context.get("time_in_state", 0))
        
        # Fill template variables
        title = template.title_template.format(
            activity=activity,
            duration=duration
        )
        
        description = template.description_template.format(
            activity=activity,
            duration=duration,
            current_activity=activity
        )
        
        # Calculate confidence
        base_confidence = template.confidence_base
        context_bonus = self._calculate_context_bonus(template, context)
        user_preference_bonus = self._get_user_preference_bonus(template.category)
        
        confidence = min(1.0, base_confidence + context_bonus + user_preference_bonus)
        
        return {
            "id": f"template_{template.category.value}_{int(datetime.now().timestamp())}",
            "category": template.category.value,
            "title": title,
            "description": description,
            "actions": template.actions.copy(),
            "confidence": confidence,
            "source": "template",
            "created_at": datetime.now().isoformat()
        }
        
    def _check_triggers(
        self,
        triggers: List[str],
        context: Dict[str, Any],
        activity_history: List[Dict[str, Any]]
    ) -> bool:
        """Check if template triggers match current context"""
        
        focus_level = context.get("focus_level", 0.5)
        productivity_score = context.get("productivity_score", 0.5)
        time_in_state = context.get("time_in_state", 0)
        
        for trigger in triggers:
            if trigger == "long_session" and time_in_state > 3600:  # 1+ hours
                return True
            elif trigger == "focus_needed" and focus_level < 0.4:
                return True
            elif trigger == "high_focus_extended" and focus_level > 0.8 and time_in_state > 1800:  # 30+ min
                return True
            elif trigger == "productivity_plateau" and productivity_score < 0.5:
                return True
            elif trigger == "repeated_short_tasks":
                if len(activity_history) >= 3:
                    recent_durations = [a.get("duration", 0) for a in activity_history[-3:]]
                    if all(d < 600 for d in recent_durations):  # All under 10 minutes
                        return True
            elif trigger == "context_switching":
                if len(activity_history) >= 3:
                    recent_types = [a.get("activity_type", "") for a in activity_history[-3:]]
                    if len(set(recent_types)) == len(recent_types):  # All different
                        return True
            elif trigger == "overwork_detected":
                total_work_time = sum(a.get("duration", 0) for a in activity_history[-10:])
                if total_work_time > 28800:  # 8+ hours
                    return True
                    
        return False
        
    def _generate_pattern_suggestions(
        self,
        activity_history: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on detected patterns"""
        
        suggestions = []
        
        if len(activity_history) < 5:
            return suggestions
            
        # Detect common sequences
        sequences = self._find_activity_sequences(activity_history)
        
        for sequence, frequency in sequences.items():
            if frequency >= 2:  # Pattern occurred at least twice
                suggestion = {
                    "id": f"pattern_{hash(sequence)}_{int(datetime.now().timestamp())}",
                    "category": "workflow",
                    "title": "Continue your usual workflow",
                    "description": f"You often follow {sequence[0]} with {sequence[1]}. Continue this pattern?",
                    "actions": [f"Proceed with {sequence[1]}", "Review workflow efficiency"],
                    "confidence": 0.6 + (frequency * 0.1),  # Higher confidence for frequent patterns
                    "source": "pattern",
                    "created_at": datetime.now().isoformat()
                }
                suggestions.append(suggestion)
                
        return suggestions
        
    def _generate_time_based_suggestions(
        self,
        context: Dict[str, Any],
        activity_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on time of day and duration"""
        
        suggestions = []
        current_hour = datetime.now().hour
        time_in_state = context.get("time_in_state", 0)
        
        # Morning suggestions
        if 6 <= current_hour <= 10:
            suggestions.append({
                "id": f"time_morning_{int(datetime.now().timestamp())}",
                "category": "productivity",
                "title": "Start your day strong",
                "description": "Morning is great for high-focus work. Tackle your most important tasks now.",
                "actions": ["Prioritize important tasks", "Minimize distractions", "Plan your day"],
                "confidence": 0.7,
                "source": "time_based",
                "created_at": datetime.now().isoformat()
            })
            
        # Afternoon suggestions
        elif 14 <= current_hour <= 16:
            suggestions.append({
                "id": f"time_afternoon_{int(datetime.now().timestamp())}",
                "category": "optimization",
                "title": "Afternoon optimization",
                "description": "Afternoon energy dip is normal. Consider lighter tasks or collaboration.",
                "actions": ["Handle administrative tasks", "Collaborate with others", "Review and organize"],
                "confidence": 0.6,
                "source": "time_based",
                "created_at": datetime.now().isoformat()
            })
            
        # Long duration suggestions
        if time_in_state > 7200:  # 2+ hours
            suggestions.append({
                "id": f"duration_long_{int(datetime.now().timestamp())}",
                "category": "wellbeing",
                "title": "Take a meaningful break",
                "description": "You've been focused for over 2 hours. Time for a substantial break.",
                "actions": ["Go for a walk", "Have a proper meal", "Change your environment"],
                "confidence": 0.8,
                "source": "time_based",
                "created_at": datetime.now().isoformat()
            })
            
        return suggestions
        
    def _find_activity_sequences(
        self, 
        activity_history: List[Dict[str, Any]]
    ) -> Dict[tuple, int]:
        """Find common activity sequences in history"""
        
        sequences: Dict[tuple, int] = {}
        
        for i in range(len(activity_history) - 1):
            current_activity = activity_history[i].get("activity_type", "")
            next_activity = activity_history[i + 1].get("activity_type", "")
            
            if current_activity and next_activity:
                sequence = (current_activity, next_activity)
                sequences[sequence] = sequences.get(sequence, 0) + 1
                
        return sequences
        
    def _score_suggestions(
        self,
        suggestions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score and rank suggestions by relevance"""
        
        for suggestion in suggestions:
            base_score = suggestion.get("confidence", 0.5)
            
            # Bonus for high-confidence suggestions
            if base_score > 0.8:
                base_score += 0.1
                
            # Bonus for user preference alignment
            category = suggestion.get("category", "")
            preference_bonus = self.user_preferences.get(category, 0.0)
            
            # Penalty for recently shown similar suggestions
            recency_penalty = self._calculate_recency_penalty(suggestion)
            
            final_score = base_score + preference_bonus - recency_penalty
            suggestion["final_score"] = max(0.0, min(1.0, final_score))
            
        # Sort by final score
        return sorted(suggestions, key=lambda x: x.get("final_score", 0), reverse=True)
        
    def _calculate_context_bonus(
        self,
        template: SuggestionTemplate,
        context: Dict[str, Any]
    ) -> float:
        """Calculate bonus based on how well template matches context"""
        
        bonus = 0.0
        
        focus_level = context.get("focus_level", 0.5)
        productivity_score = context.get("productivity_score", 0.5)
        
        # Productivity templates get bonus when productivity is low
        if template.category == SuggestionCategory.PRODUCTIVITY and productivity_score < 0.5:
            bonus += 0.1
            
        # Wellbeing templates get bonus when focus is high for too long
        if template.category == SuggestionCategory.WELLBEING and focus_level > 0.8:
            bonus += 0.1
            
        # Optimization templates get bonus when efficiency could be improved
        if template.category == SuggestionCategory.OPTIMIZATION and productivity_score < 0.6:
            bonus += 0.1
            
        return bonus
        
    def _get_user_preference_bonus(self, category: SuggestionCategory) -> float:
        """Get bonus based on user preferences for this category"""
        
        return self.user_preferences.get(category.value, 0.0)
        
    def _calculate_recency_penalty(self, suggestion: Dict[str, Any]) -> float:
        """Calculate penalty for recently shown similar suggestions"""
        
        penalty = 0.0
        suggestion_category = suggestion.get("category", "")
        
        # Check recent history for similar suggestions
        recent_suggestions = [
            s for s in self.suggestion_history[-10:]  # Last 10 suggestions
            if s.get("category") == suggestion_category
        ]
        
        if recent_suggestions:
            # Penalty based on how recently similar suggestions were shown
            penalty = len(recent_suggestions) * 0.1
            
        return min(0.5, penalty)  # Max penalty of 0.5
        
    def _format_duration(self, seconds: float) -> str:
        """Format duration in a human-readable way"""
        
        if seconds < 60:
            return "less than a minute"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            if minutes > 0:
                return f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''}"
                
    def update_user_preferences(
        self,
        category: str,
        feedback: float
    ) -> None:
        """Update user preferences based on feedback"""
        
        current_pref = self.user_preferences.get(category, 0.0)
        
        # Smooth update with learning rate
        learning_rate = 0.1
        new_pref = current_pref + (learning_rate * feedback)
        
        # Keep preferences in reasonable range
        self.user_preferences[category] = max(-0.3, min(0.3, new_pref))
        
    def record_suggestion_shown(self, suggestion: Dict[str, Any]) -> None:
        """Record that a suggestion was shown to user"""
        
        self.suggestion_history.append({
            "id": suggestion.get("id"),
            "category": suggestion.get("category"),
            "shown_at": datetime.now().isoformat(),
            "confidence": suggestion.get("confidence", 0.0)
        })
        
        # Keep history manageable
        if len(self.suggestion_history) > 100:
            self.suggestion_history = self.suggestion_history[-100:]
