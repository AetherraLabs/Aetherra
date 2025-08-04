"""
Aetherra OS Bootstrap Script
============================
Bootstraps all core systems and brings Aetherra online.

This script is the primary entry point for activating the AI-native OS.

Author: Aetherra Labs
"""

import sys
import time
import traceback

from aetherra_core.config import config_loader

# Core System Imports
from aetherra_core.engine import lyrixa_engine
from aetherra_core.memory import memory_system
from aetherra_core.orchestration import scheduler
from aetherra_core.orchestration import plugin_manager

# Optional GUI Support
try:
    from lyrixa.gui import main_gui

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# Optional Self-Metrics
try:
    from aetherra_core.self_metrics_dashboard import metrics_logger

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


def aetherra_startup():
    print("🚀 Starting Aetherra OS...")

    # Load Configuration
    config = config_loader.load_config()

    # Initialize Memory System
    print("🧠 Initializing Quantum Memory System...")
    memory_system.initialize()

    # Load Plugins
    print("🔌 Loading Plugin Ecosystem...")
    plugin_manager.load_all_plugins()

    # Initialize Scheduler
    print("📅 Initializing Task Scheduler...")
    scheduler.initialize_schedule()

    # Launch Lyrixa Intelligence
    print("🤖 Launching Lyrixa Intelligence Core...")
    lyrixa_engine.boot()

    # Start GUI (if available)
    if GUI_AVAILABLE and config.get("gui_enabled", True):
        print("🖥️ Launching Lyrixa Interface...")
        main_gui.launch_gui()

    # Start Self-Metrics Logging (optional)
    if METRICS_AVAILABLE:
        print("📊 Starting Self-Metrics Dashboard...")
        metrics_logger.start_monitoring()

    print("[OK] Aetherra OS is now ONLINE.")
    return True


if __name__ == "__main__":
    try:
        success = aetherra_startup()
        if success:
            print("🟢 System Startup Completed Successfully.")
        else:
            print("[WARN] Startup encountered issues.")
    except Exception as e:
        print("❌ Aetherra Startup Failed:")
        traceback.print_exc()
        sys.exit(1)
