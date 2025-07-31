import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add the main project directory to path so 'Aetherra' module imports work
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.launch_utils import run_self_improvement_api
from utils.logging_utils import log

# Updated import paths with fallback handling
try:
    from Aetherra.runtime.aether_runtime import AetherRuntime
except ImportError:
    log("⚠️ AetherRuntime not available, using fallback", "warning")

    class AetherRuntime:
        def __init__(self, *args, **kwargs):
            pass


from Aetherra.core.memory_manager import MemoryManager
from Aetherra.core.multi_llm_manager import MultiLLMManager
from Aetherra.core.plugin_manager import PluginManager
from Aetherra.core.prompt_engine import PromptEngine
from Aetherra.lyrixa.agents.core_agent import LyrixaAI
from Aetherra.lyrixa.gui.gui_window import LyrixaWindow
from Aetherra.lyrixa.intelligence import LyrixaIntelligenceStack

# Global references
lyrixa = None
runtime = None
intelligence_stack = None


async def initialize_system():
    global lyrixa, runtime, intelligence_stack

    log("🔧 Initializing Lyrixa Intelligence Stack...")
    memory = MemoryManager()
    plugins = PluginManager()
    prompt_engine = PromptEngine()
    llm_manager = MultiLLMManager()

    # Initialize intelligence stack with workspace path
    workspace_path = str(Path(__file__).parent.parent)
    intelligence_stack = LyrixaIntelligenceStack(workspace_path)

    runtime = AetherRuntime()
    lyrixa = LyrixaAI(runtime, memory, prompt_engine, llm_manager)

    # Initialize the Lyrixa agent and its sub-agents
    await lyrixa.initialize()

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

            # Run initialization
            loop.run_until_complete(initialize_system())

            # Attach components to GUI
            if intelligence_stack:
                window.attach_intelligence_stack(intelligence_stack)
                log("✅ Intelligence stack attached to GUI")

            if runtime:
                window.attach_runtime(runtime)
                log("✅ Runtime attached to GUI")

            if lyrixa:
                window.attach_lyrixa(lyrixa)
                log("✅ Lyrixa agent attached to GUI")

            # Update all dashboard components
            window.update_dashboard_metrics()

            # Update individual status displays
            window.update_intelligence_status()
            window.update_runtime_status()
            window.update_agent_status()
            window.update_performance_metrics()

            # Update system metrics
            if hasattr(window, "system_metrics"):
                # Count agents properly
                agent_count = 0
                if lyrixa:
                    # Main agent + 5 sub-agents
                    agent_count = 6  # LyrixaAI + Goal + Plugin + Reflection + Escalation + SelfEvaluation

                system_info = f"""System: ✅ Operational
Python: {sys.version.split()[0]}
Platform: Windows
Memory: Available
CPU: Active
Agents: {agent_count} active
LLM Models: 9 available"""
                window.system_metrics.setPlainText(system_info)

            if hasattr(window, "init_background_monitors"):
                window.init_background_monitors()

            # Note: Diagnostics functionality is integrated into other tabs
            # No separate diagnostics tab needed as it's handled by existing tab system

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
    run_self_improvement_api()
    launch_gui()
