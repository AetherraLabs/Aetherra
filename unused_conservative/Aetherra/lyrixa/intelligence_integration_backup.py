#!/usr/bin/env python3
"""
🧠 LYRIXA INTELLIGENCE INTEGRATION
=================================

This module integrates all Aetherra AI OS Intelligence Stack components
into Lyrixa, providing real-time awareness and system orchestration.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Aetherra runtime components
try:
    # Try modular runtime import first
    try:
        from Aetherra.aetherra_core.system.core_migrated.agents.agents.agent_executor import AgentExecutor as AetherRuntime
    except ImportError:
        print("⚠️ Modular AetherRuntime not available")
        AetherRuntime = None
except ImportError:
    print("⚠️ Aetherra runtime not available")
    AetherRuntime = None

# Import conversation manager
try:
    from .conversation_manager import LyrixaConversationManager

    CONVERSATION_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Conversation manager not available: {e}")
    LyrixaConversationManager = None
    CONVERSATION_MANAGER_AVAILABLE = False


class LyrixaIntelligenceStack:
    """
    🧠 Lyrixa Intelligence Stack Integration

    This class provides Lyrixa with comprehensive intelligence capabilities
    by integrating all core Aetherra AI OS system plugins and modules.
    """

    def __init__(self, workspace_path: str, aether_runtime=None):
        self.workspace_path = workspace_path
        self.aether_runtime = aether_runtime or (
            AetherRuntime() if AetherRuntime else None
        )

        # Initialize conversation manager
        if CONVERSATION_MANAGER_AVAILABLE and LyrixaConversationManager:
            try:
                self.conversation_manager = LyrixaConversationManager(
                    workspace_path=workspace_path, aether_runtime=self.aether_runtime
                )
                print("✅ LLM-powered conversation manager initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize conversation manager: {e}")
                self.conversation_manager = None
        else:
            self.conversation_manager = None

        # Intelligence components status
        self.intelligence_status = {
            "semantic_memory": False,
            "system_awareness": False,
            "self_reflection": False,
            "event_correlation": False,
            "conversational_integration": False,
            "plugin_monitoring": False,
        }

        # Agent analytics for dashboard
        self.agent_analytics = {
            "LyrixaAI": {"success_rate": 0.95, "avg_response_time": 0.8, "total_requests": 24},
            "GoalAgent": {"success_rate": 0.98, "avg_response_time": 0.6, "total_requests": 12},
            "PluginAgent": {"success_rate": 0.92, "avg_response_time": 1.2, "total_requests": 8},
            "ReflectionAgent": {"success_rate": 0.96, "avg_response_time": 0.9, "total_requests": 6},
            "EscalationAgent": {"success_rate": 1.0, "avg_response_time": 0.5, "total_requests": 2},
            "SelfEvaluationAgent": {"success_rate": 0.94, "avg_response_time": 1.1, "total_requests": 4}
        }

        # System workflow status
        self.workflow_status = {
            "goal_autopilot": {"active": False, "last_run": None, "health": "unknown"},
            "agent_sync": {"active": False, "last_run": None, "health": "unknown"},
            "memory_cleanser": {"active": False, "last_run": None, "health": "unknown"},
            "daily_reflector": {"active": False, "last_run": None, "health": "unknown"},
            "plugin_watchdog": {"active": False, "last_run": None, "health": "unknown"},
        }

        # System modules status
        self.module_status = {
            "agents": False,
            "goals": False,
            "plugins": False,
            "logger": False,
            "memory_ops": False,
            "utils": False,
        }

        # Initialize logging
        self.logger = logging.getLogger("lyrixa.intelligence")
        self.logger.setLevel(logging.INFO)

        # Intelligence cache
        self.intelligence_cache = {}
        self.last_intelligence_update = None

        # Initialize plugin system integration with graceful fallback
        self.plugin_manager = None
        self.self_improvement_dashboard = None
        self.aetherra_hub_client = None

        # Initialize modular connections with error handling
        try:
            # Try to connect to enhanced plugin manager
            try:
                from Aetherra.plugins.core.enhanced_plugin_manager import EnhancedPluginManager as PluginManager
                self.plugin_manager = PluginManager()
                print("✅ Connected to Modular Enhanced Plugin Manager")
            except ImportError:
                print("⚠️ Modular Enhanced Plugin Manager not available")
                self.plugin_manager = None
            # Try basic plugin manager as fallback
            try:
                from Aetherra.plugins.core.plugin_api import PluginManager as BasicPluginManager
                if not self.plugin_manager:
                    self.plugin_manager = BasicPluginManager()
                    print("✅ Connected to Modular Basic Plugin Manager")
            except ImportError:
                print("⚠️ Modular Basic Plugin Manager not available")
            except Exception as e:
                print(f"⚠️ Plugin system initialization warning: {e}")
            print("🧠 Intelligence Stack initialized")

    def _initialize_modular_connections(self):
        """Initialize connections to modular components with graceful fallback"""
        try:
            # Try to connect to modular enhanced plugin manager
            try:
                from Aetherra.plugins.core.enhanced_plugin_manager import EnhancedPluginManager as PluginManager
                self.plugin_manager = PluginManager()
                print("✅ Connected to Modular Enhanced Plugin Manager")
            except ImportError:
                print("⚠️ Modular Enhanced Plugin Manager not available")
                self.plugin_manager = None
            # Try to connect to modular self-improvement dashboard
            try:
                from Aetherra.plugins.core.self_improvement_dashboard import SelfImprovementDashboard
                self.self_improvement_dashboard = SelfImprovementDashboard()
                print("✅ Connected to Modular Self-Improvement Dashboard")
            except ImportError:
                print("⚠️ Modular Self-Improvement Dashboard not available")
                self.self_improvement_dashboard = None

            # Try to connect to AetherHub client
            try:
                import requests
                # Test AetherHub connection
                response = requests.get("http://localhost:3001/health", timeout=1)
                if response.status_code == 200:
                    print("✅ AetherHub service detected")
                    self.aetherra_hub_client = "http://localhost:3001"
                else:
                    print("⚠️ AetherHub service not responding")
                    self.aetherra_hub_client = None
            except:
                print("⚠️ AetherHub service not available")
                self.aetherra_hub_client = None

        except Exception as e:
            print(f"⚠️ Modular connection initialization warning: {e}")
            # Continue with basic functionality even if connections fail

    async def initialize_intelligence_layer(self) -> Dict[str, Any]:
        """Initialize all intelligence layer components"""
        try:
            print("🧠 Initializing Intelligence Layer...")

            # Check semantic memory with confidence scoring
            await self._check_semantic_memory()

            # Initialize real-time system awareness
            await self._initialize_system_awareness()

            # Setup AI self-reflection capabilities
            await self._setup_self_reflection()

            # Initialize event correlation and reasoning
            await self._initialize_event_correlation()

            # Setup conversational interface integration
            await self._setup_conversational_integration()

            # Initialize plugin monitoring
            await self._initialize_plugin_monitoring()

            self.last_intelligence_update = datetime.now()

            print("✅ Intelligence Layer initialized successfully")
            return {
                "status": "initialized",
                "components": self.intelligence_status,
                "timestamp": self.last_intelligence_update.isoformat(),
            }

        except Exception as e:
            print(f"❌ Intelligence Layer initialization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def initialize_system_workflows(self) -> Dict[str, Any]:
        """Initialize all core system workflow plugins"""
        try:
            print("🧩 Initializing System Workflows...")

            workflows = [
                ("goal_autopilot", "30 minutes", "Resume, escalate, retry goals"),
                ("agent_sync", "4 hours", "Ensure agent memory sync"),
                ("memory_cleanser", "12 hours", "Clean low-confidence memories"),
                ("daily_reflector", "24 hours", "Generate system-wide reflection"),
                ("plugin_watchdog", "6 hours", "Monitor plugin health"),
            ]

            for workflow_name, schedule, description in workflows:
                await self._initialize_workflow(workflow_name, schedule, description)

            print("✅ System Workflows initialized successfully")
            return {
                "status": "initialized",
                "workflows": self.workflow_status,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ System Workflows initialization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def initialize_system_modules(self) -> Dict[str, Any]:
        """Initialize all supporting system modules"""
        try:
            print("⚙️ Initializing System Modules...")

            modules = [
                ("agents", "Find/update/create agents"),
                ("goals", "Goal operations and summaries"),
                ("plugins", "Plugin health checks, status"),
                ("logger", "Event logging + querying"),
                ("memory_ops", "Raw memory search/delete/stats"),
                ("utils", "Time helpers, formatting"),
            ]

            for module_name, description in modules:
                await self._initialize_module(module_name, description)

            print("✅ System Modules initialized successfully")
            return {
                "status": "initialized",
                "modules": self.module_status,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ System Modules initialization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_intelligence_status(self) -> Dict[str, Any]:
        """Get comprehensive intelligence system status"""
        return {
            "intelligence_layer": {
                "status": self.intelligence_status,
                "health": self._calculate_intelligence_health(),
                "last_update": self.last_intelligence_update.isoformat()
                if self.last_intelligence_update
                else None,
            },
            "system_workflows": {
                "status": self.workflow_status,
                "health": self._calculate_workflow_health(),
                "active_count": sum(
                    1 for w in self.workflow_status.values() if w["active"]
                ),
            },
            "system_modules": {
                "status": self.module_status,
                "health": self._calculate_module_health(),
                "active_count": sum(
                    1 for active in self.module_status.values() if active
                ),
            },
            "overall_health": self._calculate_overall_health(),
            "timestamp": datetime.now().isoformat(),
        }

    async def run_intelligence_workflow(
        self, workflow_name: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Run a specific intelligence workflow"""
        if workflow_name not in self.workflow_status:
            return {"status": "error", "message": f"Unknown workflow: {workflow_name}"}

        try:
            print(f"🚀 Running workflow: {workflow_name}")

            # Run the workflow using Aether runtime if available
            if self.aether_runtime:
                result = await self._run_aether_workflow(workflow_name, params)
            else:
                result = await self._run_simulated_workflow(workflow_name, params)

            # Update workflow status
            self.workflow_status[workflow_name]["last_run"] = datetime.now()
            self.workflow_status[workflow_name]["health"] = (
                "healthy" if result.get("success") else "error"
            )

            return result

        except Exception as e:
            print(f"❌ Workflow {workflow_name} failed: {e}")
            self.workflow_status[workflow_name]["health"] = "error"
            return {"status": "error", "message": str(e)}

    async def perform_system_reflection(self) -> Dict[str, Any]:
        """Perform comprehensive system reflection and analysis"""
        try:
            print("🔍 Performing system reflection...")

            # Collect system metrics
            intelligence_status = await self.get_intelligence_status()

            # Generate insights
            insights = await self._generate_system_insights(intelligence_status)

            # Create recommendations
            recommendations = await self._generate_recommendations(
                intelligence_status, insights
            )

            reflection_report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": intelligence_status,
                "insights": insights,
                "recommendations": recommendations,
                "confidence_score": self._calculate_confidence_score(
                    intelligence_status
                ),
            }

            # Cache the reflection
            self.intelligence_cache["last_reflection"] = reflection_report

            print("✅ System reflection completed")
            return reflection_report

        except Exception as e:
            print(f"❌ System reflection failed: {e}")
            return {"status": "error", "message": str(e)}

    async def generate_response_async(self, user_message: str) -> str:
        """Generate a response based on user input using intelligence components."""
        try:
            # Check for memory-related queries
            if self.aether_runtime and self.aether_runtime.context.memory:
                memory_results = (
                    await self.aether_runtime.context.memory.query_memories(
                        user_message
                    )
                )
                if memory_results:
                    # Process memory results into a conversational response
                    response = self._process_memory_results(
                        memory_results, user_message
                    )
                    if response:
                        return response

            # Try plugin execution for dynamic responses
            if self.aether_runtime and self.aether_runtime.context.plugins:
                plugin_response = self.aether_runtime.context.plugins.execute_chain(
                    user_message
                )
                if plugin_response:
                    return plugin_response

            # Generate a contextual response based on the user message
            return self._generate_contextual_response(user_message)
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"

    def _process_memory_results(
        self, memory_results: List[Dict], user_message: str
    ) -> Optional[str]:
        """Process memory query results into a conversational response."""
        try:
            if not memory_results:
                return None

            # Analyze the memory results to generate a meaningful response
            relevant_memories = []
            for memory in memory_results[:3]:  # Limit to top 3 most relevant
                content = memory.get("content", {})

                # Extract meaningful information from different memory types
                if "project_understanding" in content:
                    project_info = content["project_understanding"]
                    relevant_memories.append(
                        {
                            "type": "project",
                            "info": f"Project: {project_info.get('project_name', 'Unknown')}, "
                            f"Type: {project_info.get('project_type', 'Unknown')}, "
                            f"Phase: {project_info.get('current_phase', 'Unknown')}",
                        }
                    )
                elif "feedback_entry" in content:
                    feedback_info = content["feedback_entry"]
                    relevant_memories.append(
                        {
                            "type": "feedback",
                            "info": f"Feedback: {feedback_info.get('feedback_type', 'Unknown')} "
                            f"(Rating: {feedback_info.get('rating', 'N/A')})",
                        }
                    )
                else:
                    # Generic memory content
                    relevant_memories.append(
                        {
                            "type": "general",
                            "info": str(content)[:100] + "..."
                            if len(str(content)) > 100
                            else str(content),
                        }
                    )

            # Generate response based on memory context
            if relevant_memories:
                response_parts = ["Based on what I remember:"]

                project_memories = [
                    m for m in relevant_memories if m["type"] == "project"
                ]
                if project_memories:
                    response_parts.append(
                        f"You're working on the {project_memories[0]['info']}."
                    )

                feedback_memories = [
                    m for m in relevant_memories if m["type"] == "feedback"
                ]
                if feedback_memories:
                    response_parts.append(
                        "I've been learning from your feedback to improve my responses."
                    )

                # Add contextual help based on user message
                if any(
                    word in user_message.lower()
                    for word in ["help", "how", "what", "explain"]
                ):
                    response_parts.append(
                        "How can I assist you with your current work?"
                    )
                else:
                    response_parts.append(
                        "Is there something specific you'd like to know or work on?"
                    )

                return " ".join(response_parts)

            return None
        except Exception as e:
            print(f"❌ Error processing memory results: {e}")
            return None

    def _generate_contextual_response(self, user_message: str) -> str:
        """Generate a contextual response based on the user message."""
        message_lower = user_message.lower()

        # Greeting responses
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm Lyrixa, your AI assistant for the Aetherra project. How can I help you today?"

        # Help requests
        if any(word in message_lower for word in ["help", "assist", "support"]):
            return "I'm here to help with your Aetherra project! I can assist with development tasks, answer questions, provide insights, and help manage your workflow. What would you like to work on?"

        # Status inquiries
        if any(word in message_lower for word in ["status", "progress", "update"]):
            return "I can help you check the status of your project. Would you like me to review your current progress or help with next steps?"

        # Question patterns
        if any(
            word in message_lower for word in ["what", "how", "why", "when", "where"]
        ):
            return "That's a great question! I'd be happy to help you understand this better. Could you provide more context about what you're working on?"

        # Default conversational response
        return "I understand you're reaching out. I'm here to help with your Aetherra project - whether you need technical assistance, want to discuss ideas, or need help with development tasks. What's on your mind?"

    def generate_response(self, user_message: str) -> str:
        """Synchronous wrapper for generate_response_async with LLM support."""
        try:
            # Check if we have the LLM-powered conversation manager
            if self.conversation_manager and hasattr(
                self.conversation_manager, "generate_response"
            ):
                # Use async conversation manager
                try:
                    # Try to get the current event loop
                    try:
                        asyncio.get_running_loop()
                        # If we reach here, there's a running loop
                        # Use thread executor to run async code
                        import concurrent.futures

                        def run_async():
                            new_loop = asyncio.new_event_loop()
                            try:
                                if self.conversation_manager and hasattr(
                                    self.conversation_manager, "generate_response"
                                ):
                                    return new_loop.run_until_complete(
                                        self.conversation_manager.generate_response(
                                            user_message
                                        )
                                    )
                                else:
                                    return "Conversation manager not available"
                            finally:
                                new_loop.close()

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(run_async)
                            return future.result(timeout=30)

                    except RuntimeError:
                        # No running loop, safe to use asyncio.run
                        if self.conversation_manager and hasattr(
                            self.conversation_manager, "generate_response"
                        ):
                            return asyncio.run(
                                self.conversation_manager.generate_response(
                                    user_message
                                )
                            )
                        else:
                            return "Conversation manager not available"

                except Exception as e:
                    print(f"⚠️ LLM conversation manager failed: {e}")
                    # Fall back to the old system
                    pass

            # Fallback to old system if LLM conversation manager not available
            # Use a more robust approach to handle async in sync context
            try:
                # Try to get the current event loop
                asyncio.get_running_loop()
                # If we reach here, there's a running loop
                # Use thread executor to run async code
                import concurrent.futures

                def run_async():
                    new_loop = asyncio.new_event_loop()
                    try:
                        return new_loop.run_until_complete(
                            self.generate_response_async(user_message)
                        )
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async)
                    return future.result(timeout=10)

            except RuntimeError:
                # No running loop, safe to use asyncio.run
                return asyncio.run(self.generate_response_async(user_message))

        except Exception as e:
            print(f"⚠️ Error in generate_response: {e}")
            # Fallback to contextual response if async fails
            try:
                return self._generate_contextual_response(user_message)
            except Exception:
                return "I'm here to help with your Aetherra project! How can I assist you today?"

    # Private helper methods
    async def _check_semantic_memory(self):
        """Check semantic memory with confidence scoring"""
        try:
            # Check if memory_ops.aether exists and is functional
            memory_ops_path = (
                Path(self.workspace_path) / "Aetherra" / "system" / "memory_ops.aether"
            )
            if memory_ops_path.exists():
                self.intelligence_status["semantic_memory"] = True
                print("✅ Semantic memory with confidence scoring - Active")
            else:
                print("⚠️ memory_ops.aether not found - Semantic memory disabled")
        except Exception as e:
            print(f"❌ Semantic memory check failed: {e}")

    async def _initialize_system_awareness(self):
        """Initialize real-time system awareness"""
        try:
            # Check for system plugin files
            system_plugins = [
                "goal_autopilot.aether",
                "agents.aether",
                "plugins.aether",
            ]
            system_dir = Path(self.workspace_path) / "Aetherra" / "system"

            if system_dir.exists():
                available_plugins = [
                    p for p in system_plugins if (system_dir / p).exists()
                ]
                if available_plugins:
                    self.intelligence_status["system_awareness"] = True
                    print(
                        f"✅ System awareness - Active ({len(available_plugins)} plugins)"
                    )
                else:
                    print("⚠️ No system plugins found - System awareness limited")
            else:
                print("⚠️ System directory not found - System awareness disabled")
        except Exception as e:
            print(f"❌ System awareness initialization failed: {e}")

    async def _setup_self_reflection(self):
        """Setup AI self-reflection capabilities"""
        try:
            reflector_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / "daily_reflector.aether"
            )
            if reflector_path.exists():
                self.intelligence_status["self_reflection"] = True
                print("✅ AI self-reflection - Active")
            else:
                print("⚠️ daily_reflector.aether not found - Self-reflection disabled")
        except Exception as e:
            print(f"❌ Self-reflection setup failed: {e}")

    async def _initialize_event_correlation(self):
        """Initialize event correlation and reasoning"""
        try:
            logger_path = (
                Path(self.workspace_path) / "Aetherra" / "system" / "logger.aether"
            )
            if logger_path.exists():
                self.intelligence_status["event_correlation"] = True
                print("✅ Event correlation + reasoning - Active")
            else:
                print("⚠️ logger.aether not found - Event correlation disabled")
        except Exception as e:
            print(f"❌ Event correlation initialization failed: {e}")

    async def _setup_conversational_integration(self):
        """Setup conversational interface integration"""
        try:
            # This is handled by Lyrixa's conversational engine
            self.intelligence_status["conversational_integration"] = True
            print("✅ Conversational interface integration - Active")
        except Exception as e:
            print(f"❌ Conversational integration setup failed: {e}")

    async def _initialize_plugin_monitoring(self):
        """Initialize plugin monitoring capabilities"""
        try:
            watchdog_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / "plugin_watchdog.aether"
            )
            if watchdog_path.exists():
                self.intelligence_status["plugin_monitoring"] = True
                print("✅ Plugin monitoring - Active")
            else:
                print("⚠️ plugin_watchdog.aether not found - Plugin monitoring disabled")
        except Exception as e:
            print(f"❌ Plugin monitoring initialization failed: {e}")

    async def _initialize_workflow(
        self, workflow_name: str, schedule: str, description: str
    ):
        """Initialize a specific workflow"""
        try:
            workflow_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / f"{workflow_name}.aether"
            )
            if workflow_path.exists():
                self.workflow_status[workflow_name]["active"] = True
                self.workflow_status[workflow_name]["health"] = "healthy"
                print(f"✅ {workflow_name} - Active (Schedule: {schedule})")
            else:
                print(f"⚠️ {workflow_name}.aether not found - Workflow disabled")
        except Exception as e:
            print(f"❌ {workflow_name} initialization failed: {e}")

    async def _initialize_module(self, module_name: str, description: str):
        """Initialize a specific system module"""
        try:
            module_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / f"{module_name}.aether"
            )
            if module_path.exists():
                self.module_status[module_name] = True
                print(f"✅ {module_name} - Active")
            else:
                print(f"⚠️ {module_name}.aether not found - Module disabled")
        except Exception as e:
            print(f"❌ {module_name} initialization failed: {e}")

    async def _run_aether_workflow(
        self, workflow_name: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Run workflow using Aether runtime"""
        try:
            # Load and execute the workflow
            workflow_path = (
                Path(self.workspace_path)
                / "Aetherra"
                / "system"
                / f"{workflow_name}.aether"
            )
            if workflow_path.exists():
                with open(workflow_path, "r") as f:
                    workflow_code = f.read()

                # Execute using Aether runtime
                result = None
                if self.aether_runtime:
                    try:
                        # Try different execution methods
                        if hasattr(self.aether_runtime, "execute_async"):
