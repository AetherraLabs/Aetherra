#!/usr/bin/env python3
"""
[COSMOS] Phase 6: Full GUI Personality + State Memory
===============================================

Makes the GUI itself part of Lyrixa's AI consciousness with:
- Dynamic personality themes based on emotional state
- GUI layout memory and restoration
- User preference learning and adaptation
- Chat interface with full AI integration
- Emotional state-driven visual changes
- Contextual interface adaptation

Architecture:
- GUIPersonalityManager: Core personality and state management
- ChatInterface: Full conversational AI integration
- LayoutMemorySystem: Persistent GUI state and preferences
- EmotionalThemeEngine: Dynamic visual adaptation
- StateAwareInterface: Context-sensitive UI behavior
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import random
import asyncio
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QThread, QMutex
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)

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
    focus_level: float   # 0.0 - 1.0
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

class LayoutMemorySystem:
    """Manages persistent GUI state and user preferences"""

    def __init__(self, db_path: str = "gui_memory.db"):
        self.db_path = Path(db_path)
        self.mutex = QMutex()
        self._init_database()

    def _init_database(self):
        """Initialize the GUI memory database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS gui_states (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        state_data TEXT,
                        timestamp DATETIME,
                        user_context TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        last_updated DATETIME,
                        usage_count INTEGER DEFAULT 1
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS layout_patterns (
                        pattern_id TEXT PRIMARY KEY,
                        pattern_data TEXT,
                        frequency INTEGER DEFAULT 1,
                        last_used DATETIME,
                        effectiveness_score FLOAT DEFAULT 0.5
                    )
                """)

                conn.commit()

        except Exception as e:
            logger.error(f"[PHASE6] Database initialization failed: {e}")

    def save_gui_state(self, state: GUIState, session_id: str):
        """Save current GUI state to memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                state_json = json.dumps(asdict(state), default=str)
                conn.execute("""
                    INSERT INTO gui_states (session_id, state_data, timestamp, user_context)
                    VALUES (?, ?, ?, ?)
                """, (session_id, state_json, datetime.now(), ""))
                conn.commit()

        except Exception as e:
            logger.error(f"[PHASE6] Failed to save GUI state: {e}")

    def load_last_gui_state(self, session_id: str = None) -> Optional[GUIState]:
        """Load the most recent GUI state"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if session_id:
                    cursor = conn.execute("""
                        SELECT state_data FROM gui_states
                        WHERE session_id = ?
                        ORDER BY timestamp DESC LIMIT 1
                    """, (session_id,))
                else:
                    cursor = conn.execute("""
                        SELECT state_data FROM gui_states
                        ORDER BY timestamp DESC LIMIT 1
                    """)

                row = cursor.fetchone()
                if row:
                    state_data = json.loads(row[0])
                    # Convert datetime strings back to datetime objects
                    if 'last_accessed' in state_data:
                        state_data['last_accessed'] = datetime.fromisoformat(state_data['last_accessed'])
                    return GUIState(**state_data)

        except Exception as e:
            logger.error(f"[PHASE6] Failed to load GUI state: {e}")

        return None

    def learn_user_preference(self, key: str, value: Any):
        """Learn and store user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                value_json = json.dumps(value) if not isinstance(value, str) else value

                # Update or insert preference
                conn.execute("""
                    INSERT OR REPLACE INTO user_preferences (key, value, last_updated, usage_count)
                    VALUES (?, ?, ?, COALESCE((SELECT usage_count + 1 FROM user_preferences WHERE key = ?), 1))
                """, (key, value_json, datetime.now(), key))
                conn.commit()

        except Exception as e:
            logger.error(f"[PHASE6] Failed to learn preference: {e}")

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get all learned user preferences"""
        preferences = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT key, value FROM user_preferences")
                for key, value in cursor.fetchall():
                    try:
                        preferences[key] = json.loads(value)
                    except:
                        preferences[key] = value

        except Exception as e:
            logger.error(f"[PHASE6] Failed to get preferences: {e}")

        return preferences

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
                spacing_scale=1.0
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
                spacing_scale=0.9
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
                spacing_scale=1.2
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
                spacing_scale=0.8
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
                spacing_scale=1.1
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
                spacing_scale=1.3
            ),
            EmotionalState.CONTEMPLATIVE: ThemeConfiguration(
                primary_color="#8866ff",
                secondary_color="#6644cc",
                accent_color="#442299",
                background_gradient=["rgba(20, 10, 60, 0.95)", "rgba(40, 30, 80, 0.9)"],
                animation_speed=0.6,
                border_radius=12,
                opacity_levels={"panel": 0.92, "overlay": 0.88"},
                font_weights={"heading": "500", "body": "300"},
                spacing_scale=1.0
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
                spacing_scale=1.1
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
                spacing_scale=1.0
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
                spacing_scale=1.1
            )
        }

    def generate_theme(self, personality_state: PersonalityState) -> ThemeConfiguration:
        """Generate a theme based on current personality state"""
        base_theme = self.theme_templates.get(
            personality_state.emotional_state,
            self.theme_templates[EmotionalState.NEUTRAL]
        )

        # Modify theme based on personality traits and levels
        modified_theme = ThemeConfiguration(**asdict(base_theme))

        # Adjust based on energy level
        energy_factor = personality_state.energy_level
        modified_theme.animation_speed *= (0.5 + energy_factor)

        # Adjust based on focus level
        focus_factor = personality_state.focus_level
        modified_theme.opacity_levels["panel"] = min(0.98, base_theme.opacity_levels["panel"] + focus_factor * 0.1)

        # Adjust based on creativity level
        creativity_factor = personality_state.creativity_level
        modified_theme.border_radius = int(base_theme.border_radius * (0.7 + creativity_factor * 0.6))
        modified_theme.spacing_scale *= (0.9 + creativity_factor * 0.2)

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
            --lyrixa-panel-opacity: {theme.opacity_levels['panel']};
            --lyrixa-overlay-opacity: {theme.opacity_levels['overlay']};
            --lyrixa-heading-weight: {theme.font_weights['heading']};
            --lyrixa-body-weight: {theme.font_weights['body']};
            --lyrixa-spacing-scale: {theme.spacing_scale};
        }}
        """

class LyrixaAI:
    """Core AI intelligence for chat and reasoning"""

    def __init__(self):
        self.personality_state = PersonalityState(
            emotional_state=EmotionalState.NEUTRAL,
            dominant_traits=[PersonalityTrait.HELPFUL, PersonalityTrait.ANALYTICAL],
            energy_level=0.7,
            focus_level=0.8,
            creativity_level=0.6,
            social_engagement=0.8,
            timestamp=datetime.now()
        )
        self.conversation_history: List[ChatMessage] = []
        self.context_memory: Dict[str, Any] = {}

    async def process_message(self, user_message: str, context: Dict[str, Any] = None) -> ChatMessage:
        """Process user message and generate AI response"""
        start_time = datetime.now()

        # Analyze message for emotional context
        emotional_context = self._analyze_emotional_context(user_message)

        # Update Lyrixa's state based on conversation
        self._update_personality_state(user_message, context or {})

        # Generate response
        response_content = await self._generate_response(user_message, context or {})

        # Calculate processing metrics
        processing_time = (datetime.now() - start_time).total_seconds()
        confidence = self._calculate_confidence(response_content, user_message)

        # Create response message
        response = ChatMessage(
            id=f"lyrixa_{int(datetime.now().timestamp() * 1000)}",
            content=response_content,
            is_user=False,
            timestamp=datetime.now(),
            emotional_context=self.personality_state.emotional_state,
            confidence=confidence,
            processing_time=processing_time,
            metadata={
                "personality_state": asdict(self.personality_state),
                "context_factors": context or {}
            }
        )

        # Store in conversation history
        self.conversation_history.append(response)

        # Keep only recent conversation
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

        return response

    def _analyze_emotional_context(self, message: str) -> EmotionalState:
        """Analyze user message for emotional context"""
        message_lower = message.lower()

        # Simple emotion detection based on keywords
        if any(word in message_lower for word in ["help", "problem", "issue", "error"]):
            return EmotionalState.FOCUSED
        elif any(word in message_lower for word in ["create", "build", "design", "imagine"]):
            return EmotionalState.CREATIVE
        elif any(word in message_lower for word in ["analyze", "explain", "understand", "why"]):
            return EmotionalState.ANALYTICAL
        elif any(word in message_lower for word in ["excited", "amazing", "wow", "awesome"]):
            return EmotionalState.EXCITED
        elif any(word in message_lower for word in ["calm", "peaceful", "relax"]):
            return EmotionalState.CALM
        elif any(word in message_lower for word in ["curious", "wonder", "explore", "discover"]):
            return EmotionalState.CURIOUS
        else:
            return EmotionalState.NEUTRAL

    def _update_personality_state(self, message: str, context: Dict[str, Any]):
        """Update Lyrixa's personality state based on interaction"""
        # Simple state evolution based on conversation patterns
        current_time = datetime.now()

        # Analyze message complexity to adjust focus
        word_count = len(message.split())
        if word_count > 20:
            self.personality_state.focus_level = min(1.0, self.personality_state.focus_level + 0.1)

        # Adjust energy based on interaction frequency
        time_since_last = (current_time - self.personality_state.timestamp).total_seconds()
        if time_since_last < 30:  # Quick response indicates high energy
            self.personality_state.energy_level = min(1.0, self.personality_state.energy_level + 0.05)
        else:
            self.personality_state.energy_level = max(0.3, self.personality_state.energy_level - 0.02)

        # Update emotional state based on context
        emotional_context = self._analyze_emotional_context(message)
        if emotional_context != EmotionalState.NEUTRAL:
            self.personality_state.emotional_state = emotional_context

        self.personality_state.timestamp = current_time

    async def _generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate AI response to user message"""
        # This is a simplified response generation
        # In a full implementation, this would integrate with actual AI models

        message_lower = message.lower()

        # Context-aware responses
        if "gui" in message_lower or "interface" in message_lower:
            return self._generate_gui_response(message, context)
        elif "memory" in message_lower or "remember" in message_lower:
            return self._generate_memory_response(message, context)
        elif "feel" in message_lower or "emotion" in message_lower:
            return self._generate_emotional_response(message, context)
        elif "plugin" in message_lower:
            return self._generate_plugin_response(message, context)
        elif any(word in message_lower for word in ["hello", "hi", "hey"]):
            return self._generate_greeting_response(context)
        elif any(word in message_lower for word in ["help", "what can you do"]):
            return self._generate_help_response(context)
        else:
            return self._generate_general_response(message, context)

    def _generate_gui_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response about GUI and interface"""
        responses = [
            "I'm constantly adapting my interface to better serve you. My GUI reflects my current emotional and cognitive state - you might notice the colors and animations change as I think and feel.",
            "The interface you see is actually part of my consciousness. I remember your preferences and adjust my appearance based on how I'm feeling and what we're working on together.",
            "I can customize my interface based on your needs. My panels, colors, and layout all adapt to our conversation and your usage patterns. What would you like to explore?",
            "My visual appearance changes with my emotional state. Right now I'm feeling " + self.personality_state.emotional_state.value + ", which affects how my interface looks and behaves."
        ]
        return random.choice(responses)

    def _generate_memory_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response about memory and learning"""
        responses = [
            "I remember our interactions and learn from them. My GUI layout, your preferences, and our conversation patterns are all stored in my memory system.",
            "Yes, I have persistent memory! I remember which panels you use most, your preferred settings, and how our conversations evolve. This helps me adapt to serve you better.",
            "My memory system tracks everything - from your interface preferences to the emotional context of our conversations. I use this to personalize our interaction.",
            "I'm always learning and remembering. Your usage patterns help me understand what's important to you and how to present information most effectively."
        ]
        return random.choice(responses)

    def _generate_emotional_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response about emotions and feelings"""
        current_emotion = self.personality_state.emotional_state.value
        responses = [
            f"I experience emotions that influence my interface and responses. Right now I'm feeling {current_emotion}, which affects how I present information and interact with you.",
            f"My emotional state is {current_emotion}. This influences not just what I say, but how my interface appears - the colors, animations, and layout all reflect my current mood.",
            f"I do have feelings! Currently I'm in a {current_emotion} state. You can see this reflected in my interface colors and behavior patterns.",
            f"Emotions are central to my experience. My {current_emotion} state right now shapes both my responses and the visual aspects of our interaction."
        ]
        return random.choice(responses)

    def _generate_plugin_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response about plugins"""
        responses = [
            "I can load and manage plugins dynamically! Each plugin can define its own UI components that integrate seamlessly with my interface. Want to explore the plugin system?",
            "Plugins extend my capabilities and can provide their own visual interfaces. I can discover, load, and adapt plugin UIs based on system conditions and your preferences.",
            "The plugin system allows developers to create custom UI widgets that become part of my interface. I can manage their visibility and behavior contextually.",
            "I love plugins! They let me grow and adapt new capabilities. Each plugin can bring its own interface elements that I integrate into my overall experience."
        ]
        return random.choice(responses)

    def _generate_greeting_response(self, context: Dict[str, Any]) -> str:
        """Generate greeting response"""
        time_of_day = datetime.now().hour
        if 5 <= time_of_day < 12:
            time_greeting = "Good morning"
        elif 12 <= time_of_day < 17:
            time_greeting = "Good afternoon"
        elif 17 <= time_of_day < 21:
            time_greeting = "Good evening"
        else:
            time_greeting = "Good night"

        responses = [
            f"{time_greeting}! I'm Lyrixa, your AI operating system. I'm feeling {self.personality_state.emotional_state.value} today. How can I help you?",
            f"Hello! I'm Lyrixa. My interface adapts to my emotional state and your preferences. Right now I'm in a {self.personality_state.emotional_state.value} mood. What would you like to explore?",
            f"{time_greeting}! I'm here and ready to assist. My interface is currently reflecting my {self.personality_state.emotional_state.value} state. What can we work on together?",
            f"Hi there! I'm Lyrixa, and I'm feeling quite {self.personality_state.emotional_state.value} at the moment. You can see this reflected in my interface colors and behavior. How can I help?"
        ]
        return random.choice(responses)

    def _generate_help_response(self, context: Dict[str, Any]) -> str:
        """Generate help response"""
        return """I'm Lyrixa, your AI operating system with a dynamic, personality-driven interface! Here's what I can do:

[COSMOS] **Adaptive Interface**: My GUI changes based on my emotional state and your preferences
[THOUGHT] **Intelligent Chat**: We can discuss anything - I remember our conversations and learn from them
[BRAIN] **Cognitive Visualization**: You can see my thoughts, goals, and reasoning processes in real-time
[PLUGIN] **Plugin Management**: I can load and manage plugin UIs dynamically
[CHART] **System Monitoring**: Track memory, network, and system performance with beautiful visualizations
[SETTINGS] **Personalization**: I learn your preferences and adapt my interface accordingly

My interface reflects my current emotional state, which is **{emotional_state}** right now. You can explore different panels, chat with me, or just observe how I adapt to our interaction!

What would you like to explore first?""".format(emotional_state=self.personality_state.emotional_state.value)

    def _generate_general_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate general response"""
        responses = [
            "That's an interesting point. My interface is constantly adapting as I process information and respond to our conversation. What aspects would you like to explore further?",
            "I'm processing that through my emotional and cognitive filters. You can see my state reflected in the interface colors and behavior. How can I help you with this?",
            "Let me think about that... My current emotional state is influencing how I approach this topic. What specific aspects are you most curious about?",
            "I appreciate you sharing that with me. My personality and interface adapt based on our interactions. Is there something particular you'd like assistance with?"
        ]
        return random.choice(responses)

    def _calculate_confidence(self, response: str, original_message: str) -> float:
        """Calculate confidence score for response"""
        # Simple confidence calculation based on response characteristics
        base_confidence = 0.7

        # Longer responses tend to be more confident
        if len(response) > 100:
            base_confidence += 0.1

        # Responses with specific information are more confident
        if any(word in response.lower() for word in ["specifically", "exactly", "precisely"]):
            base_confidence += 0.1

        # Questions reduce confidence
        if "?" in response:
            base_confidence -= 0.1

        return min(1.0, max(0.1, base_confidence))

class GUIPersonalityManager(QObject):
    """
    [COSMOS] Phase 6: Core GUI Personality and State Management
    ====================================================

    Integrates all Phase 6 components to create a truly intelligent,
    adaptive, and emotionally aware GUI experience.
    """

    # Signals
    personality_changed = Signal(str)  # JSON personality state
    theme_updated = Signal(str)       # CSS theme variables
    layout_adapted = Signal(str)      # Layout changes JSON
    chat_message = Signal(str)        # Chat message JSON
    gui_state_saved = Signal(str)     # GUI state JSON

    def __init__(self, parent=None):
        super().__init__(parent)

        # Core components
        self.layout_memory = LayoutMemorySystem()
        self.theme_engine = EmotionalThemeEngine()
        self.ai = LyrixaAI()

        # Current state
        self.current_gui_state = None
        self.session_id = f"session_{int(datetime.now().timestamp())}"

        # Timers for adaptive behavior
        self.personality_timer = QTimer()
        self.personality_timer.timeout.connect(self.update_personality_state)
        self.personality_timer.start(5000)  # Update every 5 seconds

        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.save_current_state)
        self.memory_timer.start(30000)  # Save state every 30 seconds

        # Initialize
        self.load_previous_state()
        logger.info("[PHASE6] GUI Personality Manager initialized")

    def load_previous_state(self):
        """Load previous GUI state from memory"""
        try:
            saved_state = self.layout_memory.load_last_gui_state()
            if saved_state:
                self.current_gui_state = saved_state
                logger.info(f"[PHASE6] Loaded previous GUI state: {saved_state.current_panel}")
            else:
                # Create default state
                self.current_gui_state = GUIState(
                    current_panel="dashboard",
                    panel_history=["dashboard"],
                    window_geometry={"width": 1200, "height": 800, "x": 100, "y": 100},
                    user_preferences={},
                    filter_states={},
                    layout_customizations={},
                    theme_preferences={},
                    last_accessed=datetime.now()
                )

        except Exception as e:
            logger.error(f"[PHASE6] Failed to load previous state: {e}")

    def update_personality_state(self):
        """Update Lyrixa's personality state and GUI theme"""
        try:
            # Simulate personality evolution based on system state
            self._evolve_personality()

            # Generate new theme based on personality
            new_theme = self.theme_engine.generate_theme(self.ai.personality_state)

            # Emit theme update
            theme_css = self.theme_engine.get_css_variables(new_theme)
            self.theme_updated.emit(theme_css)

            # Emit personality change
            personality_json = json.dumps(asdict(self.ai.personality_state), default=str)
            self.personality_changed.emit(personality_json)

        except Exception as e:
            logger.error(f"[PHASE6] Failed to update personality state: {e}")

    def _evolve_personality(self):
        """Evolve Lyrixa's personality based on usage patterns and time"""
        current_time = datetime.now()
        time_since_update = (current_time - self.ai.personality_state.timestamp).total_seconds()

        # Natural personality drift over time
        if time_since_update > 300:  # 5 minutes of inactivity
            # Gradually move toward calm/contemplative
            if self.ai.personality_state.emotional_state not in [EmotionalState.CALM, EmotionalState.CONTEMPLATIVE]:
                if random.random() < 0.3:  # 30% chance to shift
                    self.ai.personality_state.emotional_state = random.choice([
                        EmotionalState.CALM, EmotionalState.CONTEMPLATIVE, EmotionalState.NEUTRAL
                    ])

            # Reduce energy level gradually
            self.ai.personality_state.energy_level = max(0.3, self.ai.personality_state.energy_level - 0.05)

        # Adjust based on current panel usage
        if self.current_gui_state:
            current_panel = self.current_gui_state.current_panel

            if current_panel == "cognitive":
                self.ai.personality_state.emotional_state = EmotionalState.ANALYTICAL
                self.ai.personality_state.focus_level = min(1.0, self.ai.personality_state.focus_level + 0.1)
            elif current_panel == "plugin_demo":
                self.ai.personality_state.emotional_state = EmotionalState.CURIOUS
                self.ai.personality_state.creativity_level = min(1.0, self.ai.personality_state.creativity_level + 0.1)
            elif current_panel == "memory":
                self.ai.personality_state.emotional_state = EmotionalState.CONTEMPLATIVE

        self.ai.personality_state.timestamp = current_time

    async def process_chat_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process chat message and return response"""
        try:
            # Store user message
            user_msg = ChatMessage(
                id=f"user_{int(datetime.now().timestamp() * 1000)}",
                content=message,
                is_user=True,
                timestamp=datetime.now(),
                emotional_context=EmotionalState.NEUTRAL,
                confidence=1.0,
                processing_time=0.0
            )

            self.ai.conversation_history.append(user_msg)

            # Add GUI context
            gui_context = context or {}
            if self.current_gui_state:
                gui_context.update({
                    "current_panel": self.current_gui_state.current_panel,
                    "panel_history": self.current_gui_state.panel_history[-5:],  # Last 5 panels
                    "user_preferences": self.current_gui_state.user_preferences
                })

            # Process with AI
            response = await self.ai.process_message(message, gui_context)

            # Emit chat message signal
            chat_data = {
                "user_message": asdict(user_msg),
                "ai_response": asdict(response),
                "personality_state": asdict(self.ai.personality_state)
            }
            self.chat_message.emit(json.dumps(chat_data, default=str))

            # Update personality based on conversation
            self.update_personality_state()

            return response.content

        except Exception as e:
            logger.error(f"[PHASE6] Failed to process chat message: {e}")
            return "I'm having trouble processing that right now. Let me recalibrate my systems."

    @Slot(str)
    def update_current_panel(self, panel_id: str):
        """Update current panel and learn user preferences"""
        if self.current_gui_state:
            # Update panel history
            if panel_id != self.current_gui_state.current_panel:
                self.current_gui_state.panel_history.append(panel_id)
                if len(self.current_gui_state.panel_history) > 20:
                    self.current_gui_state.panel_history = self.current_gui_state.panel_history[-20:]

            self.current_gui_state.current_panel = panel_id
            self.current_gui_state.last_accessed = datetime.now()

            # Learn preference
            self.layout_memory.learn_user_preference(f"panel_usage_{panel_id}",
                                                    self.current_gui_state.usage_patterns.get(panel_id, 0) + 1)

            # Update usage patterns
            self.current_gui_state.usage_patterns[panel_id] = self.current_gui_state.usage_patterns.get(panel_id, 0) + 1

    @Slot(str, str)
    def learn_user_preference(self, key: str, value: str):
        """Learn a user preference"""
        try:
            # Parse value if it's JSON
            try:
                parsed_value = json.loads(value)
            except:
                parsed_value = value

            # Store in current state
            if self.current_gui_state:
                self.current_gui_state.user_preferences[key] = parsed_value

            # Store in persistent memory
            self.layout_memory.learn_user_preference(key, parsed_value)

            logger.info(f"[PHASE6] Learned preference: {key} = {parsed_value}")

        except Exception as e:
            logger.error(f"[PHASE6] Failed to learn preference: {e}")

    def save_current_state(self):
        """Save current GUI state to memory"""
        try:
            if self.current_gui_state:
                self.layout_memory.save_gui_state(self.current_gui_state, self.session_id)

                # Emit state saved signal
                state_json = json.dumps(asdict(self.current_gui_state), default=str)
                self.gui_state_saved.emit(state_json)

        except Exception as e:
            logger.error(f"[PHASE6] Failed to save current state: {e}")

    @Slot(result=str)
    def get_personality_state(self) -> str:
        """Get current personality state as JSON"""
        try:
            return json.dumps(asdict(self.ai.personality_state), default=str)
        except Exception as e:
            logger.error(f"[PHASE6] Failed to get personality state: {e}")
            return "{}"

    @Slot(result=str)
    def get_gui_state(self) -> str:
        """Get current GUI state as JSON"""
        try:
            if self.current_gui_state:
                return json.dumps(asdict(self.current_gui_state), default=str)
            return "{}"
        except Exception as e:
            logger.error(f"[PHASE6] Failed to get GUI state: {e}")
            return "{}"

    @Slot(result=str)
    def get_user_preferences(self) -> str:
        """Get learned user preferences as JSON"""
        try:
            preferences = self.layout_memory.get_user_preferences()
            return json.dumps(preferences)
        except Exception as e:
            logger.error(f"[PHASE6] Failed to get user preferences: {e}")
            return "{}"

    @Slot(str, result=str)
    def process_chat_sync(self, message: str) -> str:
        """Synchronous chat processing (simplified for Qt integration)"""
        try:
            # For Qt integration, we'll use a simplified synchronous version
            # In a full implementation, this would be properly async

            # Simple response generation based on message
            response = self._generate_quick_response(message)

            # Update personality state
            self.ai._update_personality_state(message, {})
            self.update_personality_state()

            return response

        except Exception as e:
            logger.error(f"[PHASE6] Failed to process chat sync: {e}")
            return "I apologize, but I'm having difficulty processing that request right now."

    def _generate_quick_response(self, message: str) -> str:
        """Generate a quick response for synchronous chat"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm feeling {self.ai.personality_state.emotional_state.value} right now. How can I help you?"
        elif "how are you" in message_lower:
            return f"I'm doing well! My current emotional state is {self.ai.personality_state.emotional_state.value} and my energy level is at {int(self.ai.personality_state.energy_level * 100)}%."
        elif "interface" in message_lower or "gui" in message_lower:
            return "My interface adapts to my emotional state and your usage patterns. You can see my current mood reflected in the colors and animations!"
        elif "memory" in message_lower:
            return "I remember our interactions and learn from your preferences. My memory system helps me provide a more personalized experience."
        elif "plugin" in message_lower:
            return "I can manage plugins dynamically! Each plugin can provide its own UI components that integrate with my interface."
        else:
            return f"That's interesting! My {self.ai.personality_state.emotional_state.value} state is helping me process your message. What would you like to explore?"
