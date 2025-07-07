# plugins/greet_plugin.py - Advanced Greeting Plugin
import datetime
from typing import Any, Dict

from core.plugin_manager import register_plugin


@register_plugin(
    name="greet_personal",
    description="Generate personalized greetings with context and time awareness",
    capabilities=["greetings", "personalization", "social"],
    version="1.0.0",
    author="AetherraCode Team",
    category="social",
    intent_purpose="personalized greeting generation",
    intent_triggers=["greet", "hello", "welcome", "introduce"],
    intent_scenarios=[
        "welcoming users personally",
        "creating friendly interactions",
        "time-appropriate greetings",
        "social engagement"
    ],
    ai_description="Creates personalized, context-aware greetings that consider time of day and user preferences.",
    example_usage="plugin: greet_personal 'Alice'",
    confidence_boost=1.1,
)
def greet_personal(name: str, style: str = "friendly") -> Dict[str, Any]:
    """Generate a personalized greeting"""
    try:
        if not name.strip():
            return {"error": "Name cannot be empty for personal greeting"}

        # Get current time for context
        current_hour = datetime.datetime.now().hour

        # Determine time-appropriate greeting
        if current_hour < 12:
            time_greeting = "Good morning"
        elif current_hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        # Style variations
        greetings = {
            "friendly": f"{time_greeting}, {name}! Great to see you here with AetherraCode!",
            "professional": f"{time_greeting}, {name}. Welcome to the AetherraCode environment.",
            "casual": f"Hey {name}! Hope you're having a great day with AetherraCode!",
            "enthusiastic": f"{time_greeting}, {name}! 🎉 Ready to code some amazing things together?"
        }

        greeting = greetings.get(style, greetings["friendly"])

        return {
            "success": True,
            "name": name,
            "greeting": greeting,
            "time_context": time_greeting,
            "style": style,
            "timestamp": datetime.datetime.now().isoformat(),
            "message": f"Personal greeting generated for {name}"
        }

    except Exception as e:
        return {"error": f"Personal greeting failed: {str(e)}", "success": False}


@register_plugin(
    name="greet_group",
    description="Generate greetings for groups or teams",
    capabilities=["group_greetings", "team_welcome", "social"],
    version="1.0.0",
    author="AetherraCode Team",
    category="social",
    example_usage="plugin: greet_group 'development team'",
    ai_description="Creates welcoming messages for groups, teams, or multiple people"
)
def greet_group(group_name: str, occasion: str = "general") -> Dict[str, Any]:
    """Generate a group greeting"""
    try:
        if not group_name.strip():
            return {"error": "Group name cannot be empty"}

        occasions = {
            "general": f"Welcome, {group_name}! Great to have everyone here.",
            "meeting": f"Hello {group_name}! Thanks for joining today's session.",
            "project": f"Greetings, {group_name}! Ready to build something amazing together?",
            "celebration": f"Congratulations, {group_name}! Let's celebrate this achievement!"
        }

        greeting = occasions.get(occasion, occasions["general"])

        return {
            "success": True,
            "group_name": group_name,
            "greeting": greeting,
            "occasion": occasion,
            "timestamp": datetime.datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": f"Group greeting failed: {str(e)}", "success": False}
