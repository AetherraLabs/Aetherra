#!/usr/bin/env python3
"""
💬 LYRIXA CONVERSATIONAL ENGINE
==============================

Advanced conversational capabilities with personality system,
tone adaptation, multi-turn memory, and emotional intelligence.
"""

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


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

        # Conversation tracking
        self.relationship_history = {}
        self.topic_expertise = {}
        self.emotional_patterns = {}

        # Initialize Project Knowledge Responder
        self.knowledge_responder = None
        if self.memory_system:
            self._initialize_knowledge_responder()

        print("💬 Lyrixa Conversational Engine initialized")

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
                print(f"⚠️ Error loading relationship data: {e}")
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
                print(f"⚠️ Error storing conversation memory: {e}")

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
                print(f"   ⚠️ Knowledge Responder error: {e}")
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
            response["text"] = (
                f"I love working with .aether code! {response_template.format(topic=topic)} "
            )
        elif topic == "coding":
            response["text"] = (
                f"Let's dive into some code! {response_template.format(topic=topic)} "
            )
        elif user_analysis["mood"] == "frustrated":
            response["text"] = (
                "I can sense you're having a tough time. Don't worry, we'll figure this out together! "
            )
        else:
            response["text"] = response_template.format(topic=topic)

        # Add personality-specific touches
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
                print("   ⚠️ No memory system available for Knowledge Responder")
                return

            from .project_knowledge_responder import ProjectKnowledgeResponder

            self.knowledge_responder = ProjectKnowledgeResponder(self.memory_system)
            print("   ✅ Project Knowledge Responder integrated")
        except ImportError as e:
            print(f"   ⚠️ Could not load Project Knowledge Responder: {e}")
            self.knowledge_responder = None


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_conversation():
        engine = LyrixaConversationalEngine()

        # Initialize conversation
        await engine.initialize_conversation("test_session")

        # Test different inputs
        test_inputs = [
            "Hi Lyrixa! I'm excited to learn about .aether code!",
            "I'm really frustrated with this bug in my code",
            "Can you help me optimize this function?",
            "What's the best way to structure an .aether project?",
        ]

        for user_input in test_inputs:
            print(f"\n👤 User: {user_input}")
            response = await engine.process_conversation_turn(user_input)
            print(f"🎙️ Lyrixa: {response['text']}")
            if response.get("follow_up_questions"):
                print(f"🤔 Follow-up: {response['follow_up_questions'][0]}")

        # Test personality switching
        engine.switch_personality(PersonalityType.MENTOR)
        response = await engine.process_conversation_turn(
            "I want to learn advanced .aether patterns"
        )
        print(f"\n🎙️ Lyrixa (Mentor): {response['text']}")

        # Get conversation summary
        summary = await engine.get_conversation_summary()
        print(f"\n📊 Conversation Summary: {summary}")

        # Self-reflection
        reflection = await engine.reflect_on_conversation()
        print(f"\n🧠 Self-Reflection: {reflection}")

    asyncio.run(test_conversation())
