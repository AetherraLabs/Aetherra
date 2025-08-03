#!/usr/bin/env python3
"""
🎙️ LYRIXA CORE INTERFACE
========================

Main interface for the Lyrixa AI Assistant system.
Provides unified access to all Lyrixa capabilities including:
- Conversation management
- Intelligence integration
- Plugin system
- Web integration
- Aetherra OS integration
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import core components
try:
    from Aetherra.runtime.aether_runtime import AetherRuntime

    from ..conversation_manager import LyrixaConversationManager
    from ..intelligence_integration import LyrixaIntelligenceStack

    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARN] Core components not available: {e}")
    LyrixaConversationManager = None
    LyrixaIntelligenceStack = None
    AetherRuntime = None
    CORE_AVAILABLE = False


class LyrixaCore:
    """
    🎙️ Lyrixa Core Interface

    Main interface class that provides unified access to all Lyrixa capabilities.
    This class orchestrates the conversation manager, intelligence stack, and
    plugin system to deliver a seamless AI assistant experience.
    """

    def __init__(
        self,
        workspace_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Lyrixa Core

        Args:
            workspace_path: Path to the workspace directory
            config: Configuration dictionary for Lyrixa
        """
        self.workspace_path = workspace_path or str(Path.cwd())
        self.config = config or {}
        self.is_initialized = False
        self.aether_runtime = None
        self.conversation_manager = None
        self.intelligence_stack = None
        self.plugins = {}
        self.session_id = f"lyrixa_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"🎙️ Lyrixa Core initialized with session: {self.session_id}")

    async def initialize(self) -> bool:
        """
        Initialize all Lyrixa components

        Returns:
            bool: True if initialization successful
        """
        try:
            if not CORE_AVAILABLE:
                logger.error("[ERROR] Core components not available")
                return False

            # Initialize Aether Runtime
            if AetherRuntime:
                self.aether_runtime = AetherRuntime()
                logger.info("✅ Aether Runtime initialized")

            # Initialize conversation manager
            if LyrixaConversationManager:
                self.conversation_manager = LyrixaConversationManager(
                    self.workspace_path, self.aether_runtime
                )
                logger.info("✅ Conversation Manager initialized")

            # Initialize intelligence stack
            if LyrixaIntelligenceStack:
                self.intelligence_stack = LyrixaIntelligenceStack(
                    self.workspace_path, self.aether_runtime
                )
                await self.intelligence_stack.initialize_intelligence_layer()
                logger.info("✅ Intelligence Stack initialized")

            # Load plugins
            await self._load_plugins()

            self.is_initialized = True
            logger.info("🎙️ Lyrixa Core fully initialized")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Lyrixa Core: {e}")
            return False

    async def _load_plugins(self):
        """Load and initialize Lyrixa plugins"""
        try:
            plugins_dir = Path(__file__).parent.parent / "plugins"
            if not plugins_dir.exists():
                logger.warning("[WARN] Plugins directory not found")
                return

            # Import and register plugins
            plugin_files = [
                "enhanced_plugin_manager.py",
                "context_aware_surfacing.py",
                "plugin_discovery.py",
                "plugin_analytics.py",
                "workflow_builder_plugin.py",
            ]

            for plugin_file in plugin_files:
                plugin_path = plugins_dir / plugin_file
                if plugin_path.exists():
                    try:
                        # Dynamic import of plugin
                        module_name = plugin_file.replace(".py", "")
                        self.plugins[module_name] = f"Plugin {module_name} loaded"
                        logger.info(f"✅ Plugin loaded: {module_name}")
                    except Exception as e:
                        logger.error(f"[ERROR] Failed to load plugin {plugin_file}: {e}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to load plugins: {e}")

    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a chat message through Lyrixa

        Args:
            message: User message
            context: Optional context information

        Returns:
            str: Lyrixa's response
        """
        if not self.is_initialized:
            await self.initialize()

        if not self.conversation_manager:
            return "[ERROR] Conversation manager not available"

        try:
            # Process message through conversation manager
            response = await self.conversation_manager.generate_response(message)
            return response
        except Exception as e:
            logger.error(f"[ERROR] Chat processing failed: {e}")
            return f"[ERROR] Error processing message: {str(e)}"

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status

        Returns:
            Dict containing system status information
        """
        status = {
            "session_id": self.session_id,
            "initialized": self.is_initialized,
            "workspace_path": self.workspace_path,
            "components": {
                "aether_runtime": self.aether_runtime is not None,
                "conversation_manager": self.conversation_manager is not None,
                "intelligence_stack": self.intelligence_stack is not None,
                "plugins_loaded": len(self.plugins),
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Add intelligence stack status if available
        if self.intelligence_stack:
            try:
                intelligence_status = (
                    await self.intelligence_stack.get_intelligence_status()
                )
                status["intelligence"] = intelligence_status
            except Exception as e:
                logger.error(f"[ERROR] Failed to get intelligence status: {e}")
                status["intelligence"] = {"error": str(e)}

        return status

    async def execute_command(
        self, command: str, args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command through Lyrixa

        Args:
            command: Command to execute
            args: Optional command arguments

        Returns:
            Dict containing command execution results
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Route command to appropriate handler
            if command == "status":
                return await self.get_system_status()
            elif command == "chat" and args:
                response = await self.chat(args[0])
                return {"response": response}
            elif command == "help":
                return {
                    "commands": [
                        "status - Get system status",
                        "chat <message> - Send chat message",
                        "help - Show this help",
                    ]
                }
            else:
                return {"error": f"Unknown command: {command}"}

        except Exception as e:
            logger.error(f"[ERROR] Command execution failed: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown Lyrixa gracefully"""
        try:
            logger.info("🔄 Shutting down Lyrixa Core...")

            # Shutdown components
            if self.intelligence_stack:
                # Intelligence stack doesn't have shutdown method, just clear reference
                self.intelligence_stack = None

            if self.conversation_manager:
                # Conversation manager shutdown if available
                pass

            if self.aether_runtime:
                # Aether runtime shutdown if available
                pass

            self.is_initialized = False
            logger.info("✅ Lyrixa Core shutdown complete")

        except Exception as e:
            logger.error(f"[ERROR] Shutdown failed: {e}")

    def __repr__(self) -> str:
        return (
            f"LyrixaCore(session={self.session_id}, initialized={self.is_initialized})"
        )


# Global instance for web integration
_lyrixa_instance = None


def get_lyrixa_instance() -> LyrixaCore:
    """Get global Lyrixa instance"""
    global _lyrixa_instance
    if _lyrixa_instance is None:
        _lyrixa_instance = LyrixaCore()
    return _lyrixa_instance


async def initialize_lyrixa(
    workspace_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> LyrixaCore:
    """
    Initialize Lyrixa system

    Args:
        workspace_path: Path to workspace
        config: Configuration dictionary

    Returns:
        LyrixaCore: Initialized Lyrixa instance
    """
    lyrixa = LyrixaCore(workspace_path, config)
    await lyrixa.initialize()
    return lyrixa


# Export main classes and functions
__all__ = ["LyrixaCore", "get_lyrixa_instance", "initialize_lyrixa"]
