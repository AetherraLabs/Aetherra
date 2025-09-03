#!/usr/bin/env python3
"""
Phase 6 GUI Types: Enums and Dataclasses used across the Phase 6 personality UI.
Split out for maintainability and reuse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class EmotionalState(Enum):
    """Lyrixa's emotional states that affect GUI appearance"""

    NEUTRAL = "neutral"
    FOCUSED = "focused"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    CONTEMPLATIVE = "contemplative"
    ENERGETIC = "energetic"
    CALM = "calm"
    CURIOUS = "curious"


class PersonalityTrait(Enum):
    """Lyrixa's personality traits affecting interface behavior"""

    HELPFUL = "helpful"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    EMPATHETIC = "empathetic"
    LOGICAL = "logical"
    INTUITIVE = "intuitive"
    DETAIL_ORIENTED = "detail_oriented"
    BIG_PICTURE = "big_picture"


@dataclass
class GUIState:
    """Complete GUI state for memory and restoration"""

    current_panel: str
    panel_history: List[str]
    window_geometry: Dict[str, int]
    user_preferences: Dict[str, Any]
    filter_states: Dict[str, Any]
    layout_customizations: Dict[str, Any]
    theme_preferences: Dict[str, str]
    last_accessed: datetime
    usage_patterns: Dict[str, int] = field(default_factory=dict)


@dataclass
class PersonalityState:
    """Lyrixa's current personality and emotional state"""

    emotional_state: EmotionalState
    dominant_traits: List[PersonalityTrait]
    energy_level: float  # 0.0 - 1.0
    focus_level: float  # 0.0 - 1.0
    creativity_level: float  # 0.0 - 1.0
    social_engagement: float  # 0.0 - 1.0
    timestamp: datetime
    context_factors: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatMessage:
    """Chat message with AI context"""

    id: str
    content: str
    is_user: bool
    timestamp: datetime
    emotional_context: EmotionalState
    confidence: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThemeConfiguration:
    """Dynamic theme configuration based on personality state"""

    primary_color: str
    secondary_color: str
    accent_color: str
    background_gradient: List[str]
    animation_speed: float
    border_radius: int
    opacity_levels: Dict[str, float]
    font_weights: Dict[str, str]
    spacing_scale: float


__all__ = [
    "EmotionalState",
    "PersonalityTrait",
    "GUIState",
    "PersonalityState",
    "ChatMessage",
    "ThemeConfiguration",
]
