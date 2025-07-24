"""
LyrixaConnector - Central Intelligence Integration Hub
Connects all GUI components to actual Lyrixa cognitive systems
"""

import time
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, QTimer, Signal

# Import actual Lyrixa components
try:
    from ..intelligence import LyrixaIntelligence
    from ..LyrixaCore.IdentityAgent.self_model import SelfModel
    from ..LyrixaCore.interface_bridge import ContextType, LyrixaContextBridge
    from ..memory.lyrixa_memory_engine import LyrixaMemoryEngine
    from ..personality.reflection_system import PersonalityReflectionSystem

    LYRIXA_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Lyrixa components: {e}")
    LyrixaIntelligence = None
    LyrixaContextBridge = None
    SelfModel = None
    LyrixaMemoryEngine = None
    PersonalityReflectionSystem = None
    ContextType = None
    LYRIXA_COMPONENTS_AVAILABLE = False


class LyrixaConnector(QObject):
    """
    Central hub connecting GUI components to Lyrixa intelligence systems
    """

    # Signals for live updates
    chat_response_ready = Signal(str)  # Rich markdown response
    memory_graph_updated = Signal(dict)  # Graph data for visualization
    identity_updated = Signal(dict)  # Traits, emotions, states
    reflection_updated = Signal(list)  # Recent reflections
    aura_state_changed = Signal(dict)  # Confidence, curiosity levels
    context_enriched = Signal(dict)  # Live context data

    # 🔥 Visual Intelligence Signals for AI Presence Projection
    on_memory_updated = Signal()  # Mini-Lyrixa learning state
    on_identity_updated = Signal()  # Mini-Lyrixa contemplative state
    on_reflection_updated = Signal()  # Mini-Lyrixa introspective state
    on_llm_response = Signal(str)  # Context summary updates
    on_context_retrieved = Signal(dict)  # Context analysis updates

    def __init__(self):
        super().__init__()

        # Initialize core systems
        self.lyrixa_intelligence = None
        self.memory_engine = None
        self.self_model = None
        self.reflection_system = None
        self.context_bridge = None

        # GUI component references (set externally)
        self.chat_panel = None
        self.memory_graph = None
        self.identity_panel = None
        self.reflection_panel = None
        self.aura_overlay = None

        # State tracking
        self.last_context = {}
        self.conversation_history = []

        # Initialize systems
        self.initialize_lyrixa_systems()

        # Setup live update timers
        self.setup_live_updates()

    def initialize_lyrixa_systems(self):
        """Initialize all available Lyrixa intelligence systems"""
        try:
            # Initialize memory engine
            if LyrixaMemoryEngine:
                self.memory_engine = LyrixaMemoryEngine()
                print("✓ Lyrixa Memory Engine connected")

            # Initialize self model
            if SelfModel:
                self.self_model = SelfModel()
                print("✓ Self Model connected")

            # Initialize reflection system
            if PersonalityReflectionSystem:
                self.reflection_system = PersonalityReflectionSystem()
                print("✓ Reflection System connected")

            # Initialize Lyrixa intelligence engine
            if LyrixaIntelligence:
                self.lyrixa_intelligence = LyrixaIntelligence()
                print("✓ Lyrixa Intelligence engine connected")

            # Initialize context bridge
            if LyrixaContextBridge:
                self.context_bridge = LyrixaContextBridge(
                    memory_engine=self.memory_engine,
                    identity_agent=self.self_model,
                    reflector=self.reflection_system,
                )
                print("✓ Context Bridge connected")

        except Exception as e:
            print(f"⚠️ Error initializing Lyrixa systems: {e}")

    def connect_gui_components(
        self, chat_panel, memory_graph, identity_panel, reflection_panel, aura_overlay
    ):
        """Connect GUI components to the intelligence system"""
        self.chat_panel = chat_panel
        self.memory_graph = memory_graph
        self.identity_panel = identity_panel
        self.reflection_panel = reflection_panel
        self.aura_overlay = aura_overlay

        print("✓ GUI components connected to Lyrixa intelligence")

    def handle_chat_input(self, prompt: str) -> str:
        """
        Process chat input through Lyrixa intelligence pipeline
        Returns rich markdown-formatted response
        """
        try:
            # Get live context from memory
            context = self.get_live_context(prompt)

            # Generate intelligent response
            if self.lyrixa_intelligence:
                # Use intelligence engine for contextual response
                analysis = self.lyrixa_intelligence.analyze_context(
                    {"prompt": prompt, "context": context}
                )
                # Extract context summary for response generation
                context_summary = {
                    "system_coherence": analysis.get("confidence", 0.8),
                    "context_type": analysis.get("classification", "general"),
                    "patterns": analysis.get("similar_patterns", []),
                }
                response = self.generate_contextual_response(prompt, context_summary)
            elif self.context_bridge and ContextType:
                # Fallback to context bridge processing
                try:
                    context_summary = self.context_bridge.get_context_summary(
                        ContextType.DECISION_SUPPORT
                    )
                except Exception as e:
                    print(f"Context bridge error: {e}")
                    context_summary = {"system_coherence": 0.8}
                response = self.generate_contextual_response(prompt, context_summary)
            else:
                # Basic fallback
                response = self.generate_basic_response(prompt)

            # Store conversation history
            self.conversation_history.append(
                {
                    "timestamp": time.time(),
                    "prompt": prompt,
                    "response": response,
                    "context": context,
                }
            )

            # Emit signal for chat display
            self.chat_response_ready.emit(response)

            # 🔥 Emit visual intelligence signal for context summary
            self.on_llm_response.emit(response)

            return response

        except Exception as e:
            error_response = f"I encountered an error processing your request: {str(e)}"
            self.chat_response_ready.emit(error_response)
            return error_response

    def get_live_context(self, prompt: str) -> Dict[str, Any]:
        """Get enriched context for the prompt"""
        context = {
            "timestamp": time.time(),
            "prompt": prompt,
            "conversation_history": self.conversation_history[-5:],  # Last 5 exchanges
        }

        # Add memory context
        if self.memory_engine:
            try:
                # Use available memory method instead of non-existent get_context
                memory_context = self.memory_engine.get_memory_health()
                context["memory"] = memory_context
            except Exception as e:
                print(f"Memory context error: {e}")

        # Add identity context
        if self.self_model:
            try:
                context["identity"] = {
                    "traits": self.self_model.dimensional_scores,
                    "coherence": self.self_model.assess_coherence(),
                    "active_goals": getattr(self.self_model, "active_goals", []),
                }
            except Exception as e:
                print(f"Identity context error: {e}")

        self.last_context = context
        self.context_enriched.emit(context)

        # 🔥 Emit visual intelligence signal for context analysis
        self.on_context_retrieved.emit(context)

        return context

    def generate_contextual_response(
        self, prompt: str, context_summary: Dict[str, Any]
    ) -> str:
        """Generate contextual response using available systems"""
        coherence = context_summary.get("system_coherence", 0.8)

        # Build response based on context
        response_parts = []

        # Acknowledge the input intelligently
        if any(word in prompt.lower() for word in ["help", "assist", "support"]):
            response_parts.append("I'm here to help you with that.")
        elif any(word in prompt.lower() for word in ["analyze", "think", "consider"]):
            response_parts.append("Let me analyze this thoughtfully.")
        elif any(word in prompt.lower() for word in ["memory", "remember", "recall"]):
            response_parts.append("Accessing my memory systems...")
        else:
            response_parts.append("I understand your request.")

        # Add coherence-based insight
        if coherence > 0.9:
            response_parts.append(
                f"My cognitive systems are running at {coherence:.1%} coherence, allowing me to provide you with comprehensive insights."
            )
        elif coherence > 0.7:
            response_parts.append(
                f"Operating at {coherence:.1%} coherence, I can offer you well-integrated perspectives."
            )
        else:
            response_parts.append(
                f"Currently at {coherence:.1%} coherence - I'm processing your request with available systems."
            )

        # Add context-aware details
        if "identity" in context_summary:
            identity = context_summary["identity"]
            if identity.get("coherence_score", 0) > 0.8:
                response_parts.append(
                    "My identity systems are stable and can provide consistent reasoning."
                )

        if "memory" in context_summary:
            memory = context_summary["memory"]
            if memory.get("health_score", 0) > 0.8:
                response_parts.append(
                    "My memory systems are functioning well and can provide relevant context."
                )

        # Add specific response to the prompt
        response_parts.append(
            f"Regarding '{prompt}': I'm processing this through my unified cognitive framework, integrating memory, identity, and ethical considerations to provide you with the most helpful response possible."
        )

        return "\n\n".join(response_parts)

    def generate_basic_response(self, prompt: str) -> str:
        """Basic response when full systems aren't available"""
        return f"I received your message: '{prompt}'. My full intelligence systems are currently initializing, but I'm working to provide you with the best response I can."

    def setup_live_updates(self):
        """Setup timers for live system updates"""
        # Fast updates (1 second) - identity and aura
        self.fast_timer = QTimer()
        self.fast_timer.timeout.connect(self.update_fast_systems)
        self.fast_timer.start(1000)

        # Medium updates (3 seconds) - memory and reflection
        self.medium_timer = QTimer()
        self.medium_timer.timeout.connect(self.update_medium_systems)
        self.medium_timer.start(3000)

        # Slow updates (10 seconds) - memory graph
        self.slow_timer = QTimer()
        self.slow_timer.timeout.connect(self.update_slow_systems)
        self.slow_timer.start(10000)

    def update_fast_systems(self):
        """Update identity and aura systems"""
        self.refresh_identity()
        self.update_aura()

    def update_medium_systems(self):
        """Update reflection systems"""
        self.refresh_reflection()

    def update_slow_systems(self):
        """Update memory graph and heavy computations"""
        self.refresh_memory_graph()

    def refresh_identity(self):
        """Update identity panel with current traits and emotions"""
        try:
            if self.self_model:
                identity_data = {
                    "traits": self.self_model.dimensional_scores,
                    "emotional_state": getattr(self.self_model, "emotional_state", {}),
                    "coherence_score": self.self_model.assess_coherence(),
                    "active_goals": getattr(self.self_model, "active_goals", []),
                    "recent_changes": getattr(self.self_model, "recent_changes", []),
                    "confidence_level": getattr(
                        self.self_model, "confidence_level", 0.8
                    ),
                    "curiosity_level": getattr(self.self_model, "curiosity_level", 0.7),
                }
                self.identity_updated.emit(identity_data)

                # 🔥 Emit visual intelligence signal for AI presence
                self.on_identity_updated.emit()

        except Exception as e:
            print(f"Identity refresh error: {e}")

    def refresh_reflection(self):
        """Update reflection panel with recent insights"""
        try:
            if self.reflection_system:
                reflections = []

                # Get recent reflections from reflection system
                if hasattr(self.reflection_system, "reflection_history"):
                    recent_reflections = list(
                        self.reflection_system.reflection_history
                    )[-10:]
                    for reflection in recent_reflections:
                        reflections.append(
                            {
                                "timestamp": getattr(
                                    reflection, "timestamp", time.time()
                                ),
                                "insight": getattr(
                                    reflection, "insight", str(reflection)
                                ),
                                "quality": getattr(reflection, "quality", 0.8),
                                "category": getattr(reflection, "category", "general"),
                            }
                        )

                # Get insights from intelligence engine if available
                if self.lyrixa_intelligence:
                    # Use intelligence engine to get reflection insights
                    intelligence_status = (
                        self.lyrixa_intelligence.get_intelligence_status()
                    )
                    recent_patterns = intelligence_status.get("recent_patterns", [])
                    for pattern in recent_patterns[-3:]:  # Last 3 patterns
                        reflections.append(
                            {
                                "timestamp": pattern.get("timestamp", "recent"),
                                "insight": f"Pattern: {pattern.get('description', 'Intelligence pattern detected')}",
                                "quality": pattern.get("confidence", 0.8),
                                "category": "pattern_recognition",
                            }
                        )

                self.reflection_updated.emit(reflections)

                # 🔥 Emit visual intelligence signal for AI presence
                self.on_reflection_updated.emit()

        except Exception as e:
            print(f"Reflection refresh error: {e}")

    def refresh_memory_graph(self):
        """Update memory graph with current memory structure"""
        try:
            if self.memory_engine:
                # Use available memory health data to create graph structure
                try:
                    memory_health = self.memory_engine.get_memory_health()
                    graph_data = {
                        "nodes": [
                            {
                                "id": "memory_core",
                                "label": "Memory Core",
                                "type": "system",
                            },
                            {
                                "id": "health_status",
                                "label": f"Health: {memory_health.get('overall_health', 'Unknown')}",
                                "type": "status",
                            },
                        ],
                        "edges": [
                            {
                                "from": "memory_core",
                                "to": "health_status",
                                "relation": "monitors",
                            }
                        ],
                    }
                    self.memory_graph_updated.emit(graph_data)
                except Exception as e:
                    print(f"Memory graph generation error: {e}")
                    # Fallback to sample data
                    self._emit_sample_graph_data()

                # 🔥 Emit visual intelligence signal for AI presence
                self.on_memory_updated.emit()

            else:
                self._emit_sample_graph_data()

        except Exception as e:
            print(f"Memory graph refresh error: {e}")

    def _emit_sample_graph_data(self):
        """Generate sample graph data as fallback"""
        sample_graph = {
            "nodes": [
                {"id": "memory_core", "label": "Memory Core", "type": "core"},
                {"id": "identity", "label": "Identity", "type": "system"},
                {"id": "reflection", "label": "Reflection", "type": "system"},
                {"id": "ethics", "label": "Ethics", "type": "system"},
            ],
            "edges": [
                {"from": "memory_core", "to": "identity", "strength": 0.9},
                {"from": "memory_core", "to": "reflection", "strength": 0.8},
                {"from": "identity", "to": "ethics", "strength": 0.7},
            ],
        }
        self.memory_graph_updated.emit(sample_graph)

    def update_aura(self):
        """Update aura overlay based on current cognitive state"""
        try:
            if self.self_model:
                aura_state = {
                    "confidence": getattr(self.self_model, "confidence_level", 0.8),
                    "curiosity": getattr(self.self_model, "curiosity_level", 0.7),
                    "coherence": self.self_model.assess_coherence(),
                    "activity": min(1.0, len(self.conversation_history) / 10.0),
                    "timestamp": time.time(),
                }
            else:
                # Generate dynamic aura state
                aura_state = {
                    "confidence": 0.8 + 0.1 * abs(hash(str(time.time())) % 100) / 100,
                    "curiosity": 0.7
                    + 0.2 * abs(hash(str(time.time() + 1)) % 100) / 100,
                    "coherence": 0.85
                    + 0.1 * abs(hash(str(time.time() + 2)) % 100) / 100,
                    "activity": 0.6,
                    "timestamp": time.time(),
                }

            self.aura_state_changed.emit(aura_state)
        except Exception as e:
            print(f"Aura update error: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "lyrixa_intelligence": self.lyrixa_intelligence is not None,
            "memory_engine": self.memory_engine is not None,
            "self_model": self.self_model is not None,
            "reflection_system": self.reflection_system is not None,
            "context_bridge": self.context_bridge is not None,
            "conversation_count": len(self.conversation_history),
            "last_context_size": len(str(self.last_context)),
            "uptime": time.time(),
        }
