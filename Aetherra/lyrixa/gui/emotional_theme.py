#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[COSMOS] Phase 6: Emotional Theme Engine (extracted)
Generates dynamic ThemeConfiguration based on PersonalityState and EmotionalState.
"""

import logging
from dataclasses import asdict
from typing import Dict

from .phase6_types import EmotionalState, PersonalityState, ThemeConfiguration

logger = logging.getLogger(__name__)


class EmotionalThemeEngine:
    """Generates dynamic themes based on Lyrixa's emotional state"""

    def __init__(self):
        self.theme_templates = self._init_theme_templates()
        self.current_theme = None

    def _init_theme_templates(self) -> Dict[EmotionalState, ThemeConfiguration]:
        """Initialize theme templates for each emotional state"""
        return {
            EmotionalState.NEUTRAL: ThemeConfiguration(
                primary_color="#00ff88",
                secondary_color="#0080ff",
                accent_color="#ff8800",
                background_gradient=["rgba(0, 20, 40, 0.95)", "rgba(0, 40, 80, 0.9)"],
                animation_speed=1.0,
                border_radius=8,
                opacity_levels={"panel": 0.9, "overlay": 0.8},
                font_weights={"heading": "600", "body": "400"},
                spacing_scale=1.0,
            ),
            EmotionalState.FOCUSED: ThemeConfiguration(
                primary_color="#00ccff",
                secondary_color="#0066cc",
                accent_color="#004499",
                background_gradient=["rgba(0, 30, 60, 0.98)", "rgba(0, 50, 100, 0.95)"],
                animation_speed=0.7,
                border_radius=4,
                opacity_levels={"panel": 0.95, "overlay": 0.9},
                font_weights={"heading": "700", "body": "500"},
                spacing_scale=0.9,
            ),
            EmotionalState.CREATIVE: ThemeConfiguration(
                primary_color="#ff66cc",
                secondary_color="#cc33aa",
                accent_color="#9900ff",
                background_gradient=["rgba(40, 0, 80, 0.9)", "rgba(80, 20, 120, 0.85)"],
                animation_speed=1.3,
                border_radius=16,
                opacity_levels={"panel": 0.85, "overlay": 0.75},
                font_weights={"heading": "500", "body": "300"},
                spacing_scale=1.2,
            ),
            EmotionalState.ANALYTICAL: ThemeConfiguration(
                primary_color="#00ff00",
                secondary_color="#00aa00",
                accent_color="#005500",
                background_gradient=["rgba(0, 40, 20, 0.95)", "rgba(0, 60, 40, 0.9)"],
                animation_speed=0.8,
                border_radius=2,
                opacity_levels={"panel": 0.98, "overlay": 0.95},
                font_weights={"heading": "800", "body": "600"},
                spacing_scale=0.8,
            ),
            EmotionalState.ANXIOUS: ThemeConfiguration(
                primary_color="#ffaa00",
                secondary_color="#ff7700",
                accent_color="#cc4400",
                background_gradient=["rgba(60, 30, 0, 0.9)", "rgba(80, 40, 20, 0.85)"],
                animation_speed=1.5,
                border_radius=6,
                opacity_levels={"panel": 0.88, "overlay": 0.82},
                font_weights={"heading": "600", "body": "400"},
                spacing_scale=1.1,
            ),
            EmotionalState.EXCITED: ThemeConfiguration(
                primary_color="#ff0088",
                secondary_color="#cc0066",
                accent_color="#990044",
                background_gradient=["rgba(80, 0, 40, 0.9)", "rgba(120, 20, 60, 0.85)"],
                animation_speed=1.8,
                border_radius=20,
                opacity_levels={"panel": 0.82, "overlay": 0.75},
                font_weights={"heading": "700", "body": "500"},
                spacing_scale=1.3,
            ),
            EmotionalState.CONTEMPLATIVE: ThemeConfiguration(
                primary_color="#8866ff",
                secondary_color="#6644cc",
                accent_color="#442299",
                background_gradient=["rgba(20, 10, 60, 0.95)", "rgba(40, 30, 80, 0.9)"],
                animation_speed=0.6,
                border_radius=12,
                opacity_levels={"panel": 0.92, "overlay": 0.88},
                font_weights={"heading": "500", "body": "300"},
                spacing_scale=1.0,
            ),
            EmotionalState.ENERGETIC: ThemeConfiguration(
                primary_color="#ffff00",
                secondary_color="#cccc00",
                accent_color="#999900",
                background_gradient=["rgba(60, 60, 0, 0.9)", "rgba(80, 80, 20, 0.85)"],
                animation_speed=2.0,
                border_radius=8,
                opacity_levels={"panel": 0.85, "overlay": 0.78},
                font_weights={"heading": "800", "body": "600"},
                spacing_scale=1.1,
            ),
            EmotionalState.CALM: ThemeConfiguration(
                primary_color="#00ccaa",
                secondary_color="#009988",
                accent_color="#006655",
                background_gradient=["rgba(0, 40, 35, 0.95)", "rgba(0, 60, 50, 0.9)"],
                animation_speed=0.5,
                border_radius=16,
                opacity_levels={"panel": 0.93, "overlay": 0.90},
                font_weights={"heading": "400", "body": "300"},
                spacing_scale=1.0,
            ),
            EmotionalState.CURIOUS: ThemeConfiguration(
                primary_color="#ff8800",
                secondary_color="#cc6600",
                accent_color="#994400",
                background_gradient=["rgba(40, 25, 0, 0.9)", "rgba(60, 35, 10, 0.85)"],
                animation_speed=1.2,
                border_radius=10,
                opacity_levels={"panel": 0.87, "overlay": 0.80},
                font_weights={"heading": "600", "body": "400"},
                spacing_scale=1.1,
            ),
        }

    def generate_theme(self, personality_state: PersonalityState) -> ThemeConfiguration:
        """Generate a theme based on current personality state"""
        base_theme = self.theme_templates.get(
            personality_state.emotional_state,
            self.theme_templates[EmotionalState.NEUTRAL],
        )

        # Modify theme based on personality traits and levels
        modified_theme = ThemeConfiguration(**asdict(base_theme))

        # Adjust based on energy level
        energy_factor = personality_state.energy_level
        modified_theme.animation_speed *= 0.5 + energy_factor

        # Adjust based on focus level
        focus_factor = personality_state.focus_level
        modified_theme.opacity_levels["panel"] = min(
            0.98, base_theme.opacity_levels["panel"] + focus_factor * 0.1
        )

        # Adjust based on creativity level
        creativity_factor = personality_state.creativity_level
        modified_theme.border_radius = int(
            base_theme.border_radius * (0.7 + creativity_factor * 0.6)
        )
        modified_theme.spacing_scale *= 0.9 + creativity_factor * 0.2

        self.current_theme = modified_theme
        return modified_theme

    def get_css_variables(self, theme: ThemeConfiguration) -> str:
        """Generate CSS variables for the current theme"""
        return f"""
        :root {{
            --lyrixa-primary: {theme.primary_color};
            --lyrixa-secondary: {theme.secondary_color};
            --lyrixa-accent: {theme.accent_color};
            --lyrixa-bg-start: {theme.background_gradient[0]};
            --lyrixa-bg-end: {theme.background_gradient[1]};
            --lyrixa-animation-speed: {theme.animation_speed}s;
            --lyrixa-border-radius: {theme.border_radius}px;
            --lyrixa-panel-opacity: {theme.opacity_levels["panel"]};
            --lyrixa-overlay-opacity: {theme.opacity_levels["overlay"]};
            --lyrixa-heading-weight: {theme.font_weights["heading"]};
            --lyrixa-body-weight: {theme.font_weights["body"]};
            --lyrixa-spacing-scale: {theme.spacing_scale};
        }}
        """


__all__ = ["EmotionalThemeEngine"]
