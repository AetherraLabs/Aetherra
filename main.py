"""
Aetherra Unified Bootstrapper
============================

This script initializes Lyrixa, the memory engine, and the UI/dashboard components.
Edit this file to customize startup order or add new system modules.
"""

import sys
from pathlib import Path

# Add Aetherra package to sys.path
sys.path.insert(0, str(Path(__file__).parent / "Aetherra"))

# --- Core System Imports ---
try:
    from lyrixa.launcher import launch_lyrixa
except ImportError:
    launch_lyrixa = None
    print("[WARN] Lyrixa launcher not found.")

try:
    from memory.QuantumEnhancedMemoryEngine.engine import QuantumEnhancedMemoryEngine
except ImportError:
    QuantumEnhancedMemoryEngine = None
    print("[WARN] QuantumEnhancedMemoryEngine not found.")

try:
    from gui.web_interface_server import run_server
except ImportError:
    run_server = None
    print("[WARN] Web interface server not found.")


def main():
    print("\n=== Aetherra Unified Bootstrapper ===\n")
    # Initialize memory engine
    if QuantumEnhancedMemoryEngine:
        memory_engine = QuantumEnhancedMemoryEngine()
        print("[OK] QuantumEnhancedMemoryEngine initialized.")
    else:
        memory_engine = None

    # Launch Lyrixa core
    if launch_lyrixa:
        print("[OK] Launching Lyrixa core...")
        launch_lyrixa(memory_engine=memory_engine)
    else:
        print("[WARN] Lyrixa core not launched.")

    # Start web UI/dashboard
    if run_server:
        print("[OK] Starting web interface server...")
        run_server()
    else:
        print("[WARN] Web interface server not started.")


if __name__ == "__main__":
    main()
