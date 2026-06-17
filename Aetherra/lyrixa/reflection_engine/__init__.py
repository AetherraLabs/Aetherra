# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lyrixa Reflection Engine
======================

Self-reflection and validation systems for continuous improvement.
"""

try:
    from .shadow_state_forker import ReflectionAgent
except ImportError:
    ReflectionAgent = None

try:
    from .validation_engine import (
        PersonalityReflectionSystem,
        get_reflection_system_status,
        personality_reflection_system,
        process_interaction_for_reflection,
    )
except ImportError:
    PersonalityReflectionSystem = None
    personality_reflection_system = None

    async def process_interaction_for_reflection(*args, **kwargs):
        raise ImportError("Reflection validation engine is not available")

    def get_reflection_system_status():
        return {"system_status": "unavailable"}

__all__ = [
    "PersonalityReflectionSystem",
    "ReflectionAgent",
    "get_reflection_system_status",
    "personality_reflection_system",
    "process_interaction_for_reflection",
]
