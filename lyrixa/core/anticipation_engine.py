#!/usr/bin/env python3
"""
🔮 LYRIXA ANTICIPATION ENGINE - PHASE 2
=====================================

Core anticipation engine that analyzes user context, predicts needs,
and generates proactive suggestions for enhanced productivity.
"""

import asyncio
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import Phase 1 memory system
try:
    from ..core.advanced_vector_memory import AdvancedMemorySystem
except ImportError:
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem


class SuggestionType(Enum):
    """Types of proactive suggestions"""
    WORKFLOW_CONTINUATION = "workflow_continuation"
    TASK_OPTIMIZATION = "task_optimization"
    KNOWLEDGE_DISCOVERY = "knowledge_discovery"
    PRODUCTIVITY_TIP = "productivity_tip"
    RESOURCE_SUGGESTION = "resource_suggestion"
    PATTERN_INSIGHT = "pattern_insight"


class ContextState(Enum):
    """Current user context states"""
    ACTIVE_WORKING = "active_working"
    TRANSITIONING = "transitioning"
    IDLE_BRIEF = "idle_brief"
    IDLE_EXTENDED = "idle_extended"
    FOCUSED_DEEP = "focused_deep"
    MULTITASKING = "multitasking"


@dataclass
class UserActivity:
    """Represents a single user activity"""
    activity_id: str
    timestamp: datetime
    activity_type: str
    context: Dict[str, Any]
    duration: float
    intensity: float  # 0.0 to 1.0


@dataclass
class Suggestion:
    """Represents a proactive suggestion"""
    suggestion_id: str
    suggestion_type: SuggestionType
    title: str
    description: str
    confidence: float
    context: Dict[str, Any]
    suggested_actions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None


class AnticipationEngine:
    """Core anticipation engine for proactive AI assistance"""
    
    def __init__(
        self, 
        memory_system: Optional[AdvancedMemorySystem] = None,
        db_path: str = "lyrixa_anticipation.db"
    ):
        self.memory_system = memory_system or AdvancedMemorySystem()
        self.db_path = db_path
        
        # Context tracking
        self.current_context: ContextState = ContextState.ACTIVE_WORKING
        self.activity_history: List[UserActivity] = []
        self.active_suggestions: Dict[str, Suggestion] = {}
        
        # Configuration
        self.max_activity_history = 1000
        self.suggestion_cooldown = 300  # 5 minutes between similar suggestions
        self.context_analysis_interval = 30  # Analyze context every 30 seconds
        
        # Pattern tracking
        self.workflow_patterns: Dict[str, List[str]] = {}
        self.productivity_metrics: Dict[str, float] = {}
        
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize the anticipation database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User activities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                activity_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                context TEXT NOT NULL,
                duration REAL NOT NULL,
                intensity REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Suggestions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestions (
                suggestion_id TEXT PRIMARY KEY,
                suggestion_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                confidence REAL NOT NULL,
                context TEXT NOT NULL,
                suggested_actions TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                user_response TEXT,
                was_helpful BOOLEAN,
                response_time REAL
            )
        """)
        
        # Context patterns table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_name TEXT NOT NULL,
                context_sequence TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.0,
                last_occurrence TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
    async def track_activity(
        self,
        activity_type: str,
        context: Dict[str, Any],
        duration: float = 0.0,
        intensity: float = 0.5
    ) -> str:
        """Track a user activity for pattern analysis"""
        
        activity = UserActivity(
            activity_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            activity_type=activity_type,
            context=context,
            duration=duration,
            intensity=intensity
        )
        
        # Add to memory
        self.activity_history.append(activity)
        
        # Keep history size manageable
        if len(self.activity_history) > self.max_activity_history:
            self.activity_history = self.activity_history[-self.max_activity_history:]
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_activities 
            (activity_id, timestamp, activity_type, context, duration, intensity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            activity.activity_id,
            activity.timestamp.isoformat(),
            activity.activity_type,
            json.dumps(activity.context),
            activity.duration,
            activity.intensity
        ))
        
        conn.commit()
        conn.close()
        
        # Analyze context and generate suggestions
        await self._analyze_context()
        
        return activity.activity_id
        
    async def _analyze_context(self) -> None:
        """Analyze current context and generate proactive suggestions"""
        
        if len(self.activity_history) < 3:
            return  # Need some history for meaningful analysis
            
        recent_activities = self.activity_history[-10:]  # Last 10 activities
        
        # Determine current context state
        self.current_context = self._determine_context_state(recent_activities)
        
        # Generate suggestions based on context
        suggestions = await self._generate_contextual_suggestions(recent_activities)
        
        # Add valid suggestions to active list
        for suggestion in suggestions:
            if self._should_show_suggestion(suggestion):
                self.active_suggestions[suggestion.suggestion_id] = suggestion
                await self._store_suggestion(suggestion)
                
    def _determine_context_state(self, activities: List[UserActivity]) -> ContextState:
        """Determine the current user context state"""
        
        if not activities:
            return ContextState.IDLE_EXTENDED
            
        now = datetime.now()
        recent_activity = activities[-1]
        time_since_last = (now - recent_activity.timestamp).total_seconds()
        
        # Check for idle states
        if time_since_last > 1800:  # 30 minutes
            return ContextState.IDLE_EXTENDED
        elif time_since_last > 300:  # 5 minutes
            return ContextState.IDLE_BRIEF
            
        # Check activity patterns
        recent_intensities = [a.intensity for a in activities[-5:]]
        avg_intensity = sum(recent_intensities) / len(recent_intensities)
        
        activity_types = [a.activity_type for a in activities[-5:]]
        unique_types = len(set(activity_types))
        
        if avg_intensity > 0.8:
            return ContextState.FOCUSED_DEEP
        elif unique_types > 3:
            return ContextState.MULTITASKING
        elif avg_intensity > 0.4:
            return ContextState.ACTIVE_WORKING
        else:
            return ContextState.TRANSITIONING
            
    async def _generate_contextual_suggestions(
        self, 
        activities: List[UserActivity]
    ) -> List[Suggestion]:
        """Generate suggestions based on current context"""
        
        suggestions = []
        
        # Workflow continuation suggestions
        workflow_suggestions = await self._suggest_workflow_continuations(activities)
        suggestions.extend(workflow_suggestions)
        
        # Task optimization suggestions
        optimization_suggestions = await self._suggest_task_optimizations(activities)
        suggestions.extend(optimization_suggestions)
        
        # Knowledge discovery suggestions
        knowledge_suggestions = await self._suggest_knowledge_discovery(activities)
        suggestions.extend(knowledge_suggestions)
        
        # Context-specific suggestions
        if self.current_context == ContextState.IDLE_BRIEF:
            break_suggestions = await self._suggest_break_activities()
            suggestions.extend(break_suggestions)
        elif self.current_context == ContextState.IDLE_EXTENDED:
            resumption_suggestions = await self._suggest_work_resumption(activities)
            suggestions.extend(resumption_suggestions)
        elif self.current_context == ContextState.MULTITASKING:
            focus_suggestions = await self._suggest_focus_improvements()
            suggestions.extend(focus_suggestions)
            
        return suggestions
        
    async def _suggest_workflow_continuations(
        self, 
        activities: List[UserActivity]
    ) -> List[Suggestion]:
        """Suggest natural next steps in current workflow"""
        
        suggestions = []
        
        if len(activities) < 2:
            return suggestions
            
        # Analyze recent activity sequence
        recent_types = [a.activity_type for a in activities[-5:]]
        
        # Look for known patterns
        for pattern_name, pattern_sequence in self.workflow_patterns.items():
            if self._matches_pattern_start(recent_types, pattern_sequence):
                next_step = self._predict_next_step(recent_types, pattern_sequence)
                if next_step:
                    suggestion = Suggestion(
                        suggestion_id=str(uuid.uuid4()),
                        suggestion_type=SuggestionType.WORKFLOW_CONTINUATION,
                        title=f"Continue {pattern_name} workflow",
                        description=f"Based on your pattern, you might want to {next_step}",
                        confidence=0.75,
                        context={"pattern": pattern_name, "next_step": next_step},
                        suggested_actions=[next_step],
                        created_at=datetime.now()
                    )
                    suggestions.append(suggestion)
                    
        return suggestions
        
    async def _suggest_task_optimizations(
        self, 
        activities: List[UserActivity]
    ) -> List[Suggestion]:
        """Suggest ways to optimize current tasks"""
        
        suggestions = []
        
        # Analyze for inefficient patterns
        if len(activities) >= 5:
            recent_durations = [a.duration for a in activities[-5:] if a.duration > 0]
            recent_types = [a.activity_type for a in activities[-5:]]
            
            # Look for repetitive short tasks (potential batch opportunity)
            if len(set(recent_types[-3:])) == 1 and all(d < 300 for d in recent_durations[-3:]):
                suggestion = Suggestion(
                    suggestion_id=str(uuid.uuid4()),
                    suggestion_type=SuggestionType.TASK_OPTIMIZATION,
                    title="Batch similar tasks",
                    description="You're doing several short similar tasks. Consider batching them for efficiency.",
                    confidence=0.8,
                    context={"task_type": recent_types[-1], "instances": 3},
                    suggested_actions=[
                        "Group similar tasks together",
                        "Set aside dedicated time blocks",
                        "Use task batching techniques"
                    ],
                    created_at=datetime.now()
                )
                suggestions.append(suggestion)
                
        return suggestions
        
    async def _suggest_knowledge_discovery(
        self, 
        activities: List[UserActivity]
    ) -> List[Suggestion]:
        """Suggest relevant knowledge based on current activities"""
        
        suggestions = []
        
        if not self.memory_system:
            return suggestions
            
        # Extract keywords from recent activities
        recent_contexts = [a.context for a in activities[-3:]]
        keywords = self._extract_keywords_from_contexts(recent_contexts)
        
        if keywords:
            # Search memory for related content
            try:
                related_memories = await self.memory_system.semantic_search(
                    " ".join(keywords), 
                    top_k=3,
                    min_confidence=0.6
                )
                
                if related_memories:
                    suggestion = Suggestion(
                        suggestion_id=str(uuid.uuid4()),
                        suggestion_type=SuggestionType.KNOWLEDGE_DISCOVERY,
                        title="Related knowledge found",
                        description=f"Found {len(related_memories)} relevant memories that might help",
                        confidence=0.7,
                        context={"keywords": keywords, "memory_count": len(related_memories)},
                        suggested_actions=[
                            "Review related memories",
                            "Apply previous solutions",
                            "Build on existing knowledge"
                        ],
                        created_at=datetime.now()
                    )
                    suggestions.append(suggestion)
                    
            except Exception as e:
                logging.warning(f"Error searching memories for knowledge discovery: {e}")
                
        return suggestions
        
    async def _suggest_break_activities(self) -> List[Suggestion]:
        """Suggest appropriate break activities"""
        
        suggestion = Suggestion(
            suggestion_id=str(uuid.uuid4()),
            suggestion_type=SuggestionType.PRODUCTIVITY_TIP,
            title="Take a mindful break",
            description="You've been idle briefly. A short break might help you refocus.",
            confidence=0.6,
            context={"break_type": "mindful"},
            suggested_actions=[
                "Take a 5-minute walk",
                "Do some deep breathing",
                "Stretch at your desk",
                "Drink some water"
            ],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=10)
        )
        
        return [suggestion]
        
    async def _suggest_work_resumption(
        self, 
        activities: List[UserActivity]
    ) -> List[Suggestion]:
        """Suggest how to resume work after extended idle time"""
        
        if len(activities) < 2:
            return []
            
        # Find the last meaningful work activity
        last_work_activity = None
        for activity in reversed(activities):
            if activity.intensity > 0.5:
                last_work_activity = activity
                break
                
        if last_work_activity:
            suggestion = Suggestion(
                suggestion_id=str(uuid.uuid4()),
                suggestion_type=SuggestionType.WORKFLOW_CONTINUATION,
                title="Resume your work",
                description=f"Welcome back! You were working on {last_work_activity.activity_type}",
                confidence=0.8,
                context={"last_activity": last_work_activity.activity_type},
                suggested_actions=[
                    f"Continue with {last_work_activity.activity_type}",
                    "Review what you accomplished",
                    "Set goals for this session"
                ],
                created_at=datetime.now()
            )
            return [suggestion]
            
        return []
        
    async def _suggest_focus_improvements(self) -> List[Suggestion]:
        """Suggest ways to improve focus during multitasking"""
        
        suggestion = Suggestion(
            suggestion_id=str(uuid.uuid4()),
            suggestion_type=SuggestionType.PRODUCTIVITY_TIP,
            title="Improve focus",
            description="You're multitasking. Consider focusing on one task at a time.",
            confidence=0.7,
            context={"suggestion_type": "focus_improvement"},
            suggested_actions=[
                "Choose your most important task",
                "Close unnecessary applications",
                "Use the Pomodoro Technique",
                "Set a timer for focused work"
            ],
            created_at=datetime.now()
        )
        
        return [suggestion]
        
    def _should_show_suggestion(self, suggestion: Suggestion) -> bool:
        """Determine if a suggestion should be shown to the user"""
        
        # Check if similar suggestion was recently shown
        for existing in self.active_suggestions.values():
            if (existing.suggestion_type == suggestion.suggestion_type and 
                (datetime.now() - existing.created_at).total_seconds() < self.suggestion_cooldown):
                return False
                
        # Check confidence threshold
        if suggestion.confidence < 0.5:
            return False
            
        # Check if suggestion has expired
        if suggestion.expires_at and datetime.now() > suggestion.expires_at:
            return False
            
        return True
        
    async def _store_suggestion(self, suggestion: Suggestion) -> None:
        """Store suggestion in database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO suggestions 
            (suggestion_id, suggestion_type, title, description, confidence, 
             context, suggested_actions, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            suggestion.suggestion_id,
            suggestion.suggestion_type.value,
            suggestion.title,
            suggestion.description,
            suggestion.confidence,
            json.dumps(suggestion.context),
            json.dumps(suggestion.suggested_actions),
            suggestion.created_at.isoformat(),
            suggestion.expires_at.isoformat() if suggestion.expires_at else None
        ))
        
        conn.commit()
        conn.close()
        
    async def get_active_suggestions(self) -> List[Suggestion]:
        """Get current active suggestions"""
        
        # Remove expired suggestions
        now = datetime.now()
        expired_ids = [
            sid for sid, suggestion in self.active_suggestions.items()
            if suggestion.expires_at and now > suggestion.expires_at
        ]
        
        for sid in expired_ids:
            del self.active_suggestions[sid]
            
        return list(self.active_suggestions.values())
        
    async def respond_to_suggestion(
        self, 
        suggestion_id: str, 
        response: str,
        was_helpful: bool
    ) -> None:
        """Record user response to a suggestion"""
        
        if suggestion_id in self.active_suggestions:
            suggestion = self.active_suggestions[suggestion_id]
            response_time = (datetime.now() - suggestion.created_at).total_seconds()
            
            # Store response in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE suggestions 
                SET user_response = ?, was_helpful = ?, response_time = ?
                WHERE suggestion_id = ?
            """, (response, was_helpful, response_time, suggestion_id))
            
            conn.commit()
            conn.close()
            
            # Remove from active suggestions
            del self.active_suggestions[suggestion_id]
            
            # Learn from feedback
            await self._learn_from_feedback(suggestion, was_helpful)
            
    async def _learn_from_feedback(
        self, 
        suggestion: Suggestion, 
        was_helpful: bool
    ) -> None:
        """Learn from user feedback to improve suggestions"""
        
        # Store learning in memory system
        if self.memory_system:
            learning_content = (
                f"Suggestion feedback: {suggestion.suggestion_type.value} "
                f"was {'helpful' if was_helpful else 'not helpful'}. "
                f"Context: {json.dumps(suggestion.context)}"
            )
            
            await self.memory_system.store_memory(
                content=learning_content,
                memory_type="feedback_learning",
                confidence=0.8,
                context={
                    "suggestion_type": suggestion.suggestion_type.value,
                    "was_helpful": was_helpful,
                    "original_confidence": suggestion.confidence
                }
            )
            
    def _matches_pattern_start(
        self, 
        recent_types: List[str], 
        pattern_sequence: List[str]
    ) -> bool:
        """Check if recent activities match the start of a known pattern"""
        
        if len(recent_types) < 2 or len(pattern_sequence) < 3:
            return False
            
        # Check if the last 2-3 activities match the pattern start
        for i in range(min(3, len(recent_types))):
            if (len(pattern_sequence) > i and 
                recent_types[-(i+1)] == pattern_sequence[i]):
                continue
            else:
                return False
                
        return True
        
    def _predict_next_step(
        self, 
        recent_types: List[str], 
        pattern_sequence: List[str]
    ) -> Optional[str]:
        """Predict the next step in a workflow pattern"""
        
        matching_index = 0
        for i, activity_type in enumerate(reversed(recent_types)):
            if (matching_index < len(pattern_sequence) and 
                activity_type == pattern_sequence[matching_index]):
                matching_index += 1
            else:
                break
                
        if matching_index < len(pattern_sequence):
            return pattern_sequence[matching_index]
            
        return None
        
    def _extract_keywords_from_contexts(
        self, 
        contexts: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract meaningful keywords from activity contexts"""
        
        keywords = []
        for context in contexts:
            for key, value in context.items():
                if isinstance(value, str) and len(value) > 3:
                    keywords.append(value.lower())
                elif isinstance(value, list):
                    keywords.extend([str(item).lower() for item in value if len(str(item)) > 3])
                    
        # Remove duplicates and filter common words
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        unique_keywords = list(set(keywords) - common_words)
        
        return unique_keywords[:10]  # Limit to top 10 keywords
        
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary of anticipation engine performance"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get suggestion statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_suggestions,
                AVG(confidence) as avg_confidence,
                COUNT(CASE WHEN was_helpful = 1 THEN 1 END) as helpful_count,
                COUNT(CASE WHEN was_helpful = 0 THEN 1 END) as unhelpful_count,
                AVG(response_time) as avg_response_time
            FROM suggestions 
            WHERE created_at >= datetime('now', '-7 days')
        """)
        
        suggestion_stats = cursor.fetchone()
        
        # Get activity statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_activities,
                AVG(duration) as avg_duration,
                AVG(intensity) as avg_intensity,
                COUNT(DISTINCT activity_type) as unique_activity_types
            FROM user_activities 
            WHERE timestamp >= datetime('now', '-7 days')
        """)
        
        activity_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "anticipation_performance": {
                "total_suggestions": suggestion_stats[0] or 0,
                "average_confidence": suggestion_stats[1] or 0.0,
                "helpful_suggestions": suggestion_stats[2] or 0,
                "unhelpful_suggestions": suggestion_stats[3] or 0,
                "helpfulness_rate": (suggestion_stats[2] or 0) / max(1, suggestion_stats[0] or 1),
                "average_response_time": suggestion_stats[4] or 0.0
            },
            "activity_tracking": {
                "total_activities": activity_stats[0] or 0,
                "average_duration": activity_stats[1] or 0.0,
                "average_intensity": activity_stats[2] or 0.0,
                "unique_activity_types": activity_stats[3] or 0
            },
            "current_context": self.current_context.value,
            "active_suggestions_count": len(self.active_suggestions)
        }


# Test and demonstration functions
async def test_anticipation_engine():
    """Test the anticipation engine functionality"""
    
    print("🔮 Testing Lyrixa Anticipation Engine...")
    
    # Initialize engine
    engine = AnticipationEngine()
    
    # Simulate user activities
    print("\n1. Simulating user activities...")
    
    activities = [
        ("coding", {"project": "web_app", "language": "python"}, 1800, 0.8),
        ("research", {"topic": "machine_learning", "source": "documentation"}, 600, 0.6),
        ("break", {"type": "coffee"}, 300, 0.2),
        ("coding", {"project": "web_app", "language": "python"}, 2400, 0.9),
        ("testing", {"project": "web_app", "type": "unit_tests"}, 900, 0.7)
    ]
    
    for activity_type, context, duration, intensity in activities:
        activity_id = await engine.track_activity(
            activity_type=activity_type,
            context=context,
            duration=duration,
            intensity=intensity
        )
        print(f"   📝 Tracked: {activity_type} (ID: {activity_id[:8]}...)")
        
        # Small delay to simulate real timing
        await asyncio.sleep(0.1)
        
    # Get active suggestions
    print("\n2. Generated suggestions...")
    suggestions = await engine.get_active_suggestions()
    
    for suggestion in suggestions:
        print(f"   💡 {suggestion.title}")
        print(f"      {suggestion.description}")
        print(f"      Confidence: {suggestion.confidence:.2f}")
        print(f"      Actions: {', '.join(suggestion.suggested_actions[:2])}...")
        print()
        
    # Simulate user feedback
    print("3. Simulating user feedback...")
    if suggestions:
        await engine.respond_to_suggestion(
            suggestions[0].suggestion_id,
            "accepted",
            was_helpful=True
        )
        print("   ✅ Positive feedback recorded")
        
    # Get analytics
    print("\n4. Analytics summary...")
    analytics = await engine.get_analytics_summary()
    
    print(f"   📊 Total activities: {analytics['activity_tracking']['total_activities']}")
    print(f"   📊 Total suggestions: {analytics['anticipation_performance']['total_suggestions']}")
    print(f"   📊 Current context: {analytics['current_context']}")
    print(f"   📊 Active suggestions: {analytics['active_suggestions_count']}")
    
    if analytics['anticipation_performance']['total_suggestions'] > 0:
        helpfulness = analytics['anticipation_performance']['helpfulness_rate']
        print(f"   📊 Helpfulness rate: {helpfulness:.1%}")
        
    print("\n✅ Anticipation Engine test complete!")
    return engine


if __name__ == "__main__":
    asyncio.run(test_anticipation_engine())
