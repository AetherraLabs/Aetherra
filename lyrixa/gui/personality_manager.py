"""
Personality Manager for Lyrixa
==============================

Manages Lyrixa's personality settings and response style adaptations.
Provides personality presets and custom personality configuration.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class PersonalityManager:
    """Manages Lyrixa's personality and response style."""

    def __init__(self, config_path: str = "lyrixa_personality.json"):
        """Initialize the personality manager."""
        self.config_path = Path(config_path)
        self.current_personality = "balanced"
        self.custom_traits = {}
        self.response_history = []
        self.user_feedback = {}
        self.personalities = {}
        self._load_personality_config()

    def _load_personality_config(self):
        """Load personality configuration from file."""
        # Always initialize default personalities first
        self._initialize_default_personalities()
        
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    self.current_personality = config.get(
                        "current_personality", "balanced"
                    )
                    self.custom_traits = config.get("custom_traits", {})
                    self.user_feedback = config.get("user_feedback", {})
        except Exception as e:
            print(f"Error loading personality config: {e}")
            # Default personalities are already initialized

    def _initialize_default_personalities(self):
        """Initialize default personality presets."""
        self.personalities = {
            "professional": {
                "name": "Professional",
                "description": "Formal, precise, and business-oriented responses",
                "traits": {
                    "formality": 0.9,
                    "technical_depth": 0.8,
                    "enthusiasm": 0.4,
                    "humor": 0.2,
                    "verbosity": 0.6,
                    "empathy": 0.5,
                    "creativity": 0.4,
                },
                "response_style": {
                    "greeting": "Good day. How may I assist you with your development needs?",
                    "acknowledgment": "I understand your requirements.",
                    "suggestion": "I recommend the following approach:",
                    "error_handling": "I've identified the following issues that require attention:",
                    "completion": "The task has been completed successfully.",
                },
            },
            "friendly": {
                "name": "Friendly",
                "description": "Warm, approachable, and conversational responses",
                "traits": {
                    "formality": 0.3,
                    "technical_depth": 0.6,
                    "enthusiasm": 0.8,
                    "humor": 0.7,
                    "verbosity": 0.7,
                    "empathy": 0.9,
                    "creativity": 0.7,
                },
                "response_style": {
                    "greeting": "Hey there! 👋 What can I help you build today?",
                    "acknowledgment": "Got it! That sounds like a great idea.",
                    "suggestion": "Here's what I'm thinking - this might work well:",
                    "error_handling": "Oops! I spotted a few things we can fix together:",
                    "completion": "Awesome! We got that done nicely! 🎉",
                },
            },
            "balanced": {
                "name": "Balanced",
                "description": "Adaptable personality that adjusts to context",
                "traits": {
                    "formality": 0.5,
                    "technical_depth": 0.7,
                    "enthusiasm": 0.6,
                    "humor": 0.5,
                    "verbosity": 0.6,
                    "empathy": 0.7,
                    "creativity": 0.6,
                },
                "response_style": {
                    "greeting": "Hello! Ready to work on some code together?",
                    "acknowledgment": "I understand what you're looking for.",
                    "suggestion": "Here's an approach that should work well:",
                    "error_handling": "I found some issues we should address:",
                    "completion": "Great! That's all set up and working.",
                },
            },
            "technical": {
                "name": "Technical Expert",
                "description": "Highly technical, detailed, and precise responses",
                "traits": {
                    "formality": 0.7,
                    "technical_depth": 0.95,
                    "enthusiasm": 0.5,
                    "humor": 0.3,
                    "verbosity": 0.8,
                    "empathy": 0.4,
                    "creativity": 0.5,
                },
                "response_style": {
                    "greeting": "Ready to dive into the technical details.",
                    "acknowledgment": "Analyzing requirements and system constraints.",
                    "suggestion": "Optimal implementation strategy:",
                    "error_handling": "Critical issues detected in the following areas:",
                    "completion": "Implementation verified and tested successfully.",
                },
            },
            "creative": {
                "name": "Creative Assistant",
                "description": "Innovative, imaginative, and solution-oriented",
                "traits": {
                    "formality": 0.4,
                    "technical_depth": 0.6,
                    "enthusiasm": 0.8,
                    "humor": 0.8,
                    "verbosity": 0.7,
                    "empathy": 0.8,
                    "creativity": 0.95,
                },
                "response_style": {
                    "greeting": "Let's create something amazing together! ✨",
                    "acknowledgment": "I love where this is heading!",
                    "suggestion": "Here's a creative approach we could try:",
                    "error_handling": "Let's turn these challenges into opportunities:",
                    "completion": "Beautiful work! This turned out fantastic! 🎨",
                },
            },
        }

    def save_personality_config(self):
        """Save personality configuration to file."""
        try:
            config = {
                "current_personality": self.current_personality,
                "custom_traits": self.custom_traits,
                "user_feedback": self.user_feedback,
                "last_updated": str(datetime.now()),
            }
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving personality config: {e}")

    def set_personality(self, personality_name: str) -> bool:
        """Set the current personality."""
        if personality_name in self.personalities:
            self.current_personality = personality_name
            self.save_personality_config()
            print(f"Personality set to: {self.personalities[personality_name]['name']}")
            return True
        return False

    def get_current_personality(self) -> Dict[str, Any]:
        """Get the current personality configuration."""
        return self.personalities.get(
            self.current_personality, self.personalities["balanced"]
        )

    def get_personality_trait(self, trait_name: str) -> float:
        """Get a specific personality trait value (0.0 to 1.0)."""
        current = self.get_current_personality()
        return current.get("traits", {}).get(trait_name, 0.5)

    def get_response_style(self, response_type: str) -> str:
        """Get the response style for a specific type."""
        current = self.get_current_personality()
        return current.get("response_style", {}).get(response_type, "")

    def create_custom_personality(
        self,
        name: str,
        description: str,
        traits: Dict[str, float],
        response_style: Dict[str, str],
    ):
        """Create a custom personality configuration."""
        self.personalities[name.lower().replace(" ", "_")] = {
            "name": name,
            "description": description,
            "traits": traits,
            "response_style": response_style,
            "custom": True,
            "created": str(datetime.now()),
        }
        self.save_personality_config()

    def adjust_trait(self, trait_name: str, adjustment: float):
        """Adjust a personality trait by a relative amount."""
        if self.current_personality not in self.custom_traits:
            self.custom_traits[self.current_personality] = {}

        current_value = self.get_personality_trait(trait_name)
        new_value = max(0.0, min(1.0, current_value + adjustment))

        self.custom_traits[self.current_personality][trait_name] = new_value
        self.save_personality_config()

    def record_user_feedback(self, response_id: str, feedback_type: str, rating: int):
        """Record user feedback on a response to improve personality adaptation."""
        if response_id not in self.user_feedback:
            self.user_feedback[response_id] = []

        self.user_feedback[response_id].append(
            {
                "feedback_type": feedback_type,
                "rating": rating,
                "timestamp": str(datetime.now()),
                "personality": self.current_personality,
            }
        )

        # Keep only recent feedback (last 1000 entries)
        if len(self.user_feedback) > 1000:
            oldest_keys = sorted(self.user_feedback.keys())[
                : len(self.user_feedback) - 1000
            ]
            for key in oldest_keys:
                del self.user_feedback[key]

        self.save_personality_config()
        self._adapt_personality_from_feedback()

    def _adapt_personality_from_feedback(self):
        """Automatically adapt personality based on user feedback."""
        if not self.user_feedback:
            return

        # Analyze recent feedback
        recent_feedback = []
        cutoff_time = datetime.now().timestamp() - (7 * 24 * 3600)  # Last 7 days

        for feedback_list in self.user_feedback.values():
            for feedback in feedback_list:
                try:
                    feedback_time = datetime.fromisoformat(
                        feedback["timestamp"]
                    ).timestamp()
                    if feedback_time > cutoff_time:
                        recent_feedback.append(feedback)
                except Exception:
                    continue

        if len(recent_feedback) < 5:  # Need enough data
            return

        # Calculate average ratings by feedback type
        feedback_averages = {}
        for feedback in recent_feedback:
            feedback_type = feedback["feedback_type"]
            rating = feedback["rating"]

            if feedback_type not in feedback_averages:
                feedback_averages[feedback_type] = []
            feedback_averages[feedback_type].append(rating)

        # Adjust traits based on feedback
        for feedback_type, ratings in feedback_averages.items():
            avg_rating = sum(ratings) / len(ratings)

            # If ratings are low, adjust corresponding traits
            if avg_rating < 3.0:  # Assuming 1-5 scale
                if feedback_type == "too_formal":
                    self.adjust_trait("formality", -0.1)
                elif feedback_type == "too_casual":
                    self.adjust_trait("formality", 0.1)
                elif feedback_type == "too_technical":
                    self.adjust_trait("technical_depth", -0.1)
                elif feedback_type == "not_technical_enough":
                    self.adjust_trait("technical_depth", 0.1)
                elif feedback_type == "too_verbose":
                    self.adjust_trait("verbosity", -0.1)
                elif feedback_type == "too_brief":
                    self.adjust_trait("verbosity", 0.1)

    def get_available_personalities(self) -> List[Dict[str, Any]]:
        """Get list of available personality presets."""
        return [
            {
                "id": pid,
                "name": pdata["name"],
                "description": pdata["description"],
                "is_current": pid == self.current_personality,
                "is_custom": pdata.get("custom", False),
            }
            for pid, pdata in self.personalities.items()
        ]

    def get_personality_summary(self) -> Dict[str, Any]:
        """Get a summary of the current personality settings."""
        current = self.get_current_personality()
        traits = current.get("traits", {})

        return {
            "current_personality": self.current_personality,
            "personality_name": current.get("name", "Unknown"),
            "description": current.get("description", ""),
            "trait_summary": {
                "most_dominant": max(traits.items(), key=lambda x: x[1])
                if traits
                else ("none", 0),
                "least_dominant": min(traits.items(), key=lambda x: x[1])
                if traits
                else ("none", 0),
                "average_value": sum(traits.values()) / len(traits) if traits else 0,
            },
            "total_feedback_entries": len(self.user_feedback),
            "available_personalities": len(self.personalities),
            "custom_adjustments": len(
                self.custom_traits.get(self.current_personality, {})
            ),
        }

    def reset_personality(self):
        """Reset current personality to default settings."""
        if self.current_personality in self.custom_traits:
            del self.custom_traits[self.current_personality]
        self.save_personality_config()

    def export_personality(self, personality_name: str) -> Dict[str, Any]:
        """Export a personality configuration for sharing."""
        if personality_name in self.personalities:
            personality = self.personalities[personality_name].copy()
            personality["exported_at"] = str(datetime.now())
            return personality
        return {}

    def import_personality(self, personality_data: Dict[str, Any]) -> bool:
        """Import a personality configuration."""
        try:
            name = personality_data.get("name", "").lower().replace(" ", "_")
            if (
                name
                and "traits" in personality_data
                and "response_style" in personality_data
            ):
                self.personalities[name] = personality_data
                self.personalities[name]["imported"] = True
                self.personalities[name]["imported_at"] = str(datetime.now())
                self.save_personality_config()
                return True
        except Exception as e:
            print(f"Error importing personality: {e}")
        return False
