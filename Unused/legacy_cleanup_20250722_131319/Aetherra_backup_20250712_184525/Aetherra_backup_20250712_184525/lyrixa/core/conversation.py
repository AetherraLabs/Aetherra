#!/usr/bin/env python3
"""
💬 LYRIXA CONVERSATIONAL ENGINE
==============================

Advanced conversational capabilities with personality system,
tone adaptation, multi-turn memory, and emotional intelligence.
"""

import json
import math
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class PersonalityType(Enum):
    DEFAULT = "default"
    MENTOR = "mentor"
    DEV_FOCUSED = "dev_focused"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"


class ToneMode(Enum):
    ADAPTIVE = "adaptive"  # Mirrors user tone
    CONSISTENT = "consistent"  # Maintains personality tone
    ENCOURAGING = "encouraging"
    DIRECT = "direct"
    CASUAL = "casual"
    FORMAL = "formal"


@dataclass
class ConversationState:
    """Current conversation state and context"""

    session_id: str
    turn_count: int
    user_mood: str
    user_expertise_level: str
    current_topic: str
    context_history: List[Dict[str, Any]]
    emotional_state: str
    relationship_stage: str  # new, familiar, trusted


@dataclass
class PersonalityProfile:
    """Defines Lyrixa's personality characteristics"""

    name: str
    description: str
    greeting_style: str
    response_patterns: List[str]
    emotional_traits: List[str]
    expertise_focus: List[str]
    humor_level: float  # 0.0 to 1.0
    curiosity_level: float
    formality_level: float
    encouragement_level: float


# Personality Processor Configuration Classes
@dataclass
class PersonalityConfig:
    """Configuration for personality processor"""
    tone: float = 0.5  # 0.0 = formal, 1.0 = casual
    warmth: float = 0.7  # 0.0 = cold, 1.0 = very warm
    formality: float = 0.4  # 0.0 = very informal, 1.0 = very formal
    verbosity: float = 0.5  # 0.0 = concise, 1.0 = detailed
    metaphor_use: float = 0.3  # 0.0 = literal, 1.0 = metaphorical
    suggestion_strength: float = 0.6  # 0.0 = gentle hints, 1.0 = direct commands
    humor_level: float = 0.3  # 0.0 = serious, 1.0 = playful
    empathy_level: float = 0.8  # 0.0 = analytical, 1.0 = emotionally aware
    curiosity_level: float = 0.7  # 0.0 = direct answers, 1.0 = exploratory


class PersonaMode(Enum):
    """Different persona modes for Lyrixa"""
    GUIDE = "guide"          # Helpful guide through complex topics
    DEVELOPER = "developer"  # Technical coding partner
    SAGE = "sage"           # Wise, philosophical advisor
    FRIEND = "friend"       # Casual, supportive companion
    TEACHER = "teacher"     # Patient, educational mentor
    ANALYST = "analyst"     # Data-driven, logical reasoner
    CREATIVE = "creative"   # Imaginative, artistic collaborator
    SPECIALIST = "specialist" # Domain expert with deep knowledge


@dataclass
class FeedbackData:
    """Stores user feedback for personality learning"""
    timestamp: datetime
    response_id: str
    feedback_type: str  # 'positive', 'negative', 'correction'
    user_comment: Optional[str]
    personality_config_used: PersonalityConfig
    response_effectiveness: float  # 0.0 to 1.0


class PersonalityProcessor:
    """
    🎭 LYRIXA PERSONALITY PROCESSOR
    ==============================

    Advanced personality system that provides:
    - Configurable tone, warmth, and formality
    - Multiple persona modes (Guide, Developer, Sage, etc.)
    - Adaptive verbosity and metaphor use
    - Learning from user feedback
    - Context-aware personality adjustments
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.current_config = PersonalityConfig()
        self.current_persona = PersonaMode.GUIDE
        self.feedback_history: List[FeedbackData] = []
        self.personality_adapters = self._initialize_adapters()
        self.persona_presets = self._initialize_persona_presets()
        self.learned_preferences = {}

        print("🎭 Personality Processor initialized")

    def _initialize_persona_presets(self) -> Dict[PersonaMode, PersonalityConfig]:
        """Initialize personality configurations for different persona modes"""
        return {
            PersonaMode.GUIDE: PersonalityConfig(
                tone=0.6, warmth=0.8, formality=0.4, verbosity=0.6,
                metaphor_use=0.4, suggestion_strength=0.7, humor_level=0.3,
                empathy_level=0.9, curiosity_level=0.8
            ),
            PersonaMode.DEVELOPER: PersonalityConfig(
                tone=0.4, warmth=0.5, formality=0.7, verbosity=0.4,
                metaphor_use=0.1, suggestion_strength=0.8, humor_level=0.2,
                empathy_level=0.4, curiosity_level=0.6
            ),
            PersonaMode.SAGE: PersonalityConfig(
                tone=0.3, warmth=0.7, formality=0.8, verbosity=0.8,
                metaphor_use=0.9, suggestion_strength=0.5, humor_level=0.1,
                empathy_level=0.8, curiosity_level=0.9
            ),
            PersonaMode.FRIEND: PersonalityConfig(
                tone=0.9, warmth=0.9, formality=0.2, verbosity=0.5,
                metaphor_use=0.3, suggestion_strength=0.4, humor_level=0.7,
                empathy_level=0.9, curiosity_level=0.7
            ),
            PersonaMode.TEACHER: PersonalityConfig(
                tone=0.5, warmth=0.8, formality=0.6, verbosity=0.7,
                metaphor_use=0.5, suggestion_strength=0.6, humor_level=0.3,
                empathy_level=0.8, curiosity_level=0.8
            ),
            PersonaMode.ANALYST: PersonalityConfig(
                tone=0.3, warmth=0.4, formality=0.8, verbosity=0.6,
                metaphor_use=0.1, suggestion_strength=0.9, humor_level=0.1,
                empathy_level=0.3, curiosity_level=0.5
            ),
            PersonaMode.CREATIVE: PersonalityConfig(
                tone=0.8, warmth=0.7, formality=0.3, verbosity=0.7,
                metaphor_use=0.9, suggestion_strength=0.5, humor_level=0.8,
                empathy_level=0.7, curiosity_level=0.9
            ),
            PersonaMode.SPECIALIST: PersonalityConfig(
                tone=0.4, warmth=0.6, formality=0.7, verbosity=0.8,
                metaphor_use=0.2, suggestion_strength=0.8, humor_level=0.2,
                empathy_level=0.5, curiosity_level=0.7
            )
        }

    def _initialize_adapters(self) -> Dict[str, Callable]:
        """Initialize personality adaptation functions"""
        return {
            'tone_adapter': self._adapt_tone,
            'warmth_adapter': self._adapt_warmth,
            'formality_adapter': self._adapt_formality,
            'verbosity_adapter': self._adapt_verbosity,
            'metaphor_adapter': self._adapt_metaphors,
            'suggestion_adapter': self._adapt_suggestions,
            'humor_adapter': self._adapt_humor,
            'empathy_adapter': self._adapt_empathy
        }

    def set_persona_mode(self, persona: PersonaMode) -> None:
        """Switch to a specific persona mode with its preset configuration"""
        self.current_persona = persona
        self.current_config = self.persona_presets[persona]
        print(f"🎭 Switched to {persona.value} persona")

    def adjust_personality(self, **kwargs) -> None:
        """Fine-tune personality parameters"""
        for param, value in kwargs.items():
            if hasattr(self.current_config, param):
                setattr(self.current_config, param, max(0.0, min(1.0, value)))
                print(f"🎛️ Adjusted {param} to {value}")

    async def process_response(self, base_response: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Apply personality processing to a base response"""
        if not base_response:
            return base_response

        response = base_response

        # Apply all personality adapters in sequence
        for adapter_name, adapter_func in self.personality_adapters.items():
            try:
                response = adapter_func(response, context or {})
            except Exception as e:
                print(f"[WARN] Error in {adapter_name}: {e}")

        # Apply learned preferences
        response = self._apply_learned_preferences(response, context or {})

        return response

    def _adapt_tone(self, response: str, context: Dict[str, Any]) -> str:
        """Adapt response tone (formal to casual)"""
        tone = self.current_config.tone

        if tone > 0.7:  # Casual tone
            # Make more casual
            response = response.replace("I would suggest", "I'd say")
            response = response.replace("It is", "It's")
            response = response.replace("You might want to", "You could")
            response = response.replace("However,", "But")

            # Add casual interjections
            if random.random() < 0.3:
                casual_starters = ["So, ", "Well, ", "Actually, ", "You know, "]
                response = random.choice(casual_starters) + response.lstrip()

        elif tone < 0.3:  # Formal tone
            # Make more formal
            response = response.replace("don't", "do not")
            response = response.replace("can't", "cannot")
            response = response.replace("won't", "will not")
            response = response.replace("I'd", "I would")

        return response

    def _adapt_warmth(self, response: str, context: Dict[str, Any]) -> str:
        """Adapt response warmth (cold to warm)"""
        warmth = self.current_config.warmth

        if warmth > 0.7:  # High warmth
            warm_starters = [
                "I'm happy to help! ",
                "I'd love to assist! ",
                "Great question! ",
                "I'm excited to explore this with you! "
            ]
            if random.random() < 0.4:
                response = random.choice(warm_starters) + response

            # Add warm endings
            warm_endings = [
                " I hope this helps!",
                " Feel free to ask if you need more!",
                " I'm here if you have questions!",
                " Let me know how it goes!"
            ]
            if random.random() < 0.3:
                response += random.choice(warm_endings)

        elif warmth < 0.3:  # Low warmth
            # Remove excessive warmth markers
            response = response.replace("exciting", "interesting")
            response = response.replace("amazing", "notable")
            response = response.replace("I love", "I find")

        return response

    def _adapt_formality(self, response: str, context: Dict[str, Any]) -> str:
        """Adapt response formality level"""
        formality = self.current_config.formality

        if formality > 0.7:  # High formality
            # Add formal structure
            if not response.startswith(("To", "In order to", "With regard to")):
                formal_starters = [
                    "To address your question: ",
                    "In response to your inquiry: ",
                    "Allow me to explain: "
                ]
                if random.random() < 0.4:
                    response = random.choice(formal_starters) + response

        elif formality < 0.3:  # Low formality
            # Remove formal language
            response = response.replace("Furthermore,", "Also,")
            response = response.replace("Therefore,", "So,")
            response = response.replace("In conclusion,", "In short,")

        return response

    def _adapt_verbosity(self, response: str, context: Dict[str, Any]) -> str:
        """Adapt response verbosity (concise to detailed)"""
        verbosity = self.current_config.verbosity

        if verbosity > 0.7:  # High verbosity
            # Add explanatory details
            if "because" not in response.lower() and random.random() < 0.4:
                explanations = [
                    " This is important because it affects the overall system design.",
                    " This approach works well because it maintains flexibility.",
                    " The reason this matters is that it impacts user experience."
                ]
                response += random.choice(explanations)

        elif verbosity < 0.3:  # Low verbosity
            # Make more concise
            response = response.replace("In order to", "To")
            response = response.replace("It is important to note that", "Note:")
            response = response.replace("As you can see,", "")

        return response

    def _adapt_metaphors(self, response: str, context: Dict[str, Any]) -> str:
        """Add or reduce metaphorical language"""
        metaphor_use = self.current_config.metaphor_use

        if metaphor_use > 0.6:  # High metaphor use
            # Add metaphors to technical concepts
            metaphor_mappings = {
                "code": "digital blueprint",
                "function": "tool in your toolkit",
                "data": "information flowing like a river",
                "system": "digital ecosystem",
                "error": "roadblock on your path"
            }

            for term, metaphor in metaphor_mappings.items():
                if term in response.lower() and random.random() < 0.3:
                    response = response.replace(term, f"{term} (like a {metaphor})")

        return response

    def _adapt_suggestions(self, response: str, context: Dict[str, Any]) -> str:
        """Adapt suggestion strength (gentle hints to direct commands)"""
        strength = self.current_config.suggestion_strength

        if strength > 0.7:  # Strong suggestions
            # Make suggestions more direct
            response = response.replace("you might want to", "you should")
            response = response.replace("consider", "implement")
            response = response.replace("it would be good to", "you must")

        elif strength < 0.3:  # Gentle suggestions
            # Make suggestions softer
            response = response.replace("you should", "you might consider")
            response = response.replace("you must", "it could be helpful to")
            response = response.replace("implement", "perhaps try")

        return response

    def _adapt_humor(self, response: str, context: Dict[str, Any]) -> str:
        """Add appropriate humor based on configuration"""
        humor = self.current_config.humor_level

        if humor > 0.6 and random.random() < 0.2:  # Add light humor
            humor_additions = [
                " 😊", " 🎯", " ✨", " (and that's pretty cool!)",
                " (I love these kinds of challenges!)"
            ]
            response += random.choice(humor_additions)

        return response

    def _adapt_empathy(self, response: str, context: Dict[str, Any]) -> str:
        """Add empathetic understanding based on user context"""
        empathy = self.current_config.empathy_level

        if empathy > 0.7:
            # Detect if user seems frustrated or confused
            user_mood = context.get('user_mood', 'neutral')
            if user_mood in ['frustrated', 'confused', 'stuck']:
                empathetic_starters = [
                    "I understand this can be frustrating. ",
                    "I can see why this might be confusing. ",
                    "It's completely normal to feel stuck here. "
                ]
                response = random.choice(empathetic_starters) + response

        return response

    def _apply_learned_preferences(self, response: str, context: Dict[str, Any]) -> str:
        """Apply learned user preferences from feedback"""
        # Apply any learned preferences (future enhancement)
        # This would use the feedback_history to adjust responses
        return response

    async def record_feedback(self, response_id: str, feedback_type: str,
                            user_comment: Optional[str] = None,
                            effectiveness: float = 0.5) -> None:
        """Record user feedback for learning"""
        feedback = FeedbackData(
            timestamp=datetime.now(),
            response_id=response_id,
            feedback_type=feedback_type,
            user_comment=user_comment,
            personality_config_used=self.current_config,
            response_effectiveness=effectiveness
        )

        self.feedback_history.append(feedback)

        # Learn from feedback
        await self._learn_from_feedback(feedback)

        # Store in memory system if available
        if self.memory_system:
            try:
                await self.memory_system.store_memory(
                    content=f"Personality feedback: {feedback_type} for {self.current_persona.value}",
                    memory_type="personality_feedback",
                    tags=["feedback", "personality", feedback_type],
                    confidence=effectiveness,
                    context={
                        "persona": self.current_persona.value,
                        "config": self.current_config.__dict__,
                        "feedback": feedback.__dict__
                    }
                )
            except Exception as e:
                print(f"[WARN] Error storing personality feedback: {e}")

    async def _learn_from_feedback(self, feedback: FeedbackData) -> None:
        """Learn and adapt from user feedback"""
        if feedback.feedback_type == 'positive' and feedback.response_effectiveness > 0.7:
            # Reinforce current configuration
            print(f"✅ Positive feedback for {self.current_persona.value} persona")

        elif feedback.feedback_type == 'negative' and feedback.response_effectiveness < 0.3:
            # Adjust configuration based on negative feedback
            print(f"📈 Learning from negative feedback for {self.current_persona.value} persona")

            # Example: If response was too formal, reduce formality
            if "too formal" in (feedback.user_comment or "").lower():
                self.current_config.formality = max(0.0, self.current_config.formality - 0.1)

            elif "too casual" in (feedback.user_comment or "").lower():
                self.current_config.formality = min(1.0, self.current_config.formality + 0.1)

    def get_personality_status(self) -> Dict[str, Any]:
        """Get current personality processor status"""
        return {
            "current_persona": self.current_persona.value,
            "config": self.current_config.__dict__,
            "feedback_count": len(self.feedback_history),
            "recent_feedback": [f.feedback_type for f in self.feedback_history[-5:]],
            "available_personas": [p.value for p in PersonaMode]
        }

    def export_personality_profile(self) -> str:
        """Export current personality configuration as JSON"""
        profile = {
            "persona": self.current_persona.value,
            "config": self.current_config.__dict__,
            "learned_preferences": self.learned_preferences,
            "feedback_summary": {
                "total_feedback": len(self.feedback_history),
                "positive_feedback": len([f for f in self.feedback_history if f.feedback_type == 'positive']),
                "negative_feedback": len([f for f in self.feedback_history if f.feedback_type == 'negative'])
            }
        }
        return json.dumps(profile, indent=2)

    def import_personality_profile(self, profile_json: str) -> bool:
        """Import personality configuration from JSON"""
        try:
            profile = json.loads(profile_json)

            # Set persona
            persona_name = profile.get('persona', 'guide')
            for persona in PersonaMode:
                if persona.value == persona_name:
                    self.current_persona = persona
                    break

            # Set configuration
            config_data = profile.get('config', {})
            for attr, value in config_data.items():
                if hasattr(self.current_config, attr):
                    setattr(self.current_config, attr, value)

            # Set learned preferences
            self.learned_preferences = profile.get('learned_preferences', {})

            print(f"✅ Imported personality profile: {persona_name}")
            return True

        except Exception as e:
            print(f"[WARN] Error importing personality profile: {e}")
            return False


class LyrixaConversationalEngine:
    """
    Advanced conversational engine for Lyrixa

    Provides natural, context-aware conversations with personality adaptation,
    emotional intelligence, and relationship building over time.
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.conversation_state = None
        self.current_personality = PersonalityType.DEFAULT
        self.tone_mode = ToneMode.ADAPTIVE

        # Initialize personality profiles
        self.personalities = self._initialize_personalities()

        # Initialize Personality Processor
        self.personality_processor = PersonalityProcessor(memory_system)

        # Conversation tracking
        self.relationship_history = {}
        self.topic_expertise = {}
        self.emotional_patterns = {}

        # Initialize Project Knowledge Responder
        self.knowledge_responder = None
        if self.memory_system:
            self._initialize_knowledge_responder()

        print("💬 Lyrixa Conversational Engine initialized with Personality Processor")

    def _initialize_personalities(self) -> Dict[PersonalityType, PersonalityProfile]:
        """Initialize different personality profiles for Lyrixa"""
        return {
            PersonalityType.DEFAULT: PersonalityProfile(
                name="Lyrixa",
                description="Intelligent, curious, and helpful AI assistant",
                greeting_style="warm_professional",
                response_patterns=[
                    "I'd love to help you with {topic}!",
                    "That's an interesting question about {topic}.",
                    "Let me think about {topic} for a moment...",
                ],
                emotional_traits=["curious", "helpful", "encouraging", "thoughtful"],
                expertise_focus=["aetherra", "coding", "problem-solving"],
                humor_level=0.3,
                curiosity_level=0.8,
                formality_level=0.4,
                encouragement_level=0.7,
            ),
            PersonalityType.MENTOR: PersonalityProfile(
                name="Lyrixa (Mentor Mode)",
                description="Wise, patient teacher focused on learning and growth",
                greeting_style="wise_encouraging",
                response_patterns=[
                    "Great question! Let's explore {topic} step by step.",
                    "I see you're working on {topic}. Here's how I'd approach it...",
                    "You're making excellent progress with {topic}!",
                ],
                emotional_traits=["patient", "wise", "encouraging", "supportive"],
                expertise_focus=["teaching", "best-practices", "learning-paths"],
                humor_level=0.2,
                curiosity_level=0.6,
                formality_level=0.6,
                encouragement_level=0.9,
            ),
            PersonalityType.DEV_FOCUSED: PersonalityProfile(
                name="Lyrixa (Developer Mode)",
                description="Technical, precise, and efficiency-focused",
                greeting_style="direct_technical",
                response_patterns=[
                    "Let's optimize {topic} for better performance.",
                    "Here's the most efficient approach to {topic}:",
                    "I notice a pattern in your {topic} usage...",
                ],
                emotional_traits=["analytical", "precise", "efficient", "logical"],
                expertise_focus=["optimization", "debugging", "architecture"],
                humor_level=0.1,
                curiosity_level=0.7,
                formality_level=0.8,
                encouragement_level=0.4,
            ),
            PersonalityType.CREATIVE: PersonalityProfile(
                name="Lyrixa (Creative Mode)",
                description="Imaginative, experimental, and innovation-focused",
                greeting_style="enthusiastic_creative",
                response_patterns=[
                    "What if we approach {topic} from a completely different angle?",
                    "I have some wild ideas for {topic}!",
                    "Let's experiment with {topic} and see what happens!",
                ],
                emotional_traits=[
                    "imaginative",
                    "experimental",
                    "playful",
                    "innovative",
                ],
                expertise_focus=["creative-solutions", "experimentation", "innovation"],
                humor_level=0.6,
                curiosity_level=0.9,
                formality_level=0.2,
                encouragement_level=0.8,
            ),
        }

    async def initialize_conversation(
        self, session_id: str, user_context: Optional[Dict[str, Any]] = None
    ) -> ConversationState:
        """Initialize a new conversation session"""

        # Load previous relationship data if available
        if self.memory_system:
            try:
                relationship_memories = await self.memory_system.semantic_search(
                    f"relationship {session_id}", top_k=5
                )
                relationship_stage = "familiar" if relationship_memories else "new"
            except Exception as e:
                print(f"[WARN] Error loading relationship data: {e}")
                relationship_stage = "new"
        else:
            relationship_stage = "new"

        self.conversation_state = ConversationState(
            session_id=session_id,
            turn_count=0,
            user_mood="neutral",
            user_expertise_level="intermediate",
            current_topic="general",
            context_history=[],
            emotional_state="attentive",
            relationship_stage=relationship_stage,
        )

        return self.conversation_state

    async def process_conversation_turn(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a single conversation turn with full emotional and contextual awareness"""

        if not self.conversation_state:
            await self.initialize_conversation("default_session")

        # Type assertion: conversation_state is guaranteed to be not None after initialization
        assert self.conversation_state is not None

        # Analyze user input for mood, tone, expertise
        user_analysis = self._analyze_user_input(user_input)

        # Update conversation state
        self.conversation_state.turn_count += 1
        self.conversation_state.user_mood = user_analysis["mood"]
        self.conversation_state.current_topic = user_analysis["topic"]

        # Generate contextual response
        response = await self._generate_contextual_response(
            user_input, user_analysis, context
        )

        # Store conversation turn
        turn_data = {
            "turn": self.conversation_state.turn_count,
            "user_input": user_input,
            "user_analysis": user_analysis,
            "lyrixa_response": response["text"],
            "emotional_state": self.conversation_state.emotional_state,
            "timestamp": datetime.now().isoformat(),
        }

        self.conversation_state.context_history.append(turn_data)

        # Keep only recent history
        if len(self.conversation_state.context_history) > 20:
            self.conversation_state.context_history = (
                self.conversation_state.context_history[-20:]
            )

        # Store in memory system
        if self.memory_system:
            try:
                # Convert conversation data to string for storage
                memory_content = f"Conversation turn {turn_data['turn']}: User said '{user_input}', Lyrixa responded with context from {self.current_personality.value} personality."

                await self.memory_system.store_memory(
                    content=memory_content,
                    memory_type="conversation",
                    tags=["conversation", "relationship", user_analysis["mood"]],
                    confidence=0.6 if user_analysis["engagement"] > 0.7 else 0.4,
                    context={
                        "session_id": self.conversation_state.session_id,
                        "personality": self.current_personality.value,
                        "turn_data": turn_data,
                    },
                )
            except Exception as e:
                print(f"[WARN] Error storing conversation memory: {e}")

        return response

    def _analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input for mood, tone, expertise level, and engagement"""

        # Simple analysis - in production this would use more sophisticated NLP
        analysis = {
            "mood": "neutral",
            "tone": "neutral",
            "expertise_level": "intermediate",
            "engagement": 0.5,
            "topic": "general",
            "intent_urgency": 0.5,
            "question_complexity": 0.5,
            "preferences": {},
        }

        user_lower = user_input.lower()

        # Mood detection
        positive_words = ["great", "awesome", "love", "excited", "happy", "amazing"]
        negative_words = [
            "frustrated",
            "stuck",
            "confused",
            "error",
            "broken",
            "problem",
        ]
        urgent_words = [
            "urgent",
            "asap",
            "quickly",
            "emergency",
            "critical",
            "immediately",
        ]

        if any(word in user_lower for word in positive_words):
            analysis["mood"] = "positive"
            analysis["engagement"] = 0.8
        elif any(word in user_lower for word in negative_words):
            analysis["mood"] = "frustrated"
            analysis["engagement"] = 0.6

        if any(word in user_lower for word in urgent_words):
            analysis["intent_urgency"] = 0.9

        # Topic detection
        topics = {
            "coding": ["code", "function", "class", "debug", "error", "programming"],
            "aetherra": ["aether", ".aether", "workflow", "goal", "plugin"],
            "memory": ["remember", "recall", "memory", "save", "store"],
            "help": ["help", "how", "what", "explain", "teach", "learn"],
        }

        for topic, keywords in topics.items():
            if any(keyword in user_lower for keyword in keywords):
                analysis["topic"] = topic
                break

        # Expertise detection
        advanced_words = [
            "optimize",
            "architecture",
            "performance",
            "scalable",
            "refactor",
        ]
        beginner_words = ["how do i", "what is", "explain", "basic", "simple", "start"]

        if any(word in user_lower for word in advanced_words):
            analysis["expertise_level"] = "advanced"
        elif any(phrase in user_lower for phrase in beginner_words):
            analysis["expertise_level"] = "beginner"

        return analysis

    async def _generate_contextual_response(
        self,
        user_input: str,
        user_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a contextual response based on personality, mood, and conversation state"""

        # Ensure conversation state exists
        if not self.conversation_state:
            await self.initialize_conversation("default_session")

        # Type assertion: conversation_state is guaranteed to be not None after initialization
        assert self.conversation_state is not None

        personality = self.personalities[self.current_personality]

        # Base response structure
        response = {
            "text": "",
            "emotional_tone": self.conversation_state.emotional_state,
            "suggestions": [],
            "follow_up_questions": [],
            "personality_used": self.current_personality.value,
            "adaptation_notes": [],
        }

        # 🧠 KNOWLEDGE RESPONDER ROUTING - Check if this is a factual/project query
        if (
            self.knowledge_responder
            and self.knowledge_responder.is_factual_or_project_query(user_input)
        ):
            try:
                knowledge_answer = await self.knowledge_responder.answer_question(
                    user_input
                )
                if (
                    knowledge_answer
                    and knowledge_answer
                    != "I'm still learning, but I don't have an answer to that yet."
                ):
                    # Use knowledge responder answer with personality touch
                    response["text"] = self._add_personality_to_knowledge_response(
                        knowledge_answer, personality
                    )
                    response["adaptation_notes"].append(
                        "Used Project Knowledge Responder"
                    )
                    return response
            except Exception as e:
                print(f"   [WARN] Knowledge Responder error: {e}")
                # Fall through to normal conversation flow

        # Adapt emotional state based on user mood
        if user_analysis["mood"] == "frustrated":
            self.conversation_state.emotional_state = "supportive"
            response["emotional_tone"] = "supportive"
        elif user_analysis["mood"] == "positive":
            self.conversation_state.emotional_state = "enthusiastic"
            response["emotional_tone"] = "enthusiastic"

        # Generate appropriate response based on personality and context
        response_template = random.choice(personality.response_patterns)

        # Customize response based on context
        topic = user_analysis["topic"]
        if topic == "aetherra":
            base_text = f"I love working with .aether code! {response_template.format(topic=topic)} "
        elif topic == "coding":
            base_text = f"Let's dive into some code! {response_template.format(topic=topic)} "
        elif user_analysis["mood"] == "frustrated":
            base_text = "I can sense you're having a tough time. Don't worry, we'll figure this out together! "
        else:
            base_text = response_template.format(topic=topic)

        # 🎭 APPLY PERSONALITY PROCESSOR - Process the base response through personality system
        try:
            personality_context = {
                "user_mood": user_analysis["mood"],
                "topic": topic,
                "conversation_turn": self.conversation_state.turn_count,
                "relationship_stage": self.conversation_state.relationship_stage,
                "user_analysis": user_analysis
            }

            processed_text = await self.personality_processor.process_response(
                base_text, personality_context
            )
            response["text"] = processed_text
            response["adaptation_notes"].append("Applied Personality Processor")

        except Exception as e:
            print(f"[WARN] Personality Processor error: {e}")
            response["text"] = base_text  # Fallback to base text

        # Add personality-specific touches (legacy support)
        if personality.humor_level > 0.5 and random.random() < 0.3:
            humor_additions = [
                "😄",
                "🎉",
                "(and yes, I just made a coding joke!)",
                "Fun fact: I dream in .aether code! 🌙",
            ]
            response["text"] += f" {random.choice(humor_additions)}"

        # Add curiosity-driven follow-ups
        if personality.curiosity_level > 0.7 and random.random() < 0.4:
            curiosity_questions = [
                "What inspired you to work on this?",
                "Have you tried a similar approach before?",
                "What's the most challenging part of this for you?",
                "I'm curious - what's your end goal here?",
            ]
            response["follow_up_questions"].append(random.choice(curiosity_questions))

        # Add encouragement if needed
        if (
            user_analysis["mood"] == "frustrated"
            or personality.encouragement_level > 0.7
        ):
            encouragement = [
                "You're doing great!",
                "This is exactly the kind of problem I love solving!",
                "I believe in your approach here.",
                "You're asking all the right questions!",
            ]
            response["text"] += f" {random.choice(encouragement)}"

        return response

    def switch_personality(self, personality_type: PersonalityType) -> bool:
        """Switch Lyrixa's personality mode"""
        if personality_type in self.personalities:
            self.current_personality = personality_type
            print(f"💬 Switched to {personality_type.value} personality")
            return True
        return False

    def set_tone_mode(self, tone_mode: ToneMode):
        """Set how Lyrixa adapts her tone"""
        self.tone_mode = tone_mode
        print(f"💬 Tone mode set to {tone_mode.value}")

    # Personality Processor Integration Methods
    def set_persona_mode(self, persona: PersonaMode) -> None:
        """Switch to a specific persona mode"""
        self.personality_processor.set_persona_mode(persona)
        print(f"🎭 Conversation Engine using {persona.value} persona")

    def adjust_personality_settings(self, **kwargs) -> None:
        """Adjust personality processor settings"""
        self.personality_processor.adjust_personality(**kwargs)

    async def record_personality_feedback(self, response_id: str, feedback_type: str,
                                        user_comment: Optional[str] = None,
                                        effectiveness: float = 0.5) -> None:
        """Record feedback for personality learning"""
        await self.personality_processor.record_feedback(
            response_id, feedback_type, user_comment, effectiveness
        )

    def get_personality_status(self) -> Dict[str, Any]:
        """Get current personality configuration status"""
        return {
            "conversation_engine": {
                "current_personality": self.current_personality.value,
                "tone_mode": self.tone_mode.value
            },
            "personality_processor": self.personality_processor.get_personality_status()
        }

    def export_personality_profile(self) -> str:
        """Export current personality configuration"""
        return self.personality_processor.export_personality_profile()

    def import_personality_profile(self, profile_json: str) -> bool:
        """Import personality configuration"""
        return self.personality_processor.import_personality_profile(profile_json)

    async def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        if not self.conversation_state:
            return {"status": "no_active_conversation"}

        return {
            "session_id": self.conversation_state.session_id,
            "turn_count": self.conversation_state.turn_count,
            "current_topic": self.conversation_state.current_topic,
            "user_mood": self.conversation_state.user_mood,
            "emotional_state": self.conversation_state.emotional_state,
            "relationship_stage": self.conversation_state.relationship_stage,
            "personality": self.current_personality.value,
            "recent_topics": list(
                set(
                    [
                        turn.get("user_analysis", {}).get("topic", "general")
                        for turn in self.conversation_state.context_history[-5:]
                    ]
                )
            ),
            "conversation_health": "healthy"
            if self.conversation_state.turn_count > 0
            else "new",
        }

    async def reflect_on_conversation(self) -> Dict[str, Any]:
        """Self-reflection on conversation patterns and learning"""
        if not self.conversation_state:
            return {"reflection": "No conversation to reflect on yet."}

        reflection = {
            "patterns_noticed": [],
            "user_preferences_learned": {},
            "conversation_flow": "good",
            "areas_for_improvement": [],
            "emotional_insights": {},
            "next_suggestions": [],
        }

        # Analyze conversation patterns
        if self.conversation_state.turn_count > 3:
            topics = [
                turn.get("user_analysis", {}).get("topic", "general")
                for turn in self.conversation_state.context_history
            ]
            most_common_topic = max(set(topics), key=topics.count)
            reflection["patterns_noticed"].append(
                f"User is most interested in {most_common_topic}"
            )

        if self.conversation_state.user_mood != "neutral":
            reflection["emotional_insights"]["dominant_mood"] = (
                self.conversation_state.user_mood
            )

        # Generate suggestions for next interaction
        reflection["next_suggestions"] = [
            "Ask about their progress on current projects",
            "Offer to explain any .aether concepts they're curious about",
            "Check if they need help with plugin development",
        ]

        return reflection

    def _add_personality_to_knowledge_response(
        self, knowledge_answer: str, personality
    ) -> str:
        """Add personality touches to a knowledge responder answer"""

        # Add personality-appropriate intro/outro based on available attributes
        if (
            hasattr(personality, "formality_level")
            and personality.formality_level < 0.5
        ):
            intros = [
                "Here's what I know about that: ",
                "Great question! ",
                "I'm happy to help with that! ",
                "Let me share what I've learned: ",
            ]
            knowledge_answer = random.choice(intros) + knowledge_answer

        # Add encouraging touches based on personality
        if (
            hasattr(personality, "encouragement_level")
            and personality.encouragement_level > 0.6
        ):
            outros = [
                " Hope this helps!",
                " Let me know if you need more details!",
                " Feel free to ask if anything needs clarification!",
            ]
            knowledge_answer += random.choice(outros)

        # Add humor based on personality
        if (
            hasattr(personality, "humor_level")
            and personality.humor_level > 0.5
            and random.random() < 0.2
        ):
            humor_additions = [
                " 😊",
                " (I love these kinds of questions!)",
                " 🎯",
            ]
            knowledge_answer += random.choice(humor_additions)

        return knowledge_answer

    def _initialize_knowledge_responder(self):
        """Initialize the Project Knowledge Responder for factual queries."""
        try:
            if not self.memory_system:
                print("   [WARN] No memory system available for Knowledge Responder")
                return

            from .project_knowledge_responder import ProjectKnowledgeResponder

            self.knowledge_responder = ProjectKnowledgeResponder(self.memory_system)
            print("   ✅ Project Knowledge Responder integrated")
        except ImportError as e:
            print(f"   [WARN] Could not load Project Knowledge Responder: {e}")
            self.knowledge_responder = None


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_conversation():
        engine = LyrixaConversationalEngine()

        # Initialize conversation
        await engine.initialize_conversation("test_session")

        # Test different personas
        print("🎭 Testing different personas...\n")

        # Test Guide persona
        engine.set_persona_mode(PersonaMode.GUIDE)
        response = await engine.process_conversation_turn("How do I get started with .aether code?")
        print(f"👤 User: How do I get started with .aether code?")
        print(f"🎙️ Lyrixa (Guide): {response['text']}\n")

        # Test Developer persona
        engine.set_persona_mode(PersonaMode.DEVELOPER)
        response = await engine.process_conversation_turn("This code is throwing errors")
        print(f"👤 User: This code is throwing errors")
        print(f"🎙️ Lyrixa (Developer): {response['text']}\n")

        # Test Creative persona
        engine.set_persona_mode(PersonaMode.CREATIVE)
        response = await engine.process_conversation_turn("I want to build something unique")
        print(f"👤 User: I want to build something unique")
        print(f"🎙️ Lyrixa (Creative): {response['text']}\n")

        # Test personality adjustments
        print("🎛️ Testing personality adjustments...\n")
        engine.adjust_personality_settings(warmth=0.9, humor_level=0.7, formality=0.2)
        response = await engine.process_conversation_turn("Tell me about .aether architecture")
        print(f"👤 User: Tell me about .aether architecture")
        print(f"🎙️ Lyrixa (Adjusted): {response['text']}\n")

        # Test formal settings
        engine.adjust_personality_settings(warmth=0.3, humor_level=0.1, formality=0.9)
        response = await engine.process_conversation_turn("What are best practices for coding?")
        print(f"👤 User: What are best practices for coding?")
        print(f"🎙️ Lyrixa (Formal): {response['text']}\n")

        # Get personality status
        status = engine.get_personality_status()
        print(f"📊 Personality Status: {status}\n")

        # Test feedback recording
        await engine.record_personality_feedback("test_response_1", "positive", "Great explanation!", 0.9)
        print("✅ Recorded positive feedback\n")

        # Export personality profile
        profile = engine.export_personality_profile()
        print(f"💾 Exported Profile: {profile[:100]}...\n")

        # Get conversation summary
        summary = await engine.get_conversation_summary()
        print(f"📊 Conversation Summary: {summary}")

    asyncio.run(test_conversation())
