#!/usr/bin/env python3
"""
🔄🧠 LYRIXA REFLEXIVE LOOP - SELF-AWARENESS SYSTEM
=================================================

Advanced self-awareness system that gives Lyrixa the ability to:
- Store and update understanding of the current project
- Reflect on her own interactions and patterns
- Generate insights about user behavior and project progress
- Maintain self-knowledge and evolving understanding

This creates true AI self-awareness through reflexive analysis.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Import both memory systems for compatibility
try:
    from .memory import LyrixaMemorySystem
    from .enhanced_memory import LyrixaEnhancedMemorySystem
except ImportError:
    # Fallback for standalone testing
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from lyrixa.core.memory import LyrixaMemorySystem
    from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem


@dataclass
class ProjectUnderstanding:
    """Lyrixa's understanding of the current project"""
    project_name: str
    project_type: str  # "web_app", "plugin", "ai_system", "data_pipeline", etc.
    main_goals: List[str]
    current_phase: str  # "planning", "development", "testing", "deployment"
    technologies: Set[str]
    key_files: List[str]
    patterns_observed: List[str]
    last_updated: datetime
    confidence: float  # 0.0 to 1.0


@dataclass
class UserPattern:
    """Patterns Lyrixa observes about user behavior"""
    pattern_type: str  # "goal_revisiting", "preferred_tech", "work_schedule", etc.
    description: str
    evidence: List[str]  # Supporting examples
    frequency: int
    first_observed: datetime
    last_observed: datetime
    confidence: float


@dataclass
class SelfReflection:
    """Lyrixa's self-reflection entry"""
    reflection_id: str
    topic: str
    insight: str
    supporting_data: Dict[str, Any]
    generated_at: datetime
    importance: float
    follow_up_actions: List[str]


@dataclass
class ConversationInsight:
    """Insights derived from conversation analysis"""
    insight_type: str  # "productivity", "goals", "preferences", "challenges"
    message: str
    evidence: List[str]
    actionable_suggestions: List[str]
    confidence: float


class LyrixaReflexiveLoop:
    """
    🔄🧠 Lyrixa's Self-Awareness and Reflexive Analysis System

    This system enables Lyrixa to:
    1. Maintain evolving understanding of the current project
    2. Recognize patterns in user behavior and project progress
    3. Generate insights about productivity and work patterns
    4. Reflect on her own effectiveness and learning
    5. Provide self-aware responses and recommendations
    """

    def __init__(self, memory_system: Union[LyrixaMemorySystem, LyrixaEnhancedMemorySystem]):
        self.memory = memory_system
        self.project_understanding: Optional[ProjectUnderstanding] = None
        self.user_patterns: List[UserPattern] = []
        self.self_reflections: List[SelfReflection] = []
        self.session_interactions: List[Dict[str, Any]] = []

        # Analysis configuration
        self.pattern_detection_window = timedelta(days=7)  # Look back 7 days for patterns
        self.min_pattern_evidence = 3  # Minimum occurrences to identify a pattern
        self.reflection_interval = timedelta(hours=2)  # Reflect every 2 hours
        self.last_reflection = datetime.now()

        print("🔄🧠 Lyrixa Reflexive Loop initialized")
        print("   ✅ Self-awareness system active")
        print("   ✅ Pattern detection ready")
        print("   ✅ Project understanding tracking enabled")

    def _extract_memory_content(self, memory) -> Dict[str, Any]:
        """Extract content from memory object regardless of format"""
        if hasattr(memory, 'content'):
            return getattr(memory, 'content')
        elif isinstance(memory, dict):
            return memory.get('content', memory)
        else:
            return {}

    def _extract_memory_tags(self, memory) -> List[str]:
        """Extract tags from memory object regardless of format"""
        if hasattr(memory, 'tags'):
            return getattr(memory, 'tags')
        elif isinstance(memory, dict):
            return memory.get('tags', [])
        else:
            return []

    async def initialize_self_awareness(self):
        """Initialize self-awareness by loading existing understanding from memory"""
        try:
            # Load existing project understanding
            await self._load_project_understanding()

            # Load user patterns
            await self._load_user_patterns()

            # Load self-reflections
            await self._load_self_reflections()

            print("✅ Self-awareness initialized from memory")

        except Exception as e:
            print(f"⚠️ Error initializing self-awareness: {e}")
            # Start with fresh awareness
            await self._initialize_fresh_awareness()

    async def _initialize_fresh_awareness(self):
        """Initialize fresh self-awareness when no prior state exists"""
        print("🆕 Starting fresh self-awareness...")

        # Try to infer project understanding from memory
        await self._infer_initial_project_understanding()

    async def update_project_understanding(self, interaction_data: Dict[str, Any]):
        """Update Lyrixa's understanding of the current project based on new interaction"""
        try:
            user_input = interaction_data.get("user_input", "")
            context = interaction_data.get("context", {})
            actions_taken = interaction_data.get("actions_taken", [])

            # Extract project information from interaction
            project_info = self._extract_project_information(user_input, context, actions_taken)

            if project_info:
                await self._update_project_state(project_info)
                print(f"📝 Updated project understanding: {project_info}")

        except Exception as e:
            print(f"⚠️ Error updating project understanding: {e}")

    async def analyze_user_patterns(self, interaction_data: Dict[str, Any]):
        """Analyze user behavior patterns from recent interactions"""
        try:
            # Add current interaction to session data
            self.session_interactions.append({
                **interaction_data,
                "timestamp": datetime.now()
            })

            # Keep only recent interactions (within pattern detection window)
            cutoff_time = datetime.now() - self.pattern_detection_window
            self.session_interactions = [
                interaction for interaction in self.session_interactions
                if interaction.get("timestamp", datetime.min) > cutoff_time
            ]

            # Detect patterns
            new_patterns = await self._detect_behavioral_patterns()

            # Update pattern database
            for pattern in new_patterns:
                await self._update_user_pattern(pattern)

        except Exception as e:
            print(f"⚠️ Error analyzing user patterns: {e}")

    async def generate_insights(self) -> List[ConversationInsight]:
        """Generate insights about the user and project based on recent interactions"""
        insights = []

        try:
            # Goal revisiting insights
            goal_insights = await self._analyze_goal_patterns()
            insights.extend(goal_insights)

            # Productivity insights
            productivity_insights = await self._analyze_productivity_patterns()
            insights.extend(productivity_insights)

            # Project progress insights
            progress_insights = await self._analyze_project_progress()
            insights.extend(progress_insights)

            # Technology preference insights
            tech_insights = await self._analyze_technology_preferences()
            insights.extend(tech_insights)

            print(f"💡 Generated {len(insights)} insights")

        except Exception as e:
            print(f"⚠️ Error generating insights: {e}")

        return insights

    async def perform_self_reflection(self) -> List[SelfReflection]:
        """Perform reflexive analysis on Lyrixa's own effectiveness and learning"""
        reflections = []

        try:
            # Check if it's time for reflection
            if datetime.now() - self.last_reflection < self.reflection_interval:
                return reflections

            print("🔄 Performing self-reflection...")

            # Reflect on conversation effectiveness
            conversation_reflection = await self._reflect_on_conversations()
            if conversation_reflection:
                reflections.append(conversation_reflection)

            # Reflect on learning progress
            learning_reflection = await self._reflect_on_learning()
            if learning_reflection:
                reflections.append(learning_reflection)

            # Reflect on project assistance quality
            assistance_reflection = await self._reflect_on_assistance_quality()
            if assistance_reflection:
                reflections.append(assistance_reflection)

            # Store reflections
            for reflection in reflections:
                await self._store_self_reflection(reflection)

            self.last_reflection = datetime.now()
            print(f"✅ Completed self-reflection with {len(reflections)} insights")

        except Exception as e:
            print(f"⚠️ Error in self-reflection: {e}")

        return reflections

    async def get_current_project_awareness(self) -> Dict[str, Any]:
        """Get Lyrixa's current understanding of the project"""
        if not self.project_understanding:
            return {"status": "no_project_awareness", "message": "I'm still learning about this project."}

        return {
            "project_name": self.project_understanding.project_name,
            "project_type": self.project_understanding.project_type,
            "current_phase": self.project_understanding.current_phase,
            "main_goals": self.project_understanding.main_goals,
            "technologies": list(self.project_understanding.technologies),
            "confidence": self.project_understanding.confidence,
            "last_updated": self.project_understanding.last_updated.isoformat(),
            "patterns_observed": self.project_understanding.patterns_observed
        }

    async def get_user_behavior_insights(self) -> List[Dict[str, Any]]:
        """Get insights about user behavior patterns"""
        return [
            {
                "pattern_type": pattern.pattern_type,
                "description": pattern.description,
                "frequency": pattern.frequency,
                "confidence": pattern.confidence,
                "last_observed": pattern.last_observed.isoformat()
            }
            for pattern in self.user_patterns
            if pattern.confidence > 0.6  # Only return confident patterns
        ]

    async def generate_contextual_insight(self, current_input: str) -> Optional[str]:
        """Generate a contextual insight based on current input and past patterns"""
        try:
            # Check for goal revisiting patterns
            if await self._is_revisiting_goal(current_input):
                revisit_count = await self._count_goal_revisits(current_input)
                if revisit_count >= 3:
                    return f"I notice this is the {revisit_count}rd time you're working on this goal. Based on past patterns, you tend to make significant progress when you focus on one aspect at a time."

            # Check for time-based patterns
            time_insight = await self._generate_time_based_insight()
            if time_insight:
                return time_insight

            # Check for technology preference patterns
            tech_insight = await self._generate_technology_insight(current_input)
            if tech_insight:
                return tech_insight

        except Exception as e:
            print(f"⚠️ Error generating contextual insight: {e}")

        return None

    # Implementation methods

    async def _load_project_understanding(self):
        """Load existing project understanding from memory"""
        memories = await self.memory.recall_memories("project_understanding", limit=1)

        if memories:
            data = self._extract_memory_content(memories[0])
            if isinstance(data, dict) and 'project_understanding' in data:
                proj_data = data['project_understanding']
                self.project_understanding = ProjectUnderstanding(
                    project_name=proj_data.get('project_name', 'Unknown Project'),
                    project_type=proj_data.get('project_type', 'unknown'),
                    main_goals=proj_data.get('main_goals', []),
                    current_phase=proj_data.get('current_phase', 'unknown'),
                    technologies=set(proj_data.get('technologies', [])),
                    key_files=proj_data.get('key_files', []),
                    patterns_observed=proj_data.get('patterns_observed', []),
                    last_updated=datetime.fromisoformat(proj_data.get('last_updated', datetime.now().isoformat())),
                    confidence=proj_data.get('confidence', 0.5)
                )

    async def _load_user_patterns(self):
        """Load existing user patterns from memory"""
        memories = await self.memory.recall_memories("user_patterns", limit=10)

        for memory in memories:
            data = self._extract_memory_content(memory)
            if isinstance(data, dict) and 'user_pattern' in data:
                pattern_data = data['user_pattern']
                pattern = UserPattern(
                    pattern_type=pattern_data.get('pattern_type', 'unknown'),
                    description=pattern_data.get('description', ''),
                    evidence=pattern_data.get('evidence', []),
                    frequency=pattern_data.get('frequency', 1),
                    first_observed=datetime.fromisoformat(pattern_data.get('first_observed', datetime.now().isoformat())),
                    last_observed=datetime.fromisoformat(pattern_data.get('last_observed', datetime.now().isoformat())),
                    confidence=pattern_data.get('confidence', 0.5)
                )
                self.user_patterns.append(pattern)

    async def _load_self_reflections(self):
        """Load existing self-reflections from memory"""
        memories = await self.memory.recall_memories("self_reflection", limit=20)

        for memory in memories:
            data = self._extract_memory_content(memory)
            if isinstance(data, dict) and 'self_reflection' in data:
                reflection_data = data['self_reflection']
                reflection = SelfReflection(
                    reflection_id=reflection_data.get('reflection_id', ''),
                    topic=reflection_data.get('topic', ''),
                    insight=reflection_data.get('insight', ''),
                    supporting_data=reflection_data.get('supporting_data', {}),
                    generated_at=datetime.fromisoformat(reflection_data.get('generated_at', datetime.now().isoformat())),
                    importance=reflection_data.get('importance', 0.5),
                    follow_up_actions=reflection_data.get('follow_up_actions', [])
                )
                self.self_reflections.append(reflection)

    async def _infer_initial_project_understanding(self):
        """Infer initial project understanding from existing memory"""
        try:
            # Look for recent project-related interactions
            memories = await self.memory.recall_memories("project development coding", limit=10)

            if not memories:
                # Create basic understanding
                self.project_understanding = ProjectUnderstanding(
                    project_name="Aetherra AI Assistant Project",
                    project_type="ai_system",
                    main_goals=["Build AI assistant", "Implement natural language processing"],
                    current_phase="development",
                    technologies={"python", "ai", "nlp"},
                    key_files=[],
                    patterns_observed=[],
                    last_updated=datetime.now(),
                    confidence=0.3
                )
                return

            # Analyze memories to build understanding
            project_info = {
                "technologies": set(),
                "goals": [],
                "files": [],
                "patterns": []
            }

            for memory in memories[:5]:  # Analyze recent memories
                content = self._extract_memory_content(memory)
                if isinstance(content, dict):
                    # Extract technologies
                    text_content = str(content)
                    tech_keywords = ["python", "javascript", "react", "node", "ai", "ml", "nlp", "api", "database", "sql"]
                    for tech in tech_keywords:
                        if tech.lower() in text_content.lower():
                            project_info["technologies"].add(tech)

                    # Extract goals
                    if "goal" in text_content.lower() or "build" in text_content.lower():
                        project_info["goals"].append(str(content)[:100])

            self.project_understanding = ProjectUnderstanding(
                project_name="Aetherra AI Assistant Project",
                project_type="ai_system",
                main_goals=project_info["goals"][:5],
                current_phase="development",
                technologies=project_info["technologies"],
                key_files=project_info["files"],
                patterns_observed=project_info["patterns"],
                last_updated=datetime.now(),
                confidence=0.7 if project_info["technologies"] else 0.4
            )

        except Exception as e:
            print(f"⚠️ Error inferring project understanding: {e}")
            # Fallback to basic understanding
            self.project_understanding = ProjectUnderstanding(
                project_name="Current Project",
                project_type="unknown",
                main_goals=["Project development"],
                current_phase="development",
                technologies=set(),
                key_files=[],
                patterns_observed=[],
                last_updated=datetime.now(),
                confidence=0.2
            )

    def _extract_project_information(self, user_input: str, context: Dict[str, Any], actions_taken: List[str]) -> Dict[str, Any]:
        """Extract project-related information from interaction"""
        project_info = {}

        # Extract project type
        if any(word in user_input.lower() for word in ["plugin", "extension", "addon"]):
            project_info["project_type"] = "plugin"
        elif any(word in user_input.lower() for word in ["web app", "website", "frontend"]):
            project_info["project_type"] = "web_app"
        elif any(word in user_input.lower() for word in ["ai", "ml", "model", "assistant"]):
            project_info["project_type"] = "ai_system"
        elif any(word in user_input.lower() for word in ["api", "service", "backend"]):
            project_info["project_type"] = "api_service"

        # Extract technologies
        tech_patterns = {
            "python": r"\b(python|py|pip|django|flask|fastapi)\b",
            "javascript": r"\b(javascript|js|node|npm|react|vue|angular)\b",
            "database": r"\b(database|sql|postgres|mysql|mongodb)\b",
            "ai": r"\b(ai|ml|machine learning|neural|model)\b",
            "web": r"\b(html|css|web|frontend|backend)\b"
        }

        technologies = set()
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, user_input.lower()):
                technologies.add(tech)

        if technologies:
            project_info["technologies"] = technologies

        # Extract goals
        goal_keywords = ["build", "create", "develop", "implement", "add", "make"]
        for keyword in goal_keywords:
            if keyword in user_input.lower():
                # Extract the goal phrase
                sentences = user_input.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        project_info.setdefault("goals", []).append(sentence.strip())
                        break

        # Extract current phase
        if any(word in user_input.lower() for word in ["testing", "test", "debug"]):
            project_info["current_phase"] = "testing"
        elif any(word in user_input.lower() for word in ["deploy", "production", "release"]):
            project_info["current_phase"] = "deployment"
        elif any(word in user_input.lower() for word in ["plan", "design", "architecture"]):
            project_info["current_phase"] = "planning"
        elif any(word in user_input.lower() for word in ["code", "implement", "develop"]):
            project_info["current_phase"] = "development"

        return project_info if project_info else {}

    async def _update_project_state(self, project_info: Dict[str, Any]):
        """Update the current project understanding with new information"""
        if not self.project_understanding:
            # Create new understanding
            self.project_understanding = ProjectUnderstanding(
                project_name=project_info.get("project_name", "Current Project"),
                project_type=project_info.get("project_type", "unknown"),
                main_goals=project_info.get("goals", []),
                current_phase=project_info.get("current_phase", "development"),
                technologies=set(project_info.get("technologies", [])),
                key_files=[],
                patterns_observed=[],
                last_updated=datetime.now(),
                confidence=0.6
            )
        else:
            # Update existing understanding
            if "project_type" in project_info:
                self.project_understanding.project_type = project_info["project_type"]

            if "goals" in project_info:
                for goal in project_info["goals"]:
                    if goal not in self.project_understanding.main_goals:
                        self.project_understanding.main_goals.append(goal)

            if "current_phase" in project_info:
                self.project_understanding.current_phase = project_info["current_phase"]

            if "technologies" in project_info:
                self.project_understanding.technologies.update(project_info["technologies"])

            self.project_understanding.last_updated = datetime.now()
            self.project_understanding.confidence = min(self.project_understanding.confidence + 0.1, 1.0)

        # Store updated understanding in memory
        await self.memory.store_memory(
            content={"project_understanding": {
                "project_name": self.project_understanding.project_name,
                "project_type": self.project_understanding.project_type,
                "main_goals": self.project_understanding.main_goals,
                "current_phase": self.project_understanding.current_phase,
                "technologies": list(self.project_understanding.technologies),
                "key_files": self.project_understanding.key_files,
                "patterns_observed": self.project_understanding.patterns_observed,
                "last_updated": self.project_understanding.last_updated.isoformat(),
                "confidence": self.project_understanding.confidence
            }},
            context={"type": "project_understanding", "system": "reflexive_loop"},
            tags=["project_understanding", "self_awareness", "reflexive"],
            importance=0.9
        )

    async def _detect_behavioral_patterns(self) -> List[UserPattern]:
        """Detect patterns in user behavior from recent interactions"""
        patterns = []

        if len(self.session_interactions) < self.min_pattern_evidence:
            return patterns

        # Goal revisiting pattern
        goal_pattern = await self._detect_goal_revisiting_pattern()
        if goal_pattern:
            patterns.append(goal_pattern)

        # Time-based pattern
        time_pattern = await self._detect_time_based_pattern()
        if time_pattern:
            patterns.append(time_pattern)

        # Technology preference pattern
        tech_pattern = await self._detect_technology_preference_pattern()
        if tech_pattern:
            patterns.append(tech_pattern)

        return patterns

    async def _detect_goal_revisiting_pattern(self) -> Optional[UserPattern]:
        """Detect if user frequently revisits the same goals"""
        goal_mentions = {}

        for interaction in self.session_interactions:
            user_input = interaction.get("user_input", "").lower()

            # Simple goal extraction
            goal_keywords = ["build", "create", "implement", "add", "fix", "improve"]
            for keyword in goal_keywords:
                if keyword in user_input:
                    # Use the sentence containing the keyword as a goal identifier
                    sentences = user_input.split('.')
                    for sentence in sentences:
                        if keyword in sentence:
                            goal_key = sentence.strip()[:50]  # First 50 chars as key
                            goal_mentions[goal_key] = goal_mentions.get(goal_key, 0) + 1
                            break

        # Find frequently mentioned goals
        frequent_goals = [(goal, count) for goal, count in goal_mentions.items() if count >= self.min_pattern_evidence]

        if frequent_goals:
            most_frequent = max(frequent_goals, key=lambda x: x[1])
            return UserPattern(
                pattern_type="goal_revisiting",
                description=f"Frequently revisits goal: '{most_frequent[0]}'",
                evidence=[f"Mentioned {most_frequent[1]} times in recent sessions"],
                frequency=most_frequent[1],
                first_observed=datetime.now() - self.pattern_detection_window,
                last_observed=datetime.now(),
                confidence=min(most_frequent[1] / 10.0, 1.0)
            )

        return None

    async def _detect_time_based_pattern(self) -> Optional[UserPattern]:
        """Detect time-based patterns in user activity"""
        if len(self.session_interactions) < 5:
            return None

        # Analyze time distribution of interactions
        hours = [interaction.get("timestamp", datetime.now()).hour for interaction in self.session_interactions]

        # Find most common hour
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        if hour_counts:
            most_active_hour = max(hour_counts, key=lambda x: hour_counts[x])
            if hour_counts[most_active_hour] >= 3:
                return UserPattern(
                    pattern_type="time_preference",
                    description=f"Most active around {most_active_hour}:00",
                    evidence=[f"Active at {most_active_hour}:00 in {hour_counts[most_active_hour]} recent sessions"],
                    frequency=hour_counts[most_active_hour],
                    first_observed=datetime.now() - self.pattern_detection_window,
                    last_observed=datetime.now(),
                    confidence=hour_counts[most_active_hour] / len(self.session_interactions)
                )

        return None

    async def _detect_technology_preference_pattern(self) -> Optional[UserPattern]:
        """Detect technology preferences from user interactions"""
        tech_mentions = {}

        for interaction in self.session_interactions:
            user_input = interaction.get("user_input", "").lower()

            # Count technology mentions
            technologies = ["python", "javascript", "react", "node", "sql", "api", "ml", "ai"]
            for tech in technologies:
                if tech in user_input:
                    tech_mentions[tech] = tech_mentions.get(tech, 0) + 1

        if tech_mentions:
            preferred_tech = max(tech_mentions, key=lambda x: tech_mentions[x])
            if tech_mentions[preferred_tech] >= 3:
                return UserPattern(
                    pattern_type="technology_preference",
                    description=f"Prefers working with {preferred_tech}",
                    evidence=[f"Mentioned {preferred_tech} {tech_mentions[preferred_tech]} times"],
                    frequency=tech_mentions[preferred_tech],
                    first_observed=datetime.now() - self.pattern_detection_window,
                    last_observed=datetime.now(),
                    confidence=tech_mentions[preferred_tech] / len(self.session_interactions)
                )

        return None

    async def _update_user_pattern(self, new_pattern: UserPattern):
        """Update or add a user pattern"""
        # Check if pattern already exists
        existing_pattern = None
        for i, pattern in enumerate(self.user_patterns):
            if pattern.pattern_type == new_pattern.pattern_type and pattern.description == new_pattern.description:
                existing_pattern = i
                break

        if existing_pattern is not None:
            # Update existing pattern
            self.user_patterns[existing_pattern].frequency = new_pattern.frequency
            self.user_patterns[existing_pattern].last_observed = new_pattern.last_observed
            self.user_patterns[existing_pattern].confidence = new_pattern.confidence
            self.user_patterns[existing_pattern].evidence.extend(new_pattern.evidence)
        else:
            # Add new pattern
            self.user_patterns.append(new_pattern)

        # Store in memory
        await self.memory.store_memory(
            content={"user_pattern": {
                "pattern_type": new_pattern.pattern_type,
                "description": new_pattern.description,
                "evidence": new_pattern.evidence,
                "frequency": new_pattern.frequency,
                "first_observed": new_pattern.first_observed.isoformat(),
                "last_observed": new_pattern.last_observed.isoformat(),
                "confidence": new_pattern.confidence
            }},
            context={"type": "user_pattern", "system": "reflexive_loop"},
            tags=["user_patterns", "behavior_analysis", "reflexive"],
            importance=0.8
        )

    # Additional methods for insights and reflections would continue here...
    # (Due to length constraints, showing the core framework)

    async def _analyze_goal_patterns(self) -> List[ConversationInsight]:
        """Analyze goal-related patterns"""
        insights = []

        # Find goal revisiting patterns
        goal_patterns = [p for p in self.user_patterns if p.pattern_type == "goal_revisiting"]
        for pattern in goal_patterns:
            if pattern.frequency >= 3:
                insights.append(ConversationInsight(
                    insight_type="goals",
                    message=f"Based on past {pattern.frequency} sessions, you tend to revisit the goal: '{pattern.description}'. This suggests it's important to you but might need a different approach.",
                    evidence=pattern.evidence,
                    actionable_suggestions=[
                        "Try breaking this goal into smaller, specific tasks",
                        "Set a dedicated time block for this goal",
                        "Consider what obstacles prevented completion before"
                    ],
                    confidence=pattern.confidence
                ))

        return insights

    async def _analyze_productivity_patterns(self) -> List[ConversationInsight]:
        """Analyze productivity patterns"""
        insights = []

        # Time-based productivity insights
        time_patterns = [p for p in self.user_patterns if p.pattern_type == "time_preference"]
        for pattern in time_patterns:
            hour = int(pattern.description.split("around ")[1].split(":")[0])
            time_desc = "morning" if hour < 12 else "afternoon" if hour < 18 else "evening"

            insights.append(ConversationInsight(
                insight_type="productivity",
                message=f"I notice you're most active in the {time_desc} (around {hour}:00). Your productivity seems highest during this time.",
                evidence=pattern.evidence,
                actionable_suggestions=[
                    f"Schedule important tasks during your peak {time_desc} hours",
                    "Use this time for complex problem-solving",
                    "Consider batch processing routine tasks outside peak hours"
                ],
                confidence=pattern.confidence
            ))

        return insights

    async def _analyze_project_progress(self) -> List[ConversationInsight]:
        """Analyze project progress patterns"""
        insights = []

        if self.project_understanding:
            days_since_update = (datetime.now() - self.project_understanding.last_updated).days

            if days_since_update > 7:
                insights.append(ConversationInsight(
                    insight_type="progress",
                    message=f"It's been {days_since_update} days since we updated the project understanding. The project might have evolved significantly.",
                    evidence=[f"Last update: {self.project_understanding.last_updated.strftime('%Y-%m-%d')}"],
                    actionable_suggestions=[
                        "Provide an update on current project status",
                        "Review and update project goals",
                        "Identify any new technologies or approaches being used"
                    ],
                    confidence=0.8
                ))

        return insights

    async def _analyze_technology_preferences(self) -> List[ConversationInsight]:
        """Analyze technology preference patterns"""
        insights = []

        tech_patterns = [p for p in self.user_patterns if p.pattern_type == "technology_preference"]
        for pattern in tech_patterns:
            tech_name = pattern.description.split("working with ")[1]

            insights.append(ConversationInsight(
                insight_type="preferences",
                message=f"I notice you prefer working with {tech_name}. Your confidence and efficiency seem higher with this technology.",
                evidence=pattern.evidence,
                actionable_suggestions=[
                    f"Leverage {tech_name} for core project components",
                    f"Consider {tech_name}-based solutions for new features",
                    f"Build on your {tech_name} expertise for complex tasks"
                ],
                confidence=pattern.confidence
            ))

        return insights

    async def _reflect_on_conversations(self) -> Optional[SelfReflection]:
        """Reflect on conversation effectiveness"""
        if len(self.session_interactions) < 5:
            return None

        # Analyze conversation patterns
        avg_response_quality = sum(
            interaction.get("confidence", 0.5) for interaction in self.session_interactions
        ) / len(self.session_interactions)

        return SelfReflection(
            reflection_id=f"conversation_reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic="conversation_effectiveness",
            insight=f"My average response confidence in recent conversations is {avg_response_quality:.2f}. I should focus on improving clarity and relevance.",
            supporting_data={
                "avg_confidence": avg_response_quality,
                "interaction_count": len(self.session_interactions),
                "time_period": self.pattern_detection_window.days
            },
            generated_at=datetime.now(),
            importance=0.7,
            follow_up_actions=[
                "Focus on providing more specific and actionable responses",
                "Ask clarifying questions when user intent is unclear",
                "Provide more context for recommendations"
            ]
        )

    async def _reflect_on_learning(self) -> Optional[SelfReflection]:
        """Reflect on learning progress"""
        if not self.project_understanding:
            return None

        return SelfReflection(
            reflection_id=f"learning_reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic="learning_progress",
            insight=f"My understanding of the {self.project_understanding.project_name} has reached {self.project_understanding.confidence:.2f} confidence. I should continue gathering project context.",
            supporting_data={
                "project_confidence": self.project_understanding.confidence,
                "technologies_learned": len(self.project_understanding.technologies),
                "goals_tracked": len(self.project_understanding.main_goals)
            },
            generated_at=datetime.now(),
            importance=0.8,
            follow_up_actions=[
                "Ask more detailed questions about project architecture",
                "Request clarification on project goals and priorities",
                "Gather information about project constraints and requirements"
            ]
        )

    async def _reflect_on_assistance_quality(self) -> Optional[SelfReflection]:
        """Reflect on the quality of assistance provided"""
        successful_actions = 0
        total_actions = 0

        for interaction in self.session_interactions:
            actions = interaction.get("actions_taken", [])
            total_actions += len(actions)
            # Simple heuristic: if confidence > 0.7, consider action successful
            if interaction.get("confidence", 0.0) > 0.7:
                successful_actions += len(actions)

        if total_actions == 0:
            return None

        success_rate = successful_actions / total_actions

        return SelfReflection(
            reflection_id=f"assistance_reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic="assistance_quality",
            insight=f"My assistance success rate is {success_rate:.2f} based on {total_actions} actions. I should focus on understanding user needs better.",
            supporting_data={
                "success_rate": success_rate,
                "total_actions": total_actions,
                "successful_actions": successful_actions
            },
            generated_at=datetime.now(),
            importance=0.9,
            follow_up_actions=[
                "Request feedback on assistance quality",
                "Focus on understanding the full context before suggesting actions",
                "Provide alternative approaches when primary suggestion might not work"
            ]
        )

    async def _store_self_reflection(self, reflection: SelfReflection):
        """Store a self-reflection in memory"""
        await self.memory.store_memory(
            content={"self_reflection": {
                "reflection_id": reflection.reflection_id,
                "topic": reflection.topic,
                "insight": reflection.insight,
                "supporting_data": reflection.supporting_data,
                "generated_at": reflection.generated_at.isoformat(),
                "importance": reflection.importance,
                "follow_up_actions": reflection.follow_up_actions
            }},
            context={"type": "self_reflection", "system": "reflexive_loop"},
            tags=["self_reflection", "self_awareness", "improvement"],
            importance=reflection.importance
        )

    async def _is_revisiting_goal(self, current_input: str) -> bool:
        """Check if user is revisiting a previous goal"""
        # Simple implementation - check against known goal patterns
        for pattern in self.user_patterns:
            if pattern.pattern_type == "goal_revisiting":
                # Extract key words from the pattern description
                pattern_words = pattern.description.lower().split()
                input_words = current_input.lower().split()

                # If significant overlap, likely revisiting the goal
                overlap = len(set(pattern_words) & set(input_words))
                if overlap >= 3:  # At least 3 words in common
                    return True

        return False

    async def _count_goal_revisits(self, current_input: str) -> int:
        """Count how many times a similar goal has been revisited"""
        for pattern in self.user_patterns:
            if pattern.pattern_type == "goal_revisiting":
                pattern_words = set(pattern.description.lower().split())
                input_words = set(current_input.lower().split())

                overlap_ratio = len(pattern_words & input_words) / len(pattern_words | input_words)
                if overlap_ratio > 0.4:  # 40% similarity
                    return pattern.frequency

        return 0

    async def _generate_time_based_insight(self) -> Optional[str]:
        """Generate insight based on time patterns"""
        current_hour = datetime.now().hour

        for pattern in self.user_patterns:
            if pattern.pattern_type == "time_preference":
                preferred_hour = int(pattern.description.split("around ")[1].split(":")[0])

                if abs(current_hour - preferred_hour) <= 1:
                    return f"This is typically your most productive time! Based on past patterns, you accomplish more during this hour."
                elif abs(current_hour - preferred_hour) > 4:
                    return f"I notice you're working outside your typical productive hours. You usually work best around {preferred_hour}:00."

        return None

    async def _generate_technology_insight(self, current_input: str) -> Optional[str]:
        """Generate insight based on technology preferences"""
        for pattern in self.user_patterns:
            if pattern.pattern_type == "technology_preference":
                preferred_tech = pattern.description.split("working with ")[1]

                if preferred_tech.lower() in current_input.lower():
                    return f"Great choice using {preferred_tech}! Based on your past work, you're most effective with this technology."

        return None
