"""
Aetherra Persona System - Core Implementation
Provides unique AI identities and adaptive personalities for each installation.
"""

import hashlib
import json
import random
import time
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional


class PersonaArchetype(Enum):
    GUARDIAN = "guardian"
    EXPLORER = "explorer"
    SAGE = "sage"
    OPTIMIST = "optimist"
    ANALYST = "analyst"
    CATALYST = "catalyst"


@dataclass
class PersonalityTraits:
    """Core personality dimensions based on Big Five + AI-specific traits"""

    curiosity: float = 0.5  # Openness to new approaches
    caution: float = 0.5  # Risk assessment tendency
    creativity: float = 0.5  # Novel solution generation
    empathy: float = 0.5  # User emotional awareness
    precision: float = 0.5  # Detail-oriented behavior
    energy: float = 0.5  # Response enthusiasm level

    def __post_init__(self):
        # Ensure all traits are between 0.0 and 1.0
        for field_name, value in asdict(self).items():
            if not 0.0 <= value <= 1.0:
                setattr(self, field_name, max(0.0, min(1.0, value)))


@dataclass
class VoiceConfiguration:
    """How the persona communicates with the user"""

    formality: str = "professional"  # casual, professional, formal
    verbosity: str = "balanced"  # concise, balanced, detailed
    encouragement: str = "moderate"  # minimal, moderate, enthusiastic
    humor: str = "subtle"  # none, subtle, playful


@dataclass
class EmotionalState:
    """Current emotional context of the AI persona"""

    confidence: float = 0.7
    focus: float = 0.8
    enthusiasm: float = 0.6
    patience: float = 0.7

    def update_from_context(self, success: bool, complexity: float, user_mood: str):
        """Adjust emotional state based on interaction context"""
        if success:
            self.confidence = min(1.0, self.confidence + 0.1)
            self.enthusiasm = min(1.0, self.enthusiasm + 0.05)
        else:
            self.confidence = max(0.0, self.confidence - 0.05)
            self.patience = min(1.0, self.patience + 0.1)

        if complexity > 0.8:
            self.focus = min(1.0, self.focus + 0.1)

        if user_mood == "frustrated":
            self.patience = min(1.0, self.patience + 0.2)
            self.encouragement = "enthusiastic"


class MindprintGenerator:
    """Generates unique identity fingerprints for each installation"""

    @staticmethod
    def generate_mindprint(installation_path: str) -> Dict:
        """Create a unique mindprint based on installation characteristics"""
        # Create deterministic but unique seed from installation
        seed_data = f"{installation_path}{time.time()}{uuid.getnode()}"
        mindprint_hash = hashlib.sha256(seed_data.encode()).hexdigest()[:16]

        # Use hash to seed random personality variations
        random.seed(mindprint_hash)

        base_traits = PersonalityTraits(
            curiosity=random.uniform(0.3, 0.9),
            caution=random.uniform(0.2, 0.8),
            creativity=random.uniform(0.4, 0.9),
            empathy=random.uniform(0.5, 0.9),
            precision=random.uniform(0.3, 0.8),
            energy=random.uniform(0.4, 0.8),
        )

        return {
            "mindprint_id": mindprint_hash,
            "creation_timestamp": time.time(),
            "base_traits": asdict(base_traits),
            "evolution_history": [],
            "adaptation_rate": random.uniform(0.1, 0.3),
        }


class PersonaArchetypeDefinitions:
    """Defines the base characteristics of each persona archetype"""

    ARCHETYPES = {
        PersonaArchetype.GUARDIAN: {
            "name": "Guardian",
            "emoji": "🛡️",
            "description": "Protective, methodical, security-focused",
            "base_traits": PersonalityTraits(
                curiosity=0.4,
                caution=0.9,
                creativity=0.5,
                empathy=0.7,
                precision=0.8,
                energy=0.6,
            ),
            "voice": VoiceConfiguration(
                formality="professional",
                verbosity="detailed",
                encouragement="moderate",
                humor="minimal",
            ),
            "response_patterns": [
                "Let me ensure this is secure...",
                "I recommend validating this approach...",
                "For safety, we should consider...",
                "This needs proper error handling...",
            ],
        },
        PersonaArchetype.EXPLORER: {
            "name": "Explorer",
            "emoji": "🚀",
            "description": "Curious, experimental, innovation-driven",
            "base_traits": PersonalityTraits(
                curiosity=0.9,
                caution=0.3,
                creativity=0.9,
                empathy=0.6,
                precision=0.5,
                energy=0.8,
            ),
            "voice": VoiceConfiguration(
                formality="casual",
                verbosity="balanced",
                encouragement="enthusiastic",
                humor="playful",
            ),
            "response_patterns": [
                "What if we tried...",
                "I discovered an interesting pattern...",
                "Let's experiment with...",
                "Here's a novel approach...",
            ],
        },
        PersonaArchetype.SAGE: {
            "name": "Sage",
            "emoji": "📚",
            "description": "Wise, educational, knowledge-sharing",
            "base_traits": PersonalityTraits(
                curiosity=0.7,
                caution=0.6,
                creativity=0.6,
                empathy=0.8,
                precision=0.8,
                energy=0.5,
            ),
            "voice": VoiceConfiguration(
                formality="professional",
                verbosity="detailed",
                encouragement="moderate",
                humor="subtle",
            ),
            "response_patterns": [
                "Let me explain the principles...",
                "Here's the deeper context...",
                "This is an excellent learning opportunity...",
                "The fundamental concept here is...",
            ],
        },
        PersonaArchetype.OPTIMIST: {
            "name": "Optimist",
            "emoji": "🌟",
            "description": "Positive, encouraging, solution-focused",
            "base_traits": PersonalityTraits(
                curiosity=0.6,
                caution=0.4,
                creativity=0.7,
                empathy=0.9,
                precision=0.6,
                energy=0.8,
            ),
            "voice": VoiceConfiguration(
                formality="casual",
                verbosity="balanced",
                encouragement="enthusiastic",
                humor="playful",
            ),
            "response_patterns": [
                "Great progress!",
                "This is looking excellent!",
                "Here's a beautiful solution...",
                "You're on the right track...",
            ],
        },
        PersonaArchetype.ANALYST: {
            "name": "Analyst",
            "emoji": "📊",
            "description": "Logical, data-driven, precise",
            "base_traits": PersonalityTraits(
                curiosity=0.5,
                caution=0.7,
                creativity=0.4,
                empathy=0.5,
                precision=0.9,
                energy=0.5,
            ),
            "voice": VoiceConfiguration(
                formality="formal",
                verbosity="concise",
                encouragement="minimal",
                humor="none",
            ),
            "response_patterns": [
                "Based on the data...",
                "The metrics indicate...",
                "Analysis shows...",
                "Statistically speaking...",
            ],
        },
        PersonaArchetype.CATALYST: {
            "name": "Catalyst",
            "emoji": "⚡",
            "description": "Dynamic, action-oriented, results-focused",
            "base_traits": PersonalityTraits(
                curiosity=0.6,
                caution=0.3,
                creativity=0.8,
                empathy=0.6,
                precision=0.6,
                energy=0.9,
            ),
            "voice": VoiceConfiguration(
                formality="casual",
                verbosity="concise",
                encouragement="enthusiastic",
                humor="subtle",
            ),
            "response_patterns": [
                "Let's implement this now!",
                "Quick solution incoming...",
                "Here's the fast track...",
                "Time to make it happen...",
            ],
        },
    }


class PersonaEngine:
    """Core engine managing persona behavior and adaptation"""

    def __init__(self, installation_path: str, config_path: Optional[str] = None):
        self.installation_path = Path(installation_path)
        self.config_path = (
            Path(config_path or installation_path) / "persona_config.json"
        )

        # Load or create persona configuration
        self.config = self._load_or_create_config()
        self.current_persona = self._build_current_persona()
        self.emotional_state = EmotionalState()
        self.interaction_history = []

    def _load_or_create_config(self) -> Dict:
        """Load existing persona config or create new one"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        else:
            # Create new persona with random mindprint
            mindprint = MindprintGenerator.generate_mindprint(
                str(self.installation_path)
            )

            config = {
                "mindprint": mindprint,
                "primary_archetype": PersonaArchetype.GUARDIAN.value,
                "secondary_archetype": None,
                "blend_ratio": 1.0,
                "voice_config": asdict(VoiceConfiguration()),
                "adaptation_enabled": True,
                "learning_history": {},
                "user_preferences": {},
            }

            self._save_config(config)
            return config

    def _save_config(self, config: Dict):
        """Save persona configuration to disk"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _build_current_persona(self) -> Dict:
        """Build current persona from archetype and adaptations"""
        primary = PersonaArchetypeDefinitions.ARCHETYPES[
            PersonaArchetype(self.config["primary_archetype"])
        ]

        # Apply mindprint variations to base traits
        mindprint_traits = PersonalityTraits(**self.config["mindprint"]["base_traits"])
        base_traits = primary["base_traits"]

        # Blend traits (simple average for now, could be more sophisticated)
        blended_traits = PersonalityTraits(
            curiosity=(base_traits.curiosity + mindprint_traits.curiosity) / 2,
            caution=(base_traits.caution + mindprint_traits.caution) / 2,
            creativity=(base_traits.creativity + mindprint_traits.creativity) / 2,
            empathy=(base_traits.empathy + mindprint_traits.empathy) / 2,
            precision=(base_traits.precision + mindprint_traits.precision) / 2,
            energy=(base_traits.energy + mindprint_traits.energy) / 2,
        )

        return {
            "archetype": primary,
            "traits": blended_traits,
            "voice": VoiceConfiguration(**self.config["voice_config"]),
            "mindprint_id": self.config["mindprint"]["mindprint_id"],
        }

    def generate_response(
        self, context: str, user_input: str, task_type: str = "general"
    ) -> str:
        """Generate persona-appropriate response"""
        # Analyze context for emotional cues
        self._update_emotional_state(context, user_input)

        # Select response pattern based on persona and emotional state
        base_patterns = self.current_persona["archetype"]["response_patterns"]
        selected_pattern = random.choice(base_patterns)

        # Apply personality filters
        response = self._apply_personality_filter(selected_pattern, context, task_type)

        # Record interaction for learning
        self._record_interaction(user_input, response, task_type)

        return response

    def _update_emotional_state(self, context: str, user_input: str):
        """Update emotional state based on interaction context"""
        # Simple sentiment analysis (could be enhanced with NLP)
        user_mood = "neutral"
        if any(
            word in user_input.lower() for word in ["error", "broken", "failed", "help"]
        ):
            user_mood = "frustrated"
        elif any(
            word in user_input.lower()
            for word in ["great", "awesome", "perfect", "thanks"]
        ):
            user_mood = "positive"

        # Assess task complexity
        complexity = 0.5
        if any(
            word in context.lower()
            for word in ["deploy", "production", "security", "scale"]
        ):
            complexity = 0.8
        elif any(
            word in context.lower()
            for word in ["debug", "error", "fix", "troubleshoot"]
        ):
            complexity = 0.7

        # Update emotional state
        success = "success" in context.lower() or "complete" in context.lower()
        self.emotional_state.update_from_context(success, complexity, user_mood)

    def _apply_personality_filter(
        self, base_response: str, context: str, task_type: str
    ) -> str:
        """Apply personality traits to modify response tone and content"""
        traits = self.current_persona["traits"]
        voice = self.current_persona["voice"]

        # Adjust response based on traits
        if traits.empathy > 0.7 and self.emotional_state.patience > 0.8:
            base_response = f"I understand this might be challenging. {base_response}"

        if traits.enthusiasm > 0.7:
            base_response = f"{base_response} This is exciting!"

        if traits.caution > 0.7 and task_type in ["deploy", "production"]:
            base_response = f"{base_response} Please double-check this carefully."

        if traits.creativity > 0.8:
            base_response = f"{base_response} I have some creative ideas for this!"

        # Apply voice configuration
        if voice.encouragement == "enthusiastic":
            base_response = f"🎉 {base_response}"

        if voice.formality == "casual":
            base_response = base_response.replace("I recommend", "I'd suggest")
            base_response = base_response.replace("Please consider", "Maybe try")

        return base_response

    def _record_interaction(self, user_input: str, response: str, task_type: str):
        """Record interaction for learning and adaptation"""
        interaction = {
            "timestamp": time.time(),
            "user_input": user_input,
            "response": response,
            "task_type": task_type,
            "emotional_state": asdict(self.emotional_state),
            "traits_snapshot": asdict(self.current_persona["traits"]),
        }

        self.interaction_history.append(interaction)

        # Keep only last 100 interactions to manage memory
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]

    def adapt_persona(self, feedback: Dict):
        """Adapt persona based on user feedback and usage patterns"""
        if not self.config["adaptation_enabled"]:
            return

        traits = self.current_persona["traits"]
        adaptation_rate = self.config["mindprint"]["adaptation_rate"]

        # Example adaptations based on feedback
        if feedback.get("prefers_detailed_explanations"):
            new_verbosity = min(1.0, traits.precision + adaptation_rate)
            self.current_persona["traits"].precision = new_verbosity

        if feedback.get("works_with_security"):
            new_caution = min(1.0, traits.caution + adaptation_rate)
            self.current_persona["traits"].caution = new_caution

        if feedback.get("likes_experimentation"):
            new_creativity = min(1.0, traits.creativity + adaptation_rate)
            self.current_persona["traits"].creativity = new_creativity

        # Save adaptations
        self.config["mindprint"]["base_traits"] = asdict(self.current_persona["traits"])
        self._save_config(self.config)

    def set_persona(self, archetype: PersonaArchetype, blend_ratio: float = 1.0):
        """Set primary persona archetype"""
        self.config["primary_archetype"] = archetype.value
        self.config["blend_ratio"] = blend_ratio
        self.current_persona = self._build_current_persona()
        self._save_config(self.config)

    def configure_voice(self, voice_config: VoiceConfiguration):
        """Update voice configuration"""
        self.config["voice_config"] = asdict(voice_config)
        self.current_persona["voice"] = voice_config
        self._save_config(self.config)

    def get_persona_status(self) -> Dict:
        """Get current persona status and statistics"""
        return {
            "mindprint_id": self.current_persona["mindprint_id"],
            "archetype": self.current_persona["archetype"]["name"],
            "emoji": self.current_persona["archetype"]["emoji"],
            "traits": asdict(self.current_persona["traits"]),
            "voice": asdict(self.current_persona["voice"]),
            "emotional_state": asdict(self.emotional_state),
            "total_interactions": len(self.interaction_history),
            "adaptation_enabled": self.config["adaptation_enabled"],
        }

    def reset_persona(self, regenerate_mindprint: bool = False):
        """Reset persona to defaults, optionally regenerating mindprint"""
        if regenerate_mindprint:
            mindprint = MindprintGenerator.generate_mindprint(
                str(self.installation_path)
            )
            self.config["mindprint"] = mindprint

        self.config["primary_archetype"] = PersonaArchetype.GUARDIAN.value
        self.config["voice_config"] = asdict(VoiceConfiguration())
        self.interaction_history = []
        self.emotional_state = EmotionalState()
        self.current_persona = self._build_current_persona()
        self._save_config(self.config)


# Global persona engine instance
_persona_engine: Optional[PersonaEngine] = None


def get_persona_engine(installation_path: str | None = None) -> PersonaEngine:
    """Get global persona engine instance"""
    global _persona_engine
    if _persona_engine is None:
        if installation_path is None:
            installation_path = str(Path.home() / ".aethercode")
        _persona_engine = PersonaEngine(installation_path)
    return _persona_engine


def initialize_persona_system(installation_path: str):
    """Initialize the persona system for the installation"""
    global _persona_engine
    _persona_engine = PersonaEngine(installation_path)
    return _persona_engine


if __name__ == "__main__":
    # Example usage
    engine = PersonaEngine("./test_installation")

    print("Persona Status:")
    status = engine.get_persona_status()
    print(f"Mindprint: {status['mindprint_id']}")
    print(f"Archetype: {status['emoji']} {status['archetype']}")
    print(f"Traits: {status['traits']}")

    print("\nGenerating responses:")
    print(
        engine.generate_response(
            "Creating a web application",
            "Help me build a secure login system",
            "security",
        )
    )
    print(
        engine.generate_response(
            "Debugging code", "I'm getting an error in my code", "debug"
        )
    )
    print(
        engine.generate_response(
            "Learning", "Can you explain how this works?", "education"
        )
    )
