#!/usr/bin/env python3
"""
🎯 LYRIXA KNOWLEDGE RESPONSE SYNTHESIZER
=======================================

Advanced response synthesis with memory integration, personality adaptation,
and context-aware knowledge retrieval.

Features:
- Vector-based memory search and retrieval
- Personality-driven response generation
- Context-aware tone adaptation
- Multi-turn conversation continuity
- Confidence-based response quality
- Cross-phase communication integration
"""

import asyncio
import json
import logging
import random
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import Lyrixa core components
try:
    from ..gui.unified.context_bridge import ContextBridge, EventType
    from .advanced_vector_memory import AdvancedMemorySystem
    from .conversation import ConversationState, PersonalityType, ToneMode
except ImportError:
    # Fallback imports for standalone testing
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
    from lyrixa.core.conversation import ConversationState, PersonalityType, ToneMode
    from lyrixa.gui.unified.context_bridge import ContextBridge, EventType

# Setup logging
logger = logging.getLogger(__name__)


class ResponseQuality(Enum):
    """Response quality levels based on memory confidence."""

    EXCELLENT = "excellent"  # 0.8+ confidence
    GOOD = "good"  # 0.6-0.8 confidence
    MODERATE = "moderate"  # 0.4-0.6 confidence
    UNCERTAIN = "uncertain"  # 0.2-0.4 confidence
    UNKNOWN = "unknown"  # <0.2 confidence


@dataclass
class ResponseContext:
    """Context information for response generation."""

    user_input: str
    conversation_state: Optional[ConversationState]
    personality: PersonalityType
    tone_mode: ToneMode
    retrieved_memories: List[Dict[str, Any]]
    confidence_score: float
    response_quality: ResponseQuality
    timestamp: datetime


class KnowledgeResponder:
    """
    Advanced response synthesizer that combines memory retrieval,
    personality adaptation, and contextual understanding.
    """

    def __init__(
        self,
        memory_system: AdvancedMemorySystem,
        context_bridge: Optional[ContextBridge] = None,
    ):
        """Initialize the Knowledge Responder."""
        self.memory = memory_system
        self.context = context_bridge

        # Response templates by personality
        self.personality_templates = {
            PersonalityType.DEFAULT: {
                "greeting": "Let me help you with that.",
                "uncertain": "I have some information about this:",
                "confident": "Here's what I know:",
                "no_knowledge": "I don't have information on that topic yet. Could you tell me more?",
            },
            PersonalityType.MENTOR: {
                "greeting": "Great question! Let me share what I know about that.",
                "uncertain": "That's an interesting area to explore. Here's what I can tell you so far:",
                "confident": "Based on my experience, here's what I'd recommend:",
                "no_knowledge": "I haven't encountered that specific topic yet, but I'd love to learn more. Can you tell me about it?",
            },
            PersonalityType.DEV_FOCUSED: {
                "greeting": "Let me check what I know about that...",
                "uncertain": "I have some information on this, but it might need verification:",
                "confident": "Here's what I found in my knowledge base:",
                "no_knowledge": "No direct matches found. Could you provide more technical details?",
            },
            PersonalityType.CREATIVE: {
                "greeting": "Ooh, that's fascinating! Let me see what I can find...",
                "uncertain": "This sparks some interesting connections in my memory:",
                "confident": "I love this topic! Here's what I remember:",
                "no_knowledge": "What an intriguing question! I don't have experience with that yet - tell me more!",
            },
            PersonalityType.ANALYTICAL: {
                "greeting": "Analyzing available data for your query...",
                "uncertain": "Based on available information with moderate confidence:",
                "confident": "High-confidence match found. Analysis indicates:",
                "no_knowledge": "Insufficient data for comprehensive response. Request additional parameters.",
            },
            PersonalityType.FRIENDLY: {
                "greeting": "Hey there! I'd be happy to help with that!",
                "uncertain": "I think I can help, though I'm not 100% certain:",
                "confident": "Oh, I know about this! Here's what I can share:",
                "no_knowledge": "Hmm, that's new to me! I'd love to learn more about it though.",
            },
            PersonalityType.PROFESSIONAL: {
                "greeting": "I'll be glad to assist you with that inquiry.",
                "uncertain": "I can provide some information, though additional verification may be beneficial:",
                "confident": "I can provide comprehensive information on this topic:",
                "no_knowledge": "I don't currently have information on that topic. Could you provide more details?",
            },
        }

        # Tone adjustment patterns
        self.tone_adjustments = {
            ToneMode.ENCOURAGING: [
                "Great question!",
                "You're on the right track!",
                "Excellent point!",
            ],
            ToneMode.DIRECT: ["Here's the answer:", "Simply put:", "The key point is:"],
            ToneMode.CASUAL: [
                "So basically,",
                "Yeah, about that -",
                "Here's the deal:",
            ],
            ToneMode.FORMAL: [
                "According to available information,",
                "The data indicates that",
                "Research suggests that",
            ],
        }

        print("🎯 Knowledge Responder initialized")
        if self.context:
            print("   ✅ Context bridge connected")
        print("   ✅ Memory system connected")
        print("   ✅ Personality templates loaded")

    async def answer_question(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive response to a user question.

        Args:
            user_input: The user's question or input
            context: Optional context dictionary with personality, conversation state, etc.

        Returns:
            Dictionary with response, confidence, quality metrics, and metadata
        """
        try:
            # Parse context with better error handling
            try:
                personality = (
                    PersonalityType(context.get("personality", "default"))
                    if context
                    else PersonalityType.DEFAULT
                )
            except (ValueError, TypeError):
                print(
                    f"⚠️ Invalid personality in context: {context.get('personality') if context else 'None'}, using default"
                )
                personality = PersonalityType.DEFAULT

            try:
                tone_mode = (
                    ToneMode(context.get("tone_mode", "adaptive"))
                    if context
                    else ToneMode.ADAPTIVE
                )
            except (ValueError, TypeError):
                print(
                    f"⚠️ Invalid tone_mode in context: {context.get('tone_mode') if context else 'None'}, using adaptive"
                )
                tone_mode = ToneMode.ADAPTIVE

            conversation_state = context.get("conversation_state") if context else None

            # Step 1: Embed user question and search memory
            print(f"🔍 Processing query: {user_input[:50]}...")
            memories = await self._search_memories(user_input)

            # Step 2: Calculate confidence and quality
            confidence_score = self._calculate_confidence(memories)
            response_quality = self._determine_quality(confidence_score)

            # Step 3: Create response context
            response_context = ResponseContext(
                user_input=user_input,
                conversation_state=conversation_state,
                personality=personality,
                tone_mode=tone_mode,
                retrieved_memories=memories,
                confidence_score=confidence_score,
                response_quality=response_quality,
                timestamp=datetime.now(),
            )

            # Step 4: Synthesize response
            response_text = await self._synthesize_response(response_context)

            # Step 5: Apply personality and tone adjustments
            final_response = self._apply_personality_tone(
                response_text, response_context
            )

            # Step 6: Generate metadata
            metadata = self._generate_response_metadata(response_context)

            # Step 7: Emit cross-phase events if context bridge available
            if self.context:
                await self._emit_response_events(response_context, final_response)

            result = {
                "response": final_response,
                "confidence": confidence_score,
                "quality": response_quality.value,
                "personality": personality.value,
                "tone": tone_mode.value,
                "sources_count": len(memories),
                "metadata": metadata,
                "timestamp": response_context.timestamp.isoformat(),
            }

            print(
                f"✅ Response generated (confidence: {confidence_score:.2f}, quality: {response_quality.value})"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return {
                "response": "I encountered an error processing your question. Could you try rephrasing it?",
                "confidence": 0.0,
                "quality": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _search_memories(
        self, user_input: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search memory system for relevant information."""
        try:
            print(f"🔍 Searching memories for: '{user_input[:30]}...'")

            # Use the semantic_search method from AdvancedMemorySystem
            if hasattr(self.memory, "semantic_search"):
                memories = await self.memory.semantic_search(user_input, top_k=limit)
                print(f"📚 Found {len(memories)} relevant memories")
                return memories if memories else []
            else:
                # Fallback for different memory API
                print("⚠️ Memory search method not available, using empty results")
                return []
        except Exception as e:
            print(f"⚠️ Memory search failed: {e}")
            logger.warning(f"Memory search error for query '{user_input}': {e}")

            # Try alternative search methods
            try:
                if hasattr(self.memory, "_fallback_search"):
                    print("🔄 Attempting fallback search...")
                    memories = await self.memory._fallback_search(
                        user_input, limit, None
                    )
                    print(f"📚 Fallback found {len(memories)} memories")
                    return memories if memories else []
            except Exception as fallback_error:
                print(f"⚠️ Fallback search also failed: {fallback_error}")

            return []

    def _calculate_confidence(self, memories: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieved memories."""
        if not memories:
            return 0.0

        # Calculate confidence based on memory scores and count
        scores = []
        for memory in memories:
            # Try different confidence field names
            score = (
                memory.get("confidence", 0.0)
                or memory.get("relevance_score", 0.0)
                or memory.get("score", 0.0)
                or 0.5  # Default moderate confidence
            )
            scores.append(score)

        if not scores:
            return 0.3  # Low default confidence

        # Weighted average with diminishing returns for additional memories
        weighted_score = scores[0] * 0.6  # Primary match gets 60% weight
        if len(scores) > 1:
            weighted_score += sum(scores[1:]) * 0.4 / (len(scores) - 1)

        # Boost confidence if multiple relevant memories found
        if len(memories) >= 3:
            weighted_score = min(1.0, weighted_score * 1.1)

        return round(weighted_score, 3)

    def _determine_quality(self, confidence: float) -> ResponseQuality:
        """Determine response quality based on confidence score."""
        if confidence >= 0.8:
            return ResponseQuality.EXCELLENT
        elif confidence >= 0.6:
            return ResponseQuality.GOOD
        elif confidence >= 0.4:
            return ResponseQuality.MODERATE
        elif confidence >= 0.2:
            return ResponseQuality.UNCERTAIN
        else:
            return ResponseQuality.UNKNOWN

    async def _synthesize_response(self, context: ResponseContext) -> str:
        """Synthesize the core response content."""
        memories = context.retrieved_memories

        if not memories:
            return self._get_no_knowledge_response(context.personality)

        # Extract content from top memories
        content_sources = []

        for memory in memories[:3]:  # Use top 3 memories
            content = self._extract_memory_content(memory)
            if content:
                content_sources.append(content)

        if not content_sources:
            return self._get_uncertain_response(context.personality)

        # Synthesize response based on quality
        if context.response_quality == ResponseQuality.EXCELLENT:
            response = self._synthesize_confident_response(content_sources, context)
        elif context.response_quality in [
            ResponseQuality.GOOD,
            ResponseQuality.MODERATE,
        ]:
            response = self._synthesize_moderate_response(content_sources, context)
        else:
            response = self._synthesize_uncertain_response(content_sources, context)

        return response

    def _extract_memory_content(self, memory: Dict[str, Any]) -> str:
        """Extract relevant content from a memory object."""
        # Try different content field names
        content = (
            memory.get("content", "")
            or memory.get("text", "")
            or memory.get("summary", "")
            or memory.get("data", {}).get("content", "")
            if isinstance(memory.get("data"), dict)
            else "" or str(memory.get("data", ""))
            if memory.get("data")
            else ""
        )

        # If content is a dict, try to extract meaningful text
        if isinstance(content, dict):
            content = (
                content.get("summary", "")
                or content.get("text", "")
                or content.get("content", "")
                or str(content)
            )

        return str(content).strip()

    def _synthesize_confident_response(
        self, content_sources: List[str], context: ResponseContext
    ) -> str:
        """Synthesize a confident response from high-quality memory matches."""
        primary_content = content_sources[0]

        # Check if we have multiple supporting sources
        if len(content_sources) > 1:
            response = f"{primary_content}"

            # Add supporting information if it adds value
            for i, content in enumerate(content_sources[1:], 1):
                if len(content) > 20 and not self._is_duplicate_content(
                    primary_content, content
                ):
                    if i == 1:
                        response += f"\n\nAdditionally, {content}"
                    else:
                        response += f" Also, {content.lower()}"
                    if i >= 2:  # Limit to 3 sources max
                        break
        else:
            response = primary_content

        return response

    def _synthesize_moderate_response(
        self, content_sources: List[str], context: ResponseContext
    ) -> str:
        """Synthesize a moderate confidence response."""
        primary_content = content_sources[0]

        # Add qualifying language for moderate confidence
        qualifiers = [
            "Based on what I know, ",
            "From my understanding, ",
            "According to my information, ",
            "Here's what I can tell you: ",
        ]

        qualifier = random.choice(qualifiers)
        response = f"{qualifier}{primary_content}"

        return response

    def _synthesize_uncertain_response(
        self, content_sources: List[str], context: ResponseContext
    ) -> str:
        """Synthesize an uncertain response with caveats."""
        primary_content = content_sources[0]

        # Add uncertainty qualifiers
        uncertain_phrases = [
            "I have some information about this, though I'm not entirely certain: ",
            "This might be relevant, but I'd recommend verifying: ",
            "Here's what I found, though it may not be complete: ",
            "I have partial information on this topic: ",
        ]

        qualifier = random.choice(uncertain_phrases)
        response = f"{qualifier}{primary_content}"

        return response

    def _get_no_knowledge_response(self, personality: PersonalityType) -> str:
        """Get appropriate response when no relevant memories found."""
        templates = self.personality_templates.get(
            personality, self.personality_templates[PersonalityType.DEFAULT]
        )
        return templates["no_knowledge"]

    def _get_uncertain_response(self, personality: PersonalityType) -> str:
        """Get appropriate response for uncertain situations."""
        templates = self.personality_templates.get(
            personality, self.personality_templates[PersonalityType.DEFAULT]
        )
        return templates["uncertain"]

    def _is_duplicate_content(self, content1: str, content2: str) -> bool:
        """Check if two content pieces are essentially duplicates."""
        # Simple duplicate detection based on word overlap
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        overlap = len(words1.intersection(words2))
        smaller_set = min(len(words1), len(words2))

        return overlap / smaller_set > 0.7  # 70% word overlap threshold

    def _apply_personality_tone(self, response: str, context: ResponseContext) -> str:
        """Apply personality and tone adjustments to the response."""
        personality = context.personality
        tone_mode = context.tone_mode

        # Get personality templates with fallback to DEFAULT
        templates = self.personality_templates.get(personality)
        if not templates:
            print(f"⚠️ Unknown personality type: {personality}, using default")
            templates = self.personality_templates[PersonalityType.DEFAULT]

        # Choose appropriate introduction based on confidence
        if context.confidence_score >= 0.7:
            intro = templates["confident"]
        elif context.confidence_score >= 0.4:
            intro = templates["uncertain"]
        else:
            intro = templates["greeting"]

        # Apply tone adjustments
        if tone_mode in self.tone_adjustments:
            tone_phrases = self.tone_adjustments[tone_mode]
            if tone_mode == ToneMode.ENCOURAGING:
                intro = f"{random.choice(tone_phrases)} {intro}"
            elif tone_mode == ToneMode.DIRECT:
                intro = random.choice(tone_phrases)
            else:
                # For casual and formal, modify the response structure
                pass

        # Combine introduction with response
        if intro and not response.startswith(intro):
            final_response = f"{intro} {response}"
        else:
            final_response = response

        return final_response.strip()

    def _generate_response_metadata(self, context: ResponseContext) -> Dict[str, Any]:
        """Generate metadata about the response generation process."""
        return {
            "memory_sources_used": len(context.retrieved_memories),
            "confidence_breakdown": {
                "overall": context.confidence_score,
                "quality_level": context.response_quality.value,
                "memory_count": len(context.retrieved_memories),
            },
            "personality_applied": context.personality.value,
            "tone_mode": context.tone_mode.value,
            "processing_timestamp": context.timestamp.isoformat(),
            "response_characteristics": {
                "has_multiple_sources": len(context.retrieved_memories) > 1,
                "high_confidence": context.confidence_score >= 0.7,
                "uncertainty_noted": context.response_quality
                in [ResponseQuality.UNCERTAIN, ResponseQuality.UNKNOWN],
            },
        }

    async def _emit_response_events(self, context: ResponseContext, response: str):
        """Emit cross-phase events about the response generation."""
        try:
            if not self.context:
                return

            # Emit confidence score event
            self.context.emit_event(
                EventType.CONFIDENCE_SCORE,
                source_phase="knowledge_responder",
                target_phase="analytics",
                data={
                    "confidence": context.confidence_score,
                    "quality": context.response_quality.value,
                    "memory_sources": len(context.retrieved_memories),
                    "timestamp": context.timestamp.isoformat(),
                },
            )

            # Emit semantic event for memory updates
            if context.retrieved_memories:
                self.context.emit_event(
                    EventType.SEMANTIC_EVENT,
                    source_phase="knowledge_responder",
                    target_phase="memory",
                    data={
                        "query": context.user_input,
                        "response_generated": True,
                        "sources_used": len(context.retrieved_memories),
                        "confidence": context.confidence_score,
                    },
                )

        except Exception as e:
            logger.warning(f"Failed to emit response events: {e}")

    # Utility methods for different response types

    async def quick_answer(self, user_input: str, personality: str = "default") -> str:
        """Generate a quick response with minimal context."""
        result = await self.answer_question(
            user_input, context={"personality": personality, "tone_mode": "direct"}
        )
        return result["response"]

    async def detailed_answer(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a detailed response with full metadata."""
        return await self.answer_question(user_input, context)

    async def conversational_answer(
        self,
        user_input: str,
        conversation_state: ConversationState,
        personality: PersonalityType = PersonalityType.FRIENDLY,
    ) -> Dict[str, Any]:
        """Generate a response within an ongoing conversation context."""
        context = {
            "personality": personality.value,
            "tone_mode": "adaptive",
            "conversation_state": conversation_state,
        }
        return await self.answer_question(user_input, context)


# Convenience function for easy integration
async def create_knowledge_responder(
    memory_system: AdvancedMemorySystem, context_bridge: Optional[ContextBridge] = None
) -> KnowledgeResponder:
    """Create and initialize a Knowledge Responder."""
    responder = KnowledgeResponder(memory_system, context_bridge)
    print("🎯 Knowledge Responder ready for queries")
    return responder


# Example usage
if __name__ == "__main__":

    async def demo():
        """Demo the Knowledge Responder."""
        print("🎯 KNOWLEDGE RESPONDER DEMO")
        print("=" * 40)

        # Create memory system (mock for demo)
        memory = AdvancedMemorySystem()
        responder = await create_knowledge_responder(memory)

        # Demo queries
        test_queries = [
            "How do I implement async functions in Python?",
            "What is machine learning?",
            "How do I create a REST API?",
            "Tell me about quantum computing",
        ]

        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            result = await responder.answer_question(
                query, context={"personality": "mentor", "tone_mode": "encouraging"}
            )
            print(f"📝 Response: {result['response']}")
            print(f"📊 Confidence: {result['confidence']:.2f} ({result['quality']})")

    # Run demo
    asyncio.run(demo())
