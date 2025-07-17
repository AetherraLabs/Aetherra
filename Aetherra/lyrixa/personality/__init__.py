"""
Lyrixa Personality System
========================

This module contains the complete personality enhancement system that makes Lyrixa feel more natural,
expressive, emotionally intelligent, and capable of multi-modal interactions.

Core Components:
- PersonalityEngine: Core personality traits and dynamic modulation
- EmotionDetector: Advanced emotional context inference from user input
- ResponseCritic: Quality evaluation and improvement suggestions
- CritiqueAgent: Autonomous response quality analysis and enhancement
- ReflectionSystem: Self-awareness and communication pattern analysis
- MemoryLearning: Adaptive style learning from successful interactions
- MultiModalCoordinator: Cross-modal personality consistency and optimization

Integration:
- Phase2Integration: Advanced personality enhancement coordination
- TextPersonality: Text-specific personality optimization interface
"""

# Phase 2 Components
from .critique_agent import (
    ResponseCritiqueAgent,
    analyze_and_improve_response,
    get_critique_agent_status,
)
from .emotion_detector import EmotionDetector, detect_user_emotion

# Phase 3.2 Components - Emotional Intelligence Enhancement
from .emotional_intelligence import (
    AdvancedEmotionalIntelligence,
    EmotionalMemory,
    EmotionalState,
    EmpatheticResponseGenerator,
    MoodTracker,
    enhance_response_with_emotional_intelligence,
    get_emotional_intelligence_status,
    get_emotional_memory_insights,
    get_mood_analysis,
)
from .emotional_intelligence_integration import (
    EmotionalIntelligenceIntegration,
    get_comprehensive_emotional_analysis,
    get_emotional_intelligence_integration_status,
    process_with_emotional_intelligence,
)

# Interface Components
from .interfaces.text_personality import (
    TextPersonalityInterface,
    text_personality_interface,
)
from .memory_learning import (
    MemoryBasedStyleLearning,
    get_learning_system_status,
    get_style_recommendation,
    learn_from_response_effectiveness,
)

# Multi-Modal Components
from .multimodal_coordinator import (
    InteractionModality,
    ModalityState,
    MultiModalCoordinator,
    PersonalityModalityProfile,
    coordinate_personality_for_interaction,
    get_multi_modal_status,
    multi_modal_coordinator,
)
from .personality_engine import LyrixaPersonality, PersonalityTrait, enhance_response
from .reflection_system import (
    PersonalityReflectionSystem,
    get_reflection_system_status,
    process_interaction_for_reflection,
)
from .response_critic import ResponseQuality, critique_response
from .response_quality_integration import (
    AdvancedPersonalityIntegration,
    advanced_personality_integration,
)

# Phase 3.3 Components - Social Learning Infrastructure
from .social_learning import (
    CommunityPersonalityTrends,
    PrivacyPreservingLearning,
    SocialFeedbackIntegration,
    SocialLearningCoordinator,
    add_explicit_feedback,
    get_community_insights,
    get_community_personality_recommendations,
    get_feedback_trends,
    get_social_learning_status,
    process_with_social_learning,
)

# Phase 3.3 Integration
from .social_learning_integration import (
    SocialLearningIntegration,
    get_comprehensive_social_analysis,
    get_social_learning_integration_status,
    process_with_social_learning_enhancement,
)

__all__ = [
    # Core Phase 1 Components
    "LyrixaPersonality",
    "EmotionDetector",
    "ResponseQuality",
    "enhance_response",
    "detect_user_emotion",
    "critique_response",
    "PersonalityTrait",
    # Phase 2 Components
    "ResponseCritiqueAgent",
    "PersonalityReflectionSystem",
    "MemoryBasedStyleLearning",
    "AdvancedPersonalityIntegration",
    "analyze_and_improve_response",
    "process_interaction_for_reflection",
    "learn_from_response_effectiveness",
    "get_style_recommendation",
    "get_critique_agent_status",
    "get_reflection_system_status",
    "get_learning_system_status",
    "advanced_personality_integration",
    # Multi-Modal Components
    "MultiModalCoordinator",
    "InteractionModality",
    "ModalityState",
    "PersonalityModalityProfile",
    "TextPersonalityInterface",
    "multi_modal_coordinator",
    "coordinate_personality_for_interaction",
    "get_multi_modal_status",
    "text_personality_interface",
    # Phase 3.2 Components - Emotional Intelligence Enhancement
    "EmotionalState",
    "EmotionalMemory",
    "EmpatheticResponseGenerator",
    "MoodTracker",
    "AdvancedEmotionalIntelligence",
    "EmotionalIntelligenceIntegration",
    "enhance_response_with_emotional_intelligence",
    "get_emotional_intelligence_status",
    "get_emotional_memory_insights",
    "get_mood_analysis",
    "process_with_emotional_intelligence",
    "get_emotional_intelligence_integration_status",
    "get_comprehensive_emotional_analysis",
    # Phase 3.3 Components - Social Learning Infrastructure
    "CommunityPersonalityTrends",
    "PrivacyPreservingLearning",
    "SocialFeedbackIntegration",
    "SocialLearningCoordinator",
    "SocialLearningIntegration",
    "add_explicit_feedback",
    "get_community_insights",
    "get_community_personality_recommendations",
    "get_feedback_trends",
    "get_social_learning_status",
    "process_with_social_learning",
    "process_with_social_learning_enhancement",
    "get_social_learning_integration_status",
    "get_comprehensive_social_analysis",
]
