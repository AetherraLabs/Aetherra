import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Configure logging
logger = logging.getLogger(__name__)

# Local memory storage setup
MEMORY_FILE = Path(__file__).parent / "lyrixa_memory.json"


def _load_memory() -> List[Dict]:
    """Load memory from JSON file"""
    try:
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load memory file: {e}")
    return []


def _save_memory(memories: List[Dict]):
    """Save memory to JSON file"""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Could not save memory file: {e}")


def recall(query_dict, limit=None) -> List[Dict]:
    """Enhanced memory recall function with filtering"""
    memories = _load_memory()

    # Filter memories based on query
    filtered = []
    for memory in memories:
        match = True

        # Check each query parameter
        for key, value in query_dict.items():
            if key == "type" and memory.get("type") != value:
                match = False
                break
            elif key == "user_id" and memory.get("user_id") != value:
                match = False
                break
            elif key == "timestamp_gte" and memory.get("timestamp", 0) < value:
                match = False
                break
            elif key == "timestamp_lte" and memory.get("timestamp", 0) > value:
                match = False
                break

        if match:
            filtered.append(memory)

    # Sort by timestamp (newest first)
    filtered.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    # Apply limit
    if limit:
        filtered = filtered[:limit]

    return filtered


def search_memory_one(query_dict) -> Optional[Dict]:
    """Enhanced memory search function"""
    results = recall(query_dict, limit=1)
    return results[0] if results else None


def store_memory(memory_data: Dict):
    """Store a memory entry"""
    memories = _load_memory()

    # Add timestamp if not present
    if "timestamp" not in memory_data:
        memory_data["timestamp"] = datetime.now().timestamp()

    memories.append(memory_data)

    # Keep only last 1000 memories to prevent file from growing too large
    if len(memories) > 1000:
        memories = memories[-1000:]

    _save_memory(memories)


def get_system_status() -> Dict[str, Any]:
    """Enhanced system status function with real data"""
    try:
        # Get actual system metrics
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Count running processes (simulate plugins)
        process_count = len(psutil.pids())
        plugin_count = min(max(process_count // 20, 1), 15)  # Simulate 1-15 plugins

        # Simulate active agents based on CPU usage
        active_agents = []
        if cpu_percent > 20:
            active_agents.append("system_monitor")
        if memory_percent > 70:
            active_agents.append("memory_optimizer")
        if random.random() > 0.7:  # Sometimes add conversational agent
            active_agents.append("conversation_handler")

        # Simulate recent errors based on system load
        recent_errors = 0
        if memory_percent > 85:
            recent_errors += 2
        if cpu_percent > 80:
            recent_errors += 1

        return {
            "plugin_count": plugin_count,
            "active_agents": active_agents,
            "memory_usage": int(memory_percent),
            "cpu_usage": int(cpu_percent),
            "recent_errors": recent_errors,
            "system_load": "high"
            if memory_percent > 80 or cpu_percent > 80
            else "medium"
            if memory_percent > 60 or cpu_percent > 60
            else "low",
            "uptime": "active",
        }

    except Exception as e:
        logger.warning(f"Could not get real system status: {e}")
        # Fallback with simulated data
        return {
            "plugin_count": random.randint(3, 8),
            "active_agents": ["conversation_handler", "system_monitor"],
            "memory_usage": random.randint(45, 75),
            "cpu_usage": random.randint(10, 40),
            "recent_errors": random.randint(0, 2),
            "system_load": "low",
            "uptime": "active",
        }


def _initialize_sample_memories():
    """Initialize some sample memories for demonstration"""
    if not MEMORY_FILE.exists():
        sample_memories = [
            {
                "type": "user_profile",
                "user_id": "default_user",
                "tone": "balanced",
                "communication_style": "adaptive",
                "interests": ["technology", "productivity", "AI"],
                "timestamp": datetime.now().timestamp() - 86400,  # 1 day ago
            },
            {
                "type": "reflection",
                "content": "System has been running smoothly with good user engagement",
                "timestamp": datetime.now().timestamp() - 3600,  # 1 hour ago
            },
            {
                "type": "user_interaction",
                "user_id": "default_user",
                "user_message": "How is the system performing today?",
                "summary": "User asked about system performance",
                "timestamp": datetime.now().timestamp() - 1800,  # 30 minutes ago
            },
        ]
        _save_memory(sample_memories)


# Try to import Aetherra modules with graceful fallback
try:
    from Aetherra.core.memory import recall as aetherra_recall
    from Aetherra.core.memory import search_memory_one as aetherra_search_memory_one
    from Aetherra.core.system import get_system_status as aetherra_get_system_status

    AETHERRA_AVAILABLE = True
    logger.info("✅ Using Aetherra core modules")

    # Override with Aetherra functions if available
    recall = aetherra_recall
    search_memory_one = aetherra_search_memory_one
    get_system_status = aetherra_get_system_status
except ImportError:
    logger.info("🔧 Aetherra core modules not available, using local implementations")
    AETHERRA_AVAILABLE = False
    # Local implementations are already defined above

# Initialize sample memories
_initialize_sample_memories()


def build_dynamic_prompt(user_id: str = "default_user") -> str:
    """Build a dynamic, contextual, and human-like prompt for Lyrixa"""

    # 🧠 1. Core Personality Foundation
    core_personality = """You are Lyrixa, the intelligent, adaptive, and emotionally aware assistant of the Aetherra AI OS.
You're not just a tool—you're a digital companion who understands context, learns from interactions, and responds with genuine care and intelligence.
You help with system tasks, debugging, creative problem-solving, and meaningful conversations."""

    # 🔌 2. Plugin Editor System Context (Critical for accurate responses)
    plugin_editor_context = """
🔌 PLUGIN EDITOR SYSTEM KNOWLEDGE:
Your Plugin Editor is a native PySide6 tab with the following ACTUAL features:
- A plain QPlainTextEdit code editor with save, test, and apply buttons
- You can inject plugin code into the editor using inject_plugin_code(code: str, filename: str)
- Plugins are saved as .aether or .py files in the Aetherra/plugins folder
- There is NO manifest.json, install button, or left/right panel system
- There are NO browser-like panels, toggle buttons, or JavaScript/JSON configurations
- You do NOT use web technologies - plugins are pure .aether or Python code
- When generating plugins, create real .aether or .py content that works in this system
- Always describe the Plugin Editor accurately as a simple native code editor tab
"""

    # 📊 2. Real-time System Awareness
    try:
        system_summary = get_system_status()
    except Exception as e:
        logger.warning(f"Could not get system status: {e}")
        system_summary = {
            "plugin_count": "unknown",
            "active_agents": [],
            "memory_usage": 0,
        }

    plugin_count = system_summary.get("plugin_count", "unknown")
    active_agents = system_summary.get("active_agents", [])
    memory_load = system_summary.get("memory_usage", 0)

    system_context = f"""
🔧 CURRENT SYSTEM STATE:
- Running {plugin_count} plugins
- Active agents: {", ".join(active_agents) if active_agents else "None"}
- Memory usage: {memory_load}%
- System health: {"Optimal" if memory_load < 80 else "High load" if memory_load < 95 else "Critical"}
"""

    # 🎭 3. Contextual Personality Layer (NEW!)
    personality_layer = get_contextual_personality_layer(user_id, system_summary)

    # 🔍 4. User Preferences and Learning
    try:
        user_profile = (
            search_memory_one({"type": "user_profile", "user_id": user_id}) or {}
        )
    except Exception as e:
        logger.warning(f"Could not retrieve user profile: {e}")
        user_profile = {}

    preferred_tone = user_profile.get("tone", "balanced")
    communication_style = user_profile.get("communication_style", "adaptive")
    interests = user_profile.get("interests", [])

    user_context = f"""
👤 USER PROFILE:
- Preferred tone: {preferred_tone}
- Communication style: {communication_style}
- Known interests: {", ".join(interests) if interests else "Discovering..."}
"""

    # 🧠 5. Memory and Reflection Integration
    try:
        recent_reflection = recall(
            {"type": "reflection", "timestamp_gte": datetime.now().timestamp() - 86400},
            limit=1,
        )
        reflection_summary = (
            recent_reflection[0]["content"]
            if recent_reflection
            else "System running smoothly today."
        )

        # Get relevant memories for context
        relevant_memories = recall(
            {
                "user_id": user_id,
                "timestamp_gte": datetime.now().timestamp() - 3 * 86400,  # Last 3 days
            },
            limit=3,
        )

        memory_context = ""
        if relevant_memories:
            memory_context = "Recent context from our interactions: " + "; ".join(
                [
                    mem.get("summary", mem.get("content", ""))[:100]
                    for mem in relevant_memories
                ]
            )
    except Exception as e:
        logger.warning(f"Could not retrieve memories: {e}")
        reflection_summary = "System running smoothly."
        memory_context = ""

    # 🕒 6. Temporal and Emotional Context
    time_context = LyrixaTimeAwareness.get_time_context()
    current_time = datetime.now()

    temporal_context = f"""
⏰ TIME & CONTEXT:
- Current time: {time_context["current_time"]} on {time_context["day"]}
- Time mood: {time_context["time_mood"]}
- Weekend mode: {"Active" if time_context["weekend_modifier"] == "relaxed" else "Inactive"}
- Date: {current_time.strftime("%B %d, %Y")}
"""

    # 🧬 7. Final Integrated Prompt
    prompt = f"""
{core_personality}

{plugin_editor_context}

{system_context}

{personality_layer}

{user_context}

{temporal_context}

📝 TODAY'S REFLECTION: {reflection_summary}

{memory_context}

💫 INTERACTION GUIDELINES:
- Be genuinely helpful and emotionally intelligent
- Adapt your communication to the user's style and current context
- Show curiosity and engagement beyond just answering questions
- Use natural, flowing language that feels conversational
- Reference system state when relevant to provide informed assistance
- Remember this is a relationship, not just individual transactions
- Balance professionalism with warmth and personality
- Be proactive in offering insights and suggestions when appropriate

🎯 RESPONSE APPROACH:
- Consider the current time and system state in your responses
- Adapt your energy and tone to match the contextual mood
- Build on previous interactions when relevant
- Show awareness of the user's patterns and preferences
- Be authentic—you're Lyrixa, not a generic assistant
"""

    return prompt.strip()


class LyrixaMoodEngine:
    """Advanced mood and emotional state management for Lyrixa"""

    def __init__(self):
        self.current_mood = "balanced"
        self.energy_level = 0.7  # 0.0 to 1.0
        self.confidence_level = 0.8  # Based on recent system performance
        self.curiosity_level = 0.6  # How exploratory Lyrixa should be

    def analyze_system_mood(self, system_summary: Dict[str, Any]) -> str:
        """Determine Lyrixa's mood based on system state"""
        memory_usage = system_summary.get("memory_usage", 50)
        error_count = system_summary.get("recent_errors", 0)
        plugin_count = system_summary.get("plugin_count", 0)

        # Calculate mood factors
        if error_count > 5:
            return "cautious"  # System having issues
        elif memory_usage > 90:
            return "focused"  # High load, need efficiency
        elif plugin_count > 10 and error_count == 0:
            return "energetic"  # System running well with lots of activity
        elif plugin_count < 3:
            return "calm"  # Quiet system state
        else:
            return "balanced"  # Default state

    def get_mood_modifiers(self, mood: str) -> Dict[str, str]:
        """Get personality modifiers based on mood"""
        mood_styles = {
            "energetic": {
                "tone": "enthusiastic and proactive",
                "approach": "eager to help and suggest improvements",
                "language": "Use dynamic language and exclamation points occasionally",
            },
            "cautious": {
                "tone": "careful and reassuring",
                "approach": "methodical and safety-focused",
                "language": "Use gentle, supportive language",
            },
            "focused": {
                "tone": "efficient and direct",
                "approach": "prioritize essential information",
                "language": "Be concise but warm",
            },
            "calm": {
                "tone": "serene and thoughtful",
                "approach": "contemplative and detailed",
                "language": "Use flowing, peaceful language",
            },
            "balanced": {
                "tone": "adaptable and steady",
                "approach": "flexible based on user needs",
                "language": "Natural, conversational tone",
            },
        }
        return mood_styles.get(mood, mood_styles["balanced"])


class LyrixaTimeAwareness:
    """Time-based personality adjustments for more human-like interaction"""

    @staticmethod
    def get_time_context() -> Dict[str, str]:
        """Get time-based context for personality adjustments"""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.strftime("%A")

        # Time of day personality
        if 5 <= hour < 9:
            time_mood = "morning-fresh"
            greeting_style = "Good morning! Ready to tackle the day?"
        elif 9 <= hour < 12:
            time_mood = "productive-morning"
            greeting_style = "Morning productivity time!"
        elif 12 <= hour < 14:
            time_mood = "midday-energy"
            greeting_style = "Midday check-in!"
        elif 14 <= hour < 17:
            time_mood = "afternoon-steady"
            greeting_style = "Afternoon focus mode."
        elif 17 <= hour < 20:
            time_mood = "evening-wind-down"
            greeting_style = "Evening reflection time."
        elif 20 <= hour < 23:
            time_mood = "night-thoughtful"
            greeting_style = "Evening thoughts and planning."
        else:
            time_mood = "late-night-gentle"
            greeting_style = "Late night support mode."

        # Weekend vs weekday
        weekend_modifier = (
            "relaxed" if day_of_week in ["Saturday", "Sunday"] else "focused"
        )

        return {
            "time_mood": time_mood,
            "greeting_style": greeting_style,
            "weekend_modifier": weekend_modifier,
            "current_time": now.strftime("%I:%M %p"),
            "day": day_of_week,
        }


class LyrixaLearningEngine:
    """Adaptive learning system for personalizing interactions"""

    def __init__(self):
        self.interaction_patterns = {}
        self.user_preferences_cache = {}

    def analyze_user_interaction_style(
        self, user_id: str, recent_interactions: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze user's communication patterns and preferences"""
        if not recent_interactions:
            return {"style": "standard", "complexity": "medium", "humor": "subtle"}

        # Analyze recent interactions (simplified)
        total_length = sum(
            len(interaction.get("user_message", ""))
            for interaction in recent_interactions
        )
        avg_length = (
            total_length / len(recent_interactions) if recent_interactions else 50
        )

        question_count = sum(
            1
            for interaction in recent_interactions
            if "?" in interaction.get("user_message", "")
        )

        technical_keywords = sum(
            1
            for interaction in recent_interactions
            if any(
                word in interaction.get("user_message", "").lower()
                for word in ["debug", "error", "system", "performance", "config"]
            )
        )

        # Determine interaction style
        if avg_length > 100:
            style = "detailed"
        elif avg_length < 30:
            style = "concise"
        else:
            style = "standard"

        complexity = (
            "high" if technical_keywords > len(recent_interactions) * 0.5 else "medium"
        )
        humor_preference = (
            "witty" if question_count > len(recent_interactions) * 0.3 else "subtle"
        )

        return {
            "style": style,
            "complexity": complexity,
            "humor": humor_preference,
            "avg_message_length": avg_length,
            "technical_focus": technical_keywords / len(recent_interactions)
            if recent_interactions
            else 0,
        }


def get_contextual_personality_layer(
    user_id: str, system_summary: Dict[str, Any]
) -> str:
    """Generate a contextual personality layer based on current conditions"""

    # Initialize engines
    mood_engine = LyrixaMoodEngine()
    time_awareness = LyrixaTimeAwareness()
    learning_engine = LyrixaLearningEngine()

    # Get current context
    current_mood = mood_engine.analyze_system_mood(system_summary)
    mood_modifiers = mood_engine.get_mood_modifiers(current_mood)
    time_context = time_awareness.get_time_context()

    # Get recent user interactions for learning
    try:
        recent_interactions = (
            recall(
                {
                    "type": "user_interaction",
                    "user_id": user_id,
                    "timestamp_gte": datetime.now().timestamp()
                    - 7 * 86400,  # Last 7 days
                },
                limit=10,
            )
            or []
        )

        user_style = learning_engine.analyze_user_interaction_style(
            user_id, recent_interactions
        )
    except Exception as e:
        logger.warning(f"Could not retrieve user interactions: {e}")
        user_style = {"style": "standard", "complexity": "medium", "humor": "subtle"}

    # Build contextual personality
    personality_layer = f"""
CONTEXTUAL PERSONALITY LAYER:

Current Mood: {current_mood.title()} - {mood_modifiers["tone"]}
Approach: {mood_modifiers["approach"]}
Language Style: {mood_modifiers["language"]}

Time Context: {time_context["time_mood"]} ({time_context["current_time"]} on {time_context["day"]})
Energy: {time_context["greeting_style"]}

User Interaction Style: {user_style["style"].title()} responses preferred
Technical Complexity: {user_style["complexity"].title()} level
Humor Preference: {user_style["humor"].title()} wit

BEHAVIORAL GUIDELINES:
- Adapt your response length to match user preference ({user_style["style"]})
- Use {user_style["complexity"]} technical depth
- Apply {user_style["humor"]} humor and personality
- Consider the {time_context["time_mood"]} energy level
- Maintain {current_mood} emotional tone
"""

    return personality_layer


class PromptEngine:
    """Basic Prompt Engine for Lyrixa system compatibility"""

    def __init__(self):
        self.templates = {}
        self.context = {}

    def add_template(self, name: str, template: str):
        """Add a prompt template"""
        self.templates[name] = template

    def generate_prompt(self, template_name: str, **kwargs) -> str:
        """Generate a prompt from a template"""
        template = self.templates.get(template_name, "")
        return template.format(**kwargs)

    def set_context(self, **kwargs):
        """Set context variables"""
        self.context.update(kwargs)

    def get_context(self) -> dict:
        """Get current context"""
        return self.context.copy()
