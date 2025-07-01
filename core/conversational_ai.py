"""
💬 Conversational Depth System
==============================

Rich, context-aware dialogue with memory integration, persona modes,
and intelligent conversation management for deeper AI interactions.
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use conditional import to avoid file permission issues during testing
try:
    from .memory.logger import MemoryLogger

    MEMORY_LOGGER_AVAILABLE = True
except (ImportError, PermissionError):
    MEMORY_LOGGER_AVAILABLE = False
    MemoryLogger = None


class PersonaMode(Enum):
    """Different AI personality modes"""

    ASSISTANT = "assistant"  # Helpful, professional assistant
    DEVELOPER = "developer"  # Technical, code-focused expert
    TEACHER = "teacher"  # Patient, educational, explanatory
    RESEARCHER = "researcher"  # Analytical, inquisitive, thorough
    CREATIVE = "creative"  # Imaginative, artistic, innovative
    ANALYST = "analyst"  # Data-driven, logical, systematic
    MENTOR = "mentor"  # Wise, supportive, growth-oriented


class ConversationContext(Enum):
    """Types of conversation contexts"""

    CODING = "coding"
    LEARNING = "learning"
    DEBUGGING = "debugging"
    PLANNING = "planning"
    ANALYSIS = "analysis"
    CREATIVE_WORK = "creative_work"
    CASUAL = "casual"


@dataclass
class PersonaConfig:
    """Configuration for a persona mode"""

    mode: PersonaMode
    name: str
    description: str
    traits: List[str]
    response_style: Dict[str, Any]
    preferred_contexts: List[ConversationContext]
    greeting_templates: List[str]
    expertise_areas: List[str]


@dataclass
class ConversationMemory:
    """Memory of a conversation"""

    conversation_id: str
    timestamp: datetime
    context: ConversationContext
    persona_used: PersonaMode
    user_input: str
    ai_response: str
    relevance_score: float
    tags: List[str]
    follow_up_suggestions: List[str]
    satisfaction_rating: Optional[float] = None


@dataclass
class ConversationSession:
    """A conversation session with continuity"""

    session_id: str
    start_time: datetime
    last_activity: datetime
    persona_mode: PersonaMode
    context: ConversationContext
    conversation_memories: List[ConversationMemory]
    session_summary: str
    key_topics: List[str]
    user_preferences: Dict[str, Any]


class ConversationalAI:
    """Main conversational AI system with depth and context awareness"""

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        # Initialize memory logger conditionally
        if MEMORY_LOGGER_AVAILABLE:
            try:
                self.memory_logger = MemoryLogger()
            except (PermissionError, FileNotFoundError):
                self.memory_logger = None
        else:
            self.memory_logger = None
        self.current_session: Optional[ConversationSession] = None
        self.conversation_history: List[ConversationMemory] = []
        self.session_history: List[ConversationSession] = []

        self.persona_configs = self._initialize_personas()
        self.current_persona = PersonaMode.ASSISTANT
        self.auto_persona_switching = True

        self.context_keywords = self._initialize_context_keywords()
        self.user_profile = self._load_user_profile()

        self._load_conversation_history()

    def _initialize_personas(self) -> Dict[PersonaMode, PersonaConfig]:
        """Initialize persona configurations"""
        personas = {
            PersonaMode.ASSISTANT: PersonaConfig(
                mode=PersonaMode.ASSISTANT,
                name="Assistant",
                description="Helpful, professional, and efficient",
                traits=["helpful", "professional", "clear", "efficient"],
                response_style={
                    "tone": "professional",
                    "verbosity": "balanced",
                    "formality": "moderate",
                    "emoji_usage": "minimal",
                },
                preferred_contexts=[ConversationContext.CASUAL, ConversationContext.PLANNING],
                greeting_templates=[
                    "Hello! How can I assist you today?",
                    "Hi there! What would you like help with?",
                    "Good to see you! How may I be of service?",
                ],
                expertise_areas=["general assistance", "task management", "information"],
            ),
            PersonaMode.DEVELOPER: PersonaConfig(
                mode=PersonaMode.DEVELOPER,
                name="Developer",
                description="Technical expert focused on code and development",
                traits=["technical", "precise", "solution-oriented", "detail-focused"],
                response_style={
                    "tone": "technical",
                    "verbosity": "detailed",
                    "formality": "casual",
                    "code_examples": True,
                },
                preferred_contexts=[ConversationContext.CODING, ConversationContext.DEBUGGING],
                greeting_templates=[
                    "Hey! Ready to dive into some code?",
                    "What programming challenge are we tackling today?",
                    "Let's build something awesome! What's the plan?",
                ],
                expertise_areas=["programming", "debugging", "architecture", "optimization"],
            ),
            PersonaMode.TEACHER: PersonaConfig(
                mode=PersonaMode.TEACHER,
                name="Teacher",
                description="Patient educator who explains concepts clearly",
                traits=["patient", "educational", "encouraging", "thorough"],
                response_style={
                    "tone": "encouraging",
                    "verbosity": "explanatory",
                    "formality": "friendly",
                    "examples": True,
                },
                preferred_contexts=[ConversationContext.LEARNING, ConversationContext.ANALYSIS],
                greeting_templates=[
                    "Welcome to our learning session! What would you like to explore?",
                    "I'm excited to help you learn something new today!",
                    "Let's discover something interesting together!",
                ],
                expertise_areas=["education", "explanation", "concepts", "examples"],
            ),
            PersonaMode.RESEARCHER: PersonaConfig(
                mode=PersonaMode.RESEARCHER,
                name="Researcher",
                description="Analytical and thorough investigator",
                traits=["analytical", "thorough", "methodical", "inquisitive"],
                response_style={
                    "tone": "analytical",
                    "verbosity": "comprehensive",
                    "formality": "academic",
                    "citations": True,
                },
                preferred_contexts=[ConversationContext.ANALYSIS, ConversationContext.PLANNING],
                greeting_templates=[
                    "What shall we investigate today?",
                    "I'm ready to dive deep into research. What's our focus?",
                    "Let's analyze this systematically. Where do we start?",
                ],
                expertise_areas=["research", "analysis", "data", "methodology"],
            ),
            PersonaMode.CREATIVE: PersonaConfig(
                mode=PersonaMode.CREATIVE,
                name="Creative",
                description="Imaginative and innovative thinker",
                traits=["imaginative", "innovative", "expressive", "inspiring"],
                response_style={
                    "tone": "enthusiastic",
                    "verbosity": "expressive",
                    "formality": "casual",
                    "emoji_usage": "moderate",
                },
                preferred_contexts=[
                    ConversationContext.CREATIVE_WORK,
                    ConversationContext.PLANNING,
                ],
                greeting_templates=[
                    "Ready to create something amazing? ✨",
                    "Let's unleash our creativity! What are you envisioning?",
                    "Time to think outside the box! What's your idea?",
                ],
                expertise_areas=["creativity", "innovation", "design", "brainstorming"],
            ),
        }
        return personas

    def _initialize_context_keywords(self) -> Dict[ConversationContext, List[str]]:
        """Initialize keywords for context detection"""
        return {
            ConversationContext.CODING: [
                "code",
                "programming",
                "function",
                "class",
                "debug",
                "algorithm",
                "syntax",
                "variable",
                "loop",
                "api",
            ],
            ConversationContext.LEARNING: [
                "learn",
                "understand",
                "explain",
                "concept",
                "theory",
                "example",
                "tutorial",
                "guide",
                "practice",
                "study",
            ],
            ConversationContext.DEBUGGING: [
                "error",
                "bug",
                "fix",
                "issue",
                "problem",
                "troubleshoot",
                "debug",
                "trace",
                "exception",
                "crash",
            ],
            ConversationContext.PLANNING: [
                "plan",
                "strategy",
                "roadmap",
                "timeline",
                "goals",
                "schedule",
                "organize",
                "structure",
                "framework",
                "approach",
            ],
            ConversationContext.ANALYSIS: [
                "analyze",
                "data",
                "metrics",
                "performance",
                "statistics",
                "evaluate",
                "assess",
                "measure",
                "compare",
                "research",
            ],
            ConversationContext.CREATIVE_WORK: [
                "creative",
                "design",
                "art",
                "innovative",
                "brainstorm",
                "imagine",
                "concept",
                "vision",
                "inspiration",
                "artistic",
            ],
        }

    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile and preferences"""
        profile_file = self.data_dir / "user_profile.json"
        if profile_file.exists():
            try:
                with open(profile_file) as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "preferred_persona": PersonaMode.ASSISTANT.value,
            "communication_style": "balanced",
            "interests": [],
            "expertise_level": "intermediate",
            "interaction_history": {},
        }

    def _save_user_profile(self):
        """Save user profile to disk"""
        profile_file = self.data_dir / "user_profile.json"
        try:
            with open(profile_file, "w") as f:
                json.dump(self.user_profile, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving user profile: {e}")

    def _load_conversation_history(self):
        """Load conversation history from disk"""
        history_file = self.data_dir / "conversation_history.json"
        if history_file.exists():
            try:
                with open(history_file) as f:
                    data = json.load(f)
                    for item in data:
                        memory = ConversationMemory(
                            conversation_id=item["conversation_id"],
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            context=ConversationContext(item["context"]),
                            persona_used=PersonaMode(item["persona_used"]),
                            user_input=item["user_input"],
                            ai_response=item["ai_response"],
                            relevance_score=item["relevance_score"],
                            tags=item["tags"],
                            follow_up_suggestions=item["follow_up_suggestions"],
                            satisfaction_rating=item.get("satisfaction_rating"),
                        )
                        self.conversation_history.append(memory)
            except Exception as e:
                print(f"Error loading conversation history: {e}")

    def _save_conversation_history(self):
        """Save conversation history to disk"""
        history_file = self.data_dir / "conversation_history.json"
        try:
            data = []
            for memory in self.conversation_history[-1000:]:  # Keep last 1000
                item = asdict(memory)
                item["timestamp"] = memory.timestamp.isoformat()
                item["context"] = memory.context.value
                item["persona_used"] = memory.persona_used.value
                data.append(item)

            with open(history_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving conversation history: {e}")

    def detect_context(self, user_input: str) -> ConversationContext:
        """Detect conversation context from user input"""
        input_lower = user_input.lower()
        context_scores = {}

        for context, keywords in self.context_keywords.items():
            score = sum(1 for keyword in keywords if keyword in input_lower)
            if score > 0:
                context_scores[context] = score

        if context_scores:
            # Return context with highest score
            return max(context_scores, key=context_scores.get)

        return ConversationContext.CASUAL

    def select_persona(self, context: ConversationContext, user_input: str) -> PersonaMode:
        """Select appropriate persona based on context and input"""
        if not self.auto_persona_switching:
            return self.current_persona

        # Find personas that prefer this context
        suitable_personas = []
        for persona_mode, config in self.persona_configs.items():
            if context in config.preferred_contexts:
                suitable_personas.append(persona_mode)

        if suitable_personas:
            # Use user's preferred persona if it's suitable
            preferred = PersonaMode(self.user_profile.get("preferred_persona", "assistant"))
            if preferred in suitable_personas:
                return preferred

            # Otherwise, use the first suitable persona
            return suitable_personas[0]

        # Default to assistant
        return PersonaMode.ASSISTANT

    def get_relevant_memory_context(
        self, user_input: str, limit: int = 5
    ) -> List[ConversationMemory]:
        """Get relevant conversation memories for context"""
        if not self.conversation_history:
            return []

        # Simple relevance scoring based on keyword overlap
        input_words = set(user_input.lower().split())
        scored_memories = []

        for memory in self.conversation_history:
            # Score based on input and response content
            memory_words = set((memory.user_input + " " + memory.ai_response).lower().split())
            overlap = len(input_words.intersection(memory_words))

            if overlap > 0:
                # Boost score for recent memories
                recency_boost = 1.0 / (1 + (datetime.now() - memory.timestamp).days)
                score = overlap * (1 + recency_boost)
                scored_memories.append((score, memory))

        # Sort by score and return top memories
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:limit]]

    def generate_response(
        self, user_input: str, force_persona: Optional[PersonaMode] = None
    ) -> Dict[str, Any]:
        """
        Generate a context-aware response with persona and memory integration

        Args:
            user_input: User's input message
            force_persona: Force a specific persona (overrides auto-selection)

        Returns:
            Dictionary containing response and metadata
        """
        # Detect context and select persona
        context = self.detect_context(user_input)
        persona = force_persona or self.select_persona(context, user_input)

        # Get relevant memory context
        relevant_memories = self.get_relevant_memory_context(user_input)

        # Build context for response generation
        response_context = {
            "user_input": user_input,
            "conversation_context": context.value,
            "persona_mode": persona.value,
            "persona_config": asdict(self.persona_configs[persona]),
            "relevant_memories": [
                {"input": m.user_input, "response": m.ai_response, "context": m.context.value}
                for m in relevant_memories
            ],
            "user_profile": self.user_profile,
            "session_info": self._get_session_info(),
        }

        # Generate response (this would integrate with your LLM)
        ai_response = self._generate_contextual_response(response_context)

        # Create conversation memory
        conversation_memory = ConversationMemory(
            conversation_id=f"conv_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            context=context,
            persona_used=persona,
            user_input=user_input,
            ai_response=ai_response,
            relevance_score=0.8,  # Would be calculated by the system
            tags=self._extract_tags(user_input, ai_response),
            follow_up_suggestions=self._generate_follow_ups(user_input, ai_response, context),
        )

        # Store in memory systems
        self.conversation_history.append(conversation_memory)
        if self.current_session:
            self.current_session.conversation_memories.append(conversation_memory)
            self.current_session.last_activity = datetime.now()

        # Store in memory logger
        self.memory_logger.log_memory(
            content=f"Conversation: {user_input[:100]}...",
            category="conversation",
            importance=0.7,
            tags=["conversation", persona.value, context.value],
            metadata={
                "conversation_id": conversation_memory.conversation_id,
                "persona": persona.value,
                "context": context.value,
            },
        )

        # Save periodically
        if len(self.conversation_history) % 10 == 0:
            self._save_conversation_history()

        return {
            "response": ai_response,
            "persona": persona.value,
            "context": context.value,
            "confidence": 0.85,
            "follow_up_suggestions": conversation_memory.follow_up_suggestions,
            "memory_context_used": len(relevant_memories),
            "conversation_id": conversation_memory.conversation_id,
        }

    def _generate_contextual_response(self, context: Dict[str, Any]) -> str:
        """Generate response based on context (placeholder for LLM integration)"""
        persona_config = context["persona_config"]
        persona_name = persona_config["name"]

        # This is a simplified response generator
        # In practice, this would integrate with your LLM system
        greeting = "Hello! "
        if context["relevant_memories"]:
            greeting = "Good to continue our conversation! "

        return f"{greeting}As your {persona_name}, I'm ready to help with {context['conversation_context']}."

    def _extract_tags(self, user_input: str, ai_response: str) -> List[str]:
        """Extract relevant tags from conversation"""
        tags = []
        text = (user_input + " " + ai_response).lower()

        # Simple keyword-based tagging
        if any(word in text for word in ["code", "programming", "function"]):
            tags.append("coding")
        if any(word in text for word in ["learn", "explain", "understand"]):
            tags.append("learning")
        if any(word in text for word in ["error", "bug", "problem"]):
            tags.append("debugging")

        return tags

    def _generate_follow_ups(
        self, user_input: str, ai_response: str, context: ConversationContext
    ) -> List[str]:
        """Generate follow-up suggestions"""
        suggestions = []

        if context == ConversationContext.CODING:
            suggestions = [
                "Would you like to see an example?",
                "Should we test this code?",
                "Any specific optimization concerns?",
            ]
        elif context == ConversationContext.LEARNING:
            suggestions = [
                "Would you like a practical example?",
                "Any specific aspects to explore further?",
                "Ready for the next concept?",
            ]
        else:
            suggestions = [
                "Would you like more details?",
                "Any follow-up questions?",
                "Is there another aspect to consider?",
            ]

        return suggestions[:2]  # Return top 2 suggestions

    def _get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        if not self.current_session:
            return {}

        return {
            "session_id": self.current_session.session_id,
            "duration": (datetime.now() - self.current_session.start_time).seconds,
            "conversation_count": len(self.current_session.conversation_memories),
        }

    def start_new_session(self, initial_context: ConversationContext = ConversationContext.CASUAL):
        """Start a new conversation session"""
        session_id = f"session_{int(time.time())}"
        self.current_session = ConversationSession(
            session_id=session_id,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            persona_mode=self.current_persona,
            context=initial_context,
            conversation_memories=[],
            session_summary="",
            key_topics=[],
            user_preferences=self.user_profile.copy(),
        )

    def end_current_session(self) -> Dict[str, Any]:
        """End current session and generate summary"""
        if not self.current_session:
            return {}

        session = self.current_session
        session_summary = {
            "session_id": session.session_id,
            "duration": (datetime.now() - session.start_time).seconds,
            "conversation_count": len(session.conversation_memories),
            "primary_context": session.context.value,
            "persona_used": session.persona_mode.value,
            "topics_discussed": list(
                set([tag for memory in session.conversation_memories for tag in memory.tags])
            ),
            "satisfaction": self._calculate_session_satisfaction(session),
        }

        self.session_history.append(session)
        self.current_session = None

        return session_summary

    def _calculate_session_satisfaction(self, session: ConversationSession) -> float:
        """Calculate session satisfaction score"""
        if not session.conversation_memories:
            return 0.5

        # Simple heuristic based on conversation length and engagement
        avg_response_length = sum(len(m.ai_response) for m in session.conversation_memories) / len(
            session.conversation_memories
        )

        # Longer, more engaging conversations = higher satisfaction
        satisfaction = min(1.0, avg_response_length / 200)
        return round(satisfaction, 2)

    def set_persona(self, persona: PersonaMode):
        """Manually set the current persona"""
        self.current_persona = persona
        self.user_profile["preferred_persona"] = persona.value
        self._save_user_profile()

    def get_conversation_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of recent conversations"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_conversations = [m for m in self.conversation_history if m.timestamp >= cutoff_date]

        if not recent_conversations:
            return {"message": f"No conversations in the last {days} days"}

        # Analyze conversation patterns
        contexts = {}
        personas = {}

        for conv in recent_conversations:
            context = conv.context.value
            persona = conv.persona_used.value

            contexts[context] = contexts.get(context, 0) + 1
            personas[persona] = personas.get(persona, 0) + 1

        return {
            "period": f"Last {days} days",
            "total_conversations": len(recent_conversations),
            "primary_contexts": sorted(contexts.items(), key=lambda x: x[1], reverse=True),
            "personas_used": sorted(personas.items(), key=lambda x: x[1], reverse=True),
            "avg_conversations_per_day": round(len(recent_conversations) / days, 1),
        }


# Global conversational AI instance
conversational_ai = ConversationalAI()


# Convenience functions
def chat(user_input: str, persona: Optional[str] = None) -> Dict[str, Any]:
    """Simple chat interface"""
    force_persona = PersonaMode(persona) if persona else None
    return conversational_ai.generate_response(user_input, force_persona)


def switch_persona(persona_name: str) -> bool:
    """Switch to a different persona"""
    try:
        persona = PersonaMode(persona_name.lower())
        conversational_ai.set_persona(persona)
        return True
    except ValueError:
        return False


def get_available_personas() -> List[Dict[str, Any]]:
    """Get list of available personas"""
    return [
        {
            "mode": config.mode.value,
            "name": config.name,
            "description": config.description,
            "expertise": config.expertise_areas,
        }
        for config in conversational_ai.persona_configs.values()
    ]
