#!/usr/bin/env python3
"""
🚀 AETHERRA LYRIXA LAUNCHER - HYBRID UI
🎯 11-Tab Revolutionary Interface (183% Completion)
⚡ Features: Chat, System, Agents, Performance, Self-Improvement,
   Plugins, Plugin Editor, Memory Viewer, Goal Tracker,
   Execute Plugin, Agent Collaboration

Updated to use the new hybrid_window.py with all 11 tabs integrated.
"""

import sys
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print(
        "⚠️ python-dotenv not available - environment variables from .env file won't be loaded"
    )

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add the main project directory to path so 'Aetherra' module imports work
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.launch_utils import run_self_improvement_api, wait_for_api_server
from utils.logging_utils import log

# Updated import paths with fallback handling
try:
    from Aetherra.runtime.aether_runtime import AetherRuntime
except ImportError:
    log("⚠️ AetherRuntime not available, using fallback", "warning")

    class AetherRuntime:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass


from Aetherra.core.memory_manager import MemoryManager
from Aetherra.core.multi_llm_manager import MultiLLMManager
from Aetherra.core.plugin_manager import PluginManager
from Aetherra.core.prompt_engine import PromptEngine
from Aetherra.lyrixa.agents.core_agent import LyrixaAI
from Aetherra.lyrixa.gui.hybrid_window import (
    LyrixaWindow,  # ✅ Updated to use new hybrid UI
)
from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

# Global references
lyrixa = None
runtime = None
intelligence_stack = None


async def initialize_system(gui_window=None):
    global lyrixa, runtime, intelligence_stack

    log("🔧 Initializing Lyrixa Intelligence Stack...")
    memory = MemoryManager()
    prompt_engine = PromptEngine()
    llm_manager = MultiLLMManager()

    # Initialize intelligence stack with workspace path and GUI interface
    workspace_path = str(Path(__file__).parent.parent)
    intelligence_stack = LyrixaIntelligenceStack(
        workspace_path, gui_interface=gui_window
    )

    runtime = AetherRuntime()
    lyrixa = LyrixaAI(runtime, memory, prompt_engine, llm_manager, intelligence_stack)

    # Initialize the Lyrixa agent and its sub-agents
    await lyrixa.initialize()

    # 🔗 CRITICAL FIX: Initialize plugin discovery integration
    log("🔍 Initializing plugin discovery integration...")
    try:
        plugin_integration_success = (
            await intelligence_stack.initialize_plugin_discovery_integration()
        )
        if plugin_integration_success:
            log(
                "✅ Plugin discovery integrated - Lyrixa can now see and recommend plugins!"
            )
        else:
            log(
                "⚠️ Plugin discovery integration failed - Lyrixa won't see plugins",
                "warning",
            )
    except Exception as e:
        log(f"❌ Plugin discovery integration error: {e}", "error")

    log("✅ Intelligence stack and runtime initialized.")


def launch_gui():
    app = QApplication(sys.argv)
    window = LyrixaWindow()

    # Show window first
    window.show()

    # Initialize system after GUI is shown
    def initialize_and_attach():
        try:
            import asyncio

            # Create new event loop for initialization
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run initialization with GUI window reference
            loop.run_until_complete(initialize_system(window))

            # Attach components to GUI using modular methods
            print(f"🔧 DEBUG: intelligence_stack = {intelligence_stack}")
            print(f"🔧 DEBUG: runtime = {runtime}")
            print(f"🔧 DEBUG: lyrixa = {lyrixa}")

            if intelligence_stack:
                window.attach_intelligence_stack(intelligence_stack)
                log("✅ Intelligence stack attached to GUI")

            if runtime:
                window.attach_runtime(runtime)
                log("✅ Runtime attached to GUI")

            if lyrixa:
                print(f"🔧 DEBUG: About to call attach_lyrixa with {type(lyrixa)}")
                window.attach_lyrixa(lyrixa)
                # 🎯 Phase 1: Auto-Populate Plugin Editor - Set GUI interface reference
                lyrixa.gui_interface = window
                log("✅ Lyrixa agent attached to GUI with auto-population enabled")
            else:
                print("❌ DEBUG: lyrixa is None or undefined!")
                log("❌ Lyrixa is not available for attachment", "error")

            # 🔌 Update GUI plugin display with discovered plugins
            try:
                if hasattr(window, "refresh_plugin_discovery"):
                    window.refresh_plugin_discovery()
                    log("✅ GUI plugin display updated with discovered plugins")
                else:
                    log("⚠️ GUI plugin refresh method not available", "warning")
            except Exception as e:
                log(f"⚠️ Could not refresh GUI plugin display: {e}", "warning")

            # 🧩 Plugin Editor Tab (Built-in to Hybrid UI)
            try:
                # Note: Plugin Editor tab is now built-in to the hybrid UI (Tab 7/11)
                # No need to add it dynamically - it's always present
                log("✅ Plugin Editor tab available (built-in to hybrid UI)")
            except Exception as e:
                log(f"⚠️ Plugin Editor tab verification: {e}", "warning")

            # Update all dashboard components using modular methods
            window.update_dashboard_metrics()

            # Update individual status displays using modular methods
            window.update_intelligence_status()
            window.update_runtime_status()
            window.update_agent_status()
            window.update_performance_metrics()

            # Populate the model dropdown if available
            try:
                if hasattr(window, "populate_model_dropdown"):
                    window.populate_model_dropdown()
                    log("✅ Model dropdown populated")
            except Exception as e:
                log(f"⚠️ Could not populate model dropdown: {e}", "warning")

            # Initialize background monitoring using modular methods
            if hasattr(window, "init_background_monitors"):
                window.init_background_monitors()
                log("✅ Background monitoring initialized")

            loop.close()
            log("🎯 GUI initialization complete")

        except Exception as e:
            log(f"❌ Initialization error: {e}", "error")
            import traceback

            traceback.print_exc()

    # Use QTimer to run initialization after GUI is shown
    from PySide6.QtCore import QTimer

    QTimer.singleShot(500, initialize_and_attach)  # Delay to let GUI fully load

    sys.exit(app.exec())


if __name__ == "__main__":
    log("🚀 Launching Lyrixa Desktop Interface...")

    # Start API server and wait for it to be ready
    log("🔧 Starting Enhanced API server first...")
    api_ready = run_self_improvement_api()

    if not api_ready:
        log("⚠️ API server not ready - some features may not work", "warning")

    log("🎮 Starting GUI...")
    launch_gui()
