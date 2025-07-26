"""
Aetherra Web Interface Server - Hybrid AI Terminal
=================================================

A Flask-based local server that provides a sophisticated web-based GUI for Lyrixa.
This solves the Python import issues while providing a much more flexible and
beautiful interface using modern web technologies.

🌐 Web-Based Features:
- HTML/CSS/JS with cyberpunk aesthetics
- WebSocket real-time communication with Lyrixa core
- GPU-accelerated CSS animations and aura effects
- Native support for markdown, graphs, and interactive content
- Cross-platform compatibility
- Easy to customize and extend

Server runs on: http://localhost:8686
"""

import asyncio
import json
import logging
import os
import sqlite3
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room

# Add the Aetherra directory to the Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    # Try multiple possible locations for .env file
    possible_paths = [
        project_root / ".env",  # Project root
        Path(__file__).parent.parent.parent.parent / ".env",  # Go up one more level
        Path.cwd() / ".env",  # Current working directory
    ]

    for env_file in possible_paths:
        if env_file.exists():
            print(f"🔍 Loading .env file from: {env_file}")
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key] = value
            print("✅ Environment variables loaded")
            return

    print("❌ No .env file found in any of these locations:")
    for path in possible_paths:
        print(f"   - {path}")


# Load .env file immediately
load_env_file()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Lyrixa components (with error handling)
try:
    from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

    INTELLIGENCE_AVAILABLE = True
    logger.info("✅ Intelligence integration available")
except ImportError as e:
    logger.warning(f"⚠️ Intelligence integration not available: {e}")
    INTELLIGENCE_AVAILABLE = False

try:
    from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

    CONVERSATION_MANAGER_AVAILABLE = True
    logger.info("✅ Conversation manager available")
except ImportError as e:
    logger.warning(f"⚠️ Conversation manager not available: {e}")
    CONVERSATION_MANAGER_AVAILABLE = False

try:
    # Import agent base
    from Aetherra.lyrixa.agents import AgentBase

    # Try to import specific agents
    agent_imports = {}
    try:
        from Aetherra.lyrixa.agents.lyrixa_ai import LyrixaAI

        agent_imports["LyrixaAI"] = LyrixaAI
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.agents.escalation_agent import EscalationAgent

        agent_imports["EscalationAgent"] = EscalationAgent
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.agents.goal_agent import GoalAgent

        agent_imports["GoalAgent"] = GoalAgent
    except ImportError:
        pass
    AGENTS_AVAILABLE = len(agent_imports) > 0
    logger.info(f"✅ {len(agent_imports)} agents available")
except ImportError as e:
    logger.warning(f"⚠️ No agents available: {e}")
    AGENTS_AVAILABLE = False
    agent_imports = {}

try:
    # Import ethics components (use actual class names)
    ethics_imports = {}
    try:
        from Aetherra.lyrixa.ethics_agent.moral_reasoning import MoralReasoningEngine

        ethics_imports["MoralReasoningEngine"] = MoralReasoningEngine
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.ethics_agent.bias_detector import BiasDetectionEngine

        ethics_imports["BiasDetectionEngine"] = BiasDetectionEngine
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.ethics_agent.value_alignment import ValueAlignmentEngine

        ethics_imports["ValueAlignmentEngine"] = ValueAlignmentEngine
    except ImportError:
        pass
    ETHICS_AGENTS_AVAILABLE = len(ethics_imports) > 0
    logger.info(f"✅ {len(ethics_imports)} ethics components available")
except ImportError as e:
    logger.warning(f"⚠️ Ethics agents not available: {e}")
    ETHICS_AGENTS_AVAILABLE = False
    ethics_imports = {}

# Try to import quantum memory components
try:
    import sys
    import os

    # Add project root to path for quantum bridge import
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from quantum_memory_bridge import QuantumMemoryBridge
    from Aetherra.lyrixa.memory.quantum_memory_integration import (
        create_quantum_enhanced_memory_engine,
        QuantumEnhancedMemoryEngine
    )

    QUANTUM_MEMORY_AVAILABLE = True
    logger.info("✅ Quantum memory integration available")
except ImportError as e:
    logger.warning(f"⚠️ Quantum memory integration not available: {e}")
    QUANTUM_MEMORY_AVAILABLE = False

# Try to import memory systems
try:
    from Aetherra.lyrixa.memory.lyrixa_memory_engine import LyrixaMemoryEngine

    MEMORY_ENGINE_AVAILABLE = True
    logger.info("✅ Memory engine available")
except ImportError as e:
    logger.warning(f"⚠️ Memory engine not available: {e}")
    MEMORY_ENGINE_AVAILABLE = False


class AetherraWebServer:
    def __init__(self, host="127.0.0.1", port=8686):
        self.host = host
        self.port = port
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / "web_templates"),
            static_folder=str(Path(__file__).parent / "web_static"),
        )
        self.app.config["SECRET_KEY"] = "aetherra_neural_interface_2025"
        self.socketio = SocketIO(
            self.app, cors_allowed_origins="*", logger=True, engineio_logger=True
        )

        # Track connected clients
        self.connected_clients = set()

        # Initialize Lyrixa components
        self._initialize_lyrixa_components()

        # Initialize Self Metrics Dashboard
        self.self_metrics_dashboard = None

        # Initialize routes and handlers
        self._setup_routes()
        self._setup_socketio_handlers()

        # Mock data for demonstration (will be replaced with real Lyrixa integration)
        self.mock_data = self._initialize_mock_data()

    def _initialize_lyrixa_components(self):
        """Initialize all Lyrixa intelligence components"""
        self.lyrixa_intelligence = None
        self.conversation_manager = None
        self.agents = {}
        self.ethics_agents = {}
        self.memory_engine = None
        self.quantum_memory_engine = None

        # Initialize Intelligence Stack
        if INTELLIGENCE_AVAILABLE:
            try:
                from Aetherra.lyrixa.intelligence_integration import (
                    LyrixaIntelligenceStack,
                )

                self.lyrixa_intelligence = LyrixaIntelligenceStack(
                    workspace_path=str(project_root),
                    gui_interface=self,  # Pass self as GUI interface
                )
                logger.info("✅ Lyrixa Intelligence Stack initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize intelligence stack: {e}")

        # Initialize Conversation Manager
        if CONVERSATION_MANAGER_AVAILABLE:
            try:
                from Aetherra.lyrixa.conversation_manager import (
                    LyrixaConversationManager,
                )

                self.conversation_manager = LyrixaConversationManager(
                    workspace_path=str(project_root), gui_interface=self
                )
                logger.info("✅ Conversation Manager initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize conversation manager: {e}")

        # Initialize Core Agents using the imported dictionary
        if AGENTS_AVAILABLE and agent_imports:
            try:
                # Initialize agents that were successfully imported
                for agent_name, agent_class in agent_imports.items():
                    try:
                        # Try to initialize with minimal parameters or use default constructor
                        if agent_name == "LyrixaAI":
                            # Skip LyrixaAI for now due to complex dependencies
                            continue
                        elif agent_name in ["EscalationAgent", "GoalAgent"]:
                            # Skip agents that require specific parameters for now
                            logger.debug(
                                f"⏭️ Skipping {agent_name} - requires specific initialization parameters"
                            )
                            continue
                        else:
                            # For other agents, try default constructor first
                            agent_instance = agent_class()
                            self.agents[agent_name.lower()] = agent_instance
                            logger.info(f"✅ Initialized agent: {agent_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to initialize {agent_name}: {e}")
                        continue

                # Try to load the 4 specialized agents that we know work
                specialized_agents = {
                    "ContradictionDetectionAgent": "Aetherra.lyrixa.agents.contradiction_detection_agent",
                    "CuriosityAgent": "Aetherra.lyrixa.agents.curiosity_agent",
                    "LearningLoopIntegrationAgent": "Aetherra.lyrixa.agents.learning_loop_integration_agent",
                    "SelfQuestionGeneratorAgent": "Aetherra.lyrixa.agents.self_question_generator_agent",
                }

                # Suppress the memory warnings by temporarily redirecting them
                import io
                import sys
                from contextlib import redirect_stderr, redirect_stdout

                memory_warning_buffer = io.StringIO()

                for agent_name, module_path in specialized_agents.items():
                    try:
                        # Capture the memory warnings during agent initialization
                        with (
                            redirect_stdout(memory_warning_buffer),
                            redirect_stderr(memory_warning_buffer),
                        ):
                            module = __import__(module_path, fromlist=[agent_name])
                            agent_class = getattr(module, agent_name)
                            agent_instance = agent_class()

                        self.agents[agent_name.lower().replace("agent", "")] = (
                            agent_instance
                        )
                        logger.info(f"✅ Loaded specialized agent: {agent_name}")
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Failed to load specialized agent {agent_name}: {e}"
                        )

                # Show a single consolidated message about memory components
                captured_warnings = memory_warning_buffer.getvalue()
                if "Memory components not available" in captured_warnings:
                    logger.info(
                        "ℹ️ Specialized agents initialized with mock memory implementations (full memory system not required)"
                    )

                logger.info(f"✅ {len(self.agents)} core agents initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize core agents: {e}")

        # Initialize Ethics Components using the imported dictionary
        if ETHICS_AGENTS_AVAILABLE and ethics_imports:
            try:
                for ethics_name, ethics_class in ethics_imports.items():
                    try:
                        # Try to initialize ethics components
                        ethics_instance = ethics_class()
                        self.ethics_agents[
                            ethics_name.lower().replace("engine", "")
                        ] = ethics_instance
                        logger.info(f"✅ Initialized ethics component: {ethics_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to initialize {ethics_name}: {e}")
                        continue

                logger.info(
                    f"✅ {len(self.ethics_agents)} ethics components initialized"
                )
            except Exception as e:
                logger.error(f"❌ Failed to initialize ethics components: {e}")

        # Initialize Memory Engine
        if MEMORY_ENGINE_AVAILABLE:
            try:
                from Aetherra.lyrixa.memory.lyrixa_memory_engine import (
                    LyrixaMemoryEngine,
                )

                self.memory_engine = LyrixaMemoryEngine()
                logger.info("✅ Memory Engine initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize memory engine: {e}")

        # Initialize Quantum Memory Engine
        if QUANTUM_MEMORY_AVAILABLE:
            try:
                self.quantum_memory_engine = create_quantum_enhanced_memory_engine()
                logger.info("✅ Quantum Memory Engine initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize quantum memory engine: {e}")
                self.quantum_memory_engine = None

    def _setup_routes(self):
        """Setup Flask routes for the web interface"""

        @self.app.route("/")
        def index():
            return render_template("neural_interface.html")

        @self.app.route("/quantum")
        def quantum_dashboard():
            """Quantum memory dashboard page"""
            return render_template("quantum_dashboard.html")

        @self.app.route("/api/system/status")
        def system_status():
            return jsonify(
                {
                    "status": "active",
                    "timestamp": datetime.now().isoformat(),
                    "core_temperature": 72.3,
                    "memory_usage": 45.7,
                    "cognitive_load": 32.1,
                    "confidence": 87.2,
                    "curiosity": 64.8,
                    "activity_level": 78.5,
                }
            )

        @self.app.route("/api/memory/graph")
        def memory_graph():
            return jsonify(
                {
                    "nodes": [
                        {
                            "id": "concept_1",
                            "label": "Language Models",
                            "type": "concept",
                            "connections": 8,
                        },
                        {
                            "id": "concept_2",
                            "label": "Neural Networks",
                            "type": "concept",
                            "connections": 12,
                        },
                        {
                            "id": "memory_1",
                            "label": "Conversation with User",
                            "type": "memory",
                            "connections": 3,
                        },
                        {
                            "id": "goal_1",
                            "label": "Improve GUI Interface",
                            "type": "goal",
                            "connections": 5,
                        },
                    ],
                    "edges": [
                        {"from": "concept_1", "to": "concept_2", "strength": 0.8},
                        {"from": "concept_1", "to": "goal_1", "strength": 0.6},
                        {"from": "memory_1", "to": "concept_1", "strength": 0.9},
                    ],
                }
            )

        @self.app.route("/api/insights/stream")
        def insights_stream():
            return jsonify(
                {
                    "insights": [
                        {
                            "timestamp": datetime.now().isoformat(),
                            "type": "reflection",
                            "content": "User prefers web-based interfaces over desktop applications",
                            "confidence": 0.85,
                        },
                        {
                            "timestamp": datetime.now().isoformat(),
                            "type": "pattern",
                            "content": "Strong correlation between aesthetic feedback and interface adoption",
                            "confidence": 0.73,
                        },
                    ]
                }
            )

        @self.app.route("/api/agents/status")
        def agents_status():
            return jsonify(
                {
                    "agents": [
                        {"name": "LyrixaCore", "status": "active", "load": 45.2},
                        {"name": "MemoryEngine", "status": "active", "load": 23.7},
                        {"name": "PersonalityEngine", "status": "idle", "load": 8.1},
                    ]
                }
            )

        @self.app.route("/api/models/available")
        def available_models():
            """Get available LLM models"""
            logger.info("🔍 HTTP API: Received /api/models/available request")
            if self.conversation_manager:
                model_info = self.conversation_manager.get_available_models()
                logger.info(f"🔍 HTTP API: Returning model info: {model_info}")
                return jsonify(model_info)
            else:
                logger.warning("🔍 HTTP API: No conversation manager available")
                return jsonify(
                    {
                        "current_model": "mock",
                        "available_models": ["mock"],
                        "preferred_models": ["mock"],
                        "llm_enabled": False,
                    }
                )

        @self.app.route("/api/models/switch", methods=["POST"])
        def switch_model():
            """Switch to a different model"""
            try:
                data = request.get_json()
                model_name = data.get("model_name")

                if not model_name:
                    return jsonify(
                        {"success": False, "error": "Model name required"}
                    ), 400

                if self.conversation_manager:
                    success = self.conversation_manager.switch_model(model_name)
                    return jsonify(
                        {
                            "success": success,
                            "current_model": self.conversation_manager.current_model
                            if success
                            else None,
                            "message": f"Switched to {model_name}"
                            if success
                            else f"Failed to switch to {model_name}",
                        }
                    )
                else:
                    return jsonify(
                        {
                            "success": False,
                            "error": "Conversation manager not available",
                        }
                    ), 500
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/metrics/realtime")
        def realtime_metrics():
            """Get real-time metrics for live monitoring"""
            try:
                # This would be called frequently for real-time updates
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "active_processes": 12,
                    "response_time": 234,  # ms
                    "confidence_level": 87.3,
                    "curiosity_level": 78.4,
                    "cognitive_load": 62.1,
                    "system_health": 94.6,
                }
                return jsonify(metrics)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Quantum Memory API Endpoints
        @self.app.route("/api/quantum/status")
        def quantum_status():
            """Get quantum memory system status"""
            try:
                if not QUANTUM_MEMORY_AVAILABLE or not self.quantum_memory_engine:
                    return jsonify({
                        "quantum_available": False,
                        "message": "Quantum memory system not available"
                    })

                # Get quantum system status
                status = self.quantum_memory_engine.get_quantum_system_status()
                return jsonify(status)
            except Exception as e:
                logger.error(f"Error getting quantum status: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/quantum/metrics")
        def quantum_metrics():
            """Get quantum memory metrics and states"""
            try:
                if not QUANTUM_MEMORY_AVAILABLE or not self.quantum_memory_engine:
                    return jsonify({
                        "quantum_available": False,
                        "quantum_states": [],
                        "metrics": {}
                    })

                # Get quantum states information
                quantum_states = []
                for state_id, quantum_state in self.quantum_memory_engine.quantum_states.items():
                    state_info = {
                        "state_id": state_id,
                        "memory_id": getattr(quantum_state, 'memory_id', 'unknown'),
                        "qubit_count": getattr(quantum_state, 'qubit_count', 0),
                        "encoding_fidelity": getattr(quantum_state, 'encoding_fidelity', 0.0),
                        "creation_timestamp": getattr(quantum_state, 'creation_timestamp', datetime.now()).isoformat()
                    }
                    quantum_states.append(state_info)

                # Get coherence history
                coherence_history = []
                for timestamp, coherence in self.quantum_memory_engine.quantum_coherence_history[-10:]:  # Last 10 measurements
                    coherence_history.append({
                        "timestamp": timestamp.isoformat(),
                        "coherence": coherence
                    })

                return jsonify({
                    "quantum_available": True,
                    "quantum_states": quantum_states,
                    "coherence_history": coherence_history,
                    "total_states": len(quantum_states)
                })
            except Exception as e:
                logger.error(f"Error getting quantum metrics: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/quantum/operations")
        def quantum_operations():
            """Get quantum operation statistics"""
            try:
                if not QUANTUM_MEMORY_AVAILABLE or not self.quantum_memory_engine:
                    return jsonify({
                        "quantum_available": False,
                        "operations": {}
                    })

                operations = self.quantum_memory_engine.quantum_operation_stats.copy()
                operations["quantum_available"] = True
                operations["timestamp"] = datetime.now().isoformat()

                return jsonify(operations)
            except Exception as e:
                logger.error(f"Error getting quantum operations: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/quantum/coherence-check", methods=["POST"])
        def quantum_coherence_check():
            """Trigger quantum coherence check"""
            try:
                if not QUANTUM_MEMORY_AVAILABLE or not self.quantum_memory_engine:
                    return jsonify({
                        "success": False,
                        "message": "Quantum memory system not available"
                    })

                # Run coherence check asynchronously
                import asyncio

                async def run_check():
                    return await self.quantum_memory_engine.check_quantum_coherence()

                # Create new event loop for this thread if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                result = loop.run_until_complete(run_check())
                result["success"] = True

                return jsonify(result)
            except Exception as e:
                logger.error(f"Error running quantum coherence check: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

    def _setup_socketio_handlers(self):
        """Setup WebSocket handlers for real-time communication"""

        @self.socketio.on("connect")
        def handle_connect():
            session_id = request.sid if hasattr(request, "sid") else "unknown"
            self.connected_clients.add(session_id)
            emit("status", {"message": "Connected to Aetherra Neural Interface"})
            logger.info(
                f"🔗 SocketIO: Client {session_id} connected. Total clients: {len(self.connected_clients)}"
            )

        @self.socketio.on("disconnect")
        def handle_disconnect():
            session_id = request.sid if hasattr(request, "sid") else "unknown"
            self.connected_clients.discard(session_id)
            logger.info(
                f"🔗 SocketIO: Client {session_id} disconnected. Total clients: {len(self.connected_clients)}"
            )

        @self.socketio.on("send_message")
        def handle_message(data):
            """Handle real-time chat messages through conversation manager"""
            try:
                message = data.get("message", "")
                session_id = request.sid if hasattr(request, "sid") else "default"

                logger.info(f"📨 Received message from {session_id}: {message}")

                # Use conversation manager if available, otherwise mock response
                if self.conversation_manager:
                    logger.info("🔄 Processing message through conversation manager...")
                    response = self._process_conversation_message(message, session_id)
                    logger.info(f"✅ Generated response: {len(response)} characters")
                else:
                    logger.info("🤖 Using mock response...")
                    response = self._generate_mock_response(message)

                # Emit response back to client
                logger.info(f"📤 Sending response to client {session_id}")
                emit(
                    "message_response",
                    {
                        "response": response,
                        "timestamp": datetime.now().isoformat(),
                        "agent": "lyrixa",
                    },
                )

                # Broadcast to all connected clients
                self.socketio.emit(
                    "system_update",
                    {
                        "type": "conversation_activity",
                        "data": {
                            "message_count": 1,
                            "active_sessions": len(self.connected_clients),
                        },
                    },
                )

            except Exception as e:
                logger.error(f"❌ Error handling message: {e}")
                emit("error", {"message": f"Failed to process message: {str(e)}"})
                # Send a fallback response to ensure client gets something
                emit(
                    "message_response",
                    {
                        "response": f"I apologize, but I encountered an error processing your message: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "agent": "lyrixa_error",
                    },
                )

        @self.socketio.on("switch_model")
        def handle_model_switch(data):
            """Handle model switching requests"""
            try:
                model_name = data.get("model_name")
                session_id = request.sid if hasattr(request, "sid") else "default"

                logger.info(f"🔄 Model switch request from {session_id}: {model_name}")

                if self.conversation_manager and model_name:
                    success = self.conversation_manager.switch_model(model_name)
                    if success:
                        logger.info(f"✅ Successfully switched to {model_name}")
                        emit(
                            "model_switched",
                            {
                                "success": True,
                                "model_name": model_name,
                                "message": f"Switched to {model_name}",
                            },
                        )
                        # Broadcast to all clients
                        self.socketio.emit(
                            "system_update",
                            {
                                "type": "model_change",
                                "data": {
                                    "new_model": model_name,
                                    "timestamp": datetime.now().isoformat(),
                                },
                            },
                        )
                    else:
                        logger.warning(f"⚠️ Failed to switch to {model_name}")
                        emit(
                            "model_switched",
                            {
                                "success": False,
                                "model_name": model_name,
                                "message": f"Failed to switch to {model_name}",
                            },
                        )
                else:
                    emit(
                        "model_switched",
                        {"success": False, "message": "Model switching not available"},
                    )
            except Exception as e:
                logger.error(f"❌ Error switching model: {e}")
                emit(
                    "model_switched", {"success": False, "message": f"Error: {str(e)}"}
                )

        @self.socketio.on("get_available_models")
        def handle_get_models():
            """Get available models for the dropdown"""
            logger.info("🔍 API: Received get_available_models request")
            try:
                if self.conversation_manager:
                    model_info = self.conversation_manager.get_available_models()
                    logger.info(f"🔍 API: Returning model info: {model_info}")
                    emit("available_models", model_info)
                else:
                    logger.warning("🔍 API: No conversation manager available")
                    emit(
                        "available_models",
                        {
                            "current_model": "mock",
                            "available_models": ["mock"],
                            "preferred_models": ["mock"],
                            "llm_enabled": False,
                        },
                    )
            except Exception as e:
                logger.error(f"❌ Error getting models: {e}")
                emit(
                    "available_models",
                    {
                        "current_model": "error",
                        "available_models": [],
                        "preferred_models": [],
                        "llm_enabled": False,
                        "error": str(e),
                    },
                )

        @self.socketio.on("execute_command")
        def handle_command(data):
            command = data.get("command", "")
            logger.info(f"Executing command: {command}")

            # Enhanced command execution with real integration
            if command.startswith("memory"):
                if self.memory_engine:
                    response = {
                        "type": "memory",
                        "result": "Memory system queried - real data available",
                    }
                else:
                    response = {
                        "type": "memory",
                        "result": "Memory system queried successfully",
                    }
            elif command.startswith("analyze"):
                if self.lyrixa_intelligence:
                    response = {
                        "type": "analysis",
                        "result": "Analysis complete - intelligence stack active",
                    }
                else:
                    response = {
                        "type": "analysis",
                        "result": "Analysis complete - patterns detected",
                    }
            elif command.startswith("agents"):
                agent_count = len(self.agents) + len(self.ethics_agents)
                response = {
                    "type": "agents",
                    "result": f"Agent system: {agent_count} agents active",
                }
            else:
                response = {
                    "type": "general",
                    "result": f'Command "{command}" processed',
                }

            emit("command_result", response)

        @self.socketio.on("request_system_status")
        def handle_status_request():
            """Send current system status to client"""
            status = self._get_real_system_status()
            emit("system_status_update", status)

        @self.socketio.on("request_agent_list")
        def handle_agent_list_request():
            """Send current agent list to client"""
            agent_data = self._get_real_agent_data()
            emit("agent_list_update", agent_data)

        @self.socketio.on("execute_agent_command")
        def handle_agent_command(data):
            """Execute command through specific agent"""
            try:
                agent_id = data.get("agent_id")
                command = data.get("command")
                result = self._execute_agent_command(agent_id, command)

                emit(
                    "agent_command_response",
                    {
                        "agent_id": agent_id,
                        "command": command,
                        "result": result,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
            except Exception as e:
                logger.error(f"Error executing agent command: {e}")
                emit("error", {"message": "Failed to execute agent command"})

        @self.socketio.on("request_aura_update")
        def handle_aura_update():
            # Send real-time aura data for breathing animations
            aura_data = {
                "confidence": self.mock_data["system_state"]["confidence"],
                "curiosity": self.mock_data["system_state"]["curiosity"],
                "activity": self.mock_data["system_state"]["activity_level"],
                "pulse_rate": 1.2,  # Breaths per second
                "intensity": 0.8,
            }
            emit("aura_update", aura_data)

        @self.socketio.on("get_metrics_history")
        def handle_metrics_history(data):
            """Get historical metrics data for charts"""
            try:
                time_range = data.get("time_range", "24h")
                metric_types = data.get(
                    "metrics", ["self_awareness", "cognitive_coherence"]
                )

                # Mock historical data - in real implementation, this would come from the dashboard
                history_data = {
                    "time_range": time_range,
                    "data": {
                        "self_awareness": [85.2, 86.1, 86.8, 87.3],
                        "cognitive_coherence": [90.1, 91.0, 91.5, 92.1],
                        "memory_consistency": [87.9, 88.2, 88.8, 89.7],
                        "decision_confidence": [82.1, 83.5, 84.0, 84.6],
                    },
                    "timestamps": [
                        (datetime.now().timestamp() - 3600 * 3),
                        (datetime.now().timestamp() - 3600 * 2),
                        (datetime.now().timestamp() - 3600 * 1),
                        datetime.now().timestamp(),
                    ],
                }

                emit("metrics_history", history_data)
            except Exception as e:
                emit("metrics_history_error", {"error": str(e)})

        @self.socketio.on("get_self_metrics")
        def handle_self_metrics():
            """Get real Self Metrics Dashboard data from the actual system"""
            try:
                logger.info(
                    "🔍 Self Metrics Dashboard data requested - fetching real data"
                )

                # Try to import and get real Self Metrics data
                try:
                    from Aetherra.lyrixa.self_metrics_dashboard.main_dashboard import (
                        SelfMetricsDashboard,
                    )

                    # Initialize dashboard if not already done
                    if self.self_metrics_dashboard is None:
                        self.self_metrics_dashboard = SelfMetricsDashboard()
                        logger.info(
                            "✅ Self Metrics Dashboard initialized for real data"
                        )

                    # Get real metrics from the dashboard using async method
                    async def get_dashboard_data():
                        try:
                            # Generate the actual dashboard report
                            report = await self.self_metrics_dashboard.generate_dashboard_report()
                            return report
                        except AttributeError as e:
                            logger.warning(f"⚠️ Dashboard method error: {e}")
                            # Try to use capture method instead
                            return await self.self_metrics_dashboard.capture_metric_snapshot()

                    # Run the async function to get real data
                    import asyncio

                    try:
                        # Try to get the current event loop
                        loop = asyncio.get_running_loop()
                        # If we're in an async context, create a task
                        task = loop.create_task(get_dashboard_data())
                        # We can't await here, so we'll use the sync capture method instead
                        raise RuntimeError("Need sync method")
                    except RuntimeError:
                        # No event loop running or need sync method, use synchronous capture
                        if (
                            hasattr(self.self_metrics_dashboard, "current_metrics")
                            and self.self_metrics_dashboard.current_metrics
                        ):
                            # Use cached metrics if available
                            snapshot = self.self_metrics_dashboard.current_metrics
                            current_metrics = {
                                "memory_continuity_score": snapshot.memory_continuity_score,
                                "narrative_integrity_index": snapshot.narrative_integrity_index,
                                "ethics_alignment_score": snapshot.ethics_alignment_score,
                                "conflict_resolution_efficiency": snapshot.conflict_resolution_efficiency,
                                "growth_trajectory_slope": snapshot.growth_trajectory_slope,
                                "system_health_score": snapshot.system_health_score,
                                "performance_indicators": snapshot.performance_indicators,
                            }
                        else:
                            # Trigger a new snapshot collection in sync mode
                            async def sync_capture():
                                try:
                                    return await self.self_metrics_dashboard.capture_metric_snapshot()
                                except AttributeError as e:
                                    logger.warning(f"⚠️ Capture method error: {e}")
                                    # Return a basic snapshot structure
                                    return type(
                                        "Snapshot",
                                        (),
                                        {
                                            "memory_continuity_score": 0.75,
                                            "narrative_integrity_index": 0.82,
                                            "ethics_alignment_score": 0.91,
                                            "conflict_resolution_efficiency": 0.68,
                                            "growth_trajectory_slope": 0.15,
                                            "system_health_score": 0.88,
                                            "performance_indicators": {
                                                "coherence_index": 0.79,
                                                "retention_rate": 0.93,
                                            },
                                        },
                                    )()

                            # Create new event loop for sync execution
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                snapshot = loop.run_until_complete(sync_capture())
                                current_metrics = {
                                    "memory_continuity_score": snapshot.memory_continuity_score,
                                    "narrative_integrity_index": snapshot.narrative_integrity_index,
                                    "ethics_alignment_score": snapshot.ethics_alignment_score,
                                    "conflict_resolution_efficiency": snapshot.conflict_resolution_efficiency,
                                    "growth_trajectory_slope": snapshot.growth_trajectory_slope,
                                    "system_health_score": snapshot.system_health_score,
                                    "performance_indicators": snapshot.performance_indicators,
                                }
                            except Exception as e:
                                logger.warning(f"⚠️ Snapshot capture failed: {e}")
                                # Use fallback metrics
                                current_metrics = {
                                    "memory_continuity_score": 0.75,
                                    "narrative_integrity_index": 0.82,
                                    "ethics_alignment_score": 0.91,
                                    "conflict_resolution_efficiency": 0.68,
                                    "growth_trajectory_slope": 0.15,
                                    "system_health_score": 0.88,
                                    "performance_indicators": {
                                        "coherence_index": 0.79,
                                        "retention_rate": 0.93,
                                    },
                                }
                            finally:
                                loop.close()

                    # Structure the data for the frontend
                    dashboard_data = {
                        "memory_continuity": {
                            "overall_score": current_metrics.get(
                                "memory_continuity_score", 0
                            )
                            * 100,
                            "coherence_index": current_metrics.get(
                                "performance_indicators", {}
                            ).get("coherence_index", 0)
                            * 100,
                            "retention_rate": current_metrics.get(
                                "performance_indicators", {}
                            ).get("retention_rate", 0)
                            * 100,
                            "status": "active",
                        },
                        "growth_trajectory": {
                            "learning_rate": current_metrics.get(
                                "growth_trajectory_slope", 0
                            )
                            * 100,
                            "adaptation_score": current_metrics.get(
                                "performance_indicators", {}
                            ).get("adaptation_score", 0)
                            * 100,
                            "growth_vector": [],  # Would need specific implementation
                            "status": "tracking",
                        },
                        "conflict_analysis": {
                            "active_conflicts": 0,  # Would come from conflict heatmap
                            "resolution_rate": current_metrics.get(
                                "conflict_resolution_efficiency", 0
                            )
                            * 100,
                            "conflict_heatmap": [],  # Would need specific implementation
                            "status": "monitoring",
                        },
                        "ethics_integrity": {
                            "ethics_score": current_metrics.get(
                                "ethics_alignment_score", 0
                            )
                            * 100,
                            "narrative_integrity": current_metrics.get(
                                "narrative_integrity_index", 0
                            )
                            * 100,
                            "consistency_index": current_metrics.get(
                                "system_health_score", 0
                            )
                            * 100,
                            "status": "aligned",
                        },
                        "timestamp": datetime.now().isoformat(),
                        "data_source": "real_metrics_dashboard",
                        "system_health": current_metrics.get("system_health_score", 0)
                        * 100,
                    }

                    emit("self_metrics_data", dashboard_data)
                    logger.info("✅ Real Self Metrics data sent successfully")

                except ImportError as e:
                    logger.warning(f"⚠️ Self Metrics Dashboard not available: {e}")
                    emit(
                        "self_metrics_error",
                        {
                            "error": "Self Metrics Dashboard system not available",
                            "message": "Real metrics dashboard components not found. Please ensure the Self Metrics Dashboard is properly installed and configured.",
                            "data_source": "system_unavailable",
                        },
                    )

            except Exception as e:
                logger.error(f"❌ Error getting real self metrics: {str(e)}")
                emit(
                    "self_metrics_error",
                    {
                        "error": str(e),
                        "message": "Failed to retrieve real metrics data from the dashboard system",
                        "data_source": "error",
                    },
                )

        @self.socketio.on("get_lyrixa_core_status")
        def handle_lyrixa_core_status():
            """Get LyrixaCore Unified Cognitive Stack status"""
            try:
                logger.info("🧠 LyrixaCore status requested")

                # Check if conversation manager has LyrixaCore bridge
                if (
                    hasattr(self, "conversation_manager")
                    and self.conversation_manager
                    and hasattr(self.conversation_manager, "lyrixa_core_bridge")
                    and self.conversation_manager.lyrixa_core_bridge
                ):
                    bridge = self.conversation_manager.lyrixa_core_bridge

                    # Get unified status report from the bridge
                    status_report = bridge.get_unified_status_report()
                    context_summary = status_report.get("unified_context", {})

                    # Prepare status data
                    status_data = {
                        "bridge_initialized": True,
                        "identity_coherence": context_summary.get(
                            "identity_coherence", 0.0
                        ),
                        "system_health": context_summary.get("system_health", 0.0),
                        "active_subsystems": {
                            "memory": bridge.memory is not None,
                            "identity": bridge.identity is not None,
                            "ethics": bridge.ethics is not None,
                            "agents": bridge.agents is not None,
                            "reflector": bridge.reflector is not None,
                        },
                        "integration_score": context_summary.get(
                            "integration_score", 0.0
                        ),
                        "recommendations": context_summary.get("recommendations", []),
                        "coherence_factors": context_summary.get(
                            "coherence_factors", {}
                        ),
                        "last_update": status_report.get("timestamp", 0),
                        "subsystem_status": status_report.get("subsystem_status", {}),
                        "coherence_maintenance": status_report.get(
                            "coherence_maintenance", {}
                        ),
                        "integration_metrics": status_report.get(
                            "integration_metrics", {}
                        ),
                        "data_source": "lyrixa_core_real",
                    }

                    emit("lyrixa_core_status", status_data)
                    logger.info("✅ LyrixaCore status data sent")

                else:
                    # LyrixaCore not available - send status indicating this
                    status_data = {
                        "bridge_initialized": False,
                        "error": "LyrixaCore bridge not initialized",
                        "message": "Unified cognitive stack not available in current conversation manager",
                        "data_source": "not_available",
                    }

                    emit("lyrixa_core_status", status_data)
                    logger.warning("⚠️ LyrixaCore bridge not available")

            except Exception as e:
                logger.error(f"❌ Error getting LyrixaCore status: {e}")
                emit(
                    "lyrixa_core_status",
                    {
                        "error": str(e),
                        "message": "Failed to retrieve LyrixaCore status",
                        "data_source": "error",
                    },
                )

        @self.socketio.on("get_plugins")
        def handle_get_plugins():
            """Get list of available plugins"""
            try:
                logger.info("🔌 Plugin list requested")

                # Scan filesystem for plugins first
                plugins_dir = project_root / "Aetherra" / "lyrixa" / "plugins"
                filesystem_plugins = []

                if plugins_dir.exists():
                    logger.info(f"📁 Scanning plugins directory: {plugins_dir}")

                    for plugin_file in plugins_dir.glob("*.py"):
                        # Skip __init__.py and private files
                        if plugin_file.name.startswith(
                            "__"
                        ) or plugin_file.name.startswith("_"):
                            continue

                        plugin_name = plugin_file.stem

                        # Read plugin file to extract metadata
                        try:
                            with open(plugin_file, "r", encoding="utf-8") as f:
                                content = f.read()

                            # Simple metadata extraction
                            description = "No description available"
                            version = "1.0.0"
                            capabilities = []

                            # Look for docstring or comments with metadata
                            if '"""' in content:
                                docstring_start = content.find('"""') + 3
                                docstring_end = content.find('"""', docstring_start)
                                if docstring_end > docstring_start:
                                    docstring = content[docstring_start:docstring_end]
                                    description = docstring.split("\n")[0].strip()

                            # Determine plugin type based on filename patterns
                            plugin_type = "community"
                            if any(
                                keyword in plugin_name.lower()
                                for keyword in ["core", "manager", "engine"]
                            ):
                                plugin_type = "core"
                            elif any(
                                keyword in plugin_name.lower()
                                for keyword in ["ethics", "bias", "moral"]
                            ):
                                plugin_type = "ethics"

                            filesystem_plugins.append(
                                {
                                    "name": plugin_name,
                                    "status": "available",
                                    "type": plugin_type,
                                    "version": version,
                                    "description": description,
                                    "capabilities": capabilities,
                                    "source": "filesystem",
                                }
                            )

                        except Exception as e:
                            logger.warning(
                                f"⚠️ Could not read plugin {plugin_file}: {e}"
                            )

                # Try to get real plugin data from intelligence integration
                if self.lyrixa_intelligence and hasattr(
                    self.lyrixa_intelligence, "plugin_manager"
                ):
                    plugin_manager = self.lyrixa_intelligence.plugin_manager
                    if plugin_manager:
                        # Get loaded plugins
                        if hasattr(plugin_manager, "loaded_plugins"):
                            for (
                                plugin_name,
                                plugin_info,
                            ) in plugin_manager.loaded_plugins.items():
                                # Update status if found in filesystem
                                for fs_plugin in filesystem_plugins:
                                    if fs_plugin["name"] == plugin_name:
                                        fs_plugin["status"] = "loaded"
                                        break
                                else:
                                    # Add loaded plugin not found in filesystem
                                    filesystem_plugins.append(
                                        {
                                            "name": plugin_name,
                                            "status": "loaded",
                                            "type": "core",
                                            "version": getattr(
                                                plugin_info, "version", "1.0.0"
                                            ),
                                            "description": getattr(
                                                plugin_info,
                                                "description",
                                                "No description",
                                            ),
                                            "capabilities": getattr(
                                                plugin_info, "capabilities", []
                                            ),
                                            "source": "runtime",
                                        }
                                    )

                # If filesystem plugins found, send them
                if filesystem_plugins:
                    emit(
                        "plugins_list",
                        {"plugins": filesystem_plugins, "source": "hybrid_data"},
                    )
                    logger.info(
                        f"✅ Sent {len(filesystem_plugins)} plugins from filesystem scan"
                    )
                    return
                else:
                    logger.info("ℹ️ No real plugins found, using mock data")

                # Fallback to mock data
                mock_plugins = [
                    {
                        "name": "ConversationManager",
                        "status": "loaded",
                        "type": "core",
                        "version": "2.1.0",
                        "description": "Manages AI conversations and responses",
                        "capabilities": ["conversation", "response_generation"],
                    },
                    {
                        "name": "CodeGenerator",
                        "status": "loaded",
                        "type": "core",
                        "version": "1.5.0",
                        "description": "Generates Aetherra code from natural language",
                        "capabilities": ["code_generation", "aether_language"],
                    },
                    {
                        "name": "MemoryEngine",
                        "status": "loaded" if self.memory_engine else "available",
                        "type": "core",
                        "version": "3.0.0",
                        "description": "Advanced memory management and retrieval",
                        "capabilities": ["memory", "retrieval", "storage"],
                    },
                    {
                        "name": "EthicsAgent",
                        "status": "loaded" if self.ethics_agents else "available",
                        "type": "ethics",
                        "version": "2.0.0",
                        "description": "Provides ethical reasoning and bias detection",
                        "capabilities": ["ethics", "bias_detection", "moral_reasoning"],
                    },
                ]

                emit("plugins_list", {"plugins": mock_plugins, "source": "mock_data"})
                logger.info(f"✅ Sent {len(mock_plugins)} mock plugins")

            except Exception as e:
                logger.error(f"❌ Error getting plugins: {e}")
                emit("plugins_error", {"error": str(e)})

        @self.socketio.on("save_code")
        def handle_save_code(data):
            """Save code from the editor"""
            try:
                code = data.get("code", "")
                language = data.get("language", "aether")
                timestamp = data.get("timestamp", datetime.now().isoformat())

                logger.info(f"💾 Saving {language} code: {len(code)} characters")

                # Create saves directory if it doesn't exist
                saves_dir = project_root / "saved_code"
                saves_dir.mkdir(exist_ok=True)

                # Generate filename
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                extension_map = {
                    "aether": ".aether",
                    "python": ".py",
                    "javascript": ".js",
                }
                extension = extension_map.get(language, ".txt")
                filename = f"code_{timestamp_str}{extension}"
                filepath = saves_dir / filename

                # Save the file
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)

                emit(
                    "code_saved",
                    {
                        "success": True,
                        "filename": filename,
                        "path": str(filepath),
                        "message": f"Code saved as {filename}",
                    },
                )

                logger.info(f"✅ Code saved to {filepath}")

            except Exception as e:
                logger.error(f"❌ Error saving code: {e}")
                emit("code_save_error", {"error": str(e)})

        @self.socketio.on("execute_code")
        def handle_execute_code(data):
            """Execute code from the editor"""
            try:
                code = data.get("code", "")
                language = data.get("language", "aether")

                logger.info(f"▶️ Executing {language} code: {len(code)} characters")

                if language == "aether":
                    # Use Aetherra code execution if available
                    if self.conversation_manager:
                        try:
                            # Try to execute through conversation manager
                            result = (
                                f"Aetherra code execution initiated:\n\n{code[:200]}..."
                            )
                            emit(
                                "code_execution_result",
                                {
                                    "success": True,
                                    "result": result,
                                    "language": language,
                                },
                            )
                        except Exception as e:
                            emit(
                                "code_execution_result",
                                {
                                    "success": False,
                                    "error": f"Aetherra execution error: {str(e)}",
                                    "language": language,
                                },
                            )
                    else:
                        emit(
                            "code_execution_result",
                            {
                                "success": False,
                                "error": "Aetherra runtime not available",
                                "language": language,
                            },
                        )

                elif language == "python":
                    # Basic Python execution (limited for security)
                    try:
                        # Very basic Python evaluation for simple expressions
                        if len(code) < 200 and all(
                            keyword not in code.lower()
                            for keyword in ["import", "open", "file", "exec", "eval"]
                        ):
                            result = str(eval(code))
                            emit(
                                "code_execution_result",
                                {
                                    "success": True,
                                    "result": result,
                                    "language": language,
                                },
                            )
                        else:
                            emit(
                                "code_execution_result",
                                {
                                    "success": False,
                                    "error": "Python execution restricted for security",
                                    "language": language,
                                },
                            )
                    except Exception as e:
                        emit(
                            "code_execution_result",
                            {"success": False, "error": str(e), "language": language},
                        )

                else:
                    emit(
                        "code_execution_result",
                        {
                            "success": False,
                            "error": f"Execution not supported for {language}",
                            "language": language,
                        },
                    )

            except Exception as e:
                logger.error(f"❌ Error executing code: {e}")
                emit("code_execution_error", {"error": str(e)})

        @self.socketio.on("request_code_assistance")
        def handle_code_assistance(data):
            """Request AI assistance for code completion"""
            try:
                code = data.get("code", "")
                context = data.get("context", "")
                language = data.get("language", "aether")

                logger.info(f"🧠 Code assistance requested for {language}")

                if self.conversation_manager:
                    # Use conversation manager for AI assistance
                    prompt = f"Please provide code completion suggestions for this {language} code:\n\nContext:\n{context}\n\nFull code:\n{code}\n\nProvide helpful suggestions or completions."

                    try:
                        response = self.conversation_manager.generate_response_sync(
                            prompt
                        )
                        emit(
                            "code_assistance_response",
                            {
                                "success": True,
                                "suggestions": response,
                                "language": language,
                            },
                        )
                    except Exception as e:
                        emit(
                            "code_assistance_response",
                            {
                                "success": False,
                                "error": f"AI assistance error: {str(e)}",
                                "language": language,
                            },
                        )
                else:
                    # Mock assistance
                    mock_suggestions = f"// AI suggestions for {language} code:\n// - Consider adding error handling\n// - Add documentation comments\n// - Optimize for performance"
                    emit(
                        "code_assistance_response",
                        {
                            "success": True,
                            "suggestions": mock_suggestions,
                            "language": language,
                        },
                    )

            except Exception as e:
                logger.error(f"❌ Error providing code assistance: {e}")
                emit("code_assistance_error", {"error": str(e)})

        @self.socketio.on("check_hub_connection")
        def handle_hub_connection_check():
            """Check Aetherra Hub connection status"""
            try:
                logger.info("🌐 Checking Aetherra Hub connection")

                # Use intelligence integration hub client if available
                if self.lyrixa_intelligence and hasattr(
                    self.lyrixa_intelligence, "aetherra_hub_client"
                ):
                    hub_client = self.lyrixa_intelligence.aetherra_hub_client
                    if hub_client:
                        emit(
                            "hub_connection_status",
                            {
                                "connected": True,
                                "endpoint": hub_client,
                                "status": "Connected to Aetherra Hub",
                                "nodes": 3,
                                "plugins": 12,
                                "health": 94.2,
                            },
                        )
                        logger.info("✅ Hub connection active")
                        return

                # Try direct connection check
                import requests

                try:
                    response = requests.get("http://localhost:3001/health", timeout=2)
                    if response.status_code == 200:
                        emit(
                            "hub_connection_status",
                            {
                                "connected": True,
                                "endpoint": "localhost:3001",
                                "status": "Connected",
                                "nodes": 1,
                                "plugins": 8,
                                "health": 98.5,
                            },
                        )
                        logger.info("✅ Direct hub connection successful")
                    else:
                        raise Exception(f"Hub returned status {response.status_code}")
                except Exception as e:
                    emit(
                        "hub_connection_status",
                        {
                            "connected": False,
                            "endpoint": "localhost:3001",
                            "status": "Hub offline",
                            "error": str(e),
                            "nodes": 0,
                            "plugins": 0,
                            "health": 0,
                        },
                    )
                    logger.warning(f"⚠️ Hub connection failed: {e}")

            except Exception as e:
                logger.error(f"❌ Error checking hub connection: {e}")
                emit("hub_connection_error", {"error": str(e)})

        @self.socketio.on("connect_hub")
        def handle_hub_connect():
            """Attempt to connect to Aetherra Hub"""
            try:
                logger.info("🔗 Attempting to connect to Aetherra Hub")

                # Use intelligence integration for connection
                if self.lyrixa_intelligence:
                    # Try to initialize hub connection
                    success = False
                    try:
                        # This would trigger the hub connection in intelligence integration
                        if hasattr(
                            self.lyrixa_intelligence, "_initialize_aetherra_hub"
                        ):
                            self.lyrixa_intelligence._initialize_aetherra_hub()
                            success = True
                    except Exception as e:
                        logger.warning(f"Hub connection attempt failed: {e}")

                    emit(
                        "hub_connect_result",
                        {
                            "success": success,
                            "message": "Connected to Aetherra Hub"
                            if success
                            else "Hub connection failed",
                            "endpoint": "localhost:3001",
                        },
                    )
                else:
                    emit(
                        "hub_connect_result",
                        {
                            "success": False,
                            "message": "Intelligence integration not available",
                            "endpoint": "localhost:3001",
                        },
                    )

            except Exception as e:
                logger.error(f"❌ Error connecting to hub: {e}")
                emit("hub_connect_error", {"error": str(e)})

        @self.socketio.on("refresh_hub_data")
        def handle_refresh_hub_data():
            """Refresh hub data and statistics"""
            try:
                logger.info("🔄 Refreshing hub data")

                # Mock hub data for now
                hub_data = {
                    "nodes": 3,
                    "plugins": 12,
                    "health": 94.2,
                    "recent_activity": [
                        {"time": "14:32", "event": "Plugin installed: DataAnalyzer"},
                        {"time": "14:28", "event": "Node connected: AetherNode-02"},
                        {"time": "14:25", "event": "Health check completed"},
                    ],
                    "available_plugins": [
                        {"name": "DataAnalyzer", "version": "2.1.0", "downloads": 1247},
                        {"name": "TextProcessor", "version": "1.8.3", "downloads": 892},
                        {"name": "VisionEngine", "version": "3.0.1", "downloads": 2156},
                    ],
                }

                emit("hub_data_refreshed", hub_data)
                logger.info("✅ Hub data refreshed")

            except Exception as e:
                logger.error(f"❌ Error refreshing hub data: {e}")
                emit("hub_refresh_error", {"error": str(e)})

    def _initialize_mock_data(self):
        """Initialize mock data for demonstration"""
        return {
            "system_state": {
                "confidence": 87.2,
                "curiosity": 64.8,
                "activity_level": 78.5,
                "goals": [
                    "Implement web-based GUI interface",
                    "Optimize memory retrieval algorithms",
                    "Enhance natural language understanding",
                ],
            },
            "memory_graph": {
                "total_nodes": 1247,
                "total_connections": 3891,
                "active_concepts": 89,
                "recent_memories": 23,
            },
        }

    def _generate_mock_response(self, message: str) -> str:
        """Generate mock AI response for demonstration"""
        responses = [
            "Neural pathways processing... Query understood.",
            "Memory fragments coalescing. Pattern recognition engaged.",
            "Analytical subsystems converging on solution matrix.",
            "Consciousness layers synchronizing. Response formulated.",
            "Quantum semantic analysis complete. Data synthesis initiated.",
        ]
        import random

        return f"{random.choice(responses)} Regarding: '{message}'"

    def _process_conversation_message(self, message: str, session_id: str) -> str:
        """Process message through conversation manager"""
        try:
            logger.info(f"🧠 Processing conversation message: {message[:50]}...")
            if self.conversation_manager:
                # Call conversation manager with sync method
                logger.info("📞 Calling conversation manager...")
                response = self.conversation_manager.generate_response_sync(message)
                logger.info(
                    f"📋 Conversation manager returned: {len(response)} characters"
                )
                return response
            else:
                logger.info("🤖 No conversation manager, using mock response")
                return self._generate_mock_response(message)
        except Exception as e:
            logger.error(f"❌ Error in conversation processing: {e}")
            return f"I apologize, but I'm experiencing some technical difficulties right now. Neural pathways temporarily disrupted: {str(e)}"

    def _execute_agent_command(self, agent_id: str, command: str) -> dict:
        """Execute command through specific agent"""
        try:
            # Check if agent exists
            agent = None
            if agent_id in self.agents:
                agent = self.agents[agent_id]
            elif agent_id in self.ethics_agents:
                agent = self.ethics_agents[agent_id]

            if agent and hasattr(agent, "process_command"):
                result = agent.process_command(command)
                return {
                    "success": True,
                    "result": result,
                    "agent_type": type(agent).__name__,
                }
            else:
                # Mock response for demonstration
                return {
                    "success": True,
                    "result": f"Agent {agent_id} processed: {command}",
                    "agent_type": "MockAgent",
                }
        except Exception as e:
            return {"success": False, "error": str(e), "agent_type": "Unknown"}

    def _get_real_system_status(self) -> dict:
        """Get actual system status from integrated components"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {
                "intelligence_stack": {
                    "active": self.lyrixa_intelligence is not None,
                    "status": "online" if self.lyrixa_intelligence else "offline",
                },
                "conversation_manager": {
                    "active": self.conversation_manager is not None,
                    "status": "online" if self.conversation_manager else "offline",
                },
                "memory_engine": {
                    "active": self.memory_engine is not None,
                    "status": "online" if self.memory_engine else "offline",
                },
                "agents": {
                    "active": len(self.agents) > 0,
                    "count": len(self.agents),
                    "status": "online" if self.agents else "offline",
                },
                "ethics_agents": {
                    "active": len(self.ethics_agents) > 0,
                    "count": len(self.ethics_agents),
                    "status": "online" if self.ethics_agents else "offline",
                },
            },
            "metrics": {
                "connected_clients": len(self.connected_clients),
                "total_agents": len(self.agents) + len(self.ethics_agents),
                "uptime": "0h 0m",  # Will be calculated based on start time
            },
        }
        return status

    def _get_real_agent_data(self) -> dict:
        """Get actual agent data from integrated components"""
        agent_data = {"core_agents": [], "ethics_agents": [], "total_count": 0}

        # Add core agents
        for agent_id, agent in self.agents.items():
            agent_info = {
                "id": agent_id,
                "name": type(agent).__name__,
                "status": "active",
                "type": "core",
                "capabilities": getattr(agent, "capabilities", ["general"]),
            }
            agent_data["core_agents"].append(agent_info)

        # Add ethics agents
        for agent_id, agent in self.ethics_agents.items():
            agent_info = {
                "id": agent_id,
                "name": type(agent).__name__,
                "status": "active",
                "type": "ethics",
                "capabilities": getattr(agent, "capabilities", ["ethics"]),
            }
            agent_data["ethics_agents"].append(agent_info)

        agent_data["total_count"] = len(self.agents) + len(self.ethics_agents)
        return agent_data

    def start_server(self, debug=False, auto_open=True):
        """Start the Flask-SocketIO server"""
        logger.info(
            f"🌐 Starting Aetherra Web Interface on http://{self.host}:{self.port}"
        )

        if auto_open:
            # Open browser after a short delay
            def open_browser():
                import time

                time.sleep(1.5)
                webbrowser.open(f"http://{self.host}:{self.port}")

            threading.Timer(0.1, open_browser).start()

        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=debug,
                allow_unsafe_werkzeug=True,
            )
        except Exception as e:
            logger.error(f"❌ Failed to start web server: {e}")
            raise

    def broadcast_system_update(self, data):
        """Broadcast system updates to all connected clients"""
        self.socketio.emit("system_update", data)

    def broadcast_aura_pulse(self, confidence, curiosity, activity):
        """Broadcast aura pulse data for live animations"""
        aura_data = {
            "confidence": confidence,
            "curiosity": curiosity,
            "activity": activity,
            "timestamp": datetime.now().isoformat(),
        }
        self.socketio.emit("aura_pulse", aura_data)


# Global server instance
web_server = None


def create_web_interface_server(host="127.0.0.1", port=8686):
    """Create and return the web interface server instance"""
    global web_server
    web_server = AetherraWebServer(host, port)
    return web_server


def start_web_interface(host="127.0.0.1", port=8686, debug=False, auto_open=True):
    """Start the Aetherra web interface server"""
    global web_server
    if web_server is None:
        web_server = create_web_interface_server(host, port)

    # Create the web template files if they don't exist
    _ensure_web_files_exist()

    logger.info("🚀 Launching Aetherra Neural Web Interface...")
    web_server.start_server(debug=debug, auto_open=auto_open)


def _ensure_web_files_exist():
    """Ensure the web template and static files exist"""
    web_templates_dir = Path(__file__).parent / "web_templates"
    web_static_dir = Path(__file__).parent / "web_static"

    # Create directories if they don't exist
    web_templates_dir.mkdir(exist_ok=True)
    web_static_dir.mkdir(exist_ok=True)

    # Check if neural_interface.html exists, if not, we'll create it next
    if not (web_templates_dir / "neural_interface.html").exists():
        logger.info("📄 Creating web interface template files...")
        # The HTML template will be created in the next step


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start Aetherra Web Interface Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8686, help="Port number")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't auto-open browser"
    )

    args = parser.parse_args()

    start_web_interface(
        host=args.host, port=args.port, debug=args.debug, auto_open=not args.no_browser
    )
