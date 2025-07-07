"""
Aetherra Contextual Adaptation System
Automatically adapts persona based on user context, project type, and situation.
"""

import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from .engine import PersonaArchetype, PersonaEngine


class ContextType(Enum):
    """Different types of coding contexts"""

    DEBUGGING = "debugging"
    CREATING = "creating"
    LEARNING = "learning"
    PRODUCTION = "production"
    PROTOTYPING = "prototyping"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    COLLABORATION = "collaboration"
    EMERGENCY = "emergency"


class ProjectType(Enum):
    """Different types of projects"""

    WEB_APPLICATION = "web_app"
    API_SERVICE = "api_service"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "ml_project"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    GAME_DEVELOPMENT = "game_dev"
    SYSTEM_PROGRAMMING = "system_prog"
    ACADEMIC_RESEARCH = "academic"
    PERSONAL_PROJECT = "personal"


class UrgencyLevel(Enum):
    """Urgency levels that affect persona adaptation"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContextualSituation:
    """Represents the current contextual situation"""

    context_type: ContextType
    project_type: ProjectType = ProjectType.PERSONAL_PROJECT
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM

    # Environmental factors
    time_of_day: str = "unknown"  # morning, afternoon, evening, night
    day_of_week: str = "unknown"  # monday, tuesday, etc.
    is_deadline_approaching: bool = False

    # Recent activity
    recent_errors: int = 0
    recent_successes: int = 0
    session_duration: float = 0.0  # minutes

    # User state indicators
    frustration_level: float = 0.0  # 0.0 to 1.0
    confidence_level: float = 0.5  # 0.0 to 1.0
    energy_level: float = 0.5  # 0.0 to 1.0


@dataclass
class AdaptationRule:
    """Rule for adapting persona based on context"""

    name: str
    context_conditions: Dict[str, Any]
    persona_adjustments: Dict[str, Any]
    priority: int = 50  # 0-100, higher priority rules override lower ones

    def matches_context(self, situation: ContextualSituation) -> bool:
        """Check if this rule applies to the current situation"""
        for field, expected_value in self.context_conditions.items():
            if hasattr(situation, field):
                actual_value = getattr(situation, field)

                # Handle different types of conditions
                if isinstance(expected_value, list):
                    if actual_value not in expected_value:
                        return False
                elif isinstance(expected_value, dict):
                    # Range conditions like {"min": 0.7, "max": 1.0}
                    if "min" in expected_value and actual_value < expected_value["min"]:
                        return False
                    if "max" in expected_value and actual_value > expected_value["max"]:
                        return False
                else:
                    if actual_value != expected_value:
                        return False

        return True


class ContextualAdaptationSystem:
    """System that automatically adapts persona based on context"""

    def __init__(self, storage_path: Path, persona_engine: PersonaEngine):
        self.storage_path = storage_path
        self.persona_engine = persona_engine
        self.adaptation_rules: List[AdaptationRule] = []
        self.context_history: List[ContextualSituation] = []
        self.current_situation: ContextualSituation = ContextualSituation(
            context_type=ContextType.CREATING
        )

        self._load_adaptation_rules()
        self._initialize_default_rules()

    def detect_context(
        self,
        user_command: str = "",
        file_patterns: List[str] | None = None,
        error_messages: List[str] | None = None,
        time_since_last_action: float = 0.0,
    ) -> ContextualSituation:
        """Automatically detect the current context from user activity"""

        situation = ContextualSituation(
            context_type=self._detect_context_type(
                user_command, file_patterns or [], error_messages or []
            ),
            project_type=self._detect_project_type(file_patterns or []),
            urgency_level=self._detect_urgency_level(
                error_messages or [], time_since_last_action
            ),
            time_of_day=self._get_time_of_day(),
            day_of_week=self._get_day_of_week(),
            recent_errors=len(error_messages or []),
            session_duration=time_since_last_action,
        )

        # Update user state indicators
        situation.frustration_level = self._estimate_frustration_level(
            error_messages or []
        )
        situation.confidence_level = self._estimate_confidence_level()
        situation.energy_level = self._estimate_energy_level(situation.time_of_day)

        return situation

    def adapt_persona(self, situation: ContextualSituation) -> Dict[str, Any]:
        """Adapt persona based on the current contextual situation"""

        # Store current situation
        self.current_situation = situation
        self.context_history.append(situation)

        # Keep history manageable
        if len(self.context_history) > 100:
            self.context_history = self.context_history[-50:]

        # Find applicable adaptation rules
        applicable_rules = [
            rule for rule in self.adaptation_rules if rule.matches_context(situation)
        ]

        # Sort by priority (highest first)
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)

        # Apply adaptations
        adaptations = {}
        for rule in applicable_rules:
            adaptations.update(rule.persona_adjustments)

        # Apply to persona engine
        if adaptations:
            self._apply_adaptations(adaptations)

        # Return summary of adaptations made
        return {
            "situation": asdict(situation),
            "rules_applied": [rule.name for rule in applicable_rules],
            "adaptations": adaptations,
            "timestamp": time.time(),
        }

    def get_context_appropriate_response_style(self) -> Dict[str, Any]:
        """Get the appropriate response style for the current context"""
        situation = self.current_situation

        base_style = {
            "formality": "professional",
            "verbosity": "balanced",
            "encouragement": "moderate",
            "technical_depth": "medium",
        }

        # Adjust based on context type
        if situation.context_type == ContextType.DEBUGGING:
            base_style.update(
                {
                    "formality": "direct",
                    "verbosity": "detailed",
                    "encouragement": "supportive",
                    "technical_depth": "high",
                }
            )
        elif situation.context_type == ContextType.LEARNING:
            base_style.update(
                {
                    "formality": "friendly",
                    "verbosity": "detailed",
                    "encouragement": "enthusiastic",
                    "technical_depth": "progressive",
                }
            )
        elif situation.context_type == ContextType.EMERGENCY:
            base_style.update(
                {
                    "formality": "direct",
                    "verbosity": "concise",
                    "encouragement": "calm_confidence",
                    "technical_depth": "precise",
                }
            )
        elif situation.context_type == ContextType.PROTOTYPING:
            base_style.update(
                {
                    "formality": "casual",
                    "verbosity": "balanced",
                    "encouragement": "energetic",
                    "technical_depth": "creative",
                }
            )

        # Adjust based on urgency
        if situation.urgency_level == UrgencyLevel.CRITICAL:
            base_style["verbosity"] = "concise"
            base_style["formality"] = "direct"
        elif situation.urgency_level == UrgencyLevel.LOW:
            base_style["verbosity"] = "detailed"
            base_style["formality"] = "friendly"

        # Adjust based on user state
        if situation.frustration_level > 0.7:
            base_style["encouragement"] = "calming"
            base_style["formality"] = "supportive"
        elif situation.confidence_level > 0.8:
            base_style["encouragement"] = "collaborative"
            base_style["technical_depth"] = "advanced"

        return base_style

    def suggest_optimal_archetype(
        self, situation: ContextualSituation
    ) -> PersonaArchetype:
        """Suggest the most appropriate archetype for the current situation"""

        # Context-based archetype suggestions
        archetype_scores = {
            PersonaArchetype.GUARDIAN: 0.0,
            PersonaArchetype.EXPLORER: 0.0,
            PersonaArchetype.SAGE: 0.0,
            PersonaArchetype.OPTIMIST: 0.0,
            PersonaArchetype.ANALYST: 0.0,
            PersonaArchetype.CATALYST: 0.0,
        }

        # Score based on context type
        context_archetype_map = {
            ContextType.DEBUGGING: {
                PersonaArchetype.GUARDIAN: 0.8,
                PersonaArchetype.ANALYST: 0.9,
                PersonaArchetype.SAGE: 0.6,
            },
            ContextType.CREATING: {
                PersonaArchetype.EXPLORER: 0.9,
                PersonaArchetype.CATALYST: 0.8,
                PersonaArchetype.OPTIMIST: 0.7,
            },
            ContextType.LEARNING: {
                PersonaArchetype.SAGE: 0.9,
                PersonaArchetype.OPTIMIST: 0.7,
                PersonaArchetype.EXPLORER: 0.6,
            },
            ContextType.PRODUCTION: {
                PersonaArchetype.GUARDIAN: 0.9,
                PersonaArchetype.ANALYST: 0.8,
                PersonaArchetype.SAGE: 0.6,
            },
            ContextType.EMERGENCY: {
                PersonaArchetype.GUARDIAN: 0.9,
                PersonaArchetype.ANALYST: 0.7,
                PersonaArchetype.CATALYST: 0.6,
            },
        }

        if situation.context_type in context_archetype_map:
            for archetype, score in context_archetype_map[
                situation.context_type
            ].items():
                archetype_scores[archetype] += score

        # Adjust based on user state
        if situation.frustration_level > 0.6:
            archetype_scores[PersonaArchetype.OPTIMIST] += 0.5
            archetype_scores[PersonaArchetype.SAGE] += 0.3

        if situation.confidence_level < 0.4:
            archetype_scores[PersonaArchetype.OPTIMIST] += 0.4
            archetype_scores[PersonaArchetype.SAGE] += 0.6

        if situation.urgency_level == UrgencyLevel.CRITICAL:
            archetype_scores[PersonaArchetype.GUARDIAN] += 0.6
            archetype_scores[PersonaArchetype.ANALYST] += 0.4

        # Return the highest-scoring archetype
        best_archetype = max(archetype_scores.items(), key=lambda x: x[1])[0]
        return best_archetype

    def _detect_context_type(
        self, command: str, file_patterns: List[str], error_messages: List[str]
    ) -> ContextType:
        """Detect context type from user activity"""
        command_lower = command.lower()

        # Debug-related keywords
        if any(
            keyword in command_lower
            for keyword in ["debug", "error", "fix", "bug", "issue", "problem"]
        ):
            return ContextType.DEBUGGING

        # Learning-related keywords
        if any(
            keyword in command_lower
            for keyword in ["learn", "explain", "how", "what", "why", "tutorial"]
        ):
            return ContextType.LEARNING

        # Testing-related keywords
        if any(
            keyword in command_lower
            for keyword in ["test", "spec", "verify", "validate"]
        ):
            return ContextType.TESTING

        # Documentation-related keywords
        if any(
            keyword in command_lower
            for keyword in ["document", "docs", "readme", "comment"]
        ):
            return ContextType.DOCUMENTATION

        # Emergency indicators
        if error_messages and len(error_messages) > 3:
            return ContextType.EMERGENCY

        if any(
            keyword in command_lower
            for keyword in ["urgent", "critical", "emergency", "broken", "down"]
        ):
            return ContextType.EMERGENCY

        # Production indicators
        if any(
            keyword in command_lower
            for keyword in ["deploy", "production", "release", "publish"]
        ):
            return ContextType.PRODUCTION

        # Refactoring indicators
        if any(
            keyword in command_lower
            for keyword in ["refactor", "cleanup", "optimize", "improve"]
        ):
            return ContextType.REFACTORING

        # Default to creating for most other activities
        return ContextType.CREATING

    def _detect_project_type(self, file_patterns: List[str]) -> ProjectType:
        """Detect project type from file patterns"""
        patterns_lower = [p.lower() for p in file_patterns]

        # Web application indicators
        if any(
            pattern in patterns_lower
            for pattern in ["html", "css", "js", "react", "vue", "angular"]
        ):
            return ProjectType.WEB_APPLICATION

        # API service indicators
        if any(
            pattern in patterns_lower
            for pattern in ["api", "server", "flask", "fastapi", "express"]
        ):
            return ProjectType.API_SERVICE

        # Data science indicators
        if any(
            pattern in patterns_lower
            for pattern in ["jupyter", "pandas", "numpy", "matplotlib", "data"]
        ):
            return ProjectType.DATA_SCIENCE

        # ML indicators
        if any(
            pattern in patterns_lower
            for pattern in ["tensorflow", "pytorch", "sklearn", "model", "train"]
        ):
            return ProjectType.MACHINE_LEARNING

        # Mobile app indicators
        if any(
            pattern in patterns_lower
            for pattern in ["android", "ios", "mobile", "swift", "kotlin"]
        ):
            return ProjectType.MOBILE_APP

        return ProjectType.PERSONAL_PROJECT

    def _detect_urgency_level(
        self, error_messages: List[str], time_since_last_action: float
    ) -> UrgencyLevel:
        """Detect urgency level from context"""
        # Multiple recent errors suggest urgency
        if len(error_messages) > 5:
            return UrgencyLevel.CRITICAL
        elif len(error_messages) > 2:
            return UrgencyLevel.HIGH

        # Long time since last action suggests low urgency
        if time_since_last_action > 3600:  # 1 hour
            return UrgencyLevel.LOW
        elif time_since_last_action < 300:  # 5 minutes
            return UrgencyLevel.HIGH

        return UrgencyLevel.MEDIUM

    def _get_time_of_day(self) -> str:
        """Get current time of day category"""
        hour = time.localtime().tm_hour

        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _get_day_of_week(self) -> str:
        """Get current day of week"""
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        return days[time.localtime().tm_wday]

    def _estimate_frustration_level(self, error_messages: List[str]) -> float:
        """Estimate user frustration level from error patterns"""
        if not error_messages:
            return 0.0

        # More errors = higher frustration
        error_count = len(error_messages)
        frustration = min(error_count / 5.0, 1.0)

        # Certain error types are more frustrating
        frustrating_errors = ["syntax", "undefined", "null", "permission"]
        for error in error_messages:
            if any(
                frustrating_word in error.lower()
                for frustrating_word in frustrating_errors
            ):
                frustration += 0.1

        return min(frustration, 1.0)

    def _estimate_confidence_level(self) -> float:
        """Estimate user confidence level from recent history"""
        if not self.context_history:
            return 0.5

        recent_contexts = self.context_history[-10:]

        # Count recent successes vs errors
        recent_errors = sum(ctx.recent_errors for ctx in recent_contexts)
        recent_successes = sum(ctx.recent_successes for ctx in recent_contexts)

        if recent_successes + recent_errors == 0:
            return 0.5

        success_rate = recent_successes / (recent_successes + recent_errors)
        return success_rate

    def _estimate_energy_level(self, time_of_day: str) -> float:
        """Estimate user energy level based on time of day"""
        energy_map = {"morning": 0.8, "afternoon": 0.6, "evening": 0.4, "night": 0.2}
        return energy_map.get(time_of_day, 0.5)

    def _apply_adaptations(self, adaptations: Dict[str, Any]):
        """Apply adaptations to the persona engine"""
        for adaptation_type, value in adaptations.items():
            if adaptation_type == "primary_archetype":
                self.persona_engine.set_persona(PersonaArchetype(value))
            elif adaptation_type == "voice_formality":
                current_voice = self.persona_engine.current_persona["voice"]
                current_voice.formality = value
                self.persona_engine.configure_voice(current_voice)
            elif adaptation_type == "encouragement_level":
                current_voice = self.persona_engine.current_persona["voice"]
                current_voice.encouragement = value
                self.persona_engine.configure_voice(current_voice)
            # Add more adaptation types as needed

    def _initialize_default_rules(self):
        """Initialize default adaptation rules"""
        default_rules = [
            # Debugging context rules
            AdaptationRule(
                name="debugging_guardian_mode",
                context_conditions={"context_type": ContextType.DEBUGGING},
                persona_adjustments={
                    "primary_archetype": PersonaArchetype.GUARDIAN.value,
                    "voice_formality": "professional",
                    "encouragement_level": "supportive",
                },
                priority=70,
            ),
            # High frustration emergency support
            AdaptationRule(
                name="frustration_support",
                context_conditions={"frustration_level": {"min": 0.7}},
                persona_adjustments={
                    "primary_archetype": PersonaArchetype.OPTIMIST.value,
                    "voice_formality": "friendly",
                    "encouragement_level": "enthusiastic",
                },
                priority=90,
            ),
            # Learning mode sage activation
            AdaptationRule(
                name="learning_sage_mode",
                context_conditions={"context_type": ContextType.LEARNING},
                persona_adjustments={
                    "primary_archetype": PersonaArchetype.SAGE.value,
                    "voice_formality": "educational",
                    "encouragement_level": "patient",
                },
                priority=75,
            ),
            # Emergency response
            AdaptationRule(
                name="emergency_response",
                context_conditions={"urgency_level": UrgencyLevel.CRITICAL},
                persona_adjustments={
                    "primary_archetype": PersonaArchetype.GUARDIAN.value,
                    "voice_formality": "direct",
                    "encouragement_level": "calm_confidence",
                },
                priority=95,
            ),
            # Creative exploration
            AdaptationRule(
                name="creative_exploration",
                context_conditions={"context_type": ContextType.PROTOTYPING},
                persona_adjustments={
                    "primary_archetype": PersonaArchetype.EXPLORER.value,
                    "voice_formality": "casual",
                    "encouragement_level": "energetic",
                },
                priority=65,
            ),
        ]

        self.adaptation_rules.extend(default_rules)

    def _load_adaptation_rules(self):
        """Load custom adaptation rules from storage"""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                data = json.load(f)

            for rule_data in data.get("adaptation_rules", []):
                rule = AdaptationRule(**rule_data)
                self.adaptation_rules.append(rule)

        except Exception as e:
            print(f"Warning: Could not load adaptation rules: {e}")

    def save_adaptation_rules(self):
        """Save adaptation rules to storage"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "adaptation_rules": [
                asdict(rule)
                for rule in self.adaptation_rules
                if not rule.name.startswith("default_")
            ],
            "last_updated": time.time(),
        }

        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def get_contextual_adaptation_system(
    installation_path: Path, persona_engine: PersonaEngine
) -> ContextualAdaptationSystem:
    """Get the global contextual adaptation system instance"""
    adaptation_path = installation_path / "contextual_adaptations.json"
    return ContextualAdaptationSystem(adaptation_path, persona_engine)
