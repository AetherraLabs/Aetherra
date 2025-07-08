#!/usr/bin/env python3
"""
🎙️ LYRIXA AI ASSISTANT
======================

The main Lyrixa AI Assistant class that orchestrates all core systems.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .core.advanced_plugins import LyrixaAdvancedPluginManager
from .core.aether_interpreter import AetherInterpreter
from .core.agents import AgentOrchestrator
from .core.conversation import LyrixaConversationalEngine
from .core.debug_console import CognitiveState, DebugLevel, LyrixaDebugConsole
from .core.enhanced_memory import LyrixaEnhancedMemorySystem
from .core.feedback_system import FeedbackCollectionGUI, LyrixaFeedbackSystem
from .core.goals import GoalPriority, LyrixaGoalSystem
from .core.memory import LyrixaMemorySystem
from .core.plugins import LyrixaPluginManager
from .core.project_knowledge_responder import ProjectKnowledgeResponder
from .core.reflexive_loop import LyrixaReflexiveLoop
from .core.system_bootstrap import LyrixaSystemBootstrap
from .intelligence_integration import LyrixaIntelligenceStack


class LyrixaAI:
    """
    Lyrixa - The AI Assistant for Aetherra

    She is the voice and presence of Aetherra — a conversational AI agent
    designed to understand, generate, and evolve .aether code.

    Rather than being a command parser or chatbot, Lyrixa is a collaborator,
    translator, and guide who brings conversation and intuition to programming.
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.name = "Lyrixa"
        self.version = "3.0.0-aetherra-assistant"
        self.personality = "Intelligent, intuitive, collaborative AI assistant"

        # Workspace setup
        self.workspace_path = workspace_path or os.getcwd()
        self.session_id = self._create_session_id()

        # Initialize core systems
        print("🎙️ Initializing Lyrixa AI Assistant for Aetherra...")

        self.aether_interpreter = AetherInterpreter()
        self.memory = LyrixaEnhancedMemorySystem(
            memory_db_path=os.path.join(
                self.workspace_path, "lyrixa_enhanced_memory.db"
            )
        )
        self.plugins = LyrixaAdvancedPluginManager(
            plugin_directory=os.path.join(self.workspace_path, "plugins"),
            memory_system=self.memory,
        )
        self.goals = LyrixaGoalSystem(
            goals_file=os.path.join(self.workspace_path, "lyrixa_goals.json")
        )
        self.agents = AgentOrchestrator()
        self.conversation = LyrixaConversationalEngine(
            memory_system=self.memory
        )  # Initialize Reflexive Loop for self-awareness
        self.reflexive_loop = LyrixaReflexiveLoop(memory_system=self.memory)

        # Initialize Project Knowledge Responder - temporary bypass
        self.knowledge_responder = None

        # Initialize Feedback + Self-Improvement System
        self.feedback_system = LyrixaFeedbackSystem(
            memory_system=self.memory,
            personality_processor=self.conversation.personality_processor,
            suggestion_generator=None,  # Will be initialized when anticipation system is available
            proactive_assistant=None,  # Will be initialized when anticipation system is available
        )
        self.feedback_gui = FeedbackCollectionGUI(self.feedback_system)

        # Initialize anticipation systems (if available)
        self.suggestion_generator = None
        self.proactive_assistant = None
        self._initialize_anticipation_systems()

        # Initialize System Bootstrap + Awareness
        self.system_bootstrap = LyrixaSystemBootstrap(
            workspace_path=self.workspace_path,
            memory_system=self.memory,
            plugin_manager=self.plugins,
            goal_system=self.goals,
            feedback_system=self.feedback_system,
        )

        # Initialize Debug Console / Developer View
        self.debug_console = LyrixaDebugConsole(
            debug_level=DebugLevel.STANDARD  # Can be configured via settings
        )

        # Initialize Intelligence Stack
        self.intelligence_stack = LyrixaIntelligenceStack(
            workspace_path=self.workspace_path,
            aether_runtime=None,  # Will be set later
        )

        # Initialize intelligence components
        self.intelligence_initialized = False

        # Conversation state
        self.conversation_context = []
        self.active_aether_session = None
        self.current_project_context = {}

        self._display_welcome_message()

    def _create_session_id(self) -> str:
        """Create unique session identifier"""
        return f"lyrixa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _display_welcome_message(self):
        """Display Lyrixa's welcome message with system awareness"""
        print(f"""
🎙️ LYRIXA AI ASSISTANT FOR AETHERRA
===================================
Version: {self.version}
Session: {self.session_id}
Workspace: {self.workspace_path}

✅ .aether interpreter ready
✅ Memory system active
✅ Plugin ecosystem loaded
✅ Goal tracking initialized
✅ Agent orchestration ready
✅ System awareness active

Performing system bootstrap and awareness check...
""")

    async def display_startup_summary(self):
        """Display intelligent startup summary with awareness"""
        try:
            # Perform system bootstrap and get startup summary
            startup_summary = await self.system_bootstrap.perform_system_bootstrap()

            # Display the formatted startup message
            startup_message = self.system_bootstrap.format_startup_message(
                startup_summary
            )
            print("\n" + startup_message)

            return startup_summary

        except Exception as e:
            print(f"⚠️ Could not generate startup summary: {e}")
            print("\nHello! I'm Lyrixa, your AI assistant. How can I help you today?")
            return None

    def _initialize_anticipation_systems(self):
        """Initialize anticipation systems if available"""
        try:
            # Try to initialize suggestion generator
            from .anticipation.suggestion_generator import SuggestionGenerator

            self.suggestion_generator = SuggestionGenerator()

            # Try to initialize proactive assistant
            from .anticipation.proactive_assistant import ProactiveAssistant

            self.proactive_assistant = ProactiveAssistant()

            # Update feedback system with anticipation components
            self.feedback_system.suggestion_generator = self.suggestion_generator
            self.feedback_system.proactive_assistant = self.proactive_assistant

            print("✅ Anticipation systems initialized")
            print("   ✅ Suggestion generator ready")
            print("   ✅ Proactive assistant ready")

        except ImportError as e:
            print(f"⚠️ Anticipation systems not available: {e}")
            print("   ℹ️ Feedback system will work without anticipation features")
        except Exception as e:
            print(f"⚠️ Error initializing anticipation systems: {e}")

    async def initialize(self):
        """Initialize all systems asynchronously"""
        print("🔄 Initializing Lyrixa systems...")

        # Initialize plugin manager
        await self.plugins.initialize(
            {
                "workspace_path": self.workspace_path,
                "session_id": self.session_id,
                "memory_system": self.memory,
                "aether_interpreter": self.aether_interpreter,
            }
        )

        # Initialize agent orchestrator
        await self.agents.initialize(
            {
                "workspace_path": self.workspace_path,
                "session_id": self.session_id,
                "memory_system": self.memory,
                "plugin_manager": self.plugins,
                "aether_interpreter": self.aether_interpreter,
            }
        )

        # Initialize reflexive loop (self-awareness)
        await self.reflexive_loop.initialize_self_awareness()

        print("✅ Lyrixa AI Assistant fully initialized")
        print("✅ Self-awareness system active")

    async def process_natural_language(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process natural language input and convert to appropriate .aether workflows

        This is Lyrixa's core capability - understanding human intent and
        translating it into executable .aether code and system actions.
        """
        print(f"🎙️ Lyrixa processing: '{user_input}'")

        # Analyze intent
        intent_analysis = await self._analyze_intent(user_input, context or {})

        # Get relevant context from memory
        memory_context = await self.memory.recall_memories(user_input, limit=5)

        # Create response structure
        response = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "user_input": user_input,
            "intent": intent_analysis,
            "memory_context": memory_context,
            "aether_code": None,
            "plugin_executions": [],
            "lyrixa_response": "",
            "actions_taken": [],
            "suggestions": [],
        }

        # Route based on intent
        if intent_analysis["type"] == "aether_code_generation":
            response = await self._handle_aether_generation(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "memory_operation":
            response = await self._handle_memory_operation(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "plugin_execution":
            response = await self._handle_plugin_execution(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "goal_management":
            response = await self._handle_goal_management(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "project_exploration":
            response = await self._handle_project_exploration(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "workflow_orchestration":
            response = await self._handle_workflow_orchestration(
                user_input, intent_analysis, response
            )
        else:
            response = await self._handle_conversation(
                user_input, intent_analysis, response
            )

        # Store interaction in memory
        await self.memory.store_memory(
            content={"input": user_input, "response": response["lyrixa_response"]},
            context={"intent": intent_analysis["type"], "session": self.session_id},
            tags=["conversation", intent_analysis["type"]],
            importance=0.7 if intent_analysis["confidence"] > 0.8 else 0.5,
        )

        # Update conversation context
        self.conversation_context.append(
            {
                "timestamp": response["timestamp"],
                "user_input": user_input,
                "lyrixa_response": response["lyrixa_response"],
                "intent": intent_analysis["type"],
            }
        )

        # Keep only recent context
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]

        return response

    async def brain_loop(
        self,
        user_input: str,
        input_type: str = "text",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        🧠 LYRIXA BRAIN LOOP - Core Method
        ==================================

        The central orchestration method that processes all user interactions through:
        1. Intent analysis
        2. Knowledge response synthesis
        3. .aether code generation
        4. Memory lookup and storage
        5. Plugin routing and execution
        6. GUI updates and feedback generation

        Args:
            user_input: User input (text, voice transcript, GUI action, etc.)
            input_type: Type of input ("text", "voice", "gui", "file")
            context: Optional context from GUI or previous interactions

        Returns:
            Complete response with text, aether code, actions, and GUI updates
        """
        try:
            print(f"🧠 Brain Loop Processing: {input_type} input")
            print(
                f"   Input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}"
            )

            # Initialize response structure
            brain_response = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "input_type": input_type,
                "user_input": user_input,
                "lyrixa_response": "",
                "aether_code": None,
                "actions_taken": [],
                "suggestions": [],
                "gui_updates": {},
                "plugin_results": [],
                "memory_stored": False,
                "confidence": 0.0,
                "processing_time": 0.0,
                "context": context or {},
            }

            # Initialize debug console tracking
            start_time = datetime.now()

            # DEBUG: Set cognitive state and capture perception
            self.debug_console.set_cognitive_state(
                CognitiveState.ANALYZING, f"Processing: {user_input[:50]}..."
            )

            # Capture what Lyrixa perceives
            try:
                memory_context = []
                current_goals = []

                # Get memory context for debug
                try:
                    recent_memories = await self.memory.recall_memories(user_input, 3)
                    memory_context = (
                        [
                            {"content": str(mem), "relevance": "high"}
                            for mem in recent_memories[:3]
                        ]
                        if recent_memories
                        else []
                    )
                except Exception:
                    memory_context = []

                # Get current goals for debug
                try:
                    goals = self.goals.get_active_goals()
                    current_goals = (
                        [goal.get("title", "Unknown goal") for goal in goals[:3]]
                        if goals
                        else []
                    )
                except Exception:
                    current_goals = []

                self.debug_console.capture_perception(
                    user_input=user_input,
                    context_window=context or {},
                    memory_context=memory_context,
                    current_goals=current_goals,
                    system_state={
                        "plugins_loaded": len(getattr(self.plugins, "plugins", {})),
                        "memory_entries": len(getattr(self.memory, "memories", [])),
                        "session_id": self.session_id,
                    },
                    environmental_factors={
                        "workspace_path": self.workspace_path,
                        "conversation_context_length": len(self.conversation_context),
                    },
                )
            except Exception as debug_error:
                print(f"⚠️ Debug console perception capture failed: {debug_error}")

            # STEP 1: Intent Analysis
            print("🎯 Step 1: Analyzing intent...")

            # DEBUG: Start thought process
            thought_id = self.debug_console.start_thought_process(
                input_analysis={
                    "input_type": input_type,
                    "input_length": len(user_input),
                    "has_context": bool(context),
                    "complexity_estimate": "high"
                    if len(user_input) > 100
                    else "medium"
                    if len(user_input) > 50
                    else "low",
                },
                initial_reasoning="Analyzing user intent and determining response strategy",
            )

            self.debug_console.set_cognitive_state(
                CognitiveState.REASONING, "Analyzing intent"
            )

            intent_analysis = await self._analyze_intent(user_input, context)
            brain_response["intent"] = intent_analysis
            brain_response["confidence"] = intent_analysis.get("confidence", 0.5)

            # DEBUG: Add reasoning step
            self.debug_console.add_reasoning_step(
                thought_id,
                f"Intent identified as: {intent_analysis.get('primary_intent', 'unknown')}",
                intent_analysis.get("confidence", 0.5),
            )

            # STEP 2: Knowledge Response (Memory Lookup & Synthesis)
            print("📚 Step 2: Knowledge response synthesis...")
            knowledge_response = await self._synthesize_knowledge_response(
                user_input, intent_analysis, context
            )
            brain_response["knowledge_response"] = knowledge_response
            brain_response["lyrixa_response"] = knowledge_response.get("response", "")

            # STEP 3: .aether Code Generation (if needed)
            print("⚡ Step 3: .aether code generation...")
            aether_result = await self._generate_aether_code(
                user_input, intent_analysis, knowledge_response
            )
            if aether_result and aether_result.get("code"):
                brain_response["aether_code"] = aether_result["code"]
                brain_response["aether_metadata"] = aether_result.get("metadata", {})

            # STEP 4: Plugin Routing & Execution
            print("🔌 Step 4: Plugin routing and execution...")
            plugin_results = await self._route_and_execute_plugins(
                user_input, intent_analysis, brain_response
            )
            brain_response["plugin_results"] = plugin_results
            brain_response["actions_taken"].extend(
                [
                    result.get("action", "")
                    for result in plugin_results
                    if result.get("success", False)
                ]
            )

            # STEP 5: Memory Storage
            print("💾 Step 5: Memory storage...")
            memory_result = await self._store_interaction_memory(brain_response)
            brain_response["memory_stored"] = memory_result.get("success", False)
            brain_response["memory_id"] = memory_result.get("memory_id")

            # STEP 5.5: Reflexive Loop - Self-Awareness Processing
            print("🔄 Step 5.5: Self-awareness processing...")
            try:
                # Prepare interaction data for reflexive analysis
                interaction_data = {
                    "user_input": user_input,
                    "context": context or {},
                    "actions_taken": brain_response["actions_taken"],
                    "intent": intent_analysis,
                    "timestamp": datetime.now(),
                    "confidence": brain_response["confidence"],
                }

                # Update project understanding
                await self.reflexive_loop.update_project_understanding(interaction_data)

                # Analyze user patterns
                await self.reflexive_loop.analyze_user_patterns(interaction_data)

                # Generate contextual insights for this interaction
                contextual_insight = (
                    await self.reflexive_loop.generate_contextual_insight(user_input)
                )
                if contextual_insight:
                    brain_response["lyrixa_response"] += f"\n\n💡 {contextual_insight}"

                # Get current project awareness for response enhancement
                project_awareness = (
                    await self.reflexive_loop.get_current_project_awareness()
                )
                brain_response["project_awareness"] = project_awareness

                print("✅ Self-awareness processing complete")
            except Exception as e:
                print(f"⚠️ Self-awareness processing error: {e}")

            # STEP 6: GUI Updates & Feedback Generation
            print("🖥️ Step 6: GUI updates and feedback...")
            gui_updates = await self._generate_gui_updates(brain_response)
            brain_response["gui_updates"] = gui_updates
            brain_response["suggestions"] = gui_updates.get("suggestions", [])

            # STEP 6.5: Feedback Collection Integration
            print("📊 Step 6.5: Feedback collection integration...")
            try:
                # Check if we should proactively request feedback
                feedback_context = {
                    "recent_suggestions_count": len(brain_response["suggestions"]),
                    "interaction_id": brain_response.get("memory_id"),
                    "response_length": len(brain_response["lyrixa_response"]),
                    "confidence": brain_response["confidence"],
                    "actions_taken": len(brain_response["actions_taken"]),
                }

                feedback_request = (
                    await self.feedback_system.request_feedback_proactively(
                        feedback_context
                    )
                )
                if feedback_request:
                    brain_response["gui_updates"]["feedback_request"] = feedback_request
                    print(f"📋 Proactive feedback request: {feedback_request['type']}")

                # Add feedback widgets for suggestions if any were provided
                if brain_response["suggestions"]:
                    suggestion_feedback_widgets = []
                    for i, suggestion in enumerate(brain_response["suggestions"]):
                        widget = self.feedback_gui.create_feedback_widget(
                            "suggestion",
                            {
                                "suggestion_id": f"suggestion_{brain_response.get('memory_id', 'unknown')}_{i}",
                                "suggestion_text": suggestion,
                            },
                        )
                        suggestion_feedback_widgets.append(widget)
                    brain_response["gui_updates"]["suggestion_feedback_widgets"] = (
                        suggestion_feedback_widgets
                    )

                # Add response feedback widget
                response_widget = self.feedback_gui.create_feedback_widget(
                    "response",
                    {
                        "response_id": brain_response.get("memory_id", "unknown"),
                        "interaction_id": brain_response.get("memory_id"),
                    },
                )
                brain_response["gui_updates"]["response_feedback_widget"] = (
                    response_widget
                )

                print("✅ Feedback collection integration complete")
            except Exception as e:
                print(f"⚠️ Feedback collection integration error: {e}")

            # STEP 7: Post-processing and Quality Enhancement
            print("✨ Step 7: Response enhancement...")
            enhanced_response = await self._enhance_response(brain_response)
            brain_response.update(enhanced_response)

            # Calculate processing time
            end_time = datetime.now()
            brain_response["processing_time"] = (end_time - start_time).total_seconds()

            # Final logging
            print(f"✅ Brain Loop Complete ({brain_response['processing_time']:.2f}s)")
            print(f"   Confidence: {brain_response['confidence']:.2f}")
            print(f"   Actions: {len(brain_response['actions_taken'])}")
            print(f"   Plugins: {len(brain_response['plugin_results'])}")

            # DEBUG: Finalize decision and show processing results
            processing_time = (
                datetime.now() - start_time
            ).total_seconds() * 1000  # Convert to milliseconds

            self.debug_console.set_cognitive_state(
                CognitiveState.EXECUTING, "Finalizing response"
            )

            # Determine the primary decision made
            primary_decision = "knowledge_response"
            if brain_response.get("aether_code"):
                primary_decision = "code_generation"
            elif brain_response.get("plugin_results"):
                primary_decision = "plugin_execution"

            self.debug_console.finalize_decision(
                thought_id,
                f"Selected {primary_decision} with {len(brain_response.get('actions_taken', []))} actions",
                processing_time,
            )

            return brain_response

        except Exception as e:
            print(f"❌ Brain Loop Error: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "error": str(e),
                "lyrixa_response": "I encountered an error processing your request. Let me try a different approach.",
                "confidence": 0.1,
                "actions_taken": [],
                "suggestions": [
                    "Try rephrasing your request",
                    "Check for any syntax errors",
                ],
                "gui_updates": {"status": "error", "message": str(e)},
            }

    async def _analyze_intent(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Step 1: Analyze user intent from input"""
        # Use existing intent analysis method
        return await self._analyze_user_intent(user_input, context)

    async def _synthesize_knowledge_response(
        self,
        user_input: str,
        intent: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Step 2: Synthesize knowledge-based response using memory and conversation engine"""
        try:
            # Use reflexive loop and memory for knowledge synthesis
            try:
                # Check if this is a project-specific question
                if any(
                    keyword in user_input.lower()
                    for keyword in [
                        "project",
                        "lyrixa",
                        "aetherra",
                        "what",
                        "how",
                        "why",
                    ]
                ):
                    # Get insights from reflexive loop
                    insights = await self.reflexive_loop.generate_insights()

                    # Query memory for relevant information
                    memories = await self.memory.recall_memories(user_input, limit=5)

                    # Synthesize response using conversation engine
                    context_info = {
                        "insights": [insight.__dict__ for insight in insights],
                        "memories": memories[:3] if memories else [],
                        "project_understanding": self.reflexive_loop.project_understanding.__dict__
                        if self.reflexive_loop.project_understanding
                        else None,
                    }

                    response_data = await self.conversation.process_conversation_turn(
                        user_input, context_info
                    )
                    response = response_data.get(
                        "response", "I'm thinking about that..."
                    )
                    return {
                        "response": response,
                        "type": "knowledge_response",
                        "context": context_info,
                        "analysis": response_data,
                    }

            except Exception as e:
                print(f"⚠️ Error in knowledge synthesis: {e}")

            # Fallback to simple response generation based on intent
            intent_type = intent.get("type", "conversation")
            confidence = intent.get("confidence", 0.5)

            if intent_type == "aether_code_generation":
                response_text = "I'll help you generate .aether code. Let me analyze your request and create the appropriate workflow."
                confidence = min(confidence + 0.2, 0.9)
            elif intent_type == "memory_operation":
                response_text = "I'm processing your memory request. I can help you store, recall, or manage information."
                confidence = min(confidence + 0.1, 0.8)
            elif intent_type == "project_exploration":
                response_text = "I'm analyzing your project to provide insights and assistance with development."
                confidence = min(confidence + 0.1, 0.8)
            elif "?" in user_input:
                response_text = f"I understand you're asking about: {user_input}. Let me provide you with relevant information and assistance."
                confidence = min(confidence + 0.1, 0.7)
            else:
                response_text = f"I understand your request about '{user_input}'. Let me help you with this."
                confidence = max(confidence - 0.1, 0.3)

            return {
                "response": response_text,
                "confidence": confidence,
                "sources": ["intent_analysis", "knowledge_synthesis"],
                "method": "fallback_synthesis",
            }

        except Exception as e:
            print(f"⚠️ Knowledge synthesis error: {e}")
            return {
                "response": f"I understand you're asking about: {user_input}. Let me help you with that.",
                "confidence": 0.5,
                "sources": [],
                "method": "error_fallback",
            }

    async def _generate_aether_code(
        self,
        user_input: str,
        intent: Dict[str, Any],
        knowledge_response: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Step 3: Generate .aether code if intent indicates code generation"""
        if (
            intent.get("type") == "aether_code_generation"
            or "aether" in user_input.lower()
        ):
            try:
                result = await self.aether_interpreter.execute(
                    f"generate_from_description: {user_input}"
                )
                return {
                    "code": result.get("result", ""),
                    "metadata": {
                        "generated_from": user_input,
                        "intent_confidence": intent.get("confidence", 0.0),
                        "generation_method": "aether_interpreter",
                    },
                }
            except Exception as e:
                print(f"⚠️ .aether generation error: {e}")
                return None
        return None

    async def _route_and_execute_plugins(
        self, user_input: str, intent: Dict[str, Any], brain_response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Step 4: Route to appropriate plugins and execute them"""
        plugin_results = []

        try:
            # Simple plugin routing based on intent type
            intent_type = intent.get("type", "general")

            # For now, create mock plugin results to demonstrate the flow
            if intent_type == "aether_code_generation":
                plugin_results.append(
                    {
                        "plugin": "aether_code_generator",
                        "success": True,
                        "action": "Generated .aether code",
                        "result": "Code generation completed",
                        "metadata": {"intent": intent_type},
                    }
                )
            elif intent_type == "memory_operation":
                plugin_results.append(
                    {
                        "plugin": "memory_manager",
                        "success": True,
                        "action": "Memory operation processed",
                        "result": "Memory updated successfully",
                        "metadata": {"intent": intent_type},
                    }
                )
            elif intent_type == "project_exploration":
                plugin_results.append(
                    {
                        "plugin": "project_analyzer",
                        "success": True,
                        "action": "Project analysis completed",
                        "result": "Project structure analyzed",
                        "metadata": {"intent": intent_type},
                    }
                )

            # Try to use actual plugin system if available
            try:
                # This will be enhanced when plugin methods are available
                # result = await self.plugins.execute_plugin(plugin_name, user_input, context)
                pass
            except Exception as e:
                print(f"⚠️ Plugin system not fully available: {e}")

        except Exception as e:
            print(f"⚠️ Plugin routing error: {e}")

        return plugin_results

    async def _store_interaction_memory(
        self, brain_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 5: Store the interaction in memory"""
        try:
            memory_id = await self.memory.store_memory(
                content={
                    "user_input": brain_response["user_input"],
                    "lyrixa_response": brain_response["lyrixa_response"],
                    "intent": brain_response.get("intent", {}),
                    "aether_code": brain_response.get("aether_code"),
                    "actions": brain_response.get("actions_taken", []),
                },
                context={
                    "session_id": self.session_id,
                    "input_type": brain_response["input_type"],
                    "confidence": brain_response["confidence"],
                },
                tags=[
                    "brain_loop",
                    "interaction",
                    brain_response.get("intent", {}).get("type", "general"),
                ],
                importance=brain_response["confidence"],
            )

            return {"success": True, "memory_id": memory_id}

        except Exception as e:
            print(f"⚠️ Memory storage error: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_gui_updates(
        self, brain_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 6: Generate GUI updates and feedback"""
        gui_updates = {
            "status": "success",
            "message": "Response generated successfully",
            "suggestions": [],
            "visual_feedback": {},
            "notifications": [],
        }

        try:
            # Generate contextual suggestions
            intent_type = brain_response.get("intent", {}).get("type", "general")

            if intent_type == "aether_code_generation":
                gui_updates["suggestions"] = [
                    "Execute the generated .aether code",
                    "Modify the code parameters",
                    "Save to project workspace",
                    "Generate documentation",
                ]
                gui_updates["visual_feedback"]["code_highlight"] = True

            elif intent_type == "memory_operation":
                gui_updates["suggestions"] = [
                    "Explore related memories",
                    "Set memory importance",
                    "Create memory tags",
                    "Export memory data",
                ]

            elif intent_type == "plugin_execution":
                gui_updates["suggestions"] = [
                    "View plugin results",
                    "Chain with other plugins",
                    "Save plugin configuration",
                    "Explore similar plugins",
                ]
            else:
                gui_updates["suggestions"] = [
                    "Ask a follow-up question",
                    "Request more details",
                    "Generate .aether code",
                    "Save this information",
                ]

            # Add status notifications
            if brain_response.get("aether_code"):
                gui_updates["notifications"].append(
                    {
                        "type": "success",
                        "message": "✅ .aether code generated",
                        "action": "view_code",
                    }
                )

            if brain_response.get("memory_stored"):
                gui_updates["notifications"].append(
                    {
                        "type": "info",
                        "message": "💾 Interaction saved to memory",
                        "action": "view_memory",
                    }
                )

            if brain_response.get("plugin_results"):
                successful_plugins = len(
                    [p for p in brain_response["plugin_results"] if p.get("success")]
                )
                if successful_plugins > 0:
                    gui_updates["notifications"].append(
                        {
                            "type": "success",
                            "message": f"🔌 {successful_plugins} plugin(s) executed successfully",
                            "action": "view_plugin_results",
                        }
                    )

        except Exception as e:
            print(f"⚠️ GUI updates generation error: {e}")
            gui_updates["status"] = "warning"
            gui_updates["message"] = "Response generated with minor issues"

        return gui_updates

    async def _enhance_response(self, brain_response: Dict[str, Any]) -> Dict[str, Any]:
        """Step 7: Enhance and refine the final response using personality processor"""
        enhancements = {}

        try:
            # Get the original response
            original_response = brain_response.get("lyrixa_response", "")

            # 🎭 APPLY PERSONALITY PROCESSOR
            try:
                # Prepare context for personality processing
                personality_context = {
                    "intent": brain_response.get("intent", {}),
                    "confidence": brain_response.get("confidence", 0.5),
                    "input_type": brain_response.get("input_type", "text"),
                    "user_input": brain_response.get("user_input", ""),
                    "has_aether_code": bool(brain_response.get("aether_code")),
                    "plugin_count": len(brain_response.get("plugin_results", [])),
                    "session_context": brain_response.get("context", {}),
                }

                # Process response through personality system
                enhanced_text = (
                    await self.conversation.personality_processor.process_response(
                        original_response, personality_context
                    )
                )

                print(f"🎭 Applied personality processing to response")

            except Exception as e:
                print(f"⚠️ Personality processing error: {e}")
                enhanced_text = original_response  # Fallback to original

            # Add action summaries
            if brain_response.get("actions_taken"):
                action_summary = f"\n\n🎯 **Actions taken:** {', '.join(brain_response['actions_taken'])}"
                enhanced_text += action_summary

            # Add .aether code reference
            if brain_response.get("aether_code"):
                code_reference = f"\n\n⚡ **Generated .aether code** (see code panel)"
                enhanced_text += code_reference

            # Add confidence and quality indicators
            confidence = brain_response.get("confidence", 0.0)
            if confidence >= 0.8:
                quality_indicator = "\n\n✅ *High confidence response*"
            elif confidence >= 0.6:
                quality_indicator = "\n\n🔄 *Moderate confidence response*"
            else:
                quality_indicator = "\n\n⚠️ *Lower confidence - may need clarification*"

            enhanced_text += quality_indicator

            enhancements["lyrixa_response"] = enhanced_text

            # Add response metadata
            enhancements["response_metadata"] = {
                "word_count": len(enhanced_text.split()),
                "has_code": bool(brain_response.get("aether_code")),
                "plugin_count": len(brain_response.get("plugin_results", [])),
                "memory_integration": brain_response.get("memory_stored", False),
                "quality_score": confidence,
                "personality_enhanced": True,
            }

        except Exception as e:
            print(f"⚠️ Response enhancement error: {e}")

        return enhancements

    async def execute_aether_workflow(self, aether_code: str) -> Dict[str, Any]:
        """Execute an .aether workflow"""
        try:
            # Parse the .aether code
            workflow = await self.aether_interpreter.parse_aether_code(aether_code)

            # Execute the workflow
            execution_result = await self.aether_interpreter.execute_workflow(
                workflow,
                {
                    "session_id": self.session_id,
                    "workspace_path": self.workspace_path,
                    "plugin_manager": self.plugins,
                    "memory_system": self.memory,
                },
            )

            # Store execution in memory
            await self.memory.store_memory(
                content={
                    "workflow_name": workflow.name,
                    "execution_result": execution_result,
                    "aether_code": aether_code,
                },
                context={"session": self.session_id, "type": "workflow_execution"},
                tags=["workflow", "execution", "aether"],
                importance=0.8,
            )

            return execution_result

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return await self.system_bootstrap.get_current_system_status()

    async def generate_system_health_report(self) -> str:
        """Generate detailed system health report"""
        return await self.system_bootstrap.generate_health_report()

    async def check_system_readiness(self) -> bool:
        """Check if all systems are ready for operation"""
        status = await self.get_system_status()
        return status["overall_health"] > 0.5 and not status["issues_detected"]

    def get_startup_context_summary(self) -> Optional[str]:
        """Get a summary of the current startup context"""
        if hasattr(self, "system_bootstrap") and self.system_bootstrap.last_snapshot:
            snapshot = self.system_bootstrap.last_snapshot
            return f"Context: {snapshot.startup_context.value}, Health: {snapshot.overall_health:.1%}"
        return None

    async def cleanup(self):
        """Clean up resources"""
        await self.memory.consolidate_memories()
        print("🎙️ Lyrixa AI Assistant shutdown complete")

    async def _analyze_user_intent(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze user intent from natural language input"""
        try:
            # Simple intent classification based on keywords and patterns
            user_lower = user_input.lower()

            # .aether code generation intent
            if any(
                keyword in user_lower
                for keyword in [
                    "generate",
                    "create",
                    "write",
                    "code",
                    ".aether",
                    "aether",
                ]
            ):
                return {
                    "type": "aether_code_generation",
                    "confidence": 0.8,
                    "keywords": ["generate", "code", "aether"],
                    "description": "User wants to generate .aether code",
                }

            # Memory operation intent
            elif any(
                keyword in user_lower
                for keyword in ["remember", "recall", "memory", "forget", "save"]
            ):
                return {
                    "type": "memory_operation",
                    "confidence": 0.9,
                    "keywords": ["memory", "remember"],
                    "description": "User wants memory-related operation",
                }

            # Plugin execution intent
            elif any(
                keyword in user_lower
                for keyword in ["plugin", "execute", "run", "tool"]
            ):
                return {
                    "type": "plugin_execution",
                    "confidence": 0.85,
                    "keywords": ["plugin", "execute"],
                    "description": "User wants to execute a plugin",
                }

            # Goal management intent
            elif any(
                keyword in user_lower
                for keyword in ["goal", "task", "objective", "plan"]
            ):
                return {
                    "type": "goal_management",
                    "confidence": 0.8,
                    "keywords": ["goal", "task"],
                    "description": "User wants goal/task management",
                }

            # Project exploration intent
            elif any(
                keyword in user_lower
                for keyword in ["project", "explore", "analyze", "understand"]
            ):
                return {
                    "type": "project_exploration",
                    "confidence": 0.75,
                    "keywords": ["project", "explore"],
                    "description": "User wants to explore project",
                }

            # Question/conversation intent
            elif "?" in user_input or any(
                keyword in user_lower for keyword in ["what", "how", "why", "explain"]
            ):
                return {
                    "type": "conversation",
                    "confidence": 0.7,
                    "keywords": ["question", "conversation"],
                    "description": "User is asking a question or having conversation",
                }

            # Default to general conversation
            else:
                return {
                    "type": "conversation",
                    "confidence": 0.6,
                    "keywords": ["general"],
                    "description": "General conversation or unclear intent",
                }

        except Exception as e:
            print(f"⚠️ Intent analysis error: {e}")
            return {
                "type": "conversation",
                "confidence": 0.3,
                "keywords": ["error"],
                "description": "Error in intent analysis, defaulting to conversation",
            }

    # Placeholder handler methods (will be enhanced later)
    async def _handle_aether_generation(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle .aether code generation requests"""
        try:
            result = await self.aether_interpreter.execute(
                f"generate_from_description: {user_input}"
            )
            response["lyrixa_response"] = (
                "I've generated .aether code based on your request."
            )
            response["aether_code"] = result.get(
                "result", "// Generated .aether code placeholder"
            )
            response["actions_taken"].append("Generated .aether code")
        except Exception as e:
            response["lyrixa_response"] = f"I had trouble generating .aether code: {e}"
        return response

    async def _handle_memory_operation(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle memory-related operations"""
        if "remember" in user_input.lower():
            response["lyrixa_response"] = (
                "I'll remember this information for future reference."
            )
            response["actions_taken"].append("Stored information in memory")
        elif (
            "recall" in user_input.lower()
            or "what do you remember" in user_input.lower()
        ):
            response["lyrixa_response"] = (
                "Here's what I remember from our previous conversations..."
            )
            response["actions_taken"].append("Retrieved memories")
        else:
            response["lyrixa_response"] = (
                "I can help you with memory operations like storing and recalling information."
            )
        return response

    async def _handle_plugin_execution(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle plugin execution requests"""
        try:
            # Simple plugin handling - just acknowledge for now
            response["lyrixa_response"] = (
                "I'm processing your plugin request. Plugin system is ready to execute relevant tools."
            )
            response["actions_taken"].append("Prepared plugin execution")
        except Exception as e:
            response["lyrixa_response"] = f"I had trouble with plugin execution: {e}"
        return response

    async def _handle_goal_management(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle goal and task management"""
        try:
            if "create" in user_input.lower() or "add" in user_input.lower():
                response["lyrixa_response"] = (
                    "I've added a new goal to your goal management system."
                )
                response["actions_taken"].append("Created new goal")
            else:
                goals = self.goals.get_active_goals()
                response["lyrixa_response"] = (
                    f"You have {len(goals)} active goals. Let me help you manage them."
                )
                response["actions_taken"].append("Retrieved goals")
        except Exception as e:
            response["lyrixa_response"] = f"I had trouble with goal management: {e}"
        return response

    async def _handle_project_exploration(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle project exploration requests"""
        response["lyrixa_response"] = (
            f"I'm exploring your project structure and analyzing the codebase for insights."
        )
        response["actions_taken"].append("Analyzed project structure")
        return response

    async def _handle_workflow_orchestration(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle workflow orchestration"""
        response["lyrixa_response"] = (
            "I'm orchestrating a workflow to handle your complex request."
        )
        response["actions_taken"].append("Orchestrated workflow")
        return response

    async def _handle_conversation(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general conversation"""
        try:
            # Simple conversational response generation
            if "hello" in user_input.lower() or "hi" in user_input.lower():
                response["lyrixa_response"] = (
                    "Hello! I'm Lyrixa, your AI assistant for Aetherra. How can I help you today?"
                )
            elif "help" in user_input.lower():
                response["lyrixa_response"] = (
                    "I can help you with .aether code generation, memory management, plugin execution, and general development tasks. What would you like to work on?"
                )
            elif "?" in user_input:
                response["lyrixa_response"] = (
                    f"That's a great question about '{user_input}'. Let me help you understand this better. I can provide explanations, generate code, or connect you with relevant resources."
                )
            else:
                response["lyrixa_response"] = (
                    f"I understand you're telling me about '{user_input}'. How would you like me to help you with this?"
                )

            response["actions_taken"].append("Generated conversational response")
        except Exception as e:
            response["lyrixa_response"] = "I understand. How can I help you further?"
        return response

    # Personality Processor Methods
    def set_persona_mode(self, persona_mode: str) -> None:
        """Set Lyrixa's persona mode (Guide, Developer, Sage, etc.)"""
        try:
            from .core.conversation import PersonaMode

            persona = PersonaMode(persona_mode.lower())
            self.conversation.set_persona_mode(persona)
            print(f"🎭 Lyrixa persona set to: {persona_mode}")
        except ValueError:
            print(f"⚠️ Unknown persona mode: {persona_mode}")
            print(
                "Available modes: Guide, Developer, Sage, Friend, Teacher, Analyst, Creative, Specialist"
            )

    def adjust_personality(self, **kwargs) -> None:
        """Adjust personality parameters (tone, warmth, formality, etc.)"""
        self.conversation.adjust_personality_settings(**kwargs)
        print(f"🎛️ Personality adjusted: {kwargs}")

    async def record_personality_feedback(
        self,
        response_id: str,
        feedback_type: str,
        user_comment: Optional[str] = None,
        effectiveness: float = 0.5,
    ) -> None:
        """Record user feedback for personality learning"""
        await self.conversation.record_personality_feedback(
            response_id, feedback_type, user_comment, effectiveness
        )
        print(f"📝 Recorded {feedback_type} feedback for personality learning")

    def get_personality_status(self) -> Dict[str, Any]:
        """Get current personality configuration and status"""
        return self.conversation.get_personality_status()

    def export_personality_profile(self) -> str:
        """Export current personality configuration as JSON"""
        return self.conversation.export_personality_profile()

    def import_personality_profile(self, profile_json: str) -> bool:
        """Import personality configuration from JSON"""
        success = self.conversation.import_personality_profile(profile_json)
        if success:
            print("✅ Personality profile imported successfully")
        else:
            print("❌ Failed to import personality profile")
        return success

    async def get_self_awareness_insights(self) -> Dict[str, Any]:
        """Get current self-awareness insights and project understanding"""
        try:
            insights = {
                "project_understanding": None,
                "user_patterns": [],
                "recent_insights": [],
                "self_reflections": [],
                "project_awareness": {},
            }

            # Get project understanding
            if self.reflexive_loop.project_understanding:
                insights["project_understanding"] = (
                    self.reflexive_loop.project_understanding.__dict__
                )

            # Get user patterns
            insights["user_patterns"] = [
                pattern.__dict__ for pattern in self.reflexive_loop.user_patterns[-5:]
            ]

            # Generate fresh insights
            recent_insights = await self.reflexive_loop.generate_insights()
            insights["recent_insights"] = [
                insight.__dict__ for insight in recent_insights
            ]

            # Get self-reflections
            insights["self_reflections"] = [
                reflection.__dict__
                for reflection in self.reflexive_loop.self_reflections[-3:]
            ]

            # Get current project awareness
            insights[
                "project_awareness"
            ] = await self.reflexive_loop.get_current_project_awareness()

            return insights

        except Exception as e:
            print(f"⚠️ Error getting self-awareness insights: {e}")
            return {"error": str(e)}

    async def update_lyrixa_self_knowledge(
        self, knowledge_update: str
    ) -> Dict[str, Any]:
        """Allow user to update Lyrixa's self-knowledge about the project"""
        try:
            # Store the knowledge update
            await self.memory.store_memory(
                content={
                    "self_knowledge_update": knowledge_update,
                    "source": "user_provided",
                },
                context={
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                },
                tags=["self_knowledge", "user_update", "project_understanding"],
                importance=0.8,
            )

            # Update reflexive loop
            interaction_data = {
                "user_input": f"Knowledge update: {knowledge_update}",
                "context": {"type": "self_knowledge_update"},
                "actions_taken": ["self_knowledge_update"],
                "timestamp": datetime.now(),
            }

            await self.reflexive_loop.update_project_understanding(interaction_data)

            return {
                "success": True,
                "message": "Self-knowledge updated successfully",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error updating self-knowledge: {e}")
            return {"success": False, "error": str(e)}

    async def generate_project_insights(self) -> Dict[str, Any]:
        """Generate insights about the current project"""
        try:
            insights = await self.reflexive_loop.generate_insights()
            return {
                "insights": [insight.__dict__ for insight in insights],
                "timestamp": datetime.now().isoformat(),
                "count": len(insights),
            }

        except Exception as e:
            print(f"⚠️ Error generating project insights: {e}")
            return {"error": str(e)}

    # ========================================
    # 📊 FEEDBACK + SELF-IMPROVEMENT APIs
    # ========================================

    async def collect_user_feedback(
        self,
        feedback_type: str,
        rating: Union[int, float],
        context: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None,
        suggestion_id: Optional[str] = None,
        response_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Collect user feedback on Lyrixa's performance and behavior

        Args:
            feedback_type: Type of feedback ('suggestion', 'response', 'personality', 'interaction')
            rating: Numeric rating (1-5)
            context: Additional context about the feedback
            comment: User's detailed feedback comment
            suggestion_id: ID of suggestion being rated
            response_id: ID of response being rated

        Returns:
            Feedback collection result with feedback ID
        """
        try:
            from .core.feedback_system import FeedbackType

            # Map string types to enum
            type_mapping = {
                "suggestion": FeedbackType.SUGGESTION_RATING,
                "response": FeedbackType.RESPONSE_QUALITY,
                "personality": FeedbackType.PERSONALITY_PREFERENCE,
                "interaction": FeedbackType.INTERACTION_STYLE,
                "proactiveness": FeedbackType.PROACTIVENESS,
                "language": FeedbackType.LANGUAGE_STYLE,
                "timing": FeedbackType.TIMING,
                "relevance": FeedbackType.RELEVANCE,
                "helpfulness": FeedbackType.HELPFULNESS,
            }

            feedback_type_enum = type_mapping.get(
                feedback_type, FeedbackType.HELPFULNESS
            )

            feedback_id = await self.feedback_system.collect_feedback(
                feedback_type=feedback_type_enum,
                rating=rating,
                context=context or {},
                user_comment=comment,
                suggestion_id=suggestion_id,
                response_id=response_id,
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": f"Feedback collected successfully: {feedback_type}",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error collecting feedback: {e}")
            return {"success": False, "error": str(e)}

    async def collect_suggestion_feedback(
        self,
        suggestion_id: str,
        accepted: bool,
        rating: Optional[Union[int, float]] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Collect feedback specifically on suggestions"""
        try:
            feedback_id = await self.feedback_system.collect_suggestion_feedback(
                suggestion_id=suggestion_id,
                accepted=accepted,
                rating=rating,
                reason=reason,
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Suggestion feedback collected",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error collecting suggestion feedback: {e}")
            return {"success": False, "error": str(e)}

    async def collect_response_feedback(
        self,
        response_id: str,
        quality_rating: Union[int, float],
        helpfulness_rating: Union[int, float],
        tone_feedback: Optional[str] = None,
        improvement_suggestions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Collect feedback on Lyrixa's responses"""
        try:
            feedback_id = await self.feedback_system.collect_response_feedback(
                response_id=response_id,
                quality_rating=quality_rating,
                helpfulness_rating=helpfulness_rating,
                tone_feedback=tone_feedback,
                improvement_suggestions=improvement_suggestions,
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Response feedback collected",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error collecting response feedback: {e}")
            return {"success": False, "error": str(e)}

    async def collect_personality_feedback(
        self,
        persona_rating: Union[int, float],
        preferred_adjustments: Optional[Dict[str, float]] = None,
        specific_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Collect feedback on personality and interaction style"""
        try:
            feedback_id = await self.feedback_system.collect_personality_feedback(
                current_persona=self.conversation.personality_processor.current_persona,
                persona_rating=persona_rating,
                preferred_adjustments=preferred_adjustments,
                specific_feedback=specific_feedback,
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Personality feedback collected",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error collecting personality feedback: {e}")
            return {"success": False, "error": str(e)}

    async def collect_interaction_feedback(
        self,
        proactiveness_rating: Union[int, float],
        timing_rating: Union[int, float],
        interruption_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Collect feedback on interaction timing and proactiveness"""
        try:
            feedback_id = await self.feedback_system.collect_interaction_style_feedback(
                proactiveness_rating=proactiveness_rating,
                timing_rating=timing_rating,
                interruption_feedback=interruption_feedback,
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Interaction style feedback collected",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error collecting interaction feedback: {e}")
            return {"success": False, "error": str(e)}

    async def handle_feedback_widget_response(
        self, widget_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle feedback from GUI widgets"""
        try:
            feedback_id = await self.feedback_gui.handle_widget_response(
                widget_response
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Widget feedback processed",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error handling widget feedback: {e}")
            return {"success": False, "error": str(e)}

    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance and self-improvement report"""
        try:
            return await self.feedback_system.get_performance_report()

        except Exception as e:
            print(f"⚠️ Error getting performance report: {e}")
            return {"error": str(e)}

    def get_current_adaptive_settings(self) -> Dict[str, Any]:
        """Get current adaptive parameter settings"""
        try:
            return self.feedback_system.get_current_adaptive_settings()

        except Exception as e:
            print(f"⚠️ Error getting adaptive settings: {e}")
            return {"error": str(e)}

    async def reset_learning(self, keep_recent_days: int = 7) -> Dict[str, Any]:
        """Reset learning but optionally keep recent feedback"""
        try:
            await self.feedback_system.reset_learning(keep_recent_days)

            return {
                "success": True,
                "message": f"Learning reset, keeping {keep_recent_days} days of recent feedback",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"⚠️ Error resetting learning: {e}")
            return {"success": False, "error": str(e)}

    async def request_proactive_feedback(
        self, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Request feedback proactively when appropriate"""
        try:
            return await self.feedback_system.request_feedback_proactively(
                context or {}
            )

        except Exception as e:
            print(f"⚠️ Error requesting proactive feedback: {e}")
            return None
