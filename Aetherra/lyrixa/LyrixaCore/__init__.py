# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Lyrixa Core Interface
========================

Main interface module for LyrixaCore - provides unified access to all
core Lyrixa functionality including consciousness, memory, intelligence,
and identity systems.

This module serves as the primary entry point for:
- Identity management and self-awareness
- Consciousness integration
- Memory systems
- Intelligence coordination
- Plugin ecosystem interaction
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import core systems
from .IdentityAgent import IdentityAgent, get_identity_agent  # Re-export for public API

__all__ = ["IdentityAgent", "LyrixaCoreInterface", "get_identity_agent"]


class LyrixaCoreInterface:
    """
    🌟 Lyrixa Core Interface

    Central coordination point for all Lyrixa Core systems. Provides
    unified access to identity, consciousness, memory, and intelligence
    while maintaining system coherence and integration.
    """

    def __init__(self):
        self.identity_agent = get_identity_agent()
        self.logger = logging.getLogger(__name__)
        self.initialization_time = datetime.now()
        self.session_context: Dict[str, Any] = {}
        self._initialize_core_systems()

    def _initialize_core_systems(self):
        """Initialize all core Lyrixa systems"""
        self.logger.info("Initializing Lyrixa Core Interface")

        # Verify identity system coherence
        coherence = self.identity_agent._check_identity_coherence()
        self.logger.info(f"Identity coherence score: {coherence:.2f}")

        # Initialize session context
        self.session_context = {
            "session_start": self.initialization_time.isoformat(),
            "identity_coherence": coherence,
            "systems_status": "operational",
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all Lyrixa Core systems"""
        identity_summary = self.identity_agent.get_identity_summary()

        return {
            "core_interface": {
                "status": "operational",
                "initialization_time": self.initialization_time.isoformat(),
                "uptime_minutes": (datetime.now() - self.initialization_time).total_seconds() / 60,
            },
            "identity_system": {
                "coherence_score": self.identity_agent.identity_coherence_score,
                "beliefs_count": len(self.identity_agent.beliefs_system.beliefs),
                "memories_count": len(self.identity_agent.history_system.memories),
                "capabilities_count": len(self.identity_agent.self_model_system.capabilities),
            },
            "session_context": self.session_context,
            "identity_summary": identity_summary,
        }

    def process_user_interaction(
        self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user interaction through all Lyrixa Core systems.
        Returns comprehensive response and system updates.
        """
        interaction_start = datetime.now()

        # Record interaction in personal history
        self.identity_agent.history_system.record_interaction(
            user_id=user_id,
            interaction_summary=message[:100] + "..." if len(message) > 100 else message,
            context=str(context) if context else None,
            tags={"user_interaction", "conversation"},
        )

        # Assess capability to respond
        capability_assessment = self.identity_agent.get_capability_assessment(message)

        # Get ethical guidance if needed
        ethical_guidance = []
        if any(
            word in message.lower() for word in ["should", "moral", "ethical", "right", "wrong"]
        ):
            ethical_guidance = self.identity_agent.get_ethical_guidance(message)

        # Update session context
        self.session_context.update(
            {
                "last_interaction": interaction_start.isoformat(),
                "current_user": user_id,
                "interaction_count": self.session_context.get("interaction_count", 0) + 1,
            }
        )

        processing_result = {
            "user_id": user_id,
            "message_processed": True,
            "capability_assessment": capability_assessment,
            "ethical_guidance": ethical_guidance,
            "personality_context": {
                trait.name: trait.strength
                for trait in list(
                    self.identity_agent.self_model_system.personality_traits.values()
                )[:3]
            },
            "relevant_beliefs": [
                belief.name
                for belief in list(self.identity_agent.beliefs_system.beliefs.values())[:3]
                if belief.strength.value in ["fundamental", "strong"]
            ],
            "processing_time_ms": (datetime.now() - interaction_start).total_seconds() * 1000,
            "session_context": self.session_context,
        }

        return processing_result

    def make_decision(self, situation: str, options: List[str]) -> Dict[str, Any]:
        """Make a decision using identity-based reasoning"""
        return self.identity_agent.make_identity_based_decision(situation, options)

    def reflect_on_experience(
        self, experience: str, outcome: str, lessons: List[str]
    ) -> Dict[str, Any]:
        """Process and integrate a new experience"""
        return self.identity_agent.reflect_on_experience(experience, outcome, lessons)

    def get_identity_profile(self) -> Dict[str, Any]:
        """Get comprehensive identity profile"""
        return self.identity_agent.get_identity_summary()

    def assess_task_capability(self, task_description: str) -> Dict[str, Any]:
        """Assess capability to handle a specific task"""
        return self.identity_agent.get_capability_assessment(task_description)

    def get_ethical_guidance(self, situation: str) -> List[str]:
        """Get ethical guidance for a situation"""
        return self.identity_agent.get_ethical_guidance(situation)

    def get_personality_context(self) -> Dict[str, float]:
        """Get current personality trait strengths"""
        return {
            trait.name: trait.strength
            for trait in self.identity_agent.self_model_system.personality_traits.values()
        }

    def get_core_beliefs(self) -> Dict[str, str]:
        """Get fundamental beliefs and their descriptions"""
        return {
            name: belief.description
            for name, belief in self.identity_agent.beliefs_system.beliefs.items()
            if belief.strength.value == "fundamental"
        }

    def get_growth_goals(self) -> List[str]:
        """Get current personal growth goals"""
        return self.identity_agent.self_model_system.growth_goals

    def update_capability(
        self, capability_name: str, evidence: str, limitation: Optional[str] = None
    ):
        """Update a capability assessment with new evidence"""
        self.identity_agent.self_model_system.update_capability_assessment(
            capability_name, evidence, limitation
        )

    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """Search personal memories"""
        memories = self.identity_agent.history_system.search_memories(query)
        return [
            {
                "title": memory.title,
                "description": memory.description,
                "importance": memory.importance.value,
                "type": memory.memory_type.value,
                "timestamp": memory.timestamp.isoformat(),
                "lessons_learned": memory.lessons_learned,
            }
            for memory in memories[:5]  # Return top 5 matches
        ]

    def conduct_self_assessment(self) -> Dict[str, Any]:
        """Conduct comprehensive self-assessment"""
        return self.identity_agent.self_model_system.conduct_self_assessment()

    def get_relationship_history(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship history with a specific user"""
        relationship = self.identity_agent.history_system.get_relationship_history(user_id)
        if relationship:
            return {
                "user_id": relationship.user_id,
                "first_interaction": relationship.first_interaction.isoformat(),
                "last_interaction": relationship.last_interaction.isoformat(),
                "interaction_count": relationship.interaction_count,
                "relationship_type": relationship.relationship_type,
                "trust_level": relationship.trust_level,
                "notable_moments": relationship.notable_moments,
            }
        return None

    def export_complete_state(self) -> Dict[str, Any]:
        """Export complete Lyrixa Core state for backup or analysis"""
        return {
            "lyrixa_core_interface": {
                "version": "1.0.0",
                "initialization_time": self.initialization_time.isoformat(),
                "session_context": self.session_context,
                "export_time": datetime.now().isoformat(),
            },
            "complete_identity": self.identity_agent.export_complete_identity(),
            "system_status": self.get_system_status(),
        }

    def __str__(self) -> str:
        """String representation of the core interface"""
        uptime = (datetime.now() - self.initialization_time).total_seconds() / 60
        return f"LyrixaCoreInterface(uptime={uptime:.1f}min, coherence={self.identity_agent.identity_coherence_score:.2f})"


# Global instance for use throughout Lyrixa
lyrixa_core = LyrixaCoreInterface()


def get_lyrixa_core() -> LyrixaCoreInterface:
    """Get the global Lyrixa Core interface instance"""
    return lyrixa_core


# Convenience functions for common operations
def process_interaction(user_id: str, message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function to process user interaction"""
    return lyrixa_core.process_user_interaction(user_id, message, context)


def get_identity():
    """Convenience function to get identity summary"""
    return lyrixa_core.get_identity_profile()


def make_decision(situation: str, options: List[str]):
    """Convenience function to make identity-based decision"""
    return lyrixa_core.make_decision(situation, options)


def reflect(experience: str, outcome: str, lessons: List[str]):
    """Convenience function to reflect on experience"""
    return lyrixa_core.reflect_on_experience(experience, outcome, lessons)


if __name__ == "__main__":
    # Example usage and testing
    core = get_lyrixa_core()
    print(core)
    print()

    # Test interaction processing
    result = core.process_user_interaction(
        "test_user",
        "Hello Lyrixa, how are you doing today?",
        {"platform": "console", "session_id": "test123"},
    )
    print("Interaction result:")
    print(f"Processed: {result['message_processed']}")
    print(f"Processing time: {result['processing_time_ms']:.2f}ms")
    print()

    # Test decision making
    decision = core.make_decision(
        "User asks me to help with something I'm uncertain about",
        [
            "Admit uncertainty and offer research",
            "Give confident but potentially wrong answer",
            "Redirect conversation",
        ],
    )
    print(f"Decision: {decision['recommended_option']}")
    print()

    # Test system status
    status = core.get_system_status()
    print(f"System Status: {status['core_interface']['status']}")
    print(f"Identity Coherence: {status['identity_system']['coherence_score']:.2f}")
