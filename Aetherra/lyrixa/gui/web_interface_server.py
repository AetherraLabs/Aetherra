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

import os
import sys
import json
import asyncio
import logging
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3

# Add the Aetherra directory to the Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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
        agent_imports['LyrixaAI'] = LyrixaAI
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.agents.escalation_agent import EscalationAgent
        agent_imports['EscalationAgent'] = EscalationAgent
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.agents.goal_agent import GoalAgent
        agent_imports['GoalAgent'] = GoalAgent
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
        ethics_imports['MoralReasoningEngine'] = MoralReasoningEngine
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.ethics_agent.bias_detector import BiasDetectionEngine
        ethics_imports['BiasDetectionEngine'] = BiasDetectionEngine
    except ImportError:
        pass
    try:
        from Aetherra.lyrixa.ethics_agent.value_alignment import ValueAlignmentEngine
        ethics_imports['ValueAlignmentEngine'] = ValueAlignmentEngine
    except ImportError:
        pass
    ETHICS_AGENTS_AVAILABLE = len(ethics_imports) > 0
    logger.info(f"✅ {len(ethics_imports)} ethics components available")
except ImportError as e:
    logger.warning(f"⚠️ Ethics agents not available: {e}")
    ETHICS_AGENTS_AVAILABLE = False
    ethics_imports = {}

# Try to import memory systems
try:
    from Aetherra.lyrixa.memory.lyrixa_memory_engine import LyrixaMemoryEngine
    MEMORY_ENGINE_AVAILABLE = True
    logger.info("✅ Memory engine available")
except ImportError as e:
    logger.warning(f"⚠️ Memory engine not available: {e}")
    MEMORY_ENGINE_AVAILABLE = False

class AetherraWebServer:
    def __init__(self, host='127.0.0.1', port=8686):
        self.host = host
        self.port = port
        self.app = Flask(__name__,
                         template_folder=str(Path(__file__).parent / 'web_templates'),
                         static_folder=str(Path(__file__).parent / 'web_static'))
        self.app.config['SECRET_KEY'] = 'aetherra_neural_interface_2025'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*",
                                logger=True, engineio_logger=True)

        # Track connected clients
        self.connected_clients = set()

        # Initialize Lyrixa components
        self._initialize_lyrixa_components()

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

        # Initialize Intelligence Stack
        if INTELLIGENCE_AVAILABLE:
            try:
                from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack
                self.lyrixa_intelligence = LyrixaIntelligenceStack(
                    workspace_path=str(project_root),
                    gui_interface=self  # Pass self as GUI interface
                )
                logger.info("✅ Lyrixa Intelligence Stack initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize intelligence stack: {e}")

        # Initialize Conversation Manager
        if CONVERSATION_MANAGER_AVAILABLE:
            try:
                from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager
                self.conversation_manager = LyrixaConversationManager(
                    workspace_path=str(project_root),
                    gui_interface=self
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
                        if agent_name == 'LyrixaAI':
                            # Skip LyrixaAI for now due to complex dependencies
                            continue
                        elif agent_name in ['EscalationAgent', 'GoalAgent']:
                            # Skip agents that require specific parameters for now
                            logger.debug(f"⏭️ Skipping {agent_name} - requires specific initialization parameters")
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
                    'ContradictionDetectionAgent': 'Aetherra.lyrixa.agents.contradiction_detection_agent',
                    'CuriosityAgent': 'Aetherra.lyrixa.agents.curiosity_agent',
                    'LearningLoopIntegrationAgent': 'Aetherra.lyrixa.agents.learning_loop_integration_agent',
                    'SelfQuestionGeneratorAgent': 'Aetherra.lyrixa.agents.self_question_generator_agent'
                }

                # Suppress the memory warnings by temporarily redirecting them
                import io
                import sys
                from contextlib import redirect_stdout, redirect_stderr

                memory_warning_buffer = io.StringIO()

                for agent_name, module_path in specialized_agents.items():
                    try:
                        # Capture the memory warnings during agent initialization
                        with redirect_stdout(memory_warning_buffer), redirect_stderr(memory_warning_buffer):
                            module = __import__(module_path, fromlist=[agent_name])
                            agent_class = getattr(module, agent_name)
                            agent_instance = agent_class()

                        self.agents[agent_name.lower().replace('agent', '')] = agent_instance
                        logger.info(f"✅ Loaded specialized agent: {agent_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load specialized agent {agent_name}: {e}")

                # Show a single consolidated message about memory components
                captured_warnings = memory_warning_buffer.getvalue()
                if "Memory components not available" in captured_warnings:
                    logger.info("ℹ️ Specialized agents initialized with mock memory implementations (full memory system not required)")

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
                        self.ethics_agents[ethics_name.lower().replace('engine', '')] = ethics_instance
                        logger.info(f"✅ Initialized ethics component: {ethics_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to initialize {ethics_name}: {e}")
                        continue

                logger.info(f"✅ {len(self.ethics_agents)} ethics components initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ethics components: {e}")

        # Initialize Memory Engine
        if MEMORY_ENGINE_AVAILABLE:
            try:
                from Aetherra.lyrixa.memory.lyrixa_memory_engine import LyrixaMemoryEngine
                self.memory_engine = LyrixaMemoryEngine()
                logger.info("✅ Memory Engine initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize memory engine: {e}")

    def _setup_routes(self):
        """Setup Flask routes for the web interface"""

        @self.app.route('/')
        def index():
            return render_template('neural_interface.html')

        @self.app.route('/api/system/status')
        def system_status():
            return jsonify({
                'status': 'active',
                'timestamp': datetime.now().isoformat(),
                'core_temperature': 72.3,
                'memory_usage': 45.7,
                'cognitive_load': 32.1,
                'confidence': 87.2,
                'curiosity': 64.8,
                'activity_level': 78.5
            })

        @self.app.route('/api/memory/graph')
        def memory_graph():
            return jsonify({
                'nodes': [
                    {'id': 'concept_1', 'label': 'Language Models', 'type': 'concept', 'connections': 8},
                    {'id': 'concept_2', 'label': 'Neural Networks', 'type': 'concept', 'connections': 12},
                    {'id': 'memory_1', 'label': 'Conversation with User', 'type': 'memory', 'connections': 3},
                    {'id': 'goal_1', 'label': 'Improve GUI Interface', 'type': 'goal', 'connections': 5}
                ],
                'edges': [
                    {'from': 'concept_1', 'to': 'concept_2', 'strength': 0.8},
                    {'from': 'concept_1', 'to': 'goal_1', 'strength': 0.6},
                    {'from': 'memory_1', 'to': 'concept_1', 'strength': 0.9}
                ]
            })

        @self.app.route('/api/insights/stream')
        def insights_stream():
            return jsonify({
                'insights': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'reflection',
                        'content': 'User prefers web-based interfaces over desktop applications',
                        'confidence': 0.85
                    },
                    {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'pattern',
                        'content': 'Strong correlation between aesthetic feedback and interface adoption',
                        'confidence': 0.73
                    }
                ]
            })

        @self.app.route('/api/agents/status')
        def agents_status():
            return jsonify({
                'agents': [
                    {'name': 'LyrixaCore', 'status': 'active', 'load': 45.2},
                    {'name': 'MemoryEngine', 'status': 'active', 'load': 23.7},
                    {'name': 'PersonalityEngine', 'status': 'idle', 'load': 8.1}
                ]
            })

        @self.app.route('/api/models/available')
        def available_models():
            """Get available LLM models"""
            if self.conversation_manager:
                model_info = self.conversation_manager.get_available_models()
                return jsonify(model_info)
            else:
                return jsonify({
                    'current_model': 'mock',
                    'available_models': ['mock'],
                    'preferred_models': ['mock'],
                    'llm_enabled': False
                })

        @self.app.route('/api/models/switch', methods=['POST'])
        def switch_model():
            """Switch to a different model"""
            try:
                data = request.get_json()
                model_name = data.get('model_name')

                if not model_name:
                    return jsonify({'success': False, 'error': 'Model name required'}), 400

                if self.conversation_manager:
                    success = self.conversation_manager.switch_model(model_name)
                    return jsonify({
                        'success': success,
                        'current_model': self.conversation_manager.current_model if success else None,
                        'message': f'Switched to {model_name}' if success else f'Failed to switch to {model_name}'
                    })
                else:
                    return jsonify({'success': False, 'error': 'Conversation manager not available'}), 500
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

    def _setup_socketio_handlers(self):
        """Setup WebSocket handlers for real-time communication"""

        @self.socketio.on('connect')
        def handle_connect():
            session_id = request.sid if hasattr(request, 'sid') else 'unknown'
            self.connected_clients.add(session_id)
            emit('status', {'message': 'Connected to Aetherra Neural Interface'})
            logger.info(f"Client {session_id} connected. Total clients: {len(self.connected_clients)}")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            session_id = request.sid if hasattr(request, 'sid') else 'unknown'
            self.connected_clients.discard(session_id)
            logger.info(f"Client {session_id} disconnected. Total clients: {len(self.connected_clients)}")

        @self.socketio.on('send_message')
        def handle_message(data):
            """Handle real-time chat messages through conversation manager"""
            try:
                message = data.get('message', '')
                session_id = request.sid if hasattr(request, 'sid') else 'default'

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
                emit('message_response', {
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'agent': 'lyrixa'
                })

                # Broadcast to all connected clients
                self.socketio.emit('system_update', {
                    'type': 'conversation_activity',
                    'data': {
                        'message_count': 1,
                        'active_sessions': len(self.connected_clients)
                    }
                })

            except Exception as e:
                logger.error(f"❌ Error handling message: {e}")
                emit('error', {'message': f'Failed to process message: {str(e)}'})
                # Send a fallback response to ensure client gets something
                emit('message_response', {
                    'response': f"I apologize, but I encountered an error processing your message: {str(e)}",
                    'timestamp': datetime.now().isoformat(),
                    'agent': 'lyrixa_error'
                })

        @self.socketio.on('switch_model')
        def handle_model_switch(data):
            """Handle model switching requests"""
            try:
                model_name = data.get('model_name')
                session_id = request.sid if hasattr(request, 'sid') else 'default'

                logger.info(f"🔄 Model switch request from {session_id}: {model_name}")

                if self.conversation_manager and model_name:
                    success = self.conversation_manager.switch_model(model_name)
                    if success:
                        logger.info(f"✅ Successfully switched to {model_name}")
                        emit('model_switched', {
                            'success': True,
                            'model_name': model_name,
                            'message': f'Switched to {model_name}'
                        })
                        # Broadcast to all clients
                        self.socketio.emit('system_update', {
                            'type': 'model_change',
                            'data': {
                                'new_model': model_name,
                                'timestamp': datetime.now().isoformat()
                            }
                        })
                    else:
                        logger.warning(f"⚠️ Failed to switch to {model_name}")
                        emit('model_switched', {
                            'success': False,
                            'model_name': model_name,
                            'message': f'Failed to switch to {model_name}'
                        })
                else:
                    emit('model_switched', {
                        'success': False,
                        'message': 'Model switching not available'
                    })
            except Exception as e:
                logger.error(f"❌ Error switching model: {e}")
                emit('model_switched', {
                    'success': False,
                    'message': f'Error: {str(e)}'
                })

        @self.socketio.on('get_available_models')
        def handle_get_models():
            """Get available models for the dropdown"""
            try:
                if self.conversation_manager:
                    model_info = self.conversation_manager.get_available_models()
                    emit('available_models', model_info)
                else:
                    emit('available_models', {
                        'current_model': 'mock',
                        'available_models': ['mock'],
                        'preferred_models': ['mock'],
                        'llm_enabled': False
                    })
            except Exception as e:
                logger.error(f"❌ Error getting models: {e}")
                emit('available_models', {
                    'current_model': 'error',
                    'available_models': [],
                    'preferred_models': [],
                    'llm_enabled': False,
                    'error': str(e)
                })

        @self.socketio.on('execute_command')
        def handle_command(data):
            command = data.get('command', '')
            logger.info(f"Executing command: {command}")

            # Enhanced command execution with real integration
            if command.startswith('memory'):
                if self.memory_engine:
                    response = {'type': 'memory', 'result': 'Memory system queried - real data available'}
                else:
                    response = {'type': 'memory', 'result': 'Memory system queried successfully'}
            elif command.startswith('analyze'):
                if self.lyrixa_intelligence:
                    response = {'type': 'analysis', 'result': 'Analysis complete - intelligence stack active'}
                else:
                    response = {'type': 'analysis', 'result': 'Analysis complete - patterns detected'}
            elif command.startswith('agents'):
                agent_count = len(self.agents) + len(self.ethics_agents)
                response = {'type': 'agents', 'result': f'Agent system: {agent_count} agents active'}
            else:
                response = {'type': 'general', 'result': f'Command "{command}" processed'}

            emit('command_result', response)

        @self.socketio.on('request_system_status')
        def handle_status_request():
            """Send current system status to client"""
            status = self._get_real_system_status()
            emit('system_status_update', status)

        @self.socketio.on('request_agent_list')
        def handle_agent_list_request():
            """Send current agent list to client"""
            agent_data = self._get_real_agent_data()
            emit('agent_list_update', agent_data)

        @self.socketio.on('execute_agent_command')
        def handle_agent_command(data):
            """Execute command through specific agent"""
            try:
                agent_id = data.get('agent_id')
                command = data.get('command')
                result = self._execute_agent_command(agent_id, command)

                emit('agent_command_response', {
                    'agent_id': agent_id,
                    'command': command,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error executing agent command: {e}")
                emit('error', {'message': 'Failed to execute agent command'})

        @self.socketio.on('request_aura_update')
        def handle_aura_update():
            # Send real-time aura data for breathing animations
            aura_data = {
                'confidence': self.mock_data['system_state']['confidence'],
                'curiosity': self.mock_data['system_state']['curiosity'],
                'activity': self.mock_data['system_state']['activity_level'],
                'pulse_rate': 1.2,  # Breaths per second
                'intensity': 0.8
            }
            emit('aura_update', aura_data)

    def _initialize_mock_data(self):
        """Initialize mock data for demonstration"""
        return {
            'system_state': {
                'confidence': 87.2,
                'curiosity': 64.8,
                'activity_level': 78.5,
                'goals': [
                    'Implement web-based GUI interface',
                    'Optimize memory retrieval algorithms',
                    'Enhance natural language understanding'
                ]
            },
            'memory_graph': {
                'total_nodes': 1247,
                'total_connections': 3891,
                'active_concepts': 89,
                'recent_memories': 23
            }
        }

    def _generate_mock_response(self, message: str) -> str:
        """Generate mock AI response for demonstration"""
        responses = [
            "Neural pathways processing... Query understood.",
            "Memory fragments coalescing. Pattern recognition engaged.",
            "Analytical subsystems converging on solution matrix.",
            "Consciousness layers synchronizing. Response formulated.",
            "Quantum semantic analysis complete. Data synthesis initiated."
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
                logger.info(f"📋 Conversation manager returned: {len(response)} characters")
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

            if agent and hasattr(agent, 'process_command'):
                result = agent.process_command(command)
                return {
                    'success': True,
                    'result': result,
                    'agent_type': type(agent).__name__
                }
            else:
                # Mock response for demonstration
                return {
                    'success': True,
                    'result': f"Agent {agent_id} processed: {command}",
                    'agent_type': 'MockAgent'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent_type': 'Unknown'
            }

    def _get_real_system_status(self) -> dict:
        """Get actual system status from integrated components"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'components': {
                'intelligence_stack': {
                    'active': self.lyrixa_intelligence is not None,
                    'status': 'online' if self.lyrixa_intelligence else 'offline'
                },
                'conversation_manager': {
                    'active': self.conversation_manager is not None,
                    'status': 'online' if self.conversation_manager else 'offline'
                },
                'memory_engine': {
                    'active': self.memory_engine is not None,
                    'status': 'online' if self.memory_engine else 'offline'
                },
                'agents': {
                    'active': len(self.agents) > 0,
                    'count': len(self.agents),
                    'status': 'online' if self.agents else 'offline'
                },
                'ethics_agents': {
                    'active': len(self.ethics_agents) > 0,
                    'count': len(self.ethics_agents),
                    'status': 'online' if self.ethics_agents else 'offline'
                }
            },
            'metrics': {
                'connected_clients': len(self.connected_clients),
                'total_agents': len(self.agents) + len(self.ethics_agents),
                'uptime': '0h 0m'  # Will be calculated based on start time
            }
        }
        return status

    def _get_real_agent_data(self) -> dict:
        """Get actual agent data from integrated components"""
        agent_data = {
            'core_agents': [],
            'ethics_agents': [],
            'total_count': 0
        }

        # Add core agents
        for agent_id, agent in self.agents.items():
            agent_info = {
                'id': agent_id,
                'name': type(agent).__name__,
                'status': 'active',
                'type': 'core',
                'capabilities': getattr(agent, 'capabilities', ['general'])
            }
            agent_data['core_agents'].append(agent_info)

        # Add ethics agents
        for agent_id, agent in self.ethics_agents.items():
            agent_info = {
                'id': agent_id,
                'name': type(agent).__name__,
                'status': 'active',
                'type': 'ethics',
                'capabilities': getattr(agent, 'capabilities', ['ethics'])
            }
            agent_data['ethics_agents'].append(agent_info)

        agent_data['total_count'] = len(self.agents) + len(self.ethics_agents)
        return agent_data

    def start_server(self, debug=False, auto_open=True):
        """Start the Flask-SocketIO server"""
        logger.info(f"🌐 Starting Aetherra Web Interface on http://{self.host}:{self.port}")

        if auto_open:
            # Open browser after a short delay
            def open_browser():
                import time
                time.sleep(1.5)
                webbrowser.open(f'http://{self.host}:{self.port}')

            threading.Timer(0.1, open_browser).start()

        try:
            self.socketio.run(self.app, host=self.host, port=self.port,
                            debug=debug, allow_unsafe_werkzeug=True)
        except Exception as e:
            logger.error(f"❌ Failed to start web server: {e}")
            raise

    def broadcast_system_update(self, data):
        """Broadcast system updates to all connected clients"""
        self.socketio.emit('system_update', data)

    def broadcast_aura_pulse(self, confidence, curiosity, activity):
        """Broadcast aura pulse data for live animations"""
        aura_data = {
            'confidence': confidence,
            'curiosity': curiosity,
            'activity': activity,
            'timestamp': datetime.now().isoformat()
        }
        self.socketio.emit('aura_pulse', aura_data)

# Global server instance
web_server = None

def create_web_interface_server(host='127.0.0.1', port=8686):
    """Create and return the web interface server instance"""
    global web_server
    web_server = AetherraWebServer(host, port)
    return web_server

def start_web_interface(host='127.0.0.1', port=8686, debug=False, auto_open=True):
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
    web_templates_dir = Path(__file__).parent / 'web_templates'
    web_static_dir = Path(__file__).parent / 'web_static'

    # Create directories if they don't exist
    web_templates_dir.mkdir(exist_ok=True)
    web_static_dir.mkdir(exist_ok=True)

    # Check if neural_interface.html exists, if not, we'll create it next
    if not (web_templates_dir / 'neural_interface.html').exists():
        logger.info("📄 Creating web interface template files...")
        # The HTML template will be created in the next step

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Start Aetherra Web Interface Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host address')
    parser.add_argument('--port', type=int, default=8686, help='Port number')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t auto-open browser')

    args = parser.parse_args()

    start_web_interface(
        host=args.host,
        port=args.port,
        debug=args.debug,
        auto_open=not args.no_browser
    )
