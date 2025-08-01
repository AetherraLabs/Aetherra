# Aetherra Library Integration for Lyrixa
# Main integration module that handles script library initialization and management

import os
import sys
from typing import Any, Dict

from Aetherra.runtime.script_memory_integrator import script_memory_integrator
from Aetherra.runtime.script_registry_loader import script_registry_loader
from Aetherra.runtime.script_router import ScriptRouter

# Add the project root to Python path if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class LyrixaScriptIntegration:
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.script_router = None
        self.registry = None
        self.initialized = False

    def initialize(self, context: Dict[str, Any] = None) -> bool:
        """Initialize the script integration system"""
        try:
            print("🚀 Initializing Aetherra Script Library Integration...")

            # Load script registry
            self.registry = script_registry_loader.load_script_registry()
            if not self.registry:
                print("❌ Failed to load script registry")
                return False

            # Set up memory integration
            if self.memory_system:
                script_memory_integrator.memory_system = self.memory_system
                script_memory_integrator.export_script_metadata(self.registry)

            # Initialize script router
            if not context:
                context = {
                    "memory": self.memory_system,
                    "plugins": None,
                    "agents": None,
                }

            self.script_router = ScriptRouter(context)

            # Print initialization summary
            stats = self.registry.get("execution_statistics", {})
            print("✅ Script Library initialized successfully!")
            print(f"📊 Total scripts: {stats.get('total_scripts', 0)}")
            print(f"📂 Categories: {len(self.registry.get('categories', {}))}")
            print(f"🔧 Commands: {stats.get('total_commands', 0)}")

            self.initialized = True
            return True

        except Exception as e:
            print(f"❌ Failed to initialize script integration: {e}")
            return False

    def handle_script_request(self, user_input: str) -> str:
        """Handle script-related requests from user"""
        if not self.initialized:
            return "❌ Script system not initialized. Please initialize first."

        if not self.script_router:
            return "❌ Script router not available."

        return self.script_router.handle_input(user_input)

    def get_script_suggestions(self, goal: str, context: Dict[str, Any] = None) -> str:
        """Get script suggestions for a specific goal"""
        if not self.initialized:
            return "❌ Script system not initialized."

        if not self.script_router:
            return "❌ Script router not available."

        return self.script_router.suggest_script(goal)

    def get_available_categories(self) -> str:
        """Get all available script categories"""
        if not self.initialized:
            return "❌ Script system not initialized."

        if not self.script_router:
            return "❌ Script router not available."

        return self.script_router.get_script_categories()

    def execute_script(
        self, script_name: str, parameters: Dict[str, Any] = None
    ) -> str:
        """Execute a script with given parameters"""
        if not self.initialized:
            return "❌ Script system not initialized."

        if not self.script_router:
            return "❌ Script router not available."

        # Format as run command
        command = f"run {script_name}"
        return self.script_router.handle_input(command)

    def get_script_insights(self) -> Dict[str, Any]:
        """Get insights about script usage and performance"""
        if not self.initialized:
            return {"error": "Script system not initialized"}

        insights = script_memory_integrator.generate_script_insights()
        return insights

    def get_registry_info(self) -> Dict[str, Any]:
        """Get information about the script registry"""
        if not self.registry:
            return {"error": "Registry not loaded"}

        return {
            "registry_info": self.registry.get("registry_info", {}),
            "categories": self.registry.get("categories", {}),
            "execution_statistics": self.registry.get("execution_statistics", {}),
            "integration_info": self.registry.get("integration_info", {}),
        }

    def is_script_command(self, user_input: str) -> bool:
        """Check if user input is a script-related command"""
        script_keywords = [
            "run",
            "execute",
            "script",
            "scripts",
            "suggest",
            "categories",
            "list scripts",
            "available scripts",
            "describe",
            "help scripts",
        ]

        user_input_lower = user_input.lower().strip()

        # Check for exact matches or starts with
        for keyword in script_keywords:
            if keyword in user_input_lower:
                return True

        # Check for script names
        if self.registry:
            scripts = self.registry.get("scripts", {})
            for script_name in scripts.keys():
                if script_name.lower() in user_input_lower:
                    return True

        return False

    def get_quick_help(self) -> str:
        """Get quick help for script commands"""
        return """
🤖 **Aetherra Script Library Help**

**Available Commands:**
• `list scripts` - Show all available scripts
• `categories` - Show script categories
• `suggest [goal]` - Get script suggestions for a goal
• `run [script_name]` - Execute a script
• `describe [script_name]` - Get script details
• `list [category] scripts` - Show scripts in a category

**Examples:**
• `suggest daily maintenance`
• `run bootstrap`
• `describe reflect`
• `list memory scripts`

**Categories:**
🧠 Memory • ⚙️ System • 👤 User • 🤖 Agents
"""


# Initialize global integration instance
lyrixa_script_integration = LyrixaScriptIntegration()


# Convenience functions for easy integration
def initialize_script_library(memory_system=None, context=None):
    """Initialize the script library for Lyrixa"""
    lyrixa_script_integration.memory_system = memory_system
    return lyrixa_script_integration.initialize(context)


def handle_script_command(user_input: str) -> str:
    """Handle script commands from Lyrixa"""
    return lyrixa_script_integration.handle_script_request(user_input)


def is_script_related(user_input: str) -> bool:
    """Check if user input is script-related"""
    return lyrixa_script_integration.is_script_command(user_input)


def get_script_help() -> str:
    """Get script help text"""
    return lyrixa_script_integration.get_quick_help()


# Auto-initialize if this module is imported
if __name__ != "__main__":
    # Try to auto-initialize with basic setup
    try:
        initialize_script_library()
    except Exception as e:
        print(f"Note: Auto-initialization failed: {e}")
        print("Script library will need to be initialized manually.")
